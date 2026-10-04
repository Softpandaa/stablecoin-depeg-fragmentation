"""Every parameter of the study, declared once."""

import pandas as pd

DATA = "data/binance_us_1m.csv"
FIGURE = "latex/decomposition.png"
DPI = 300

M = 1e4  # basis points

# Pair column prefixes and output labels (B BTC, U USD, T USDT, C USDC).
LABELS = {"btc_usd": "B/U", "btc_usdt": "B/T", "btc_usdc": "B/C",
          "usdt_usd": "T/U", "usdc_usd": "C/U"}
# Per coin Q: (B/Q pair, Q/U pair). B/U is common to both.
COINS = {"USDT": ("btc_usdt", "usdt_usd"), "USDC": ("btc_usdc", "usdc_usd")}
BU = "btc_usd"
REGIMES = ("pre", "crisis", "post")

# Depeg detector: start rewind and 20-min merge from Perez Riaza & Gnabo (2025, Sec. 6.1);
# 60-min minimum from the original code (replaces the source's two-observation rule).
PEG = 1.0
PEG_TOL = 1e-14
MIN_DURATION = "60min"
MERGE_WITHIN = "20min"
BASE_FREQ = "5min"
BASE_THETA = 0.005
REWIND = True             # baseline start: last bar at the peg before the breach

# Liquidity measures: window lengths in bars.
K_BARS = 5
RV_BARS = 120

# Table 3 quantiles of |b|.
QUANTILES = (0.50, 0.95, 0.99)

# Inference.
HAC_LAGS = 60             # observations of the estimation sample, not minutes

# VAR / connectedness.
VAR_FREQ = "5min"
VAR_MAXLAGS = 6
FEVD_H = 10

# Robustness (Table 7) and alternative windows (Table 1).
R1_FREQ = "5min"          # R1 bar length for Tables 4-5; same time spans as the 1-minute baseline
R1_STEP = pd.Timedelta(R1_FREQ) // pd.Timedelta("1min")
R1_K_BARS, R1_RV_BARS, R1_HAC_LAGS = K_BARS // R1_STEP, RV_BARS // R1_STEP, HAC_LAGS // R1_STEP  # HAC: 60 / bar length
R3_THETA = 0.010
R6_REWIND = False         # R6: start at the threshold crossing (source's main start rule)

# Figure 1: Okabe-Ito colours with distinct dash patterns; legend labels match the report's symbols.
FIG_PAD = "12h"           # plotted span: crisis window of each stablecoin +/- FIG_PAD
STYLE = {"D": ("#0072B2", "-", "$D$"), "delta": ("#D55E00", "--", r"$\delta$"), "b": ("#009E73", "-", "$b$")}
