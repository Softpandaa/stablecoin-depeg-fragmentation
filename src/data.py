"""Load the one-minute klines, aggregate bars, and build the cross-quote decomposition."""

import numpy as np
import pandas as pd

from config import BU, COINS, DATA, M

AGG = {"high": "max", "low": "min", "close": "last", "volume": "sum", "quote_volume": "sum"}


def load():
    """Read the Binance.US one-minute file, indexed by UTC minute."""
    return pd.read_csv(DATA, index_col="time", parse_dates=["time"])


def to_bars(df, freq):
    """Aggregate one-minute klines to `freq` bars (high max, low min, close last, volumes summed)."""
    rules = {c: AGG[c.split("_", 2)[2]] for c in df.columns}
    return df.resample(freq).agg(rules)


def decompose(df, coin):
    """D = m(ln B/Q - ln B/U), delta = m ln Q/U, b = -D - delta; F = all legs traded, FF = F_t F_{t-1}."""
    bq, qu = COINS[coin]
    out = pd.DataFrame(index=df.index)
    out["D"] = M * (np.log(df[f"{bq}_close"]) - np.log(df[f"{BU}_close"]))
    out["delta"] = M * np.log(df[f"{qu}_close"])
    out["b"] = -out["D"] - out["delta"]
    out["F"] = (df[[f"{p}_volume" for p in (BU, bq, qu)]] > 0).all(axis=1)
    out["FF"] = out["F"] & out["F"].shift(1, fill_value=False)
    return out
