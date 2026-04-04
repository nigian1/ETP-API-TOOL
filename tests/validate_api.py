import requests
import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path so we can import core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.entsoe_client import ENTSOEClient

def validate_connection():
    """
    Diagnostic script to verify API key and platform connectivity.
    """
    print("--- ENTSO-E API Validation ---")
    
    # 1. Check for API key
    key_file = os.path.join(os.path.dirname(__file__), "..", "ENTSOE_API_KEY.txt")
    if not os.path.exists(key_file):
        print(f"FAILED: API key file not found at {key_file}")
        return

    try:
        with open(key_file, "r") as f:
            key_line = f.read().strip()
            api_key = key_line.split('=')[-1].strip("'\" ")
            print(f"OK: API key file found ({len(api_key)} chars).")
    except Exception as e:
        print(f"FAILED: Could not read API key: {e}")
        return

    # 2. Check site availability
    client = ENTSOEClient(api_key)
    if client.check_site_availability():
        print("OK: ENTSO-E API is reachable.")
    else:
        print("FAILED: ENTSO-E API is unreachable (Site might be down).")
        return

    # 3. Test a tiny query (1 hour of load for Belgium)
    print("Testing data retrieval (1 hour of Total Load for BE)...")
    try:
        start = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:00")
        end = (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d %H:15")
        
        df = client.query(start, end, country_code='BE', document_type='A65', process_type='A16')
        
        if not df.empty:
            print(f"SUCCESS: Retrieved {len(df)} points of data.")
            print("--- Validation Complete ---")
        else:
            print("FAILED: API responded but returned no data (Check your API permissions).")
    except Exception as e:
        print(f"ERROR: Query failed during validation: {e}")

if __name__ == "__main__":
    validate_connection()
