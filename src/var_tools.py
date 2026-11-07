import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from src import config as C


def fit_var(df):
    """Reduced-form VAR(4) with a constant."""
    res = VAR(df).fit(C.NLAGS, trend="c")
    assert res.nobs == len(df) - C.NLAGS
    assert res.is_stable()
    return res


def granger_table(res):
    """Table 1.A: rows = predictor, columns = dependent variable (diagonal left blank)."""
    out = pd.DataFrame(np.nan, index=C.NAMES, columns=C.NAMES)
    for dep in C.NAMES:
        for reg in C.NAMES:
            if dep != reg:
                test = res.test_causality(caused=dep, causing=reg, kind="f")
                out.loc[reg, dep] = test.pvalue
    return out


def fevd_table(res):
    """Table 1.B: standard error and shock shares (%) at each horizon."""
    top = max(C.FEVD_HORIZONS)
    fe = res.fevd(top)
    mse = res.mse(top)                       # shape (top, 3, 3)

    rows = []
    for i, v in enumerate(C.NAMES):
        for h in C.FEVD_HORIZONS:
            shares = fe.decomp[i, h - 1, :] * 100
            rows.append([v, h, np.sqrt(mse[h - 1][i, i]), *shares])

    out = pd.DataFrame(rows, columns=["variable", "h", "SE", "pi shock", "u shock", "R shock"])
    out = out.set_index(["variable", "h"])

    # Every row must sum to 100
    assert np.allclose(out[["pi shock", "u shock", "R shock"]].sum(axis=1), 100)
    return out


def irf_results(res, repl=1000, seed=42):
    """Figure 1: orthogonalised IRFs with asymptotic and Monte Carlo bands."""
    P = np.linalg.cholesky(res.sigma_u)
    assert np.allclose(P @ P.T, res.sigma_u)      # Cholesky check
    scale = np.diag(P)

    irf = res.irf(C.IRF_HORIZON)
    point = irf.orth_irfs / scale
    se = irf.stderr(orth=True) / scale

    lower, upper = irf.errband_mc(orth=True, repl=repl, signif=0.32,
                                  rng=np.random.RandomState(seed))

    return {"point": point,
            "lower_a": point - se, "upper_a": point + se,
            "lower_mc": lower / scale, "upper_mc": upper / scale}


def adf_table(df):
    """ADF tests (diagnostic only; variables stay in levels)."""
    adf = {}
    for c in C.NAMES:
        result = adfuller(df[c], regression="c", autolag="AIC", result_object=False)
        adf[c] = {"ADF stat": result[0], "p-value": result[1]}
    return pd.DataFrame(adf).T
