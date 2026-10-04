"""Depeg event windows: port of the original DepeggingDetector._detect_one_threshold.
Start rewind and merge: Perez Riaza & Gnabo (2025, Sec. 6.1); 60-min minimum: original code."""

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
    """Move each run start back to the last bar exactly at the peg, unless the bar before is at the peg."""
    out = []
    for start, end in runs:
        pos = price.index.searchsorted(start)
        if pos <= 1 or abs(price.iloc[pos - 1] - PEG) <= PEG_TOL:
            out.append((start, end))
            continue
        i = pos - 1
        while i >= 0 and abs(price.iloc[i] - PEG) > PEG_TOL:
            i -= 1
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


def detect(close, freq, theta, rewind):
    """Depeg events of a Q/U close: last close per `freq` bar outside [peg - theta, peg + theta].
    Port of _detect_one_threshold: runs, start rewind, merge within MERGE_WITHIN, keep end - start >= MIN_DURATION.
    rewind=False starts each run at the threshold crossing (the source's main start rule; robustness R6).
    The rewind moves a start back to the last bar exactly at the peg, which can lengthen a short breach;
    if the bar before the run is already at the peg the start is kept; if no bar at the peg exists before
    the run, the original's index -1 wraps to the last bar (kept as is; unreachable on this data)."""
    price = close.resample(freq).last()
    runs = _runs((price <= PEG - theta) | (price >= PEG + theta))
    runs = _merge(_early_start(price, runs) if rewind else runs)
    return [(s, e) for s, e in runs if e - s >= pd.Timedelta(MIN_DURATION)]


def regimes(index, window):
    """REGIMES labels: pre for t < start, crisis for start <= t <= end, post for t > end."""
    start, end = window
    pre, crisis, post = REGIMES
    return pd.Series(np.select([index < start, index <= end], [pre, crisis], post), index=index)
