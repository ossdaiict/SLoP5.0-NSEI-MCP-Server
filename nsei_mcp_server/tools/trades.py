import pandas as pd
import requests
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from typing import Any

def _post_process_bhav_copy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Post-process the Bhav Copy DataFrame to ensure it has the correct columns and data types.
    
    Args:
        df: pandas DataFrame containing the Bhav Copy data
    Returns:
        pandas DataFrame containing the post-processed Bhav Copy data
    """
    # For now, return as-is. Implement filtering logic as needed
    return df

def _download_bhav_copy(date: str):
    """
    Downloads the NSE Bhav Copy for a given date and returns it as a DataFrame.
    
    Args:
        date: Date string in format 'YYYY-MM-DD'
    
    Returns:
        pandas DataFrame containing the Bhav Copy data
    """
    try:
        session = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Handle date format conversion
        if '-' in date:
            try:
                parsed_date = datetime.strptime(date, "%Y-%m-%d")
                date = parsed_date.strftime("%Y%m%d")
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")
                return None
                
        url = f"https://nsearchives.nseindia.com/content/cm/BhavCopy_NSE_CM_0_0_0_{date}_F_0000.csv.zip"
        
        response = session.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"Download failed with status code: {response.status_code} for URL: {url}")
            return None
        
        # Process zip file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
            temp_zip.write(response.content)
            temp_zip_path = temp_zip.name
        
        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]
            if not csv_files:
                print("No CSV file found in zip archive")
                os.unlink(temp_zip_path)
                return None
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_csv:
                temp_csv.write(zip_ref.read(csv_files[0]))
                temp_csv_path = temp_csv.name
        
        # Read and process data
        df = pd.read_csv(temp_csv_path)
        df = _post_process_bhav_copy(df)
        
        # Cleanup
        os.unlink(temp_zip_path)
        os.unlink(temp_csv_path)
        
        return df
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return None

def get_data_for_date_range(date: str, ndays: int):
    """
    Get data for a specific date range.
    
    Args:
        date: date string in format 'YYYY-MM-DD' (end date)
        ndays: number of days to get data leading up to the given date
    
    Returns:
        pandas.DataFrame: Combined DataFrame of all days in the range
    """
    # Convert end date string to datetime
    end_date = datetime.strptime(date, "%Y-%m-%d")
    
    # Calculate start date (ndays before end_date)
    start_date = end_date - timedelta(days=ndays - 1)
    
    # Container for daily DataFrames
    all_data = []
    
    # Iterate through each date
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        try:
            # Call the existing function to download for that date
            df = _download_bhav_copy(date_str)
            if df is not None and not df.empty:
                all_data.append(df)
        except Exception as e:
            print(f"Failed to fetch data for {date_str}: {e}")
        
        # Move to next day
        current_date += timedelta(days=1)
    
    # Combine all DataFrames
    if all_data:
        master_df = pd.concat(all_data, ignore_index=True)
    else:
        master_df = pd.DataFrame()  # empty DataFrame fallback
    
    return master_df

def get_trades(date: str, ndays: int) -> list[dict[str, Any]]:
    """
    Get summarized trade data for stocks over a date range.
    
    Args:
        date: End date string in format 'YYYY-MM-DD'
        ndays: Number of days to get data leading up to the given date
    
    Returns:
        List of dictionaries containing summarized trade data for each symbol
        Each dictionary contains:
            - symbol: Stock symbol
            - total_volume: Total traded volume across all days
            - total_value: Total traded value across all days
            - first_open: Opening price from the first day
            - last_close: Closing price from the last day
    """
    try:
        # Fetch data using the data_fetcher utility
        df = get_data_for_date_range(date, ndays)
        
        # Check if DataFrame is empty
        if df is None or df.empty:
            print(f"No data available for the specified date range")
            return []
        
        # Print available columns for debugging
        print(f"Available columns: {df.columns.tolist()}")
        
        # Ensure required columns exist
        required_columns = ['TckrSymb', 'TtlTradgVol', 'TtlTrfVal', 'OpnPric', 'ClsPric', 'TradDt']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return []
        
        # Convert TradDt to datetime for proper sorting
        df['TradDt'] = pd.to_datetime(df['TradDt'])
        
        # Sort by symbol and date to ensure proper ordering
        df = df.sort_values(['TckrSymb', 'TradDt'])
        
        # Group by symbol and aggregate
        result = []
        
        for symbol, group in df.groupby('TckrSymb'):
            # Calculate aggregated metrics
            total_volume = group['TtlTradgVol'].sum()
            total_value = group['TtlTrfVal'].sum()
            
            # Get first opening price (earliest date)
            first_open = group.iloc[0]['OpnPric']
            
            # Get last closing price (latest date)
            last_close = group.iloc[-1]['ClsPric']
            
            # Create summary dictionary
            summary = {
                'symbol': symbol,
                'total_volume': float(total_volume),
                'total_value': float(total_value),
                'first_open': float(first_open),
                'last_close': float(last_close)
            }
            
            result.append(summary)
        
        # Sort result by symbol for consistent output
        result = sorted(result, key=lambda x: x['symbol'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_trades: {str(e)}")
        import traceback
        traceback.print_exc()
        return []


# Example usage and testing
if __name__ == "__main__":
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    
    # Test the function with a recent date
    # Note: Use a date that's likely to have data (weekday, not too recent)
    print("Testing get_trades function...")
    print("=" * 60)
    
    trades = get_trades('2025-01-15', 5)
    
    if trades:
        print(f"\nSuccessfully retrieved data for {len(trades)} symbols")
        print("\nSample data (first 5 symbols):")
        print("=" * 60)
        for trade in trades[:5]:
            print(f"\nSymbol: {trade['symbol']}")
            print(f"  Total Volume: {trade['total_volume']:,.0f}")
            print(f"  Total Value: Rs.{trade['total_value']:,.2f}")
            print(f"  First Open: Rs.{trade['first_open']:.2f}")
            print(f"  Last Close: Rs.{trade['last_close']:.2f}")
    else:
        print("No trades data retrieved")
