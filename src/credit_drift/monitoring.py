from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset

from credit_drift.config import FEATURES, LOGS_DIR, REPORTS_DIR
from credit_drift.contracts import validate_features
from credit_drift.data import load_applications
from credit_drift.drift import calculate_drift, classification_metrics, simulate_production
from credit_drift.model import build_model

logger = logging.getLogger("credit_drift")


def run_pipeline(max_rows: int = 60000) -> dict:
    start = time.perf_counter()
    for directory in (REPORTS_DIR,):
        directory.mkdir(parents=True, exist_ok=True)
    applications = load_applications(max_rows=max_rows)
    features = applications[FEATURES]
    validate_features(features)

    # A deterministic split represents a clean reference population and a later production batch.
    ordered = applications.sample(frac=1, random_state=42).reset_index(drop=True)
    cut = int(len(ordered) * 0.75)
    reference, holdout = ordered.iloc[:cut].copy(), ordered.iloc[cut:].copy()
    model = build_model()
    model.fit(reference[FEATURES], reference["TARGET"])
    base_prob = model.predict_proba(holdout[FEATURES])[:, 1]
    baseline_metrics = classification_metrics(holdout["TARGET"], base_prob)

    production = simulate_production(holdout)
    validate_features(production[FEATURES])
    production_prob = model.predict_proba(production[FEATURES])[:, 1]
    production_metrics = classification_metrics(production["TARGET"], production_prob)

    # Evidence of concept drift: the outcome rate and the model's measured quality change.
    drift = calculate_drift(reference[FEATURES], production[FEATURES])
    drift.to_csv(REPORTS_DIR / "drift_statistics.csv", index=False)
    report = Report([DataDriftPreset()], include_tests=True)
    snapshot = report.run(
        current_data=production[FEATURES], reference_data=reference[FEATURES],
        name="Home Credit - Data Drift"
    )
    snapshot.save_html(str(REPORTS_DIR / "evidently_data_drift.html"))

    timestamp = datetime.now(timezone.utc).isoformat()
    metrics = {
        "timestamp_utc": timestamp,
        "dataset": "Home Credit Default Risk / application_train.csv",
        "rows_loaded_after_contract_preparation": int(len(applications)),
        "reference_rows": int(len(reference)),
        "production_rows": int(len(production)),
        "reference_default_rate": float(reference["TARGET"].mean()),
        "production_default_rate": float(production["TARGET"].mean()),
        "baseline_metrics": baseline_metrics,
        "production_metrics": production_metrics,
        "drifted_feature_tests": int(drift["drift_detected"].sum()),
        "pipeline_duration_seconds": round(time.perf_counter() - start, 3),
        "validation_status": "passed",
    }
    (REPORTS_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    with (LOGS_DIR / "pipeline_events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps({"event": "pipeline_completed", **metrics}, ensure_ascii=False) + "\n")
    logger.info("Pipeline concluido: %s", json.dumps(metrics, ensure_ascii=False))
    return metrics


def demonstrate_contract_failure() -> str:
    """Inject representative bad rows and return the contract failure summary."""
    sample = load_applications(max_rows=100)[FEATURES].copy().reset_index(drop=True)
    sample.loc[0, "AGE_YEARS"] = 16
    sample.loc[1, "AMT_INCOME_TOTAL"] = -1
    sample.loc[2, "AMT_ANNUITY"] = float("nan")
    try:
        validate_features(sample)
    except Exception as exc:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        event = {
            "event": "contract_rejected_invalid_batch",
            "rows": int(len(sample)),
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
        }
        with (LOGS_DIR / "pipeline_events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        return str(exc)
    raise RuntimeError("O contrato deveria ter bloqueado o lote com dados invalidos.")
