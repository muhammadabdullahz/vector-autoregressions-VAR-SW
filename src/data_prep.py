import pandas as pd
from src import config as C


def load_data():
    raw = pd.read_excel(C.DATA_FILE, header=None)

    # Rows 0-1 are headers, data starts at row 2. Column 0 is the date.
    df = raw.iloc[2:, :4].copy()
    df.columns = ["date"] + C.NAMES
    df.index = pd.PeriodIndex(df["date"].str.upper(), freq="Q")   # "1960q1" -> 1960Q1
    df = df.drop(columns="date").astype(float)

    check_data(df)
    return df


def check_data(df):
    assert df.index.is_unique
    assert df.index.is_monotonic_increasing
    assert df.notna().all().all()
    assert len(df) == 164
    assert str(df.index[0]) == "1960Q1" and str(df.index[-1]) == "2000Q4"
