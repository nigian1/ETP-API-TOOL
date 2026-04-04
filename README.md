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

## Key Features

- **Pre-flight Site Check**: Every script checks if the ENTSO-E API is responsive before starting.
- **Intelligent Skip**: Automatically detects existing files and skips them, making it easy to resume large downloads.
- **Fail-Safe Mechanism**: Monitors consecutive API failures (e.g., 503 Service Unavailable) and halts the process if the site is consistently down.
- **Daily Chunking**: All data is requested in daily chunks for maximum stability and easy data management.

## Setup

1.  **API Key**: Create a file named `ENTSOE_API_KEY.txt` in the `ETP API TOOL` directory and paste your API key inside.
2.  **Dependencies**:
    ```bash
    pip install pandas requests
    ```
3.  **Run**: Execute scripts from within the `ETP API TOOL` folder.
    ```bash
    python download_17.1.E_prices_of_activated_balancing_energy.py
    ```

## Uploading to GitHub

1.  Create a new, empty repository on [GitHub](https://github.com/new).
2.  Open a terminal in the `ETP API TOOL` folder.
3.  Add and commit your files:
    ```bash
    git add .
    git commit -m "Initial commit: Refactored ETP API Tool"
    ```
4.  Link and push to GitHub (replace URL with your repo URL):
    ```bash
    git branch -M main
    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    git push -u origin main
    ```
