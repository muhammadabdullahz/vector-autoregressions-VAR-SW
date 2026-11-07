import pandas as pd
import matplotlib.pyplot as plt
from src import config as C

RECESSIONS = [("1960Q2", "1961Q1"), ("1969Q4", "1970Q4"), ("1973Q4", "1975Q1"),
              ("1980Q1", "1980Q3"), ("1981Q3", "1982Q4"), ("1990Q3", "1991Q1")]


def _save(fig, name):
    fig.savefig(C.OUT_FIGS / f"{name}.png", dpi=150, bbox_inches="tight")


def _shade(ax):
    for a, b in RECESSIONS:
        ax.axvspan(pd.Period(a).to_timestamp(), pd.Period(b).to_timestamp(how="end"),
                   color="grey", alpha=0.25, lw=0)


def eda_charts(df, res):
    x = df.index.to_timestamp()

    # Chart 1: the three series, recessions shaded
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    labels = ["Inflation (annualised %)", "Unemployment rate (%)", "Federal funds rate (%)"]
    for ax, c, lab in zip(axes, C.NAMES, labels):
        ax.plot(x, df[c], color="navy", lw=1.8)
        _shade(ax); ax.set_ylabel(lab); ax.grid(alpha=0.3)
    axes[0].set_title("Chart 1: Inflation, unemployment and the federal funds rate, 1960-2000 (grey = recessions)")
    plt.tight_layout(); _save(fig, "eda1_series"); plt.show()

    # Chart 2: smoothed inflation vs fed funds
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(x, df["inflation"].rolling(4).mean(), label="Inflation (4-quarter average)", color="firebrick")
    ax.plot(x, df["fedfunds"], label="Federal funds rate", color="navy")
    _shade(ax); ax.legend(); ax.grid(alpha=0.3); ax.set_ylabel("%")
    ax.set_title("Chart 2: The Fed funds rate follows inflation (the Taylor-rule idea)")
    _save(fig, "eda2_inflation_ff"); plt.show()

    # Chart 3: Phillips-curve scatter
    fig, ax = plt.subplots(figsize=(6, 5))
    sc = ax.scatter(df["unemployment"], df["inflation"], c=df.index.year, cmap="viridis", s=18)
    plt.colorbar(sc, label="Year")
    ax.set_xlabel("Unemployment rate (%)"); ax.set_ylabel("Inflation (annualised %)")
    ax.set_title("Chart 3: Unemployment vs inflation"); ax.grid(alpha=0.3)
    _save(fig, "eda3_phillips"); plt.show()

    # Chart 4: reduced-form residual correlations
    corr = pd.DataFrame(res.resid, columns=C.NAMES).corr()
    fig, ax = plt.subplots(figsize=(5, 4))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(3)); ax.set_xticklabels(C.NAMES, rotation=30)
    ax.set_yticks(range(3)); ax.set_yticklabels(C.NAMES)
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center")
    plt.colorbar(im); ax.set_title("Chart 4: Correlation of reduced-form residuals")
    plt.tight_layout(); _save(fig, "eda4_resid_corr"); plt.show()


def figure1(r):
    """3x3 impulse responses. Rows = shock, columns = response."""
    titles = ["Inflation", "Unemployment", "Federal Funds Rate"]
    q = range(C.IRF_HORIZON + 1)
    fig, axes = plt.subplots(3, 3, figsize=(12, 9), sharex=True)

    for shock in range(3):
        for resp in range(3):
            ax = axes[shock, resp]
            ax.fill_between(q, r["lower_a"][:, resp, shock], r["upper_a"][:, resp, shock],
                            color="#6495ED", alpha=0.22, label="±1 s.e. (asymptotic)")
            ax.plot(q, r["point"][:, resp, shock], color="#0B1F4D", lw=2, label="Point estimate")
            ax.plot(q, r["lower_mc"][:, resp, shock], color="#A61C2D", ls="--", lw=1.2, label="Monte Carlo 68%")
            ax.plot(q, r["upper_mc"][:, resp, shock], color="#A61C2D", ls="--", lw=1.2)
            ax.axhline(0, color="black", lw=0.7)
            ax.set_title(f"{titles[shock]} shock to {titles[resp]}", fontsize=9)
            ax.grid(axis="y", alpha=0.2)
            if shock == 2:
                ax.set_xlabel("Quarters")

    axes[0, 0].legend(fontsize=7, frameon=False)
    fig.suptitle("Figure 1: Orthogonalised Impulse Responses", fontsize=13)
    plt.tight_layout(); _save(fig, "figure1_irf"); plt.show()
