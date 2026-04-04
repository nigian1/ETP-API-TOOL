import os
import argparse
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time

PSR_MAPPING = {
    'B01': 'Biomass',
    'B02': 'Fossil Brown coal/Lignite',
    'B03': 'Fossil Coal-derived gas',
    'B04': 'Fossil Gas',
    'B05': 'Fossil Hard coal',
    'B06': 'Fossil Oil',
    'B07': 'Fossil Oil shale',
    'B08': 'Fossil Peat',
    'B09': 'Geothermal',
    'B10': 'Hydro Pumped Storage',
    'B11': 'Hydro Run-of-river and poundage',
    'B12': 'Hydro Water Reservoir',
    'B13': 'Marine',
    'B14': 'Nuclear',
    'B15': 'Other renewable',
    'B16': 'Solar',
    'B17': 'Waste',
    'B18': 'Wind Offshore',
    'B19': 'Wind Onshore',
    'B20': 'Other'
}

def parse_entsoe_xml(xml_content):
    namespace = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError as e:
        print(f"XML Parse Error: {e}")
        return []
    
    data = []
    for timeseries in root.findall('ns:TimeSeries', namespace):
        psr_type_element = timeseries.find('ns:MktPSRType/ns:psrType', namespace)
        psr_type = psr_type_element.text if psr_type_element is not None else "Unknown"
        
        period = timeseries.find('ns:Period', namespace)
        if period is None: continue
            
        start_str = period.find('ns:timeInterval/ns:start', namespace).text
        resolution = period.find('ns:resolution', namespace).text
        start_dt = pd.to_datetime(start_str)
        
        step = 15 if '15' in resolution else 60
            
        for point in period.findall('ns:Point', namespace):
            position = int(point.find('ns:position', namespace).text)
            quantity = float(point.find('ns:quantity', namespace).text)
            timestamp = start_dt + timedelta(minutes=(position - 1) * step)
            data.append({'timestamp': timestamp, 'production_type': psr_type, 'actual_generation': quantity})
    return data

def download_range(api_key, country_code, start_date, end_date, output_folder):
    domain = "10YGR-HTSO-----Y" if country_code == "GR" else country_code
    url = "https://web-api.tp.entsoe.eu/api"
    
    # ENTSO-E often limits the range per request (e.g., 1 year or less). 
    # For safety and to avoid timeouts, we can download in chunks if needed.
    # Here we do it in one go for the requested 4 months.
    
    params = {
        'securityToken': api_key,
        'documentType': 'A75',
        'processType': 'A16',
        'in_Domain': domain,
        'periodStart': f"{start_date}0000",
        'periodEnd': f"{end_date}0000"
    }

    print(f"Requesting data from {start_date} to {end_date} (UTC)...")
    
    response = requests.get(url, params=params)
    if response.status_code == 200:
        all_data = parse_entsoe_xml(response.content)
        if all_data:
            df = pd.DataFrame(all_data)
            df_pivot = df.pivot_table(index='timestamp', columns='production_type', values='actual_generation', aggfunc='sum')
            
            # Rename columns to human-readable names
            df_pivot = df_pivot.rename(columns=PSR_MAPPING)
            
            # Ensure all timestamps in the range are present
            all_timestamps = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq='h', inclusive='left', tz='UTC')
            
            # Forward fill missing values (ENTSO-E sometimes skips points if value is unchanged)
            # then fill any remaining leading NaNs with 0
            df_pivot = df_pivot.reindex(all_timestamps).ffill().fillna(0)
            df_pivot.index.name = 'timestamp'
            
            output_file = os.path.join(output_folder, f"generation_{start_date}_{end_date}.csv")
            df_pivot.to_csv(output_file)
            print(f"Saved to {output_file}")
        else:
            print("No data found or parsed.")
    else:
        print(f"Failed with status {response.status_code}")
        print(f"Response: {response.text[:200]}")

if __name__ == "__main__":
    API_KEY = "e4140b3e-5ba9-4804-b0f4-3f4951947b3a"
    COUNTRY = "GR"
    START = "20240601"
    END = "20240930"
    FOLDER = "actual production per fuel"
    
    if not os.path.exists(FOLDER):
        os.makedirs(FOLDER)
        
    download_range(API_KEY, COUNTRY, START, END, FOLDER)
