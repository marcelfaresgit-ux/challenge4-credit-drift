import numpy as np

from credit_drift.config import FEATURES
from credit_drift.drift import calculate_drift, classification_metrics, simulate_production
from credit_drift.model import build_model


def test_model_trains_and_returns_valid_classification_metrics(credit_frame):
    model = build_model()
    model.fit(credit_frame[FEATURES], credit_frame["TARGET"])
    probabilities = model.predict_proba(credit_frame[FEATURES])[:, 1]
    metrics = classification_metrics(credit_frame["TARGET"], probabilities)

    assert probabilities.shape == (len(credit_frame),)
    assert np.all((probabilities >= 0) & (probabilities <= 1))
    assert 0 <= metrics["roc_auc"] <= 1
    assert metrics["brier_score"] >= 0


def test_production_simulation_changes_features_and_outcomes(credit_frame):
    production = simulate_production(credit_frame)

    assert (production["AMT_INCOME_TOTAL"] > credit_frame["AMT_INCOME_TOTAL"]).all()
    assert (production["AMT_CREDIT"] > credit_frame["AMT_CREDIT"]).all()
    assert set(production["TARGET"].unique()) <= {0, 1}
    assert not production["TARGET"].equals(credit_frame["TARGET"])


def test_drift_statistics_report_ks_and_psi(credit_frame):
    production = simulate_production(credit_frame)
    result = calculate_drift(credit_frame[FEATURES], production[FEATURES])

    assert {"Kolmogorov-Smirnov", "PSI"} <= set(result["test"])
    assert "AMT_INCOME_TOTAL" in set(result["feature"])
    assert result["statistic"].notna().all()
