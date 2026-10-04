"""Single entry point: `python src/plots.py` from the repo root writes Figure 1 and prints all tables."""

import os

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from config import (BASE_FREQ, BASE_THETA, COINS, DPI, FIG_PAD, FIGURE, HAC_LAGS, K_BARS, QUANTILES, R1_FREQ,
                    R1_HAC_LAGS, R1_K_BARS, R1_RV_BARS, R3_THETA, R6_REWIND, REGIMES, REWIND, RV_BARS, STYLE,
                    VAR_FREQ, VAR_MAXLAGS)
from connect import returns, var
from data import decompose, load, to_bars
from events import detect, regimes
from measures import liquidity
from regress import Z, half_life, panel, transmission


def show(title, table):
    """Print a titled table."""
    print(f"\n{title}\n{table.to_string()}")


def windows(df, theta, rewind=REWIND):
    """Each coin's window [first event start, last event end], plus the union [earliest start, latest end]."""
    w = {}
    for coin, (_, qu) in COINS.items():
        ev = detect(df[f"{qu}_close"], BASE_FREQ, theta, rewind)
        w[coin] = (ev[0][0], ev[-1][1])
    w["union"] = (min(s for s, _ in w.values()), max(e for _, e in w.values()))
    return w


def table1(ws):
    """Window start, end and length in hours per coin x specification."""
    return pd.DataFrame({(coin, spec): {"start": f"{w[coin][0]:%d %b %H:%M}", "end": f"{w[coin][1]:%d %b %H:%M}",
                                        "hours": round((w[coin][1] - w[coin][0]) / pd.Timedelta("1h"), 1)}
                         for coin in COINS for spec, w in ws.items()}).T


def table3(df, w):
    """Decomposition moments per coin x regime on synchronous minutes (F = 1)."""
    out = {}
    for coin in COINS:
        dec = decompose(df, coin)
        reg = regimes(dec.index, w[coin])
        for r in REGIMES:
            s = dec[dec["F"] & (reg == r)]
            vD, ab = s["D"].var(), s["b"].abs()
            stats = {"mean D": s["D"].mean(), "mean delta": s["delta"].mean(), "mean b": s["b"].mean(),
                     "sd D": s["D"].std(), "sd delta": s["delta"].std(), "sd b": s["b"].std(),
                     "corr(D,-delta)": s["D"].corr(-s["delta"]),
                     "Var(delta)/Var(D)": s["delta"].var() / vD, "Var(b)/Var(D)": s["b"].var() / vD,
                     "2Cov(delta,b)/Var(D)": 2 * s["delta"].cov(s["b"]) / vD,
                     **{f"|b| q{100 * q:.0f}": ab.quantile(q) for q in QUANTILES}}
            out[(coin, r)] = {k: f"{v:.2f}" for k, v in stats.items()}
    return pd.DataFrame(out)


def tables45(bars, w, k_bars=K_BARS, rv_bars=RV_BARS, lags=HAC_LAGS, z=Z):
    """Tables 4 and 5 per coin x regime on FF = 1: half-lives in minutes and the transmission regression."""
    t4, t5, bar_min = {}, {}, (bars.index[1] - bars.index[0]) / pd.Timedelta("1min")
    for coin in COINS:
        p = panel(bars, coin, k_bars, rv_bars)
        reg = regimes(p.index, w[coin])
        for r in REGIMES:
            rows = p["FF"] & (reg == r)
            t4[(coin, r)] = {f"HL {x}": round(bar_min * half_life(p, rows, x), 2) for x in ("delta", "b")}
            m = transmission(p, rows, lags, z)
            t5[(coin, r)] = {**{k: f"{m['coef'][k]:.4f} ({m['t'][k]:.2f})" for k in m["coef"].index if k != "const"},
                             "R2": f"{m['r2']:.3f}", "joint p (lam1 = 0)": f"{m['p_lam1']:.3f}"}
    return pd.DataFrame(t4), pd.DataFrame(t5)


def table6(df, union):
    """VAR per regime of the union window: lag order, spillover index, share matrix, Granger tests."""
    r = returns(df, VAR_FREQ)
    reg = regimes(r.index, union)
    return {g: var(r[reg == g], VAR_MAXLAGS) for g in REGIMES}


