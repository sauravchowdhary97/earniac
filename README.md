# Earnings Date Tracker

A Python script that fetches upcoming earnings dates for multiple companies and sorts them by date and time.

## Features

- Takes company tickers either as command-line arguments or from a file
- Uses Yahoo Finance API to fetch the latest earnings dates
- Displays all times in Eastern Time (ET) zone
- Sorts companies by reporting date and time
- Displays results grouped by date in the console
- Saves results to a CSV file

## Requirements

You'll need to install the required Python packages:

```bash
pip install -r requirements.txt
```

## Usage

### With command-line arguments:

```bash
python earnings_tracker.py -t AAPL,MSFT,GOOGL,AMZN
```

### With a file containing tickers:

Create a text file (e.g., `tickers.txt`) with one ticker per line, then:

```bash
python earnings_tracker.py -f tickers.txt
```

### Specify output file (optional):

```bash
python earnings_tracker.py -t AAPL,MSFT -o my_earnings.csv
```

## Output Example

```
Processing 4 companies...
[1/4] Getting data for AAPL
  Found earnings date in 'earningsTimestamp' for AAPL
[2/4] Getting data for MSFT
  Found earnings date in 'earningsTimestamp' for MSFT
[3/4] Getting data for GOOGL
  Found earnings date in 'earningsTimestamp' for GOOGL
[4/4] Getting data for AMZN
  Found earnings date in 'earningsTimestamp' for AMZN

Earnings Dates (Eastern Time):

2025-05-01
  AAPL (Apple Inc.) - 16:30:00 EDT
  AMZN (Amazon.com, Inc.) - 16:00:00 EDT

2025-05-02
  GOOGL (Alphabet Inc.) - 16:00:00 EDT

2025-05-10
  MSFT (Microsoft Corporation) - 16:30:00 EDT

Results saved to earnings_dates.csv
Note: All times in the CSV are in Eastern Time (ET)
```

## Notes

- Yahoo Finance doesn't always have earnings dates for all companies
- The script tries multiple methods to find earnings dates
- All dates and times are converted to Eastern Time (ET)
- Companies with no available date are shown at the end