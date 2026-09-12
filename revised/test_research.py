"""Unit/regression tests on artificial inputs. No market-data access required."""
import unittest
import numpy as np
import pandas as pd
from research import *
from demo import synthetic_fixture


class RatesAndMetrics(unittest.TestCase):
    def test_effective_rate_recompounds(self):
        weekly=effective_annual_percent_to_period(5,52)
        self.assertAlmostEqual(float((1+weekly)**52-1),.05)

    def test_percent_not_decimal_simple_proxy(self):
        self.assertAlmostEqual(float(simple_yield_proxy(5,7)),.05*7/365)

    def test_zero_and_negative_rate(self):
        self.assertEqual(float(effective_annual_percent_to_period(0)),0)
        self.assertLess(float(effective_annual_percent_to_period(-.5)),0)

    def test_invalid_rate_inputs(self):
        for fn in (lambda:effective_annual_percent_to_period(-100),lambda:simple_yield_proxy(5,0),lambda:simple_yield_proxy(float('nan'),7)):
            with self.assertRaises(ValueError): fn()

    def test_initial_drawdown_is_counted(self):
        self.assertAlmostEqual(maximum_drawdown([-.2,.25]),.2)

    def test_drawdown_wealth_index(self):
        self.assertAlmostEqual(maximum_drawdown([.1,-.2,.05]),.2)

    def test_no_drawdown_on_gains(self):
        self.assertEqual(maximum_drawdown([.1,.2]),0)

    def test_total_loss(self):
        self.assertEqual(maximum_drawdown([.1,-1]),1)

    def test_invalid_returns(self):
        with self.assertRaises(ValueError): maximum_drawdown([-1.1])
        with self.assertRaises(ValueError): maximum_drawdown([np.nan])

    def test_sharpe_on_excess_series(self):
        r=np.array([.01,.03,-.02,.02]); rf=np.array([.001,.002,.003,.004])
        e=r-rf
        self.assertAlmostEqual(annualized_excess_sharpe(r,rf),float(e.mean()/e.std(ddof=1)*np.sqrt(52)))

    def test_sharpe_undefined_not_infinite(self):
        with self.assertRaises(ValueError): annualized_excess_sharpe([.01,.01],[0,0])
        with self.assertRaises(ValueError): annualized_excess_sharpe([.01,.02],[0])


class TimingAndFactors(unittest.TestCase):
    def test_asof_excludes_same_and_future_timestamp(self):
        s=pd.Series([1,9,99],index=pd.to_datetime(['2020-01-01','2020-01-03','2020-01-05']))
        got=asof_values(s,pd.to_datetime(['2020-01-03','2020-01-04']))
        np.testing.assert_equal(got.to_numpy(),[1,9])

    def test_asof_missing_and_stale_fail(self):
        s=pd.Series([1],index=pd.to_datetime(['2020-01-01']))
        for d in ['2019-12-31','2020-02-01']:
            with self.assertRaises(ValueError): asof_values(s,pd.to_datetime([d]))

    def test_duplicate_dates_fail(self):
        s=pd.Series([1,2],index=pd.to_datetime(['2020-01-01','2020-01-01']))
        with self.assertRaises(ValueError): asof_values(s,pd.to_datetime(['2020-01-02']))

    def test_factor_weights_are_dollar_neutral(self):
        _,_,ch,_=synthetic_fixture()
        w=snapshot_factor_weights(ch.iloc[::2])
        np.testing.assert_allclose(w.sum(),0,atol=1e-12)
        np.testing.assert_allclose(w.abs().sum(),2,atol=1e-12)

    def test_future_characteristics_do_not_change_past(self):
        p,_,ch,_=synthetic_fixture()
        r=price_returns(p)
        base=point_in_time_spreads(r,ch)
        changed=ch.copy(); changed.loc[changed.available_at>p.index[40],'book_to_market']*=100
        other=point_in_time_spreads(r,changed)
        pd.testing.assert_frame_equal(base.loc[:p.index[40]],other.loc[:p.index[40]])

    def test_unavailable_characteristics_rejected(self):
        p,_,ch,_=synthetic_fixture()
        ch.available_at=p.index[-1]+pd.Timedelta('1D')
        with self.assertRaises(ValueError): point_in_time_spreads(price_returns(p),ch)

    def test_full_factor_ols_recovers_known_coefficients(self):
        rng=np.random.default_rng(4); m,s,h=rng.normal(0,.02,(3,100)); rf=np.linspace(.0001,.001,100)
        y=rf+.001+1.2*(m-rf)-.3*s+.8*h
        fit=three_factor_ols(y,m,s,h,rf)
        np.testing.assert_allclose(list(fit.values()),[.001,1.2,-.3,.8],atol=1e-12)

    def test_rank_deficient_ols_rejected(self):
        with self.assertRaises(ValueError): three_factor_ols(np.arange(10),np.arange(10),np.arange(10),np.arange(10),np.zeros(10))


