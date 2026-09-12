# Local verification results

Verification date: 12 September 2026.

- Python 3.12.14
- NumPy 2.3.5
- pandas 2.2.3
- **28 unit/regression tests passed**, with 0 failures and 0 errors.
- The full deterministic synthetic demonstration ran twice with identical result dictionaries.
- No licensed market data or network requests were used by the revised demonstration.

These checks establish the tested software behavior, not historical investment performance, independent research certification or production readiness.

## Executed tests

- `test_bad_covariance_rejected (test_research.Allocation.test_bad_covariance_rejected)` — passed
- `test_black_litterman_matches_scalar_bayesian_update (test_research.Allocation.test_black_litterman_matches_scalar_bayesian_update)` — passed
- `test_black_litterman_neutral_view_preserves_prior (test_research.Allocation.test_black_litterman_neutral_view_preserves_prior)` — passed
- `test_future_prices_do_not_change_earlier_weights_or_returns (test_research.Allocation.test_future_prices_do_not_change_earlier_weights_or_returns)` — passed
- `test_no_fill_for_missing_prices (test_research.Allocation.test_no_fill_for_missing_prices)` — passed
- `test_riskfree_misalignment_rejected (test_research.Allocation.test_riskfree_misalignment_rejected)` — passed
- `test_seeded_weights_reproduce_and_sum_to_one (test_research.Allocation.test_seeded_weights_reproduce_and_sum_to_one)` — passed
- `test_turnover_uses_drifted_holdings (test_research.Allocation.test_turnover_uses_drifted_holdings)` — passed
- `test_walkforward_costs_and_first_decision (test_research.Allocation.test_walkforward_costs_and_first_decision)` — passed
- `test_drawdown_wealth_index (test_research.RatesAndMetrics.test_drawdown_wealth_index)` — passed
- `test_effective_rate_recompounds (test_research.RatesAndMetrics.test_effective_rate_recompounds)` — passed
- `test_initial_drawdown_is_counted (test_research.RatesAndMetrics.test_initial_drawdown_is_counted)` — passed
- `test_invalid_rate_inputs (test_research.RatesAndMetrics.test_invalid_rate_inputs)` — passed
- `test_invalid_returns (test_research.RatesAndMetrics.test_invalid_returns)` — passed
- `test_no_drawdown_on_gains (test_research.RatesAndMetrics.test_no_drawdown_on_gains)` — passed
- `test_percent_not_decimal_simple_proxy (test_research.RatesAndMetrics.test_percent_not_decimal_simple_proxy)` — passed
- `test_sharpe_on_excess_series (test_research.RatesAndMetrics.test_sharpe_on_excess_series)` — passed
- `test_sharpe_undefined_not_infinite (test_research.RatesAndMetrics.test_sharpe_undefined_not_infinite)` — passed
- `test_total_loss (test_research.RatesAndMetrics.test_total_loss)` — passed
- `test_zero_and_negative_rate (test_research.RatesAndMetrics.test_zero_and_negative_rate)` — passed
- `test_asof_excludes_same_and_future_timestamp (test_research.TimingAndFactors.test_asof_excludes_same_and_future_timestamp)` — passed
- `test_asof_missing_and_stale_fail (test_research.TimingAndFactors.test_asof_missing_and_stale_fail)` — passed
- `test_duplicate_dates_fail (test_research.TimingAndFactors.test_duplicate_dates_fail)` — passed
- `test_factor_weights_are_dollar_neutral (test_research.TimingAndFactors.test_factor_weights_are_dollar_neutral)` — passed
- `test_full_factor_ols_recovers_known_coefficients (test_research.TimingAndFactors.test_full_factor_ols_recovers_known_coefficients)` — passed
- `test_future_characteristics_do_not_change_past (test_research.TimingAndFactors.test_future_characteristics_do_not_change_past)` — passed
- `test_rank_deficient_ols_rejected (test_research.TimingAndFactors.test_rank_deficient_ols_rejected)` — passed
- `test_unavailable_characteristics_rejected (test_research.TimingAndFactors.test_unavailable_characteristics_rejected)` — passed

See `test_research.py` for assertions and `demo_results.json` for explicitly labeled synthetic outputs.
