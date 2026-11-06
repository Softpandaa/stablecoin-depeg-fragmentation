# Did Liquidity Govern Stablecoin Peg Pass-Through? Evidence from the March 2023 USDC Depeg

Did liquidity govern how the March 2023 USDC depeg passed into the stablecoin price of Bitcoin? Using 1-minute Binance.US data on five pairs, this study splits each stablecoin's cross-currency basis into its peg deviation and a triangular arbitrage deviation. A pass-through regression then tests whether lagged illiquidity changes how the arbitrage deviation responds to the peg deviation.

## Findings

During the crisis, the peg deviation accounted for almost all of the basis variance. The triangular arbitrage deviation closed within one sampling interval, while the peg deviations had half-lives of 1 to 5 hours. The stress that reached Bitcoin's stablecoin price was the peg deviation itself, not a failure of arbitrage.

Liquidity did not measurably govern the pass-through. The effect of USDC/USD illiquidity is significant at the 1% level at 1-minute sampling, but only at the 10% level on 5-minute bars.

Relative to BTC/USDC, price discovery stayed in BTC/USD. The share of BTC/USDC forecast error variance due to BTC/USD fell from 32.4% before the crisis to 21.4% during it, and USDC/USD and BTC/USDC Granger-caused each other only during the crisis.

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

This prints every table of the report and draws Figure 1. The printed tables label the pairs B/U, B/T, B/C, T/U and C/U for BTC/USD, BTC/USDT, BTC/USDC, USDT/USD and USDC/USD.