class Allocation(unittest.TestCase):
    def test_seeded_weights_reproduce_and_sum_to_one(self):
        a=seeded_weights(10); b=seeded_weights(10)
        np.testing.assert_array_equal(a,b)
        np.testing.assert_allclose(a.sum(axis=1),1)
        self.assertTrue((a>=0).all())

    def test_black_litterman_neutral_view_preserves_prior(self):
        c=np.array([[.04,.01],[.01,.09]]); w=np.array([.6,.4]); p=np.array([[1.,-1.]])
        prior=2.5*c@w
        got=black_litterman_posterior(c,w,2.5,p,p@prior,np.array([[.03]]))
        np.testing.assert_allclose(got,prior)

    def test_black_litterman_matches_scalar_bayesian_update(self):
        # one asset: prior=.04*2=.08; prior variance=.05*.04=.002
        got=black_litterman_posterior([[.04]],[1.],2,[[1.]],[.1],[[.003]])
        np.testing.assert_allclose(got,[.08+.002/(.002+.003)*(.1-.08)])

    def test_bad_covariance_rejected(self):
        with self.assertRaises(ValueError): black_litterman_posterior([[1,2],[2,1]],[.5,.5],2,[[1,-1]],[.1],[[.01]])

    def test_no_fill_for_missing_prices(self):
        p,_,_,_=synthetic_fixture(); p.iloc[2,0]=np.nan
        with self.assertRaises(ValueError): price_returns(p)

    def test_walkforward_costs_and_first_decision(self):
        p,rf,_,_=synthetic_fixture(n_periods=65)
        out,w=walk_forward(p,rf,n_portfolios=250)
        self.assertEqual(out.index[0],p.index[53])
        self.assertAlmostEqual(float(out.turnover_l1.iloc[0]),1)
        np.testing.assert_allclose(out.net_return,(1-out.cost_fraction)*(1+out.gross_return)-1)
        np.testing.assert_allclose(w.sum(axis=1),1)
        self.assertTrue((out.net_return<=out.gross_return).all())

    def test_turnover_uses_drifted_holdings(self):
        p,rf,_,_=synthetic_fixture(n_periods=60)
        out,w=walk_forward(p,rf,n_portfolios=1)
        r=price_returns(p)
        first=w.iloc[0].to_numpy(); first_ret=r.loc[out.index[0]].to_numpy()
        drift=first*(1+first_ret)/(1+first@first_ret)
        expected=np.abs(w.iloc[1].to_numpy()-drift).sum()
        self.assertAlmostEqual(float(out.turnover_l1.iloc[1]),float(expected))

    def test_future_prices_do_not_change_earlier_weights_or_returns(self):
        p,rf,_,_=synthetic_fixture(n_periods=80)
        a,wa=walk_forward(p,rf,n_portfolios=250)
        changed=p.copy(); changed.iloc[70:]*=np.linspace(1.1,2,len(p.columns))
        b,wb=walk_forward(changed,rf,n_portfolios=250)
        pd.testing.assert_frame_equal(a.loc[:p.index[69]],b.loc[:p.index[69]])
        # Weight on ending period 70 is decided before that price is observed.
        pd.testing.assert_frame_equal(wa.loc[:p.index[70]],wb.loc[:p.index[70]])

    def test_riskfree_misalignment_rejected(self):
        p,rf,_,_=synthetic_fixture()
        with self.assertRaises(ValueError): walk_forward(p,rf.iloc[1:])


if __name__=='__main__': unittest.main(verbosity=2)
