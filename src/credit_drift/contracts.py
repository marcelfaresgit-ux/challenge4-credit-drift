import pandera.pandas as pa
from pandera import Check

from credit_drift.config import FEATURES

FEATURE_SCHEMA = pa.DataFrameSchema(
    {
        "CODE_GENDER": pa.Column(str, Check.isin(["F", "M", "XNA"]), nullable=False),
        "AMT_INCOME_TOTAL": pa.Column(float, Check.greater_than(0), nullable=False),
        "AMT_CREDIT": pa.Column(float, Check.greater_than(0), nullable=False),
        "AMT_ANNUITY": pa.Column(float, Check.greater_than(0), nullable=False),
        "AGE_YEARS": pa.Column(float, Check.in_range(18, 100), nullable=False),
        "CNT_FAM_MEMBERS": pa.Column(float, Check.in_range(1, 20), nullable=False),
    },
    checks=[Check(lambda df: df[FEATURES].notna().all().all(), error="Features contain nulls")],
    strict=True,
    coerce=True,
    name="credit_application_feature_contract",
)


def validate_features(frame):
    """Validate the feature contract; raises a Pandera SchemaError on violations."""
    return FEATURE_SCHEMA.validate(frame, lazy=True)
