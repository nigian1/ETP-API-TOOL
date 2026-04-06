# ENTSO-E Transparency Platform API Tool

This repository provides tools for downloading data from the ENTSO-E Transparency Platform.

## Repository Structure

- **`download_16.1.B_C_actual_generation_per_type.py`**: Main script for downloading aggregated generation data by fuel type.
- **`download_17.1.E_prices_of_activated_balancing_energy.py`**: Main script for downloading balancing energy prices (aFRR CBMPs).
- **`core/`**: Internal client logic (`entsoe_client.py`) and diagnostic tools.
- **`archive/`**: Legacy scripts and logs.
- **`ENTSOE_API_KEY.txt`**: (User-created) Store your API key here. **Do not share or commit this file.**

## Data Output
Data is saved outside the code folder in a directory named `ETP_DATA` to keep the codebase clean and avoid large CSV files in your repository.
- `../ETP_DATA/16.1.B_C_actual_generation_per_type/`
- `../ETP_DATA/17.1.E_prices_of_activated_balancing_energy/`

## Setup

1.  **API Key**: Create a file named `ENTSOE_API_KEY.txt` in the `ETP API TOOL` directory. Paste your API key directly into the file (e.g., `e4140b3e-...`). The script also handles formats like `api='...'` or `api="..."`.
2.  **Dependencies**:
    ```bash
    pip install pandas requests
    ```
3.  **Run**: Execute scripts from within the `ETP API TOOL` folder.
    ```bash
    python download_17.1.E_prices_of_activated_balancing_energy.py
    ```
