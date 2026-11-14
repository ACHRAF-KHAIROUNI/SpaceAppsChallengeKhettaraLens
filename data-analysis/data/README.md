# Data

## What is in this folder
`team_data/` holds three small CSV files shared by the team. **Big NASA files (MERRA-2, GLDAS) are not stored in Git**: the notebook downloads them to the Colab disk.

> **Open question for the sender:** which latitude/longitude do these files cover? About 150 mm/year of rain does not look like Merzouga. Set `TEAM_SITE` in the notebook once confirmed.

## Data dictionary

### `team_data/power_precipitation_daily.csv` — NASA POWER, daily rain (2001-2026)
| Column | Meaning |
|---|---|
| `date` | Day |
| `rain_mm_day` | Rain that day (mm) |
| `rain_3day_mm` | Rain over 3 days (mm) |
| `extreme_rain_day` | True if the day is an extreme-rain day |
| `extreme_3day_rain` | True if the 3-day total is extreme |

### `team_data/power_monthly_rain_anomalies.csv` — monthly rain vs normal
| Column | Meaning |
|---|---|
| `date`, `year`, `month` | Month |
| `rain_mm` | Rain that month (mm) |
| `climatology_mm`, `climatology_std_mm` | Normal rain for that calendar month and its spread |
| `anomaly_mm`, `anomaly_pct`, `z_score` | Difference to normal (mm, %, standard deviations) |
| `status` | near-normal, above-normal / wet, or below-normal / deficit |

### `team_data/modis_sand_bsi_monthly.csv` — MODIS Bare Soil Index (2021-2026)
| Column | Meaning |
|---|---|
| `date` | Date of the monthly snapshot |
| `bsi_mean` | Mean Bare Soil Index (higher = more bare surface) |
| `valid_pixels` | Number of valid pixels used |
| `granules_used` | Number of satellite images used |

## Known limits
- The BSI is a **change proxy only**: one image per month, with gaps (for example no data between Dec 2021 and May 2022).
- POWER is a coarse gridded product: very large one-day values must be checked before being quoted.
- Correlations between rain and BSI are weak (about -0.15 in our first check): treat as a lead, not a proof.

## NASA data used by the notebook
| Product | Variables | Resolution |
|---|---|---|
| MERRA-2 `M2TMNXSLV` v5.12.4 | wind (U10M, V10M, variances), surface skin temperature (TS) | ~50 km, monthly |
| GLDAS Noah `GLDAS_NOAH025_M` v2.1 | soil moisture, root-zone moisture, rainfall, soil temperature | ~25 km, monthly |
| MODIS `MOD13Q1`, `MOD11A2` (optional, Earth Engine) | NDVI, land surface temperature | 250 m, 1 km |
