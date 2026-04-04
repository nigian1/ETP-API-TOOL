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

def download_generation_yearly(client, start_year, end_year, country_codes, output_dir, filename_pattern):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    for year in range(start_year, end_year + 1):
        start_dt = f"{year}-01-01"
        end_dt = f"{year+1}-01-01"
        
        for country in country_codes:
            filename = filename_pattern.format(country=country, year=year)
            output_file = os.path.join(output_dir, filename)
            
            if os.path.exists(output_file):
                logging.info(f"Skipping {country} for {year} (file exists).")
                continue
            
            logging.info(f"Downloading generation for {country} in {year}...")
            
            try:
                # Use 7-day chunks internally in the client to avoid API timeouts for a full year
                df_year = client.query(start_dt, end_dt, country_code=country, 
                                      document_type='A75', process_type='A16', 
                                      chunk_size_days=7)
                
                if not df_year.empty:
                    df_year.to_csv(output_file)
                    logging.info(f"Saved yearly file: {output_file}")
                else:
                    logging.warning(f"No data for {country} in {year}.")
            except Exception as e:
                logging.error(f"Critical error during download: {e}")
                logging.error("Stopping process due to consecutive failures or site being down.")
                sys.exit(1)
            
            time.sleep(1)

if __name__ == "__main__":
    # Load API Key
    key_file = "ENTSOE_API_KEY.txt"
    try:
        if not os.path.exists(key_file):
            logger.error(f"API key file '{key_file}' not found.")
            logger.info("Please create a file named 'ENTSOE_API_KEY.txt' in the ETP API TOOL directory and paste your API key inside.")
            sys.exit(1)
            
        with open(key_file, "r") as f:
            key_line = f.read().strip()
            api_key = key_line.split('=')[-1].strip("'\" ")
    except Exception as e:
        logger.error(f"Could not load API key from {key_file}: {e}")
        sys.exit(1)
    
    client = ENTSOEClient(api_key)
    
    # Check if site is up before starting
    if not client.check_site_availability():
        logger.error("Aborting download: ENTSO-E API is currently unavailable.")
        sys.exit(1)
    
    # --- CONFIGURATION ---
    START_YEAR = 2022
    END_YEAR = 2024
    TARGET_COUNTRIES = ['GR'] 
    
    # Output path is now relative to the script location, going one level up to ETP_DATA
    OUTPUT_DIRECTORY = "../ETP_DATA/16.1.B_C_actual_generation_per_type"
    FILENAME_PATTERN = "16.1.B_C_{country}_{year}.csv"
    
    download_generation_yearly(client, START_YEAR, END_YEAR, TARGET_COUNTRIES, OUTPUT_DIRECTORY, FILENAME_PATTERN)
