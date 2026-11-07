import pandas as pd
from IPython.display import display
from src import config as C


def side_by_side(mine, pub):
    """For every column: Replicated | Published | Diff (replicated minus published)."""
    mine = mine.loc[pub.index, pub.columns]
    parts = {col: pd.DataFrame({"Replicated": mine[col],
                                "Published": pub[col],
                                "Diff": mine[col] - pub[col]})
             for col in pub.columns}
    return pd.concat(parts, axis=1)


def save_and_show(tbl, name, title):
    t = tbl.round(2)
    t.to_csv(C.OUT_TABLES / f"{name}.csv")
    t.to_html(C.OUT_TABLES / f"{name}.html")
    display(t.style.format("{:.2f}").set_caption(title))
