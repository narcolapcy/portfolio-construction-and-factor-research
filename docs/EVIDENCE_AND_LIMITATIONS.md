# Evidence and limitations

## Source mapping

Primary source: the author's January 2024 report, *Portfolio Construction using Black-Litterman Model and Factors*, and accompanying FAMA / BL notebooks.

| Scope | Evidence in the original materials |
| --- | --- |
| 10 equities, three benchmarks, 2009–2019, Wind source | Original report, page 3 |
| 525 weekly price observations | Price workbook: 525 populated data rows, excluding header; no raw rows redistributed |
| 10,000 simulated portfolios | Report page 5; FAMA source cell 46, `range(10000)` |
| Value/size spread construction | Report pages 6–7; FAMA source cells 63–83 |
| 60-week rolling regression | FAMA source cells 98 and 100, `window = 60` |
| Risk preferences 4.5, 2.5, 0.001 | BL source cells 37, 39 and 41, and maximum-Sharpe comparisons |

Original cell references are zero-based before the public-edition introductory cell. No numerical results were independently rerun during this publication review.

## Material issues visible in the archival source

1. **Point-in-time construction:** end-of-sample characteristics used to form historical groups can create look-ahead bias. The small-universe spreads are not the published Fama–French factor series.
2. **Risk-free conventions:** some Sharpe calculations mix yield units and return frequencies. The code's rates need a consistent decimal convention and conversion to the return period. Those Sharpe values are not endorsed.
3. **Drawdown:** the helper uses cumulative returns, not the wealth index `1 + cumulative_return`. Its historical drawdown values should not be relied upon.
4. **OLS specification:** some examples omit market excess returns and use raw equity returns. They are exploratory regressions, not a verified complete Fama–French three-factor implementation.
5. **Randomness:** no fixed seed is recorded for Monte Carlo weights.
6. **Backtesting:** allocation comparisons, parameter labels and charts do not establish an executable, leakage-controlled, cost-adjusted out-of-sample backtest. Production QC and leverage constraints are not demonstrated.

These limitations are disclosed rather than silently changing historical code. The separately dated [2026 publication revision](../revised/README.md) implements corrected components and synthetic tests. It does not independently reproduce the original licensed-data results or replace the original submitted project.
