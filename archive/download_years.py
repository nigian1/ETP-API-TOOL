import os
import pandas as pd
from entsoe_client import ENTSOEClient
import logging

# Configure logging to see progress
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def download_data(client, years, countries, document_type='A75', process_type='A16'):
    for country in countries:
        for year in years:
            start_date = f"{year}-01-01"
            end_date = f"{year+1}-01-01"
            output_file = f"ENTSOE/production_{country}_{year}.csv"
            
            logging.info(f"Starting download for {country} - {year}...")
            df = client.query(start_date, end_date, country_code=country, 
                             document_type=document_type, process_type=process_type, 
                             chunk_size_days=7)
            
            if not df.empty:
                df.to_csv(output_file)
                logging.info(f"Successfully saved {country} {year} data to {output_file}")
            else:
                logging.warning(f"No data collected for {country} {year}.")

if __name__ == "__main__":
    with open("ENTSOE/api.txt", "r") as f:
        key_line = f.read()
        api_key = key_line.split("'")[1]
    
    client = ENTSOEClient(api_key)
    
    # Define your lists here
    target_years = [2022, 2024]
    target_countries = ['GR'] # Can add more like 'DE', 'FR', etc.
    
    if not os.path.exists("ENTSOE"):
        os.makedirs("ENTSOE")
        
    download_data(client, target_years, target_countries)
