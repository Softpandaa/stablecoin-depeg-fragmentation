# Did Liquidity Govern Stablecoin Peg Pass-Through? Evidence from the March 2023 USDC Depeg

This study asks whether liquidity governed how stablecoin peg stress passed through to Bitcoin's price during the March 2023 USDC depeg. Using 1-minute data from Binance.US on BTC/USD, BTC/USDT, BTC/USDC, USDT/USD and USDC/USD, we decompose each stablecoin's cross-currency basis into its peg deviation and a triangular arbitrage deviation. A pass-through regression examines whether the response of the arbitrage deviation to the peg changes with lagged illiquidity, and a VAR on 5-minute returns measures spillovers and Granger causality.

## Findings

During the crisis, the peg deviation carried most of the basis variance, while the triangular arbitrage deviation decayed with a half-life of 0.82 minutes for USDT and 0.52 minutes for USDC. Liquidity did not measurably govern the pass-through. The effect of USDC/USD illiquidity is significant at 1-minute sampling but not robust, as it loses significance on 5-minute bars. Price discovery stayed in BTC/USD, while BTC/USDC partly decoupled from it and traded with the USDC peg. The share of BTC/USDC forecast error variance due to BTC/USD fell from 32.4% before the crisis to 21.4% during it, and USDC/USD and BTC/USDC Granger-caused each other only during the crisis. The stress that reached the stablecoin price of Bitcoin was the peg itself, not a failure of arbitrage.

## Layout

```
data/     committed 1-minute prices and volumes
src/      analysis modules, every parameter declared once in config.py
report.pdf
```

The report is distributed as a compiled PDF. Its typesetting source is not included.

## Data

`data/binance_us_1m.csv` holds the 1-minute high, low, close, base volume and quote volume of BTC/USD, BTC/USDT, BTC/USDC, USDT/USD and USDC/USD on Binance.US, from 1 to 21 March 2023 in UTC.

## Reproducing

Python 3.13.

```
pip install -r requirements.txt
python src/plots.py
```

This prints every table of the report and writes Figure 1 to `latex/decomposition.png`, a folder created on first run and not tracked. The printed tables label the pairs B/U, B/T, B/C, T/U and C/U for BTC/USD, BTC/USDT, BTC/USDC, USDT/USD and USDC/USD.
