import os
import pandas as pd
from core.entsoe_client import ENTSOEClient
import logging
from datetime import datetime, timedelta
import time
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def download_generation_daily(client, start_date_str, end_date_str, country_codes, output_dir, filename_pattern):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    start_dt = pd.to_datetime(start_date_str)
    end_dt = pd.to_datetime(end_date_str)
    
    current_dt = start_dt
    while current_dt < end_dt:
        next_dt = current_dt + timedelta(days=1)
        date_str = current_dt.strftime("%Y%m%d")
        
        for country in country_codes:
            filename = filename_pattern.format(country=country, date=date_str)
            output_file = os.path.join(output_dir, filename)
            
            if os.path.exists(output_file):
                logging.info(f"Skipping {country} for {date_str} (file exists).")
                continue
            
            logging.info(f"Downloading generation for {country} on {date_str}...")
            
            try:
                # Use daily chunk size
                df_daily = client.query(current_dt, next_dt, country_code=country, 
                                      document_type='A75', process_type='A16', 
                                      chunk_size_days=1)
                
                if not df_daily.empty:
                    df_daily.to_csv(output_file)
                    logging.info(f"Saved daily file: {output_file}")
                else:
                    logging.warning(f"No data for {country} on {date_str}.")
            except Exception as e:
                logging.error(f"Critical error during download: {e}")
                logging.error("Stopping process due to consecutive failures or site being down.")
                sys.exit(1)
            
            time.sleep(0.5)
        
        current_dt = next_dt
        time.sleep(1)

if __name__ == "__main__":
    # Load API Key
    key_file = "ENTSOE_API_KEY.txt"
    try:
        if not os.path.exists(key_file):
            logger.error(f"API key file '{key_file}' not found.")
            logger.info("Please create a file named 'ENTSOE_API_KEY.txt' in the ETP API TOOL directory and paste your API key inside in the format: 'YOUR_KEY_HERE'")
            sys.exit(1)
            
        with open(key_file, "r") as f:
            key_line = f.read().strip()
            # Handle both 'KEY' and KEY formats
            api_key = key_line.split("'")[1] if "'" in key_line else key_line
    except Exception as e:
        logger.error(f"Could not load API key from {key_file}: {e}")
        sys.exit(1)
    
    client = ENTSOEClient(api_key)
    
    # Check if site is up before starting
    if not client.check_site_availability():
        logger.error("Aborting download: ENTSO-E API is currently unavailable.")
        sys.exit(1)
    
    # --- CONFIGURATION ---
    START_DATE = "2024-06-01"
    END_DATE = "2024-06-05" 
    TARGET_COUNTRIES = ['GR'] 
    
    # Output path is now relative to the script location, going one level up to ETP_DATA
    OUTPUT_DIRECTORY = "../ETP_DATA/16.1.B_C_actual_generation_per_type"
    FILENAME_PATTERN = "generation_{country}_{date}.csv"
    
    download_generation_daily(client, START_DATE, END_DATE, TARGET_COUNTRIES, OUTPUT_DIRECTORY, FILENAME_PATTERN)
