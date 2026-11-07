import pandas as pd
from src import config as C

# Table 1.A: rows = predictor, columns = dependent variable
table1a = pd.DataFrame([[0.00, 0.31, 0.00],
                        [0.02, 0.00, 0.00],
                        [0.27, 0.01, 0.00]], index=C.NAMES, columns=C.NAMES)

# Table 1.B
_rows = [
    ("inflation",    1, 0.96, 100,  0,  0), ("inflation",    4, 1.34, 88, 10,  2),
    ("inflation",    8, 1.75,  82, 17,  1), ("inflation",   12, 1.97, 82, 16,  2),
    ("unemployment", 1, 0.23,   1, 99,  0), ("unemployment", 4, 0.64,  0, 98,  2),
    ("unemployment", 8, 0.79,   7, 82, 11), ("unemployment",12, 0.92, 16, 66, 18),
    ("fedfunds",     1, 0.85,   2, 19, 79), ("fedfunds",     4, 1.84,  9, 50, 41),
    ("fedfunds",     8, 2.44,  12, 60, 28), ("fedfunds",    12, 2.63, 16, 59, 25),
]
table1b = pd.DataFrame(_rows, columns=["variable", "h", "SE", "pi shock", "u shock", "R shock"])
table1b = table1b.set_index(["variable", "h"])

# Table 2
table2 = pd.DataFrame({
    "variable": ["inflation"] * 3 + ["unemployment"] * 3 + ["fedfunds"] * 3,
    "h": [2, 4, 8] * 3,
    "RW":  [0.82, 0.73, 0.75, 0.34, 0.62, 1.12, 0.79, 1.36, 2.18],
    "AR":  [0.70, 0.65, 0.75, 0.28, 0.52, 0.95, 0.77, 1.25, 1.92],
    "VAR": [0.68, 0.63, 0.75, 0.29, 0.53, 0.78, 0.68, 1.07, 1.70],
}).set_index(["variable", "h"])
