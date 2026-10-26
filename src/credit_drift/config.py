from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DATA = ROOT / "data" / "raw" / "application_train.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
ARTIFACTS_DIR = ROOT / "data" / "artifacts"
REPORTS_DIR = ROOT / "reports" / "generated"
LOGS_DIR = ROOT / "logs"

FEATURES = [
    "CODE_GENDER",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "AGE_YEARS",
    "CNT_FAM_MEMBERS",
]
NUMERIC_FEATURES = FEATURES[1:]
CATEGORICAL_FEATURES = [FEATURES[0]]
TARGET = "TARGET"
ID_COLUMN = "SK_ID_CURR"
RANDOM_STATE = 42
MAX_ROWS = 60000
