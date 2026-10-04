"""Per-pair liquidity and volatility measures on bars, in basis points."""

import numpy as np
import pandas as pd

from config import K_BARS, LABELS, M, REGIMES

K_CS = 3 - 2 * np.sqrt(2)


def cs(high, low):
    """Corwin-Schultz (2012) spread from bars t-1, t:
    alpha = (sqrt(2 beta) - sqrt(beta)) / k - sqrt(gamma / k), k = 3 - 2 sqrt 2,
    S = 2 (e^alpha - 1) / (1 + e^alpha), clipped at 0, times m."""
    hl = np.log(high / low) ** 2
    beta = hl + hl.shift(1)
    gamma = np.log(np.maximum(high, high.shift(1)) / np.minimum(low, low.shift(1))) ** 2
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / K_CS - np.sqrt(gamma / K_CS)
    return M * (2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))).clip(lower=0)


def kyle(close, quote_volume, bars):
    """Kyle-Obizhaeva illiquidity: m (mean r^2 / sum quote volume)^(1/3) over `bars` bars; zero volume -> NaN."""
    r2 = np.log(close).diff() ** 2
    qv = quote_volume.rolling(bars).sum()
    return M * (r2.rolling(bars).mean() / qv.where(qv > 0)) ** (1 / 3)


def rv(close, bars):
    """Realized volatility: m sqrt(sum r^2) over `bars` bars."""
    return M * np.sqrt((np.log(close).diff() ** 2).rolling(bars).sum())


def liquidity(df, reg):
    """Table 2 per pair x regime: mean K and $ million per day (sum quote volume / days in regime).
    CS is not reported in levels (zero on single-trade bars)."""
    rows = {}
    for pair, label in LABELS.items():
        k = kyle(df[f"{pair}_close"], df[f"{pair}_quote_volume"], K_BARS)
        for r in REGIMES:
            in_r = reg == r
            rows[(label, r)] = {"K": k[in_r].mean(),
                                "$M/day": df.loc[in_r, f"{pair}_quote_volume"].sum() / (in_r.sum() / 1440) / 1e6}
    return pd.DataFrame(rows).T
