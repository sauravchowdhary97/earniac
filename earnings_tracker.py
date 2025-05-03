import yfinance as yf
import pandas as pd
from datetime import datetime
import argparse
import time
import pytz
from typing import List, Dict, Union, Optional

def get_earnings_date(ticker_symbol: str) -> Dict[str, Union[str, None, datetime]]:
    """
    Get the most recent or upcoming earnings date for a company ticker.
    
    Args:
        ticker_symbol: Company ticker symbol
    
    Returns:
        Dictionary with company info and earnings date
    """
    try:
        # Clean and normalize ticker
        ticker = ticker_symbol.strip().upper()
        
        # Get ticker object
        ticker_obj = yf.Ticker(ticker)
        
        # Get company info
        info = ticker_obj.info
        company_name = info.get('shortName', ticker)
        
        # Try different timestamp fields that might contain earnings info
        # Yahoo Finance API sometimes changes field names or structures
        earnings_timestamp = None
        
        # Check all possible fields where earnings date might be stored
        possible_fields = [
            'earningsTimestamp', 
            'nextEarningsDate',
            'mostRecentQuarter',
            'lastFiscalYearEnd'
        ]
        
        for field in possible_fields:
            if field in info and info[field]:
                earnings_timestamp = info[field]
                print(f"  Found earnings date in '{field}' for {ticker}")
                break
        
        # Convert timestamp to datetime if found
        if earnings_timestamp:

            current_timestamp = int(time.time())
            if earnings_timestamp < current_timestamp:
                # Try with earningsTimestampStart
                earnings_timestamp_start = info['earningsTimestampStart']
                if earnings_timestamp_start > current_timestamp:
                        earnings_timestamp = earnings_timestamp_start

            # Convert to UTC datetime first
            utc_dt = datetime.fromtimestamp(earnings_timestamp, tz=pytz.UTC)
            
            # Convert to Eastern Time
            eastern = pytz.timezone('US/Eastern')
            earnings_date = utc_dt.astimezone(eastern)
            
            # Format date in ISO format and words
            date_str_iso = earnings_date.strftime('%Y-%m-%d')
            
            # Format date in words with ordinal suffix
            day = earnings_date.day
            if 4 <= day <= 20 or 24 <= day <= 30:
                suffix = "th"
            else:
                suffix = ["st", "nd", "rd"][day % 10 - 1] if day % 10 <= 3 else "th"
                
            date_str_words = f"{day}{suffix} {earnings_date.strftime('%B')}, {earnings_date.year}"
            time_str = earnings_date.strftime('%H:%M:%S %Z')
            
            return {
                'ticker': ticker,
                'company': company_name,
                'date_iso': date_str_iso,
                'date': date_str_words,
                'time': time_str,
                'datetime': earnings_date
            }
        
        # If no timestamp found, try the calendar method
        try:
            calendar = ticker_obj.calendar
            
            # Check if calendar is a DataFrame and has data
            if isinstance(calendar, pd.DataFrame) and not calendar.empty and 'Earnings Date' in calendar.index:
                earnings_date_raw = calendar.loc['Earnings Date'].iloc[0]
                
                if isinstance(earnings_date_raw, pd.Timestamp):
                    # Convert naive datetime to UTC first if it doesn't have timezone info
                    if earnings_date_raw.tzinfo is None:
                        earnings_date_utc = pytz.UTC.localize(earnings_date_raw)
                    else:
                        earnings_date_utc = earnings_date_raw.astimezone(pytz.UTC)
                    
                    # Convert to Eastern Time
                    eastern = pytz.timezone('US/Eastern')
                    earnings_date = earnings_date_utc.astimezone(eastern)
                    
                    # Format date in ISO format and words
                    date_str_iso = earnings_date.strftime('%Y-%m-%d')
                    
                    # Format date in words with ordinal suffix
                    day = earnings_date.day
                    if 4 <= day <= 20 or 24 <= day <= 30:
                        suffix = "th"
                    else:
                        suffix = ["st", "nd", "rd"][day % 10 - 1] if day % 10 <= 3 else "th"
                        
                    date_str_words = f"{day}{suffix} {earnings_date.strftime('%B')}, {earnings_date.year}"
                    time_str = earnings_date.strftime('%H:%M:%S %Z')
                    
                    return {
                        'ticker': ticker,
                        'company': company_name,
                        'date_iso': date_str_iso,
                        'date': date_str_words,
                        'time': time_str,
                        'datetime': earnings_date
                    }
        except Exception as e:
            print(f"  Note: Could not get calendar data for {ticker}: {str(e)}")
        
        # Try earnings history as a last resort
        try:
            earnings_dates = ticker_obj.earnings_dates
            
            if isinstance(earnings_dates, pd.DataFrame) and not earnings_dates.empty:
                # Get the most recent earnings date from history
                latest_earnings = earnings_dates.iloc[0]
                earnings_date_raw = latest_earnings.name
                
                if isinstance(earnings_date_raw, pd.Timestamp):
                    # Convert naive datetime to UTC first if it doesn't have timezone info
                    if earnings_date_raw.tzinfo is None:
                        earnings_date_utc = pytz.UTC.localize(earnings_date_raw)
                    else:
                        earnings_date_utc = earnings_date_raw.astimezone(pytz.UTC)
                    
                    # Convert to Eastern Time
                    eastern = pytz.timezone('US/Eastern')
                    earnings_date = earnings_date_utc.astimezone(eastern)
                    
                    # Format date in ISO format and words
                    date_str_iso = earnings_date.strftime('%Y-%m-%d')
                    
                    # Format date in words with ordinal suffix
                    day = earnings_date.day
                    if 4 <= day <= 20 or 24 <= day <= 30:
                        suffix = "th"
                    else:
                        suffix = ["st", "nd", "rd"][day % 10 - 1] if day % 10 <= 3 else "th"
                        
                    date_str_words = f"{day}{suffix} {earnings_date.strftime('%B')}, {earnings_date.year}"
                    time_str = earnings_date.strftime('%H:%M:%S %Z')
                    
                    return {
                        'ticker': ticker,
                        'company': company_name,
                        'date_iso': date_str_iso,
                        'date': date_str_words,
                        'time': time_str,
                        'datetime': earnings_date
                    }
        except Exception as e:
            print(f"  Note: Could not get earnings_dates for {ticker}: {str(e)}")
        
        # If we get here, we couldn't find an earnings date
        print(f"  Warning: No earnings date found for {ticker}")
        return {
            'ticker': ticker,
            'company': company_name,
            'date_iso': None,
            'date': None,
            'time': None,
            'datetime': None
        }
        
    except Exception as e:
        print(f"Error processing {ticker_symbol}: {str(e)}")
        return {
            'ticker': ticker_symbol,
            'company': ticker_symbol,
            'date': None,
            'time': None,
            'datetime': None
        }

