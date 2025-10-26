from datetime import datetime, timedelta
import pandas as pd
import requests
import datetime
import tempfile
import zipfile
import os

"""
initialising a cache here
""" # fix to issue 5

cache = {} # main module level cache dictionary

def _post_process_bhav_copy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Post-process the Bhav Copy DataFrame to ensure it has the correct columns and data types.
    
    Args:
        df: pandas DataFrame containing the Bhav Copy data
    Returns:
        pandas DataFrame containing the post-processed Bhav Copy data
    """
    # TODO: Implement the logic to filter the DataFrame.
    raise NotImplementedError

def _download_bhav_copy(date: str):
    """
    Downloads the NSE Bhav Copy for a given date and returns it as a DataFrame.
    
    Args:
        date: Date string in format 'YYYY-MM-DD'
    
    Returns:
        pandas DataFrame containing the Bhav Copy data
    """
    if date in cache:
        return cache[date]
    
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

        cache[date] = df # storing in cache if data already doesnt exist
        
        return df
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        return None


def get_data_for_date_range(date: str, ndays: int):         # this function init fixes the issue #3

    all_data = []  # list to store daily DataFrames

    # converts start_date to datetime object
    current_date = datetime.strptime(date, "%Y-%m-%d")

    for _ in range(ndays): # main loop that iterates through each day in the range
        date_str = current_date.strftime("%Y-%m-%d")
        try:
            # downloads data for this date
            df = _download_bhav_copy(date_str)

            if df is not None and not df.empty:
                all_data.append(df)
            else:
                print("No data found , skipping")

        except Exception as e:
            print("Error downloading the data")

        # move to next day
        current_date += timedelta(days=1)

    if not all_data:
        # return empty DataFrame if no data was downloaded
        return pd.DataFrame()

    # combine all daily DataFrames into one master DataFrame
    combined_df = pd.concat(all_data, ignore_index=True)

    return combined_df

