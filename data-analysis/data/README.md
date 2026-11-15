# KhettaraLens data guide

The [`team_data/`](team_data/) directory contains the CSV datasets used by the visualization script. The datasets cover environmental conditions and plant adaptations relevant to the KhettaraLens investigation. Large NASA source files are downloaded by the Colab notebook rather than stored in this repository.

## Dataset inventory

### Rainfall

| File | Contents |
|---|---|
| [`power_precipitation_daily.csv`](team_data/power_precipitation_daily.csv) | Daily rainfall (`rain_mm_day`), rolling 3-day total (`rain_3day_mm`), and extreme-event flags. |
| [`power_monthly_rain_anomalies.csv`](team_data/power_monthly_rain_anomalies.csv) | Monthly rainfall and calendar-month climatology, including anomaly in millimetres and percent, z-score, year, month, and status. |
| [`precip_extreme_rain_screening_days.csv`](team_data/precip_extreme_rain_screening_days.csv) | Dates selected for extreme-rain screening, with daily and 3-day rainfall totals and event flags. |

### Wind

| File | Contents |
|---|---|
| [`merra2_wind_daily_box_mean.csv`](team_data/merra2_wind_daily_box_mean.csv) | Time series of box-mean wind components, mean and maximum speed, strong-wind hours, directional counts, and vector-mean direction. |
| [`merra2_wind_daily_sites.csv`](team_data/merra2_wind_daily_sites.csv) | Site-level wind values and coordinates, with the same wind measures as the box-mean dataset. |

### Soil moisture

| File | Contents |
|---|---|
| [`gldas_soil_monthly_box_mean.csv`](team_data/gldas_soil_monthly_box_mean.csv) | Monthly box-mean soil moisture, including `SoilMoi0_10cm_inst` and the derived `vol_m3m3_approx` field. |
| [`gldas_soil_monthly_sites.csv`](team_data/gldas_soil_monthly_sites.csv) | Monthly site-level soil moisture values with site names and coordinates. |

### Surface conditions and plant adaptations

| File | Contents |
|---|---|
| [`modis_sand_bsi_monthly.csv`](team_data/modis_sand_bsi_monthly.csv) | Monthly Bare Soil Index (`bsi_mean`), valid-pixel count, and granules used. |
| [`morocco_merzouga_plant_adaptations.csv`](team_data/morocco_merzouga_plant_adaptations.csv) | Species, family, adaptation category, specific adaptations, and leaf structure. |
| [`extracted_pdf_plant_adaptations.csv`](team_data/extracted_pdf_plant_adaptations.csv) | Plant names, extracted adaptation descriptions, and the suitability classification recorded in the source material. |

## Important fields

- `date` and `time` identify the observation date or timestamp. The visualization script parses these fields when present.
- `site`, `lat`, and `lon` identify the site and coordinates in the site-level wind and soil files.
- `wspd_mean`, `wspd_max`, and `strong_hours` describe wind speed and strong-wind exposure; directional fields record strong-wind counts by compass direction.
- `vol_m3m3_approx` is the soil-moisture field plotted by the visualization script. Consult the source product and generated provenance before interpreting its units.
- Higher `bsi_mean` values indicate a stronger bare-surface signal in this dataset. BSI should be treated as a change proxy, not a direct measurement of sand transport or vegetation cover.

## Sources and limitations

The repository includes data derived from NASA POWER, MERRA-2, GLDAS, and MODIS, alongside curated plant-adaptation tables. Product details, versions, and periods should be confirmed from the notebook's generated provenance report for the analysis run in question.

- Gridded climate products have regional-scale resolution and cannot select individual planting spots.
- Team rainfall and BSI files do not include site coordinates in their listed columns. Confirm their geographic coverage before attributing them to Merzouga.
- Satellite BSI observations can be sparse or interrupted by acquisition gaps. Compare only overlapping, quality-checked periods.
- A correlation between rainfall, wind, soil moisture, or BSI is not evidence that one variable caused another.
- The plant tables are reference material; verify species identifications and local suitability with qualified botanical expertise before making field recommendations.

For notebook usage, see the [analysis guide](../README.md) and [notebook guide](../notebooks/README.md).
