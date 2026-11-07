import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.api import VAR
from src import config as C


def weights(res, kind):
    """Taylor-rule weights: ra = R - fp*inflation - fu*unemployment."""
    if kind == "backward":
        return 1.5 / 4, -1.25 / 4

    # Forward: coefficients of the 4-quarter-ahead forecast (average over next 4 quarters)
    A = np.zeros((12, 12))                    # companion matrix of the VAR(4)
    A[:3, :] = np.hstack(res.coefs)
    A[3:, :-3] = np.eye(9)
    F = np.linalg.matrix_power(A, 4)
    avg = lambda i: sum(F[3 * j + i, :3] for j in range(4)) / 4
    pp, pu, pr = avg(0)                       # inflation forecast on current (pi, u, R)
    up, uu, ur = avg(1)                       # unemployment forecast on current (pi, u, R)
    print("pp pu pr:", np.round([pp, pu, pr], 3), "| up uu ur:", np.round([up, uu, ur], 3))

    fp1, fu1 = 1.5, -1.25
    fr2 = fp1 * pr + fu1 * ur
    return (fp1 * pp + fu1 * up) / (1 - fr2), (fp1 * pu + fu1 * uu) / (1 - fr2)


def policy_irf(df, fp, fu):
    """Responses to the policy shock, scaled so the funds rate rises 1 pp on impact."""
    Y = pd.DataFrame({"ra": df["fedfunds"] - fp * df["inflation"] - fu * df["unemployment"],
                      "p": df["inflation"], "u": df["unemployment"]})
    out = VAR(Y).fit(C.NLAGS, trend="c").irf(C.IRF_HORIZON).orth_irfs[:, :, 0]   # first shock = policy shock
    ra, p, u = out.T
    r = ra + fp * p + fu * u                                                      # funds-rate response
    return {"infl": p / r[0], "unemp": u / r[0], "real": (r - p) / r[0]}


def figure2(back, fwd):
    panels = [("infl", "Response of Inflation", (-2.5, 0.5)),
              ("unemp", "Response of Unemployment", (-1, 1)),
              ("real", "Response of Real Interest Rates", (-2.5, 3.5))]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
    for ax, (key, title, ylim) in zip(axes, panels):
        ax.axhline(0, color="black", lw=0.8)
        ax.plot(back[key], color="darkblue", lw=2, label="Backward-looking Taylor rule (solid)")
        ax.plot(fwd[key], color="darkred", lw=2, ls="--", label="Forward-looking Taylor rule (dashed)")
        ax.set_ylim(ylim); ax.set_title(title)
        ax.set_xlabel("Lag"); ax.set_ylabel("Percent"); ax.grid(alpha=0.2)
    axes[0].legend(fontsize=7, frameon=False, loc="lower left")
    fig.suptitle("Figure 2. Impulse Responses of Monetary Policy Shocks for Different Taylor Rule Identifying Assumptions")
    plt.tight_layout()
    fig.savefig(C.OUT_FIGS / "figure2_replicated.png", dpi=150, bbox_inches="tight")
    plt.show()
