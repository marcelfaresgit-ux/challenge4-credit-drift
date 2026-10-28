import pandas as pd
import pytest

from credit_drift.data import load_applications


def test_load_applications_derives_age_and_drops_duplicate_ids(tmp_path):
    source = pd.DataFrame(
        {
            "SK_ID_CURR": [1, 2, 2, 4],
            "CODE_GENDER": ["F", "M", "M", "F"],
            "AMT_INCOME_TOTAL": [50000, 70000, 70000, 80000],
            "AMT_CREDIT": [10000, 20000, 20000, 30000],
            "AMT_ANNUITY": [1000, 2000, 2000, 3000],
            "DAYS_BIRTH": [-3652, -7305, -7305, -10958],
            "CNT_FAM_MEMBERS": [1, 2, 2, 3],
            "TARGET": [0, 1, 1, 0],
        }
    )
    path = tmp_path / "application_train.csv"
    source.to_csv(path, index=False)

    result = load_applications(path=path, max_rows=None)

    assert len(result) == 3
    assert result["SK_ID_CURR"].is_unique
    assert result.loc[0, "AGE_YEARS"] == pytest.approx(3652 / 365.25)


def test_load_applications_explains_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError, match="application_train.csv"):
        load_applications(path=tmp_path / "missing.csv")
