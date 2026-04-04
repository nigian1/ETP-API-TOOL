# ENTSO-E Transparency Platform API Reference

This document provides a comprehensive guide to the ENTSO-E RESTful API document types, process types, and mandatory parameters.

## Base URL
`https://web-api.tp.entsoe.eu/api`

## Mandatory Parameters
All requests require:
- `securityToken`: Your API key.
- `documentType`: The document code (e.g., A75).
- `periodStart`: Start time in `YYYYMMDDHHMM` (UTC).
- `periodEnd`: End time in `YYYYMMDDHHMM` (UTC).
- `country_code`: Can be a friendly alias (e.g., 'GR', 'DE_50HZ') or a **raw EIC code** (e.g., '10YDE-VE-------2' for a specific SCA/LFC Area).

---

## 1. Data Categories & Document Types

### Generation
| DocumentType | Description | Area Parameter | ProcessType (Typical) |
| :--- | :--- | :--- | :--- |
| **A75** | Actual Generation per Type | `in_Domain` | `A16` (Realised) |
| **A74** | Generation Forecast | `in_Domain` | `A01` (Day Ahead) |
| **A71** | Generation unit unavailability | `in_Domain` | N/A |
| **A73** | Actual Generation per Unit | `in_Domain` | `A16` (Realised) |

### Load
| DocumentType | Description | Area Parameter | ProcessType (Typical) |
| :--- | :--- | :--- | :--- |
| **A65** | System Total Load | `outBiddingZone_Domain` | `A16` (Actual), `A01` (Forecast) |

### Balancing Prices (aFRR CBMP)
| DocumentType | Description | Area Parameter | ProcessType | BusinessType | MarketProduct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **A84** | Activated balancing prices | `controlArea_Domain` | `A67` (Central) | `A96` (aFRR) | `A01` (Standard) |

---

## 2. Process Types (`processType`)
| Code | Description |
| :--- | :--- |
| **A01** | Day ahead |
| **A02** | Intra day incremental |
| **A16** | Realised (Actual data) |
| **A31** | Week ahead |
| **A32** | Month ahead |
| **A33** | Year ahead |

---

## 3. PSR Types (Power System Resource Types)
Used in **A75** documents to identify fuel/technology.

| Code | Type | Code | Type |
| :--- | :--- | :--- | :--- |
| **B01** | Biomass | **B11** | Hydro Run-of-river |
| **B02** | Fossil Brown coal | **B12** | Hydro Water Reservoir |
| **B03** | Fossil Coal-derived gas | **B13** | Marine |
| **B04** | Fossil Gas | **B14** | Nuclear |
| **B05** | Fossil Hard coal | **B15** | Other renewable |
| **B06** | Fossil Oil | **B16** | Solar |
| **B07** | Fossil Oil shale | **B17** | Waste |
| **B08** | Fossil Peat | **B18** | Wind Offshore |
| **B09** | Geothermal | **B19** | Wind Onshore |
| **B10** | Hydro Pumped Storage | **B20** | Other |

---

## 4. Usage Example (Actual Generation)
To fetch actual generation per type for Greece:
```bash
https://web-api.tp.entsoe.eu/api?documentType=A75&processType=A16&in_Domain=10YGR-HTSO-----Y&periodStart=202401010000&periodEnd=202401020000&securityToken=YOUR_TOKEN
```

## 5. Usage Example (Total Load)
To fetch actual total load for Greece:
```bash
https://web-api.tp.entsoe.eu/api?documentType=A65&processType=A16&outBiddingZone_Domain=10YGR-HTSO-----Y&periodStart=202401010000&periodEnd=202401020000&securityToken=YOUR_TOKEN
```
