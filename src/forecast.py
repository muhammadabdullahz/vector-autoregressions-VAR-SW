import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.ar_model import AutoReg
from src import config as C


def target_value(df, h, origin):
    """Actual outcomes: average inflation over the next h quarters; u and R at quarter origin+h."""
    window = df.iloc[origin + 1: origin + h + 1]
    return np.array([window["inflation"].mean(),
                     window["unemployment"].iloc[-1],
                     window["fedfunds"].iloc[-1]])


def make_forecasts(df, h, origin, rw_inflation="last"):
    train = df.iloc[: origin + 1]                 # expanding window from 1960Q1
    out = {}

    # VAR(4): iterate forward h steps, then average inflation
    var_fit = VAR(train).fit(C.NLAGS, trend="c")
    f = var_fit.forecast(train.values[-C.NLAGS:], steps=h)
    out["VAR"] = np.array([f[:, 0].mean(), f[-1, 1], f[-1, 2]])

    # Univariate AR(4) for each variable
    ar = []
    for c in C.NAMES:
        path = AutoReg(train[c].values, lags=C.NLAGS, trend="c").fit().predict(
            start=len(train), end=len(train) + h - 1)
        ar.append(path.mean() if c == "inflation" else path[-1])
    out["AR"] = np.array(ar)

    # Random walk ("no change")
    infl_rw = train["inflation"].iloc[-1] if rw_inflation == "last" else train["inflation"].iloc[-4:].mean()
    out["RW"] = np.array([infl_rw, train["unemployment"].iloc[-1], train["fedfunds"].iloc[-1]])
    return out


def forecast_table(df, rw_inflation="last"):
    """Table 2: RMSE by variable, horizon and model (targets 1985Q1-2000Q4)."""
    targets = pd.period_range(C.FIRST_TARGET, C.LAST_TARGET, freq="Q")

    results = []
    for h in C.FORECAST_HORIZONS:
        errors = {m: [] for m in ["RW", "AR", "VAR"]}
        for target in targets:
            origin = df.index.get_loc(target) - h
            actual = target_value(df, h, origin)
            fc = make_forecasts(df, h, origin, rw_inflation)
            for m in errors:
                errors[m].append(fc[m] - actual)
        n_fc = len(errors["VAR"])
        assert n_fc == len(targets) == 64
        for j, v in enumerate(C.NAMES):
            row = {"variable": v, "h": h, "n": n_fc}
            for m in ["RW", "AR", "VAR"]:
                row[m] = np.sqrt(np.mean(np.array(errors[m])[:, j] ** 2))
            results.append(row)

    return pd.DataFrame(results).set_index(["variable", "h"])


def rw_rmse(df, h, how):
    """RMSE of the random-walk forecast under two definitions of RW inflation."""
    errs = []
    for target in pd.period_range(C.FIRST_TARGET, C.LAST_TARGET, freq="Q"):
        origin = df.index.get_loc(target) - h
        actual = target_value(df, h, origin)
        infl = df["inflation"].iloc[origin] if how == "last" else df["inflation"].iloc[origin - 3: origin + 1].mean()
        fc = np.array([infl, df["unemployment"].iloc[origin], df["fedfunds"].iloc[origin]])
        errs.append(fc - actual)
    return np.sqrt(np.mean(np.array(errs) ** 2, axis=0))


def rw_check(df, pub_table2):
    """Which RW inflation definition matches the paper?"""
    hs = C.FORECAST_HORIZONS
    return pd.DataFrame({
        "h": hs,
        "RW infl (last)": [rw_rmse(df, h, "last")[0] for h in hs],
        "RW infl (avg4)": [rw_rmse(df, h, "avg4")[0] for h in hs],
        "published": pub_table2.loc["inflation", "RW"].values,
    })
