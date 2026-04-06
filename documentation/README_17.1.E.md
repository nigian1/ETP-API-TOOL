# ENTSO-E Balancing Data Downloader (17.1.E)

This tool downloads **Prices of Activated Balancing Energy & aFRR CBMPs** from the ENTSO-E Transparency Platform.

## Data Details
- **Dataset:** aFRR Cross-Border Marginal Prices (CBMPs)
- **Reference:** 17.1.E (Prices of Activated Balancing Energy)
- **DocumentType:** `A84`
- **ProcessType:** `A67` (aFRR Central Selection / PICASSO)
- **BusinessType:** `A96` (aFRR)
- **MarketProduct:** `A01` (Standard)

## How to Use

1.  **Configure:** Open `ETP API TOOL/download_17.1.E_prices_of_activated_balancing_energy.py` and modify the `START_DATE`, `END_DATE`, and `TARGET_AREAS`.
2.  **Run:**
    ```bash
    python "ETP API TOOL/download_17.1.E_prices_of_activated_balancing_energy.py"
    ```
3.  **Output:** Data is saved as individual daily CSV files in `../ETP_DATA/17.1.E_prices_of_activated_balancing_energy/`.
    The files follow the naming convention: `17.1.E_[AREA]_[DATE].csv`.
You can use either the **Friendly Alias** or the **Raw EIC Code** in the `target_areas` list.

| Friendly Alias | Area Type | EIC Code |
| :--- | :--- | :--- |
| **DE_50HZ** | SCA / LFC Area | `10YDE-VE-------2` |
| **DE_AMPRION** | SCA / LFC Area | `10YDE-RWENET---I` |
| **DE_TENNET** | SCA / LFC Area | `10YDE-EON------1` |
| **DE_TRANSNETBW** | SCA / LFC Area | `10YDE-ENBW-----N` |
| **AT** | LFC Area | `10YAT-APG------L` |
| **BE** | LFC Area | `10YBE----------2` |
| **CH** | LFC Area | `10YCH-SWISSGRIDZ` |
| **CZ** | LFC Area | `10YCZ-CEPS-----N` |
| **DK1** | LFC Area | `10YDK-1--------W` |
| **DK2** | LFC Area | `10YDK-2--------M` |
| **ES** | LFC Area | `10YES-REE------0` |
| **FI** | LFC Area | `10YFI-1----------U` |
| **FR** | LFC Area | `10YFR-RTE------C` |
| **GR** | LFC Area | `10YGR-HTSO-----Y` |
| **HR** | LFC Area | `10YHR-HEP------M` |
| **HU** | LFC Area | `10YHU-MAVIR----U` |
| **IT_NORD** | LFC Area | `10Y1001A1001A73L` |
| **NL** | LFC Area | `10YNL----------L` |
| **NO1** | LFC Area | `10YNO-1--------2` |
| **PL** | LFC Area | `10YPL-PSE------S` |
| **PT** | LFC Area | `10YPT-REN------W` |
| **RO** | LFC Area | `10YRO-TEL------P` |
| **SI** | LFC Area | `10YSI-ELES-----W` |
| **SK** | LFC Area | `10YSK-SEPS-----K` |
| **CY** | LFC Area | `10YCY-1001A0003J` |

*Note: For any area not in this list, you can pass the **Raw EIC Code** directly in the `target_areas` list.*
https://transparencyplatform.zendesk.com/hc/en-us/articles/15885757676308-Area-List-with-Energy-Identification-Code-EIC
