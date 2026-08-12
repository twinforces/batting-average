#!/usr/bin/env python3
"""
Batting-average analysis between two symbols.
Example:
    python batting_average.py AGTHX SPY --window 21
    python batting_average.py AGTHX ^GSPC --window 252
"""

import argparse
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


def download_adjusted_closes(symbol: str, start: str, end: str) -> pd.Series:
    """Download adjusted close (total return) series."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=start, end=end, auto_adjust=True)
    if df.empty:
        raise ValueError(f"No data returned for {symbol}")
    return df["Close"].rename(symbol)


def batting_average(
    symbol_a: str,
    symbol_b: str,
    window: int = 21,
    years: int = 15,
) -> dict:
    """
    Compute overlapping-window batting average.

    Parameters
    ----------
    symbol_a : str
        The candidate fund/ticker (e.g. "AGTHX")
    symbol_b : str
        The benchmark (e.g. "SPY" or "^GSPC")
    window : int
        Number of trading days in each window (21 ≈ 1 month, 252 ≈ 1 year)
    years : int
        How many years of history to pull

    Returns
    -------
    dict with batting average, average excess return, etc.
    """
    end = datetime.today()
    start = end - timedelta(days=years * 365 + 30)  # small buffer

    a = download_adjusted_closes(symbol_a, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
    b = download_adjusted_closes(symbol_b, start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))

    # Align on common trading days
    df = pd.concat([a, b], axis=1).dropna()
    if len(df) < window + 10:
        raise ValueError("Not enough overlapping data points")

    # Daily returns
    rets = df.pct_change().dropna()

    # Rolling cumulative return over the window
    # (1 + r1)*(1 + r2)*...*(1 + rN) - 1
    roll_a = (1 + rets[symbol_a]).rolling(window).apply(lambda x: x.prod() - 1, raw=True)
    roll_b = (1 + rets[symbol_b]).rolling(window).apply(lambda x: x.prod() - 1, raw=True)

    excess = (roll_a - roll_b).dropna()

    wins = (excess > 0).sum()
    total = len(excess)
    batting = wins / total if total > 0 else float("nan")

    return {
        "symbol_a": symbol_a,
        "symbol_b": symbol_b,
        "window_trading_days": window,
        "observations": total,
        "batting_average": batting,
        "avg_excess_return": excess.mean(),
        "median_excess_return": excess.median(),
        "pct_positive_excess": batting,  # same as batting_average
        "start_date": df.index[0].date().isoformat(),
        "end_date": df.index[-1].date().isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Rolling-window batting average between two symbols")
    parser.add_argument("symbol_a", help="Candidate ticker (e.g. AGTHX)")
    parser.add_argument("symbol_b", help="Benchmark ticker (e.g. SPY or ^GSPC)")
    parser.add_argument("--window", type=int, default=21, help="Trading-day window length (default 21 ≈ 1 month)")
    parser.add_argument("--years", type=int, default=15, help="Years of history to download")
    args = parser.parse_args()

    result = batting_average(args.symbol_a, args.symbol_b, window=args.window, years=args.years)

    print(f"\nBatting average analysis")
    print(f"{'='*50}")
    print(f"Candidate : {result['symbol_a']}")
    print(f"Benchmark : {result['symbol_b']}")
    print(f"Window    : {result['window_trading_days']} trading days")
    print(f"Period    : {result['start_date']} → {result['end_date']}")
    print(f"Windows   : {result['observations']:,}")
    print(f"Batting average (win rate): {result['batting_average']:.1%}")
    print(f"Average excess return    : {result['avg_excess_return']:.2%}")
    print(f"Median excess return     : {result['median_excess_return']:.2%}")
    print()


if __name__ == "__main__":
    main()