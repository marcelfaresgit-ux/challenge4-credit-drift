import pytest
from pandera.errors import SchemaErrors

from credit_drift.config import FEATURES
from credit_drift.contracts import validate_features


def test_contract_accepts_valid_features(credit_frame):
    result = validate_features(credit_frame[FEATURES])
    assert len(result) == len(credit_frame)


def test_contract_rejects_invalid_age_income_and_missing_value(credit_frame):
    invalid = credit_frame[FEATURES].copy()
    invalid.loc[0, "AGE_YEARS"] = 16
    invalid.loc[1, "AMT_INCOME_TOTAL"] = -1
    invalid.loc[2, "AMT_ANNUITY"] = float("nan")

    with pytest.raises(SchemaErrors):
        validate_features(invalid)
