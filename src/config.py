from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data/raw/SW2001_Data.xlsx"
OUT_TABLES = ROOT / "outputs/tables"
OUT_FIGS = ROOT / "outputs/figures"

NAMES = ["inflation", "unemployment", "fedfunds"]

NLAGS = 4
IRF_HORIZON = 24
FEVD_HORIZONS = [1, 4, 8, 12]
FORECAST_HORIZONS = [2, 4, 8]
FIRST_TARGET = "1985Q1"
LAST_TARGET = "2000Q4"

OUT_TABLES.mkdir(parents=True, exist_ok=True)
OUT_FIGS.mkdir(parents=True, exist_ok=True)
