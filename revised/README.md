# Tested publication revision

**12 September 2026. AI-assisted revision prepared for Liuyu Xiong's public portfolio.**

This directory is new work prompted by a review of the original CQF notebooks. It must not be described as code submitted in 2024. Original notebook source remains under `../notebooks/`, with outputs and private metadata removed.

## Run locally

From this directory, in Python 3.11 or later:

```sh
python -m pip install -r requirements.txt
python -m unittest -v test_research.py
python demo.py
```

The exact tested Python/dependency versions appear in [TEST_RESULTS.md](TEST_RESULTS.md). No network call, credential or market-data subscription is needed after dependency installation. `demo.py` creates artificial prices and characteristics in memory and writes clearly labeled `demo_results.json`.

## Corrections and tests

| Area | Revised treatment | Evidence |
| --- | --- | --- |
| Rate units | Effective annual rates convert by compounding. Simple quoted yields have a separately named, documented accrual proxy. Neither silently treats percent as decimal. | Recompounding, zero/negative rates and percent-unit tests |
| Information timing | Strict backward as-of matching, actual availability timestamps, stale-data rejection and characteristics known before interval start | Changing future observations cannot change earlier results |
| Drawdown | Include initial wealth of 1 and calculate decline from running wealth peaks | Initial loss, recovery, monotonic gains and total-loss tests |
| Allocation | Seeded positive random weights normalized to one | Reproducible weights, nonnegative allocation and budget checks |
| Factor regression | Regress equity excess returns on market excess return, SMB and HML plus intercept | Recover known synthetic coefficients and reject rank-deficient designs |
| Black–Litterman | Consistent period excess returns and explicit uncertainty, using linear solves | Neutral views reproduce prior; scalar case matches independent formula |
| Walk-forward evaluation | Estimate on completed periods, apply weights to next interval, charge costs on drift-adjusted traded notional | Future-price perturbation, first-decision timing and turnover checks |

## Demonstration scope

The deterministic fixture has 10 artificial assets and 104 weekly return periods. The allocation demonstration uses 52 completed periods at each decision, evaluates the following 52 periods and compares 10,000 candidate portfolios per decision. Trading costs are 10 basis points per unit of gross traded notional (`sum(abs(target - drifted holdings))`), including initial deployment from cash. The generated example values are only regression-test references, not investment returns or evidence of alpha.

The factor example constructs gross median-split long-short spreads in a small artificial universe. It is not the official Fama–French construction. Its first return row is excluded because the earlier interval boundary is not supplied. Black–Litterman receives explicit hypothetical views; its illustrative posterior is not a trading strategy.

## Important limits

- The actual 2009–2019 Wind observations and historical characteristic-release times are excluded. There is **no claim of a corrected historical backtest**.
- `available_at` must mean when information could actually be known; using a financial year-end as an availability timestamp would defeat the control.
- `simple_yield_proxy` uses `annual_percent / 100 * days / 365`. This is an explicitly approximate interest-accrual convention, not a replication of a Treasury total-return index. A quoted Treasury yield is not an effective annual rate or a realized holding-period return.
- Annualized Sharpe uses square-root-of-period scaling, which does not adjust for serial correlation. No significance or confidence interval is estimated.
- Walk-forward execution assumes trading at the prior observed close. Slippage, delays, corporate actions, universe construction and delisting handling are outside this example. It is not production software.
- Publication revisions and tests were AI-assisted and are disclosed as such; no new metrics are attributed to the author's original coursework.

## Method references

- [William F. Sharpe, The Sharpe Ratio](https://web.stanford.edu/~wfsharpe/art/sr/sr.htm): differential returns and ratio interpretation.
- [FRED, DGS3MO](https://fred.stlouisfed.org/series/DGS3MO): quoted annual Treasury yield series definition, not realized weekly returns.
- [pandas merge_asof](https://pandas.pydata.org/docs/reference/api/pandas.merge_asof.html): backward matching and exclusion of exact matches.
