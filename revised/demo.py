"""Deterministic synthetic fixtures only. Not historical market performance."""
import json
from pathlib import Path
import numpy as np
import pandas as pd
from research import (asof_values, simple_yield_proxy, walk_forward,
                      annualized_excess_sharpe, maximum_drawdown,
                      point_in_time_spreads, three_factor_ols,
                      black_litterman_posterior)


def synthetic_fixture(n_periods=104, n_assets=10, seed=20260912):
    rng=np.random.default_rng(seed)
    dates=pd.date_range("2020-01-03",periods=n_periods+1,freq="W-FRI")
    assets=[f"SYNTH_{i:02}" for i in range(n_assets)]
    market=rng.normal(.001,.015,n_periods)
    shocks=market[:,None]+rng.normal(.0003,.012,(n_periods,n_assets))
    prices=pd.DataFrame(np.vstack([np.full(n_assets,100.0),100*np.cumprod(1+shocks,axis=0)]),index=dates,columns=assets)
    # Artificial annual SIMPLE quotes known one day before every holding start.
    yields=pd.Series(np.linspace(2.0,3.0,n_periods),index=dates[:-1]-pd.Timedelta("1D"))
    known=asof_values(yields,dates[:-1],max_age="8D")
    rf=pd.Series(simple_yield_proxy(known.to_numpy(),7),index=dates[1:])
    rows=[]
    for i,asset in enumerate(assets):
        rows.append({"asset":asset,"available_at":dates[0]-pd.Timedelta("2D"),"market_cap":100*(i+1),"book_to_market":.2+.1*((i*3)%n_assets)})
        rows.append({"asset":asset,"available_at":dates[52]-pd.Timedelta("1D"),"market_cap":100*(n_assets-i),"book_to_market":.25+.1*((i*7)%n_assets)})
    return prices,rf,pd.DataFrame(rows),pd.Series(market,index=dates[1:])


def run():
    prices,rf,characteristics,market=synthetic_fixture()
    result,w=walk_forward(prices,rf,lookback=52,n_portfolios=10000,seed=20260912,cost_bps=10)
    returns=prices.pct_change(fill_method=None).iloc[1:]
    factors=point_in_time_spreads(returns,characteristics)
    idx=factors.index
    ols=three_factor_ols(returns.loc[idx].iloc[:,0],market.loc[idx],factors.SMB,factors.HML,rf.loc[idx])
    # One illustrative decision after 52 completed periods; no future data used.
    cov=returns.iloc[:52].cov().to_numpy()
    p=np.zeros((1,10)); p[0,0]=1; p[0,1]=-1
    posterior=black_litterman_posterior(cov,np.full(10,.1),2.5,p,np.array([.001]),np.array([[.0001]]))
    summary={
        "data_kind":"DETERMINISTIC SYNTHETIC TEST FIXTURE; NOT MARKET DATA",
        "revision_date":"2026-09-12",
        "not_original_2024_results":True,
        "seed":20260912,
        "assets":len(prices.columns),
        "input_weekly_return_periods":len(returns),
        "lookback_periods":52,
        "evaluation_periods":len(result),
        "candidate_portfolios_per_decision":10000,
        "cost_bps_per_unit_l1_traded":10,
        "net_return_synthetic_only":float(np.prod(1+result.net_return)-1),
        "annualized_excess_sharpe_synthetic_only":annualized_excess_sharpe(result.net_return,rf.loc[result.index]),
        "max_drawdown_synthetic_only":maximum_drawdown(result.net_return),
        "max_weight_sum_error":float(np.max(np.abs(w.sum(axis=1)-1))),
        "ols_synthetic_only":ols,
        "black_litterman_posterior_finite":bool(np.isfinite(posterior).all())}
    return summary


if __name__=="__main__":
    result=run()
    text=json.dumps(result,indent=2,allow_nan=False)+"\n"
    (Path(__file__).parent/"demo_results.json").write_text(text)
    print(text)
