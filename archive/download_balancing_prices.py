import os
import pandas as pd
from entsoe_client import ENTSOEClient
import logging
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Mapping of common LFC Areas (LFA) and Scheduling Control Areas (SCA) for balancing
BALANCING_AREAS = {
    # Germany (Control Areas / SCAs)
    'DE_50HZ': '10YDE-VE-------2',
    'DE_AMPRION': '10YDE-RWENET---I',
    'DE_TENNET': '10YDE-EON------1',
    'DE_TRANSNETBW': '10YDE-ENBW-----N',
    # Other LFC Areas
    'AT': '10YAT-APG------L',  # Austria
    'BE': '10YBE----------2',  # Belgium
    'CH': '10YCH-SWISSGRIDZ',  # Switzerland
    'CZ': '10YCZ-CEPS-----N',  # Czech Republic
    'DK1': '10YDK-1--------W', # Denmark West
    'DK2': '10YDK-2--------M', # Denmark East
    'ES': '10YES-REE------0',  # Spain
    'FI': '10YFI-1----------U',# Finland
    'FR': '10YFR-RTE------C',  # France
    'GR': '10YGR-HTSO-----Y',  # Greece
    'HR': '10YHR-HEP------M',  # Croatia
    'HU': '10YHU-MAVIR----U',  # Hungary
    'IT_NORD': '10Y1001A1001A73L', # Italy North
    'NL': '10YNL----------L',  # Netherlands
    'NO1': '10YNO-1--------2', # Norway 1
    'PL': '10YPL-PSE------S',  # Poland
    'PT': '10YPT-REN------W',  # Portugal
    'RO': '10YRO-TEL------P',  # Romania
    'SI': '10YSI-ELES-----W',  # Slovenia
    'SK': '10YSK-SEPS-----K',  # Slovakia
    'CY': '10YCY-1001A0003J',  # Cyprus
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
            
            df_daily = client.query(current_dt, next_dt, country_code=eic_code, 
                                  document_type='A84', process_type='A67', 
                                  business_type='A96', market_product='A01',
                                  chunk_size_days=1)
            
            if not df_daily.empty:
                df_daily.to_csv(output_file)
                logging.info(f"Saved daily file: {output_file}")
            else:
                logging.warning(f"No data for {area_key} on {date_str}.")
            
            # Short sleep to be polite
            time.sleep(0.5)
        
        current_dt = next_dt
        time.sleep(1)

if __name__ == "__main__":
    with open("ENTSOE/api.txt", "r") as f:
        key_line = f.read()
        api_key = key_line.split("'")[1]
    
    client = ENTSOEClient(api_key)
    
    # --- CONFIGURATION ---
    START_DATE = "2024-01-01"
    END_DATE = "2024-01-02" 
    TARGET_AREAS = ['DE_50HZ'] 
    
    OUTPUT_DIRECTORY = "ENTSOE/balancing_data"
    # Note: Added {date} placeholder
    FILENAME_PATTERN = "balancing_prices_{area}_{date}.csv"
    
    download_balancing_prices_daily(client, START_DATE, END_DATE, TARGET_AREAS, OUTPUT_DIRECTORY, FILENAME_PATTERN)
