"""Depeg event windows of Section 2.2."""

import numpy as np
import pandas as pd

from config import MERGE_WITHIN, MIN_DURATION, PEG, PEG_TOL, REGIMES


def _runs(mask):
    """(start, end) bar labels of each maximal run of True."""
    runs, start, prev = [], None, None
    for t, v in mask.items():
        if v and start is None:
            start = t
        elif not v and start is not None:
            runs.append((start, prev))
            start = None
        prev = t
    if start is not None:
        runs.append((start, prev))
    return runs


def _early_start(price, runs):
    """Rewind each start to the last bar at the peg, unless the bar before is at the peg."""
    out = []
    for start, end in runs:
        pos = price.index.searchsorted(start)
        if pos <= 1 or abs(price.iloc[pos - 1] - PEG) <= PEG_TOL:
            out.append((start, end))
            continue
        i = pos - 1
        while i >= 0 and abs(price.iloc[i] - PEG) > PEG_TOL:
            i -= 1
        # No bar at the peg before the run: i = -1 wraps to the last bar and the event is dropped.
        out.append((price.index[i], end))
    return out


def _merge(runs):
    """Merge runs that start within MERGE_WITHIN of the previous end."""
    out = []
    for start, end in runs:
        if out and start <= out[-1][1] + pd.Timedelta(MERGE_WITHIN):
            out[-1] = (out[-1][0], max(end, out[-1][1]))
        else:
            out.append((start, end))
    return sorted(out)


def detect(close, freq, tau, rewind):
    """Runs of `freq` closes with |p - PEG| >= tau, rewound if asked, merged, >= MIN_DURATION."""
    price = close.resample(freq).last()
    runs = _runs((price <= PEG - tau) | (price >= PEG + tau))
    runs = _merge(_early_start(price, runs) if rewind else runs)
    return [(s, e) for s, e in runs if e - s >= pd.Timedelta(MIN_DURATION)]


def regimes(index, window):
    """REGIMES labels: pre for t < start, crisis for start <= t <= end, post for t > end."""
    start, end = window
    pre, crisis, post = REGIMES
    return pd.Series(np.select([index < start, index <= end], [pre, crisis], post), index=index)
