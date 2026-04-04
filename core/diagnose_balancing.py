import requests
import xml.etree.ElementTree as ET

def test_params(doc_type, proc_type, bus_type, area):
    api_key = 'e4140b3e-5ba9-4804-b0f4-3f4951947b3a'
    url = 'https://web-api.tp.entsoe.eu/api'
    
    params = {
        'securityToken': api_key,
        'documentType': doc_type,
        'processType': proc_type,
        'periodStart': '202401010000',
        'periodEnd': '202401010100'
    }
    
    if bus_type:
        params['businessType'] = bus_type
        
    # Area parameter mapping
    if doc_type == 'A84':
        params['controlArea_Domain'] = area
    else:
        params['in_Domain'] = area

    try:
        r = requests.get(url, params=params, timeout=30)
        print(f"Testing: doc={doc_type}, proc={proc_type}, bus={bus_type} -> Status: {r.status_code}")
        if r.status_code == 200:
            if "No data found" in r.text:
                print("   Result: No data found")
            else:
                print(f"   Result: DATA FOUND! (Length: {len(r.text)})")
                return True
    except Exception as e:
        print(f"   Error: {e}")
    return False

area_be = '10YBE----------2'
combinations = [
    ('A84', 'A67', 'A96'), # Central Selection aFRR (Your request)
    ('A84', 'A68', 'A96'), # Local Selection aFRR
    ('A84', 'A16', 'A96'), # Realised aFRR
    ('A84', 'A67', None),  # Central Selection (Generic)
    ('A84', 'A16', None),  # Realised (Generic)
]

print("Starting diagnostics for Belgium...")
for doc, proc, bus in combinations:
    if test_params(doc, proc, bus, area_be):
        break
