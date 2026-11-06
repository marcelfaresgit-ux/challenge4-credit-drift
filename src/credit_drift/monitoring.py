from __future__ import annotations

import json
import logging
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from evidently import Report
from evidently.presets import DataDriftPreset
from pandera.errors import SchemaErrors

from credit_drift.config import FEATURES, RANDOM_STATE, REPORTS_DIR
from credit_drift.contracts import validate_features
from credit_drift.data import load_applications
from credit_drift.drift import calculate_drift, classification_metrics, simulate_production
from credit_drift.events import record_event
from credit_drift.model import build_model

logger = logging.getLogger("credit_drift")


def run_pipeline(max_rows: int = 60000) -> dict[str, object]:
    start = time.perf_counter()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    applications = load_applications(max_rows=max_rows, record_events=True)
    features = applications[FEATURES]
    validation_start = time.perf_counter()
    validate_features(features)
    record_event(
        "validation_completed",
        rows=len(features),
        status="passed",
        duration_seconds=round(time.perf_counter() - validation_start, 3),
    )

    # Use a repeatable holdout, then simulate a later production batch from it.
    ordered = applications.sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
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
    drift_start = time.perf_counter()
    drift = calculate_drift(reference[FEATURES], production[FEATURES])
    drift.to_csv(REPORTS_DIR / "drift_statistics.csv", index=False)
    report = Report([DataDriftPreset()], include_tests=True)
    snapshot = report.run(
        current_data=production[FEATURES], reference_data=reference[FEATURES],
        name="Home Credit - Data Drift"
    )
    report_path = REPORTS_DIR / "evidently_data_drift.html"
    with tempfile.NamedTemporaryFile(
        dir=REPORTS_DIR, suffix=".html", delete=False
    ) as temporary_report:
        temporary_report_path = temporary_report.name
    snapshot.save_html(temporary_report_path)
    Path(temporary_report_path).replace(report_path)
    record_event(
        "drift_analysis_completed",
        rows_reference=len(reference),
        rows_production=len(production),
        tests_run=len(drift),
        drifted_feature_tests=int(drift["drift_detected"].sum()),
        duration_seconds=round(time.perf_counter() - drift_start, 3),
        status="passed",
    )

    metrics = {
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "dataset": "Home Credit Default Risk / application_train.csv",
        "rows_read_from_source": int(applications.attrs["rows_read_from_source"]),
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
    record_event("pipeline_completed", status="passed", **metrics)
    logger.info("Pipeline concluído: %s", json.dumps(metrics, ensure_ascii=False))
    return metrics


def demonstrate_contract_failure() -> str:
    """Envia um lote sintético inválido ao contrato e registra a rejeição."""
    sample = pd.DataFrame(
        {
            "CODE_GENDER": ["F", "M", "F", "M"],
            "AMT_INCOME_TOTAL": [50000.0, -1.0, 70000.0, 90000.0],
            "AMT_CREDIT": [100000.0, 120000.0, 140000.0, 160000.0],
            "AMT_ANNUITY": [10000.0, 12000.0, float("nan"), 16000.0],
            "AGE_YEARS": [30.0, 40.0, 16.0, 50.0],
            "CNT_FAM_MEMBERS": [2.0, 3.0, 4.0, 2.0],
        }
    )[FEATURES]
    try:
        validate_features(sample)
    except SchemaErrors as exc:
        failures = exc.failure_cases
        violated_rules = sorted(
            {
                f"{row.column}: {row.check}"
                for row in failures[["column", "check"]].dropna().itertuples(index=False)
                if row.column in FEATURES
            }
        )
        record_event(
            "contract_rejected_invalid_batch",
            rows=int(len(sample)),
            error_type=type(exc).__name__,
            violated_rules=violated_rules,
            status="rejected",
        )
        return "Lote rejeitado pelo Pandera. Regras violadas: " + "; ".join(violated_rules)
    raise RuntimeError("O contrato deveria ter bloqueado o lote com dados inválidos.")
