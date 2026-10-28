import pandas as pd
import pandera.pandas as pa
from pandera import Check

from credit_drift.config import FEATURES


def _features_have_no_nulls(frame: pd.DataFrame) -> bool:
    return bool(frame[FEATURES].notna().all().all())


FEATURE_SCHEMA = pa.DataFrameSchema(
    {
        "CODE_GENDER": pa.Column(str, Check.isin(["F", "M", "XNA"]), nullable=False),
        "AMT_INCOME_TOTAL": pa.Column(float, Check.greater_than(0), nullable=False),
        "AMT_CREDIT": pa.Column(float, Check.greater_than(0), nullable=False),
        "AMT_ANNUITY": pa.Column(float, Check.greater_than(0), nullable=False),
        "AGE_YEARS": pa.Column(float, Check.in_range(18, 100), nullable=False),
        "CNT_FAM_MEMBERS": pa.Column(float, Check.in_range(1, 20), nullable=False),
    },
    checks=[Check(_features_have_no_nulls, error="Há valores nulos nas features")],
    strict=True,
    coerce=True,
    name="credit_application_feature_contract",
)


def validate_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Valida as features e levanta um erro Pandera quando alguma regra falha."""
    return FEATURE_SCHEMA.validate(frame, lazy=True)
