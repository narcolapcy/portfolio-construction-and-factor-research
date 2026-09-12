"""Public research revision, 2026-09-12. Not the original 2024 submission.

All returns are decimal simple returns for one observation period. No network
access or embedded market data. Tested components, not a production trading system.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def finite(values, name="values"):
    a = np.asarray(values, dtype=float)
    if not a.size or not np.isfinite(a).all():
        raise ValueError(f"{name} must be nonempty and finite")
    return a


def dated(frame):
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("a DatetimeIndex is required")
    if frame.index.hasnans or frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("dates must be nonmissing, unique and ascending")
    return frame


def effective_annual_percent_to_period(annual_percent, periods_per_year=52):
    """Exact only for an EFFECTIVE annual rate. Treasury quotes are not this."""
    rate = finite(annual_percent, "annual percent") / 100
    if periods_per_year <= 0 or np.any(rate <= -1):
        raise ValueError("invalid rate or period count")
    return np.expm1(np.log1p(rate) / periods_per_year)


def simple_yield_proxy(annual_percent, days, day_basis=365):
    """Simple accrual proxy y%/100 * days/basis, not a Treasury total return.

    A quoted yield does not uniquely identify a traded instrument's holding-period
    return. Callers must declare this approximation and obtain the quote as of the
    start of the holding period; this function cannot establish source timing.
    """
    y = finite(annual_percent, "annual percent")
    d = finite(days, "days")
    if day_basis <= 0 or np.any(d <= 0):
        raise ValueError("day count and basis must be positive")
    return y / 100 * d / day_basis


def asof_values(observations, decisions, max_age="10D"):
    """Use only observations strictly available BEFORE each decision timestamp.

    observations.index means actual availability time, not the accounting date.
    Missing/stale quotes fail explicitly. Timestamp conventions must be consistent.
    """
    dated(observations)
    finite(observations.to_numpy())
    ds = pd.DatetimeIndex(decisions)
    dated(pd.Series(index=ds, dtype=float))
    if pd.Timedelta(max_age) <= pd.Timedelta(0):
        raise ValueError("max_age must be positive")
    left = pd.DataFrame({"decision": ds})
    right = pd.DataFrame({"available_at": observations.index, "value": observations.to_numpy()})
    joined = pd.merge_asof(left, right, left_on="decision", right_on="available_at",
                           direction="backward", allow_exact_matches=False,
                           tolerance=pd.Timedelta(max_age))
    if joined.value.isna().any():
        raise ValueError("no sufficiently recent observation known before a decision")
    return pd.Series(joined.value.to_numpy(), index=ds)


def price_returns(prices):
    dated(prices)
    a = finite(prices.to_numpy(), "prices")
    if a.ndim != 2 or len(a) < 2 or np.any(a <= 0) or prices.columns.has_duplicates:
        raise ValueError("unique assets and at least two rows of positive prices required")
    return prices.pct_change(fill_method=None).iloc[1:]


def annualized_excess_sharpe(returns, risk_free, periods_per_year=52):
    r = finite(returns, "returns")
    rf = finite(risk_free, "period risk-free returns")
    if r.ndim != 1 or len(r) < 2 or rf.shape != r.shape or periods_per_year <= 0:
        raise ValueError("matched one-dimensional period return series required")
    excess = r - rf
    sd = excess.std(ddof=1)
    if sd <= np.finfo(float).eps:
        raise ValueError("Sharpe undefined for zero excess-return volatility")
    # sqrt(T) scaling assumes comparable periods and ignores autocorrelation.
    return float(excess.mean() / sd * np.sqrt(periods_per_year))


def maximum_drawdown(returns):
    r = finite(returns, "returns")
    if r.ndim != 1 or np.any(r < -1):
        raise ValueError("simple returns must be >= -100%")
    wealth = np.r_[1.0, np.cumprod(1 + r)]
    peaks = np.maximum.accumulate(wealth)
    return float(np.max(1 - wealth / peaks))


def seeded_weights(n_assets, n_portfolios=10000, seed=20260912):
    if n_assets < 1 or n_portfolios < 1:
        raise ValueError("positive counts required")
    w = np.random.default_rng(seed).random((n_portfolios, n_assets))
    return w / w.sum(axis=1, keepdims=True)


def covariance_matrix(cov):
    c = finite(cov, "covariance")
    if c.ndim != 2 or c.shape[0] != c.shape[1] or not np.allclose(c, c.T):
        raise ValueError("square symmetric covariance required")
    if np.linalg.eigvalsh(c).min() <= 0:
        raise ValueError("positive-definite covariance required")
    return c


def black_litterman_posterior(cov, market_weights, risk_aversion, p, q, omega, tau=0.05):
    """Posterior expected EXCESS returns, with every input on the same period.

    Explicit caller-supplied views and uncertainty. No inference from future data.
    Linear solves avoid explicitly forming matrix inverses.
    """
    c = covariance_matrix(cov)
    w = finite(market_weights)
    p, q = finite(p), finite(q)
    o = covariance_matrix(omega)
    if tau <= 0 or risk_aversion <= 0 or w.shape != (len(c),):
        raise ValueError("invalid equilibrium inputs")
    if np.any(w < 0) or not np.isclose(w.sum(), 1):
        raise ValueError("market weights must be nonnegative and sum to one")
    if p.ndim != 2 or p.shape[1] != len(c) or q.shape != (len(p),) or o.shape != (len(p),len(p)):
        raise ValueError("view dimensions do not match")
    prior = risk_aversion * c @ w
    tc = tau * c
    return prior + tc @ p.T @ np.linalg.solve(p @ tc @ p.T + o, q - p @ prior)


def snapshot_factor_weights(snapshot):
    """Toy universe median spreads, NOT the published Fama-French factors."""
    if not {"asset", "market_cap", "book_to_market"}.issubset(snapshot.columns):
        raise ValueError("missing characteristics")
    if snapshot.asset.duplicated().any() or len(snapshot) < 4:
        raise ValueError("at least four unique assets required")
    cap, btm = finite(snapshot.market_cap), finite(snapshot.book_to_market)
    if np.any(cap <= 0) or np.any(btm <= 0):
        raise ValueError("positive capitalization and book-to-market required")
    def spread(long, short):
        if not long.any() or not short.any():
            raise ValueError("empty side after median split")
        return long.astype(float)/long.sum() - short.astype(float)/short.sum()
    return pd.DataFrame({"SMB":spread(cap < np.median(cap), cap > np.median(cap)),
                         "HML":spread(btm > np.median(btm), btm < np.median(btm))},
                         index=snapshot.asset)


def point_in_time_spreads(period_returns, characteristics, max_age="400D"):
    """At each interval start, select last known characteristics strictly earlier.

    Returns are indexed by interval END. First row is a boundary only and omitted
    because its preceding holding-period start is unspecified. Output is gross
    equal-weight long-short spread returns; no costs, borrow or leverage model.
    """
    dated(period_returns)
    if len(period_returns) < 2 or period_returns.columns.has_duplicates:
        raise ValueError("at least two periods and unique assets required")
    finite(period_returns.to_numpy())
    ch = characteristics.copy()
    required = {"asset", "available_at", "market_cap", "book_to_market"}
    if not required.issubset(ch.columns):
        raise ValueError("missing point-in-time fields")
    ch["available_at"] = pd.to_datetime(ch.available_at)
    if ch.available_at.isna().any() or ch.duplicated(["asset","available_at"]).any():
        raise ValueError("duplicate or missing availability timestamps")
    age = pd.Timedelta(max_age)
    if age <= pd.Timedelta(0):
        raise ValueError("max_age must be positive")
    rows = []
    for i in range(1,len(period_returns)):
        cutoff = period_returns.index[i-1]
        known = ch[(ch.available_at < cutoff) & (ch.available_at >= cutoff-age)]
        latest = known.sort_values("available_at").groupby("asset").tail(1)
        if not set(period_returns.columns).issubset(set(latest.asset)):
            raise ValueError("missing/stale characteristics for the declared universe")
        latest = latest.set_index("asset").loc[period_returns.columns].rename_axis("asset").reset_index()
        weights = snapshot_factor_weights(latest)
        realized = period_returns.iloc[i].to_numpy()
        rows.append(realized @ weights.to_numpy())
    return pd.DataFrame(rows, index=period_returns.index[1:],columns=["SMB","HML"])


def three_factor_ols(asset_returns, market_returns, smb, hml, risk_free):
    """Intercept and MKT/SMB/HML coefficients on aligned period data; no p-values."""
    arrays = [finite(x) for x in (asset_returns,market_returns,smb,hml,risk_free)]
    if any(a.ndim != 1 or a.shape != arrays[0].shape for a in arrays) or len(arrays[0]) < 6:
        raise ValueError("matched vectors with at least six observations required")
    y,m,s,h,rf=arrays
    x=np.column_stack([np.ones(len(y)),m-rf,s,h])
    if np.linalg.matrix_rank(x) != 4:
        raise ValueError("rank-deficient factor design")
    coef=np.linalg.lstsq(x,y-rf,rcond=None)[0]
    return dict(zip(("alpha_per_period","market_beta","smb_beta","hml_beta"),map(float,coef)))


def walk_forward(prices, risk_free, lookback=52, n_portfolios=10000, seed=20260912, cost_bps=10):
    """Long-only fully invested Monte Carlo selection using completed periods only.

    Weights picked at period start are applied to the NEXT observed return.
    Costs are charged on sum(abs(target - drifted_previous_weights)), with initial
    deployment from cash charged on gross purchases. Same close execution, no
    slippage/delisting simulation. This is a simplified educational test framework.
    """
    r=price_returns(prices)
    dated(risk_free)
    if not risk_free.index.equals(r.index):
        raise ValueError("risk-free returns must align exactly with price-return intervals")
    rf=finite(risk_free.to_numpy())
    if lookback < 3 or len(r) <= lookback or not (0 <= cost_bps < 10000):
        raise ValueError("invalid lookback or costs")
    w_candidates=seeded_weights(r.shape[1],n_portfolios,seed)
    previous=np.zeros(r.shape[1])
    results=[]
    weights=[]
    for t in range(lookback,len(r)):
        train=r.iloc[t-lookback:t].to_numpy()
        excess=train-rf[t-lookback:t,None]
        means=w_candidates @ excess.mean(axis=0)
        cov=np.atleast_2d(np.cov(excess,rowvar=False,ddof=1))
        vols=np.sqrt(np.maximum(np.einsum('ij,jk,ik->i',w_candidates,cov,w_candidates),0))
        valid=vols > np.finfo(float).eps
        if not valid.any():
            raise ValueError("all candidate portfolios have zero training volatility")
        score=np.full(n_portfolios,-np.inf)
        score[valid]=means[valid]/vols[valid]
        w=w_candidates[score.argmax()]
        turnover=float(np.abs(w-previous).sum())
        cost=turnover*cost_bps/10000
        if cost >= 1:
            raise ValueError("cost exceeds available wealth")
        realized=r.iloc[t].to_numpy()
        gross=float(w @ realized)
        net=(1-cost)*(1+gross)-1
        previous=w*(1+realized)/(1+gross)
        results.append([gross,net,turnover,cost])
        weights.append(w)
    idx=r.index[lookback:]
    return (pd.DataFrame(results,index=idx,columns=["gross_return","net_return","turnover_l1","cost_fraction"]),
            pd.DataFrame(weights,index=idx,columns=r.columns))
