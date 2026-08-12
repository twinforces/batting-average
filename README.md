# Batting Average Analyzer

A simple Python script that measures how often one investment beats another over rolling time windows.

It answers the practical question:  
**“If I bought and held for N trading days, what percentage of the time would I have finished ahead of the benchmark?”**

This is the same style of “batting average” analysis used in quantitative screening (overlapping windows, total-return basis).

## Features

- Downloads adjusted daily prices (total return) via `yfinance`
- Aligns the two series on common trading days
- Computes overlapping windows of any length
- Reports:
  - Batting average (win rate)
  - Average excess return
  - Median excess return
  - Number of windows and date range

## Requirements

```bash
pip install yfinance pandas
```

## Usage

```bash
python batting_average.py SYMBOL_A SYMBOL_B [options]
```

### Arguments

| Argument     | Description                          | Default |
|--------------|--------------------------------------|---------|
| `symbol_a`   | Candidate ticker (e.g. AGTHX)        | required |
| `symbol_b`   | Benchmark ticker (e.g. SPY or ^GSPC) | required |
| `--window`   | Window length in trading days        | 21      |
| `--years`    | Years of history to download         | 15      |

### Examples

```bash
# ~1-month windows (21 trading days)
python batting_average.py AGTHX SPY --window 21

# 1-year windows
python batting_average.py AGTHX SPY --window 252

# Longer history
python batting_average.py AGTHX ^GSPC --window 21 --years 20

# Recent 5-year period only
python batting_average.py AGTHX SPY --window 252 --years 5
```

## Sample Output

```
Batting average analysis
==================================================
Candidate : AGTHX
Benchmark : SPY
Window    : 252 trading days
Period    : 2011-07-18 → 2026-08-11
Windows   : 3,537
Batting average (win rate): 62.2%
Average excess return    : 1.00%
Median excess return     : 1.42%
```

## Interpretation Notes

- **Window length matters.** Short windows (≈1 month) usually produce win rates near 50%. Longer windows (1 year+) typically show more separation if an edge exists.
- Results use **total return** (adjusted closes), so dividends and splits are included.
- Overlapping windows give many more observations than non-overlapping ones. This is intentional.
- Past win rates do not guarantee future results.

## License

MIT. Use freely.
```