from __future__ import annotations

from pathlib import Path

import pandas as pd

from credit_drift.config import FEATURES, ID_COLUMN, MAX_ROWS, RANDOM_STATE, RAW_DATA, TARGET

RAW_COLUMNS = [
    ID_COLUMN,
    "CODE_GENDER",
    "AMT_INCOME_TOTAL",
    "AMT_CREDIT",
    "AMT_ANNUITY",
    "DAYS_BIRTH",
    "CNT_FAM_MEMBERS",
    TARGET,
]


def load_applications(
    path: Path = RAW_DATA, max_rows: int | None = MAX_ROWS
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em {path}. Baixe application_train.csv do Kaggle; "
            "consulte docs/DATASET.md. O acesso exige login e aceite das regras da competição."
        )
    frame = pd.read_csv(path, usecols=RAW_COLUMNS)
    frame["AGE_YEARS"] = -frame.pop("DAYS_BIRTH") / 365.25
    frame["CODE_GENDER"] = frame["CODE_GENDER"].fillna("XNA").astype(str)
    frame = frame[[ID_COLUMN, *FEATURES, TARGET]]
    frame = frame.dropna(subset=[*FEATURES, TARGET]).copy()
    frame = frame.drop_duplicates(subset=[ID_COLUMN], keep="first")
    frame[TARGET] = frame[TARGET].astype(int)
    if max_rows and len(frame) > max_rows:
        frame = frame.sample(n=max_rows, random_state=RANDOM_STATE)
    return frame.reset_index(drop=True)
