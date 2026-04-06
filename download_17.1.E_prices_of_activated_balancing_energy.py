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

# Mapping of common LFC Areas (LFA) and Scheduling Control Areas (SCA) for balancing
BALANCING_AREAS = {
    'DE_50HZ': '10YDE-VE-------2',
    'DE_AMPRION': '10YDE-RWENET---I',
    'DE_TENNET': '10YDE-EON------1',
    'DE_TRANSNETBW': '10YDE-ENBW-----N',
    'AT': '10YAT-APG------L',
    'BE': '10YBE----------2',
    'CH': '10YCH-SWISSGRIDZ',
    'CZ': '10YCZ-CEPS-----N',
    'DK1': '10YDK-1--------W',
    'DK2': '10YDK-2--------M',
    'ES': '10YES-REE------0',
    'FI': '10YFI-1----------U',
    'FR': '10YFR-RTE------C',
    'GR': '10YGR-HTSO-----Y',
    'HR': '10YHR-HEP------M',
    'HU': '10YHU-MAVIR----U',
    'IT_NORD': '10Y1001A1001A73L',
    'NL': '10YNL----------L',
    'NO1': '10YNO-1--------2',
    'PL': '10YPL-PSE------S',
    'PT': '10YPT-REN------W',
    'RO': '10YRO-TEL------P',
    'SI': '10YSI-ELES-----W',
    'SK': '10YSK-SEPS-----K',
    'CY': '10YCY-1001A0003J',
}

def download_balancing_prices_daily(client, start_date_str, end_date_str, area_keys, output_dir, filename_pattern):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    start_dt = pd.to_datetime(start_date_str)
    end_dt = pd.to_datetime(end_date_str)
    
    current_dt = start_dt
    while current_dt < end_dt:
        next_dt = current_dt + timedelta(days=1)
        date_str = current_dt.strftime("%Y%m%d")
        
        for area_key in area_keys:
            eic_code = BALANCING_AREAS.get(area_key, area_key)
            filename = filename_pattern.format(area=area_key, date=date_str)
            output_file = os.path.join(output_dir, filename)
            
            if os.path.exists(output_file):
                logging.info(f"Skipping {area_key} for {date_str} (file exists).")
                continue
            
            logging.info(f"Downloading {area_key} for {date_str}...")
            
            try:
                df_daily = client.query(current_dt, next_dt, country_code=eic_code, 
                                      document_type='A84', process_type='A67', 
                                      business_type='A96', Standard_MarketProduct='A01',
                                      chunk_size_days=1)
                
                if not df_daily.empty:
                    # Direction A01 = Up, A02 = Down
                    df_daily.to_csv(output_file)
                    logging.info(f"Saved daily file: {output_file}")
                else:
                    logging.warning(f"No data for {area_key} on {date_str}.")
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
            # Robust parsing: handles just the key, api='key', api="key", or api=key
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
    START_DATE = "2025-01-01"
    END_DATE = "2025-01-03" 
    TARGET_AREAS = ['BE'] 

    # Output path is now relative to the script location, going one level up to ETP_DATA
    OUTPUT_DIRECTORY = "../ETP_DATA/17.1.E_prices_of_activated_balancing_energy"
    FILENAME_PATTERN = "17.1.E_{area}_{date}.csv"

    download_balancing_prices_daily(client, START_DATE, END_DATE, TARGET_AREAS, OUTPUT_DIRECTORY, FILENAME_PATTERN)