def process_companies(company_list: List[str]) -> pd.DataFrame:
    """
    Process a list of company tickers and get their earnings dates.
    
    Args:
        company_list: List of company tickers
    
    Returns:
        DataFrame with earnings information sorted by date and time
    """
    results = []
    
    print(f"Processing {len(company_list)} companies...")
    for i, company in enumerate(company_list):
        print(f"[{i+1}/{len(company_list)}] Getting data for {company}")
        result = get_earnings_date(company)
        results.append(result)
        # Add a short delay to avoid hitting rate limits
        time.sleep(1)
    
    # Create dataframe
    df = pd.DataFrame(results)
    
    # If no data or no datetime column, return empty dataframe
    if df.empty or 'datetime' not in df.columns:
        print("Warning: No earnings dates found for any of the companies")
        return pd.DataFrame(columns=['ticker', 'company', 'date', 'time', 'datetime'])
    
    # Remove rows with no datetime for sorting
    df_with_dates = df.dropna(subset=['datetime'])
    df_without_dates = df[df['datetime'].isna()]
    
    # Sort rows with dates
    if not df_with_dates.empty:
        df_sorted_dates = df_with_dates.sort_values(
            by=['datetime'], 
            ascending=[True]
        )
        # Combine sorted dates with rows without dates
        df_sorted = pd.concat([df_sorted_dates, df_without_dates])
    else:
        df_sorted = df
    
    return df_sorted

