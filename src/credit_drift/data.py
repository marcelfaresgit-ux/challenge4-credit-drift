from __future__ import annotations

import time
from pathlib import Path

import pandas as pd

from credit_drift.config import FEATURES, ID_COLUMN, MAX_ROWS, RANDOM_STATE, RAW_DATA, TARGET
from credit_drift.events import record_event

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
    path: Path = RAW_DATA,
    max_rows: int | None = MAX_ROWS,
    *,
    record_events: bool = False,
) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em {path}. Baixe application_train.csv do Kaggle; "
            "consulte docs/DATASET.md. O acesso exige login e aceite das regras da competição."
        )
    ingestion_start = time.perf_counter()
    frame = pd.read_csv(path, usecols=RAW_COLUMNS)
    ingested_rows = len(frame)
    if record_events:
        record_event(
            "ingestion_completed",
            rows=ingested_rows,
            source=path.name,
            duration_seconds=round(time.perf_counter() - ingestion_start, 3),
            status="passed",
        )

    transformation_start = time.perf_counter()
    frame["AGE_YEARS"] = -frame.pop("DAYS_BIRTH") / 365.25
    frame["CODE_GENDER"] = frame["CODE_GENDER"].fillna("XNA").astype(str)
    frame = frame[[ID_COLUMN, *FEATURES, TARGET]]
    frame = frame.dropna(subset=[*FEATURES, TARGET]).copy()
    rows_after_cleaning = len(frame)
    frame = frame.drop_duplicates(subset=[ID_COLUMN], keep="first")
    rows_after_deduplication = len(frame)
    frame[TARGET] = frame[TARGET].astype(int)
    if max_rows and len(frame) > max_rows:
        frame = frame.sample(n=max_rows, random_state=RANDOM_STATE)
    result = frame.reset_index(drop=True)
    result.attrs["rows_read_from_source"] = ingested_rows
    if record_events:
        record_event(
            "transformation_completed",
            rows_in=ingested_rows,
            rows_after_cleaning=rows_after_cleaning,
            rows_after_deduplication=rows_after_deduplication,
            rows_out=len(result),
            duration_seconds=round(time.perf_counter() - transformation_start, 3),
            status="passed",
        )
    return result
