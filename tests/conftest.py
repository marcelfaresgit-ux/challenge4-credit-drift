import numpy as np
import pandas as pd
import pytest

from credit_drift.config import FEATURES


@pytest.fixture
def credit_frame() -> pd.DataFrame:
    rng = np.random.default_rng(17)
    rows = 300
    credit = rng.uniform(10000, 200000, rows)
    income = rng.uniform(20000, 250000, rows)
    age = rng.uniform(21, 75, rows)
    default_probability = 1 / (1 + np.exp(-(-2.0 + (credit - 90000) / 35000)))
    target = rng.binomial(1, default_probability)
    frame = pd.DataFrame(
        {
            "CODE_GENDER": rng.choice(["F", "M"], rows),
            "AMT_INCOME_TOTAL": income,
            "AMT_CREDIT": credit,
            "AMT_ANNUITY": credit / rng.uniform(5, 15, rows),
            "AGE_YEARS": age,
            "CNT_FAM_MEMBERS": rng.integers(1, 7, rows).astype(float),
            "TARGET": target,
        }
    )
    return frame[[*FEATURES, "TARGET"]]
