from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import ks_2samp
from sklearn.metrics import brier_score_loss, roc_auc_score

from credit_drift.config import (
    ANNUITY_DRIFT_FACTOR,
    CREDIT_DRIFT_FACTOR,
    INCOME_DRIFT_FACTOR,
    KS_P_VALUE_THRESHOLD,
    NUMERIC_FEATURES,
    PSI_THRESHOLD,
    RANDOM_STATE,
)


def simulate_production(
    reference: pd.DataFrame, seed: int = RANDOM_STATE
) -> pd.DataFrame:
    """Simula mudanças nas features e na regra que determina a inadimplência."""
    rng = np.random.default_rng(seed)
    production = reference.copy().reset_index(drop=True)
    production["AMT_INCOME_TOTAL"] *= INCOME_DRIFT_FACTOR
    production["AMT_CREDIT"] *= CREDIT_DRIFT_FACTOR
    production["AMT_ANNUITY"] *= ANNUITY_DRIFT_FACTOR

    # Reamostra o resultado com uma regra de risco diferente para representar concept drift.
    # É uma simulação didática, não um resultado futuro observado do Home Credit.
    income_low = production["AMT_INCOME_TOTAL"].rank(pct=True).to_numpy() < 0.35
    age = production["AGE_YEARS"].to_numpy()
    base_rate = float(reference["TARGET"].mean())
    logits = np.log(base_rate / (1 - base_rate)) + 0.85 + 0.8 * income_low + 0.35 * (age < 30)
    probability = 1 / (1 + np.exp(-logits))
    production["TARGET"] = rng.binomial(1, probability)
    return production


def calculate_drift(
    reference: pd.DataFrame, production: pd.DataFrame
) -> pd.DataFrame:
    rows = []
    for column in NUMERIC_FEATURES:
        result = ks_2samp(reference[column], production[column], alternative="two-sided")
        rows.append(
            {
                "feature": column,
                "test": "Kolmogorov-Smirnov",
                "statistic": result.statistic,
                "p_value": result.pvalue,
                "drift_detected": bool(result.pvalue < KS_P_VALUE_THRESHOLD),
            }
        )
        # Calcula o PSI com faixas definidas pelos quantis da população de referência.
        edges = np.unique(np.quantile(reference[column], np.linspace(0, 1, 11)))
        if len(edges) > 2:
            ref_counts = np.histogram(reference[column], bins=edges)[0].astype(float)
            cur_counts = np.histogram(production[column], bins=edges)[0].astype(float)
            ref_share = (ref_counts + 1e-6) / (ref_counts.sum() + 1e-6 * len(ref_counts))
            cur_share = (cur_counts + 1e-6) / (cur_counts.sum() + 1e-6 * len(cur_counts))
            psi = float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))
            rows.append(
                {
                    "feature": column,
                    "test": "PSI",
                    "statistic": psi,
                    "p_value": np.nan,
                    "drift_detected": bool(psi >= PSI_THRESHOLD),
                }
            )
    return pd.DataFrame(rows)


def classification_metrics(
    y_true: pd.Series | np.ndarray, probabilities: np.ndarray
) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
    }
