"""Half-life AR(1) (Table 4) and the transmission regression (Table 5), OLS with HAC errors."""

import numpy as np
import pandas as pd
import statsmodels.api as sm

from config import BU, COINS
from data import decompose
from measures import cs, kyle, rv

Z = ("CS B/Q", "K B/Q", "K Q/U")


def panel(bars, coin, k_bars, rv_bars):
    """Decomposition of `coin` plus lagged regressors: b_l, delta_l, the three z, RV of B/U; dy = b_t - b_{t-1}."""
    bq, qu = COINS[coin]
    p = decompose(bars, coin)
    p["dy"] = p["b"].diff()
    p["b_l"] = p["b"].shift()
    p["delta_l"] = p["delta"].shift()
    p["CS B/Q"] = cs(bars[f"{bq}_high"], bars[f"{bq}_low"]).shift()
    for name, pair in (("K B/Q", bq), ("K Q/U", qu)):
        p[name] = kyle(bars[f"{pair}_close"], bars[f"{pair}_quote_volume"], k_bars).shift()
    p["RV"] = rv(bars[f"{BU}_close"], rv_bars).shift()
    return p


def half_life(p, rows, x):
    """x_t = c + rho x_{t-1} + e_t by OLS on `rows`; HL = ln 0.5 / ln rho in bars."""
    s = p.loc[rows, [x, f"{x}_l"]].dropna()
    rho = sm.OLS(s[x], sm.add_constant(s[f"{x}_l"])).fit().params[f"{x}_l"]
    return np.log(0.5) / np.log(rho)


def transmission(p, rows, lags, z=Z):
    """db_t = a + beta b_{t-1} + (lam0 + lam1' z_{t-1}) delta_{t-1} + theta' z_{t-1} + kappa RV_{t-1} + e_t.
    z and RV standardized over the estimation sample.
    Returns R^2, coefficients, t-statistics and the Wald chi2 p-value of lam1 = 0."""
    cols = ["dy", "b_l", "delta_l", *z, "RV"]
    s = p.loc[rows, cols].dropna()
    zt = (s[list(z)] - s[list(z)].mean()) / s[list(z)].std()
    X = pd.concat([s["b_l"].rename("beta"), s["delta_l"].rename("lam0"),
                   zt.mul(s["delta_l"], axis=0).add_prefix("lam1 "), zt.add_prefix("theta "),
                   ((s["RV"] - s["RV"].mean()) / s["RV"].std()).rename("kappa")], axis=1)
    res = sm.OLS(s["dy"], sm.add_constant(X)).fit(cov_type="HAC", cov_kwds={"maxlags": lags})
    R = np.eye(len(res.params))[res.params.index.str.startswith("lam1")]
    return {"r2": res.rsquared, "coef": res.params, "t": res.tvalues,
            "p_lam1": float(res.wald_test(R, use_f=False, scalar=True).pvalue)}
