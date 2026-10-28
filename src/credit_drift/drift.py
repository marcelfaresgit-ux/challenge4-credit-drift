from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import brier_score_loss, roc_auc_score

from credit_drift.config import NUMERIC_FEATURES


def simulate_production(reference: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Create an auditable production scenario with feature and target mechanism drift."""
    rng = np.random.default_rng(seed)
    production = reference.copy().reset_index(drop=True)
    production["AMT_INCOME_TOTAL"] *= 1.30
    production["AMT_CREDIT"] *= 1.18
    production["AMT_ANNUITY"] *= 1.12

    # Concept drift: outcomes are resampled from a changed conditional risk mechanism.
    # This is an educational simulation, not observed future Home Credit data.
    income_low = production["AMT_INCOME_TOTAL"].rank(pct=True).to_numpy() < 0.35
    age = production["AGE_YEARS"].to_numpy()
    base_rate = float(reference["TARGET"].mean())
    logits = np.log(base_rate / (1 - base_rate)) + 0.85 + 0.8 * income_low + 0.35 * (age < 30)
    probability = 1 / (1 + np.exp(-logits))
    production["TARGET"] = rng.binomial(1, probability)
    return production


def calculate_drift(reference: pd.DataFrame, production: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for column in NUMERIC_FEATURES:
        result = ks_2samp(reference[column], production[column], alternative="two-sided")
        rows.append(
            {"feature": column, "test": "Kolmogorov-Smirnov", "statistic": result.statistic,
             "p_value": result.pvalue, "drift_detected": bool(result.pvalue < 0.05)}
        )
        # PSI with quantile bins defined on reference, including stable zero-count handling.
        edges = np.unique(np.quantile(reference[column], np.linspace(0, 1, 11)))
        if len(edges) > 2:
            ref_counts = np.histogram(reference[column], bins=edges)[0].astype(float)
            cur_counts = np.histogram(production[column], bins=edges)[0].astype(float)
            ref_share = (ref_counts + 1e-6) / (ref_counts.sum() + 1e-6 * len(ref_counts))
            cur_share = (cur_counts + 1e-6) / (cur_counts.sum() + 1e-6 * len(cur_counts))
            psi = float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))
            rows.append(
                {"feature": column, "test": "PSI", "statistic": psi, "p_value": np.nan,
                 "drift_detected": bool(psi >= 0.2)}
            )
    return pd.DataFrame(rows)


def classification_metrics(y_true, probabilities) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }
