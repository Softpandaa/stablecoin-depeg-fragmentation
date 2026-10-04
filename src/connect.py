"""VAR connectedness (generalized FEVD, Diebold-Yilmaz 2012) and Granger causality (Table 6)."""

import numpy as np
import pandas as pd
from statsmodels.tsa.api import VAR

from config import FEVD_H, LABELS, M


def returns(df, freq):
    """m x log returns of the last close per `freq` bar for the five pairs."""
    close = df[[f"{p}_close" for p in LABELS]].resample(freq).last()
    close.columns = list(LABELS.values())
    return M * np.log(close).diff()


def gfevd(res):
    """Generalized FEVD (Pesaran-Shin 1998), horizon H, rows normalized, x100:
    theta_ij = s_jj^-1 sum_h (e_i' A_h S e_j)^2 / sum_h e_i' A_h S A_h' e_i, h = 0..H-1."""
    A, S = res.ma_rep(FEVD_H - 1), np.asarray(res.sigma_u)
    num = (np.einsum("hik,kj->hij", A, S) ** 2).sum(0) / np.diag(S)
    den = np.einsum("hik,kl,hil->i", A, S, A)
    theta = num / den[:, None]
    names = res.names
    return pd.DataFrame(100 * theta / theta.sum(1, keepdims=True), index=names, columns=names)


def var(r, maxlags):
    """VAR with constant, lag order by BIC up to `maxlags`: lag order, share matrix, spillover index,
    Granger Wald chi2 (statistic, p-value) for every directed pair (cause, effect)."""
    res = VAR(r.dropna()).fit(maxlags=maxlags, ic="bic", trend="c")
    share = gfevd(res)
    tests = {(c, e): res.test_causality(e, c, kind="wald") for c in r.columns for e in r.columns if c != e}
    return {"lags": res.k_ar, "share": share,
            "spill": (share.values.sum() - np.trace(share.values)) / len(share),
            "granger": {k: (t.test_statistic, t.pvalue) for k, t in tests.items()}}
