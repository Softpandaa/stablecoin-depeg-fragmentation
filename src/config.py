"""Every parameter of the study, declared once."""

import pandas as pd

# Paths -----------------------------------------------------------------------
DATA = "data/binance_us_1m.csv"
FIGURE = "latex/decomposition.png"

# Sample ----------------------------------------------------------------------
M = 1e4                   # basis points
LABELS = {"btc_usd": "B/U", "btc_usdt": "B/T", "btc_usdc": "B/C",
          "usdt_usd": "T/U", "usdc_usd": "C/U"}
COINS = {"USDT": ("btc_usdt", "usdt_usd"), "USDC": ("btc_usdc", "usdc_usd")}   # (B/Q, Q/U)
BU = "btc_usd"
REGIMES = ("pre", "crisis", "post")

# Depeg events ----------------------------------------------------------------
PEG = 1.0
PEG_TOL = 1e-14
MIN_DURATION = "60min"
MERGE_WITHIN = "20min"
BASE_FREQ = "5min"
BASE_TAU = 0.005
REWIND = True             # start at the last bar at the peg before the breach

# Estimation ------------------------------------------------------------------
K_BARS = 5                # Kyle window, bars
RV_BARS = 120             # RV window, bars
QUANTILES = (0.50, 0.95, 0.99)   # of |b|
HAC_LAGS = 60             # observations of the estimation sample, not minutes

# VAR -------------------------------------------------------------------------
VAR_FREQ = "5min"
VAR_MAXLAGS = 6
FEVD_H = 10

# Robustness ------------------------------------------------------------------
R1_FREQ = "5min"
R1_STEP = pd.Timedelta(R1_FREQ) // pd.Timedelta("1min")
# R1 windows and HAC lags keep the baseline's nominal span.
R1_K_BARS, R1_RV_BARS, R1_HAC_LAGS = K_BARS // R1_STEP, RV_BARS // R1_STEP, HAC_LAGS // R1_STEP
R3_TAU = 0.010
R6_REWIND = False         # start at the threshold crossing

# Figure 1 --------------------------------------------------------------------
DPI = 300
FIG_PAD = "12h"           # plotted span: each crisis window +/- FIG_PAD
STYLE = {"D": ("#0072B2", "-", "$D$"), "delta": ("#D55E00", "--", r"$\delta$"),
         "b": ("#009E73", "-", "$b$")}   # Okabe-Ito colors
