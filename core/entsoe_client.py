import os
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

DIRECTION_MAPPING = {
    'A01': 'Up',
    'A02': 'Down'
}

class ENTSOEClient:
    BASE_URL = "https://web-api.tp.entsoe.eu/api"
    
    DOMAIN_MAPPING = {
        'AL': '10YAL-KESH-----5', # Albania, Control Area
        'AT': '10YAT-APG------L', # Austria, Bidding Zone / Control Area
        'BA': '10YBA-JPCC-----D', # Bosnia and Herz., Control Area
        'BE': '10YBE----------2', # Belgium, Bidding Zone / Control Area
        'BG': '10YCA-BULGARIA-R', # Bulgaria, Control Area
        'CH': '10YCH-SWISSGRIDZ', # Switzerland, Bidding Zone / Control Area
        'CY': '10YCY-1001A0003J', # Cyprus, Control Area
        'CZ': '10YCZ-CEPS-----N', # Czech Republic, Bidding Zone / Control Area
        'DE': '10Y1001A1001A83F', # Germany-Luxembourg-Austria Bidding Zone
        'DE_50HZ': '10YDE-VE-------2', # 50Hertz, Control Area
        'DE_AMPRION': '10YDE-RWENET---I', # Amprion, Control Area
        'DE_TENNET': '10YDE-EON------1', # TenneT GER, Control Area
        'DE_TRANSNETBW': '10YDE-ENBW-----N', # TransnetBW, Control Area
        'DK': '10Y1001A1001A65H', # Denmark, Bidding Zone
        'DK1': '10YDK-1--------W', # Denmark 1, Bidding Zone
        'DK2': '10YDK-2--------M', # Denmark 2, Bidding Zone
        'EE': '10Y1001A1001A39X', # Estonia, Bidding Zone / Control Area
        'ES': '10YES-REE------0', # Spain, Bidding Zone / Control Area
        'FI': '10YFI-1----------U', # Finland, Bidding Zone / Control Area
        'FR': '10YFR-RTE------C', # France, Bidding Zone / Control Area
        'GB': '10YGB----------A', # Great Britain, Bidding Zone / Control Area
        'GR': '10YGR-HTSO-----Y', # Greece, Bidding Zone / Control Area
        'HR': '10YHR-HEP------M', # Croatia, Bidding Zone / Control Area
        'HU': '10YHU-MAVIR----U', # Hungary, Bidding Zone / Control Area
        'IE': '10YIE-1001A00010', # Ireland (SEM), Bidding Zone
        'IT': '10YIT-1001A0001E', # Italy, Bidding Zone
        'IT_NORTH': '10Y1001A1001A73L', # Italy North, Bidding Zone
        'IT_SARDINIA': '10Y1001A1001A71P', # Italy Sardinia, Bidding Zone
        'IT_SICILY': '10Y1001A1001A75H', # Italy Sicily, Bidding Zone
        'LT': '10YLT-1001A0008Q', # Lithuania, Bidding Zone / Control Area
        'LU': '10YLU-CEGEDEL-NQ', # Luxembourg, Bidding Zone
        'LV': '10YLV-1001A00074', # Latvia, Bidding Zone / Control Area
        'ME': '10YME-EPCG-----P', # Montenegro, Control Area
        'MK': '10YMK-MEPSO----8', # Macedonia, Control Area
        'NL': '10YNL----------L', # Netherlands, Bidding Zone / Control Area
        'NO': '10YNO-0--------C', # Norway, Bidding Zone
        'NO1': '10YNO-1--------2', # Norway 1, Bidding Zone
        'NO2': '10YNO-2--------T', # Norway 2, Bidding Zone
        'NO3': '10YNO-3--------J', # Norway 3, Bidding Zone
        'NO4': '10YNO-4--------9', # Norway 4, Bidding Zone
        'NO5': '10Y1001A1001A48H', # Norway 5, Bidding Zone
        'PL': '10YPL-PSE------S', # Poland, Bidding Zone / Control Area
        'PT': '10YPT-REN------W', # Portugal, Bidding Zone / Control Area
        'RO': '10YRO-TEL------P', # Romania, Bidding Zone / Control Area
        'RS': '10YCS-SERBIATSOV', # Serbia, Control Area
        'SE': '10YSE-1001A0001R', # Sweden, Bidding Zone
        'SE1': '10Y1001A1001A44P', # Sweden 1, Bidding Zone
        'SE2': '10Y1001A1001A45N', # Sweden 2, Bidding Zone
        'SE3': '10Y1001A1001A46L', # Sweden 3, Bidding Zone
        'SE4': '10Y1001A1001A47J', # Sweden 4, Bidding Zone
        'SI': '10YSI-ELES-----W', # Slovenia, Bidding Zone / Control Area
        'SK': '10YSK-SEPS-----K', # Slovakia, Bidding Zone / Control Area
        'TR': '10YTR-TEIAS----W', # Turkey, Control Area
        'UA': '10YUA-WEPS-----0', # Ukraine, Bidding Zone
    }

    def __init__(self, api_key):
        self.api_key = api_key
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5

    def check_site_availability(self):
        """
        Check if the ENTSO-E API is reachable.
        """
        try:
            # We just do a HEAD or GET with no params to see if it responds
            response = requests.get(self.BASE_URL, timeout=10)
            # Even if it's 401/400, it means the server is UP.
            # 503 or ConnectionError means it's DOWN.
            if response.status_code == 503:
                logger.error("ENTSO-E API is currently down (503 Service Unavailable).")
                return False
            return True
        except Exception as e:
            logger.error(f"ENTSO-E API is unreachable: {e}")
            return False

    def _get_domain(self, country_code):
        return self.DOMAIN_MAPPING.get(country_code, country_code)

    def _parse_xml_generic(self, xml_content):
        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as e:
            logger.error(f"XML Parse Error: {e}")
            return []

        # Find namespace
        ns = root.tag.split('}')[0][1:] if '}' in root.tag else ""
        
        def find_tag(parent, tag):
            if ns:
                return parent.find(f'{{%s}}%s' % (ns, tag))
            return parent.find(tag)
            
        def find_all_tags(parent, tag):
            if ns:
                return parent.findall(f'{{%s}}%s' % (ns, tag))
            return parent.findall(tag)
        
        data = []
        time_series_list = find_all_tags(root, 'TimeSeries')
        
        for timeseries in time_series_list:
            # Extract metadata with dotted tag support
            def get_text(parent, *tags):
                for tag in tags:
                    el = find_tag(parent, tag)
                    if el is not None:
                        # If nested, try to find a child (common in CIM)
                        if not el.text or not el.text.strip():
                            for child in el:
                                if child.text and child.text.strip():
                                    return child.text
                        return el.text
                return None

            psr_type = get_text(timeseries, 'MktPSRType', 'mktPSRType.psrType', 'psrType')
            b_type = get_text(timeseries, 'businessType')
            flow_dir = get_text(timeseries, 'flowDirection', 'flowDirection.direction')
            curve_type = get_text(timeseries, 'curveType') or 'A01'

            for period in find_all_tags(timeseries, 'Period'):
                interval = find_tag(period, 'timeInterval')
                if interval is not None:
                    start_tag = find_tag(interval, 'start')
                    end_tag = find_tag(interval, 'end')
                    start_str = start_tag.text if start_tag is not None else None
                    end_str = end_tag.text if end_tag is not None else None
                else:
                    start_str = None
                    end_str = None
                
                res_tag = find_tag(period, 'resolution')
                resolution = res_tag.text if res_tag is not None else "PT60M"
                
                if not start_str or not end_str: continue
                start_dt = pd.to_datetime(start_str)
                end_dt = pd.to_datetime(end_str)
                
                import re
                match_m = re.search(r'PT(\d+)M', resolution)
                match_s = re.search(r'PT(\d+)S', resolution)
                
                if match_m:
                    step_seconds = int(match_m.group(1)) * 60
                elif match_s:
                    step_seconds = int(match_s.group(1))
                else:
                    step_seconds = 3600
                
                total_seconds = (end_dt - start_dt).total_seconds()
                total_positions = int(round(total_seconds / step_seconds)) if step_seconds > 0 else 0
                
                points_dict = {}
                for point in find_all_tags(period, 'Point'):
                    pos_tag = find_tag(point, 'position')
                    if pos_tag is None: continue
                    pos = int(pos_tag.text)
                    
                    qty = None
                    for tag in ['quantity', 'activation_Price.amount', 'price.amount']:
                        elem = find_tag(point, tag)
                        if elem is not None:
                            qty = float(elem.text)
                            break
                    points_dict[pos] = qty
                    
                if curve_type == 'A03':
                    current_qty = None
                    for pos in range(1, total_positions + 1):
                        if pos in points_dict:
                            current_qty = points_dict[pos]
                        
                        if current_qty is not None:
                            ts = start_dt + timedelta(seconds=(pos - 1) * step_seconds)
                            data.append({
                                'timestamp': ts,
                                'value': current_qty,
                                'psr_type': psr_type,
                                'business_type': b_type,
                                'direction': flow_dir
                            })
                else:
                    for pos, qty in points_dict.items():
                        if qty is not None:
                            ts = start_dt + timedelta(seconds=(pos - 1) * step_seconds)
                            data.append({
                                'timestamp': ts,
                                'value': qty,
                                'psr_type': psr_type,
                                'business_type': b_type,
                                'direction': flow_dir
                            })
        return data

    def query(self, start_date, end_date, country_code='GR', document_type='A75', process_type='A16', 
              business_type=None, Standard_MarketProduct=None, chunk_size_days=5):
        domain = self._get_domain(country_code)
        
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        
        all_data = []
        current_start = start_dt
        
        while current_start < end_dt:
            current_end = current_start + timedelta(days=chunk_size_days)
            if current_end > end_dt:
                current_end = end_dt
                
            s_str = current_start.strftime("%Y%m%d%H%M")
            e_str = current_end.strftime("%Y%m%d%H%M")
            
            logger.info(f"Fetching {document_type} for {s_str} to {e_str}...")
            
            chunk_data = self._fetch_with_retries(start_str=s_str, end_str=e_str, domain=domain, 
                                                 doc_type=document_type, proc_type=process_type, 
                                                 bus_type=business_type, market_prod=Standard_MarketProduct)
            if chunk_data:
                logger.info(f"Parsed {len(chunk_data)} points for {s_str}.")
                all_data.extend(chunk_data)
            
            current_start = current_end
            time.sleep(1) # Rate limit protection
            
        if not all_data:
            logger.warning(f"No data parsed for the entire range {start_date} - {end_date}.")
            return pd.DataFrame()
            
        df = pd.DataFrame(all_data)
        return self._post_process(df, document_type)

    def _fetch_with_retries(self, start_str, end_str, domain, doc_type, proc_type, 
                           bus_type=None, market_prod=None, max_retries=5):
        params = {
            'securityToken': self.api_key,
            'documentType': doc_type,
            'processType': proc_type,
            'periodStart': start_str,
            'periodEnd': end_str
        }
        
        if bus_type:
            params['businessType'] = bus_type
        if market_prod:
            params['Standard_MarketProduct'] = market_prod

        # Area parameter mapping based on document type
        if doc_type == 'A65':
            params['outBiddingZone_Domain'] = domain
        elif doc_type == 'A84':
            params['controlArea_Domain'] = domain
        else:
            params['in_Domain'] = domain

        retries = 0
        while retries < max_retries:
            try:
                response = requests.get(self.BASE_URL, params=params, timeout=120)
                if response.status_code == 200:
                    self.consecutive_failures = 0 # Reset on success
                    root_tag = response.text[response.text.find('<'):response.text.find('>', response.text.find('<'))+1]
                    logger.debug(f"Response root tag: {root_tag}")
                    if "Acknowledgement_MarketDocument" in response.text and "No data found" in response.text:
                        logger.warning(f"No data found for {start_str} - {end_str}")
                        return []
                    return self._parse_xml_generic(response.content)
                elif response.status_code == 429:
                    wait = (retries + 1) * 5
                    logger.warning(f"Rate limited (429). Waiting {wait}s...")
                    time.sleep(wait)
                elif response.status_code == 503:
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        raise Exception(f"Maximum consecutive failures ({self.max_consecutive_failures}) reached due to 503 errors.")
                    wait = (retries + 1) * 2
                    logger.warning(f"Service Unavailable (503). Retrying in {wait}s... (Failure {self.consecutive_failures}/{self.max_consecutive_failures})")
                    time.sleep(wait)
                else:
                    logger.error(f"API Error {response.status_code}: {response.text[:200]}")
                    break
            except Exception as e:
                self.consecutive_failures += 1
                if self.consecutive_failures >= self.max_consecutive_failures:
                    raise Exception(f"Maximum consecutive failures ({self.max_consecutive_failures}) reached due to errors: {e}")
                logger.error(f"Request failed: {e}. (Failure {self.consecutive_failures}/{self.max_consecutive_failures})")
                time.sleep(2)
            retries += 1
        return []

    def _post_process(self, df, document_type):
        if df.empty:
            return df
            
        if document_type == 'A75':
            # Pivot by psr_type
            df_pivot = df.pivot_table(index='timestamp', columns='psr_type', values='value', aggfunc='sum')
            df_pivot = df_pivot.rename(columns=PSR_MAPPING)
            df_pivot.sort_index(inplace=True)
            return df_pivot
        elif document_type == 'A65':
            # Total load usually just has one value per timestamp
            df_res = df.set_index('timestamp')['value'].to_frame('Total Load (MW)')
            df_res.sort_index(inplace=True)
            return df_res
        elif document_type == 'A84':
            # Pivot by direction
            df_pivot = df.pivot_table(index='timestamp', columns='direction', values='value', aggfunc='first')
            # Rename columns from A01/A02 to Up/Down
            df_pivot = df_pivot.rename(columns=DIRECTION_MAPPING)
            # Ensure both Up and Down columns exist
            for col in ['Up', 'Down']:
                if col not in df_pivot.columns:
                    df_pivot[col] = float('nan')
            
            # Sort by timestamp
            df_pivot = df_pivot.sort_index()
            return df_pivot
        else:
            # Generic return
            return df.set_index('timestamp')

if __name__ == "__main__":
    # Quick test if run directly
    with open("ENTSOE/api.txt", "r") as f:
        key = f.read().split("'")[1]
    
    client = ENTSOEClient(key)
    # Test Load (A65) for 1 day
    print("Testing Load (A65)...")
    df_load = client.query('2024-01-01', '2024-01-02', document_type='A65', process_type='A16')
    print(df_load.head())
    
    # Test Generation (A75) for 1 day
    print("\nTesting Generation (A75)...")
    df_gen = client.query('2024-01-01', '2024-01-02', document_type='A75', process_type='A16')
    print(df_gen.head())