def table7(df, w):
    """Key crisis estimates: R0 baseline, R1 5-minute bars, R2 each liquidity measure alone."""
    specs = {"R0 baseline": (df, {}),
             "R1 5-minute bars": (to_bars(df, R1_FREQ), {"k_bars": R1_K_BARS, "rv_bars": R1_RV_BARS, "lags": R1_HAC_LAGS}),
             **{f"R2 {z} alone": (df, {"z": (z,)}) for z in Z}}
    rows = {}
    for name, (bars, kw) in specs.items():
        t4, t5 = tables45(bars, w, **kw)
        z = kw.get("z", Z)
        lam1 = f"lam1 {'K Q/U' if 'K Q/U' in z else z[0]}"
        rows[name] = {"USDC lam1": t5[("USDC", "crisis")][lam1],
                      "USDC joint p": t5[("USDC", "crisis")]["joint p (lam1 = 0)"],
                      "USDT lam0": t5[("USDT", "crisis")]["lam0"],
                      **{f"{coin} {x}": t4[(coin, "crisis")][x] for x in t4.index for coin in COINS}}
    return pd.DataFrame(rows).T


def figure1(df, w):
    """Per stablecoin (columns): D and delta (top) and b (bottom), crisis window +/- FIG_PAD, window shaded."""
    plt.rcParams["font.family"] = "serif"
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharex="col")
    pad = pd.Timedelta(FIG_PAD)
    for j, coin in enumerate(COINS):
        s, e = w[coin]
        dec = decompose(df, coin).loc[s - pad:e + pad]
        for i, names in enumerate((("D", "delta"), ("b",))):
            ax = axes[i, j]
            ax.axvspan(s, e, color="0.88", label="crisis window")
            for name in names:
                colour, dash, label = STYLE[name]
                ax.plot(dec.index, dec[name], color=colour, linestyle=dash, linewidth=0.8, label=label)
            ax.set_ylabel("basis points")
            ax.legend(loc="upper right", frameon=True, framealpha=0.9, edgecolor="none")
        axes[0, j].set_title(coin)
        axes[1, j].set_xlim(s - pad, e + pad)
        axes[1, j].xaxis.set_major_locator(mdates.DayLocator())
        axes[1, j].xaxis.set_major_formatter(mdates.DateFormatter("%d"))
        axes[1, j].set_xlabel("March 2023 (UTC day)")
    fig.tight_layout()
    os.makedirs(os.path.dirname(FIGURE), exist_ok=True)
    fig.savefig(FIGURE, dpi=DPI)


def main():
    """Write Figure 1 and print Tables 1-7 with the appendix tables."""
    df = load()
    w = windows(df, BASE_THETA)
    figure1(df, w)
    show("Table 1. Depeg windows (5-minute Q/U close)",
         table1({"baseline": w, "R3": windows(df, R3_THETA), "R6": windows(df, BASE_THETA, R6_REWIND)}))
    show("Table 2. Liquidity by pair and regime (union window)",
         liquidity(df, regimes(df.index, w["union"])).round(2))
    show("Tables 3 and B1. Decomposition, synchronous minutes F = 1", table3(df, w))
    t4, t5 = tables45(df, w)
    show("Table 4. Half-life in minutes, FF = 1", t4)
    show(f"Tables 5 and B2. Transmission regression, FF = 1, HAC {HAC_LAGS} lags: coefficient (t)", t5)
    t6 = table6(df, w["union"])
    show("Table 6. VAR (5-minute returns): BIC lag order and total spillover index",
         pd.DataFrame.from_dict({g: {"lags": t6[g]["lags"], "spillover": round(t6[g]["spill"], 1)} for g in REGIMES},
                                orient="index"))
    for g in REGIMES:
        show(f"Tables 6 and C1. Generalized FEVD shares (row <- column), {g}", t6[g]["share"].round(1))
    show("Tables 6 and C2. Granger Wald chi2 statistic (p-value), cause->effect",
         pd.DataFrame({g: {f"{c}->{e}": f"{w_:.2f} ({p:.3f})" for (c, e), (w_, p) in t6[g]["granger"].items()}
                       for g in REGIMES}))
    show("Table 7. Key crisis estimates: coefficient (t), half-lives in minutes", table7(df, w))


if __name__ == "__main__":
    main()
