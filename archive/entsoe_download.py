import os
import argparse
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

def parse_entsoe_xml(xml_content):
    """
    Parses ENTSO-E A75 XML (Actual Generation per Production Type) into a list of dicts.
    """
    namespace = {'ns': 'urn:iec62325.351:tc57wg16:451-6:generationloaddocument:3:0'}
    root = ET.fromstring(xml_content)
    
    data = []
    
    for timeseries in root.findall('ns:TimeSeries', namespace):
        # Get Production Type
        psr_type_element = timeseries.find('ns:MktPSRType/ns:psrType', namespace)
        psr_type = psr_type_element.text if psr_type_element is not None else "Unknown"
        
        # Get Period and resolution
        period = timeseries.find('ns:Period', namespace)
        if period is None:
            continue
            
        start_str = period.find('ns:timeInterval/ns:start', namespace).text
        resolution = period.find('ns:resolution', namespace).text # e.g., PT60M or PT15M
        
        # Parse start time
        start_dt = pd.to_datetime(start_str)
        
        # Determine step in minutes
        if '60' in resolution:
            step = 60
        elif '15' in resolution:
            step = 15
        else:
            step = 60 # Default
            
        for point in period.findall('ns:Point', namespace):
            position = int(point.find('ns:position', namespace).text)
            quantity = float(point.find('ns:quantity', namespace).text)
            
            # Calculate actual timestamp for this point
            timestamp = start_dt + timedelta(minutes=(position - 1) * step)
            
            data.append({
                'timestamp': timestamp,
                'production_type': psr_type,
                'actual_generation': quantity
            })
            
    return data

def download_entsoe_rest(api_key, country_code, start_date, end_date, output_file):
    """
    Downloads Actual Generation per Production Type via REST API.
    Dates expected in YYYYMMDD format.
    """
    # Mapping for Greece (Domain)
    # 10YGR-HTSO-----Y is the Control Area for Greece
    domain = "10YGR-HTSO-----Y" if country_code == "GR" else country_code
    
    url = "https://web-api.tp.entsoe.eu/api"
    params = {
        'securityToken': api_key,
        'documentType': 'A75',
        'processType': 'A16',
        'in_Domain': domain,
        'periodStart': f"{start_date}0000",
        'periodEnd': f"{end_date}0000"
    }

    print(f"Requesting data from {params['periodStart']} to {params['periodEnd']} (UTC)...")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        if "No data found" in response.text:
            print("No data found for the requested period.")
            return

        # Parse XML
        all_data = parse_entsoe_xml(response.content)
        
        if not all_data:
            print("No TimeSeries data extracted from XML.")
            # Print raw response snippet if it failed to parse meaningfully
            print(f"Response snippet: {response.text[:200]}")
            return
            
        df = pd.DataFrame(all_data)
        
        # Pivot to have Production Types as columns
        df_pivot = df.pivot(index='timestamp', columns='production_type', values='actual_generation')
        
        # Save to CSV
        df_pivot.to_csv(output_file)
        print(f"Successfully saved data to {output_file}")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        if response.content:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download dataset from ENTSO-E REST API.')
    parser.add_argument('--api_key', type=str, required=True)
    parser.add_argument('--country', type=str, default='GR')
    parser.add_argument('--start', type=str, default='20240601')
    parser.add_argument('--end', type=str, default='20240602')
    parser.add_argument('--output', type=str, default='test.csv')

    args = parser.parse_args()
    
    download_entsoe_rest(args.api_key, args.country, args.start, args.end, args.output)