def format_output(df: pd.DataFrame) -> str:
    """
    Format the dataframe for nice display.
    
    Args:
        df: DataFrame with earnings information
    
    Returns:
        Formatted string for display
    """
    if df.empty:
        return "No earnings data found for the requested companies."
    
    # Copy the dataframe for display
    display_df = df.copy()
    
    # Drop the datetime column if it exists
    if 'datetime' in display_df.columns:
        display_df = display_df.drop('datetime', axis=1)
    
    # For companies with no earnings date, mark as "No date available"
    display_df['date'] = display_df['date'].fillna("No date available")
    display_df['time'] = display_df['time'].fillna("--")
    
    # Add header indicating Eastern Time
    header = "Earnings Dates (Eastern Time):"
    
    # Group by date_iso (for sorting) but display the word format
    current_date_iso = None
    current_date_words = None
    lines = [header]
    no_date_lines = []
    
    # Sort the dataframe by date_iso if it exists
    if 'date_iso' in display_df.columns:
        df_with_dates = display_df.dropna(subset=['date_iso'])
        df_without_dates = display_df[display_df['date_iso'].isna()]
        
        # Sort by date_iso
        if not df_with_dates.empty:
            df_with_dates = df_with_dates.sort_values(by='date_iso')
            
        # Recombine
        display_df = pd.concat([df_with_dates, df_without_dates])
    
    for _, row in display_df.iterrows():
        company_info = f"  {row['ticker']} ({row['company']})"
        if row['time'] != "--":
            company_info += f" - {row['time']}"
            
        if row['date'] == "No date available":
            no_date_lines.append(company_info)
        else:
            date_iso = row.get('date_iso', None)
            if date_iso != current_date_iso:
                current_date_iso = date_iso
                current_date_words = row['date']
                lines.append(f"\n\033[1m{current_date_words} ({current_date_iso})\033[0m")
            lines.append(company_info)
    
    # Add companies with no date at the end
    if no_date_lines:
        lines.append("\n\033[1mNo Date Available\033[0m")
        lines.extend(no_date_lines)
    
    if len(lines) <= 1:
        return "No earnings data found for the requested companies."
    
    return "\n".join(lines)

def save_to_csv(df: pd.DataFrame, output_file: str) -> None:
    """
    Save the results to a CSV file.
    
    Args:
        df: DataFrame with earnings information
        output_file: Output file path
    """
    if df.empty:
        # Create empty dataframe with required columns
        save_df = pd.DataFrame(columns=['ticker', 'company', 'date_iso', 'date', 'time'])
    else:
        # Create a copy
        save_df = df.copy()
        
        # Drop the datetime column if it exists
        if 'datetime' in save_df.columns:
            save_df = save_df.drop('datetime', axis=1)
    
    save_df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Get upcoming earnings dates for companies (displayed in Eastern Time)')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-t', '--tickers', help='Comma-separated list of ticker symbols (e.g., AAPL,MSFT,GOOGL)')
    group.add_argument('-f', '--file', help='File containing ticker symbols (one per line)')
    
    parser.add_argument('-o', '--output', help='Output CSV file', default='earnings_dates.csv')
    
    args = parser.parse_args()
    
    if args.tickers:
        companies = [ticker.strip() for ticker in args.tickers.split(',')]
    else:
        with open(args.file, 'r') as f:
            companies = [line.strip() for line in f if line.strip()]
    
    print("All times will be displayed in Eastern Time (ET)")
    
    # Get and process the earnings dates
    results_df = process_companies(companies)
    
    # Display the results
    formatted_output = format_output(results_df)
    print("\n" + formatted_output)
    
    # Save to CSV
    save_to_csv(results_df, args.output)
    print("Note: All times in the CSV are in Eastern Time (ET)")

if __name__ == "__main__":
    main()