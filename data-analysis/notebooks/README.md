# KhettaraLens trend-analysis notebook

[`dune_detective_trends_EN.ipynb`](dune_detective_trends_EN.ipynb) is a Google Colab notebook that compares environmental trends across four study sites: Merzouga, Timbuktu, Nouakchott, and Siwa. It downloads NASA data, calculates annual series, and exports figures, tables, an interactive dashboard, and a data-provenance report.

## Open in Google Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/ACHRAF-KHAIROUNI/SpaceAppsChallengeWebSite/blob/main/data-analysis/notebooks/dune_detective_trends_EN.ipynb)

Alternatively, open Colab and use **File → Open notebook → GitHub**, or download the notebook and use **File → Upload notebook**.

## Before running

1. Sign in to NASA Earthdata. If access is denied, authorize the NASA GESDISC application in your Earthdata account.
2. Open the notebook in Colab and run its cells in order. The first cell installs notebook dependencies; a later cell prompts for Earthdata authentication.
3. If using the team rainfall and BSI analysis, upload these three files from [`../data/team_data/`](../data/team_data/) into a `team_data/` folder in the Colab working directory:
   - `power_precipitation_daily.csv`
   - `power_monthly_rain_anomalies.csv`
   - `modis_sand_bsi_monthly.csv`
4. The Earth Engine/NDVI section is optional and disabled by default. Enable it only after configuring an Earth Engine project.

## Notebook settings

The settings are in Step 2 of the notebook.

| Setting | Purpose |
|---|---|
| `SITES` | Names and latitude/longitude coordinates for the four study sites |
| `START_WIND`, `END_WIND` | MERRA-2 analysis period (currently 2000–2025) |
| `START_SOIL`, `END_SOIL` | GLDAS analysis period (currently 2000–2025) |
| `BOX_HALF_WIDTH` | Half-width in degrees of the area averaged around each site |
| `TEAM_SITE` | Label assigned to the annual team rainfall series; confirm the files' location before changing this from its placeholder |
| `USE_GEE`, `EE_PROJECT` | Optional Google Earth Engine vegetation and land-surface-temperature analysis |

## Method and outputs

For annual series, the notebook retains complete years, estimates change per decade with Sen's slope, and tests trends using the Mann-Kendall method. The notebook uses a p-value threshold of 0.05; a result that does not meet it is described as **no demonstrated trend**, not proof that no change exists.

The notebook writes its deliverables to `outputs_trends/`, including:

- `trend_results.csv` and `annual_series.csv`
- `trend_summary.png` and `variable_links.png`
- `team_bsi_vs_rain.png` when the required team files are available
- `trend_dashboard.html`
- `README.md` and `data_provenance.csv`

Use the notebook's final export step to download the output archive, then follow the [results guide](../results/README.md). Preserve the repository's results-folder README when copying generated files.

## Troubleshooting

| Symptom | Check |
|---|---|
| Earthdata access or `EulaNotAccepted` error | Confirm the account is signed in and the required GESDISC application is authorized. |
| Team-data section is skipped | Confirm the three CSV files are in the Colab `team_data/` folder and their filenames are unchanged. |
| A site has no usable data | Check its coordinates and `BOX_HALF_WIDTH`; avoid moving a site without documenting why. |
| Notebook takes a long time | NASA downloads and processing can take several minutes. Keep the Colab session active or reduce the analysis period for a test run. |
| NDVI is skipped | This is expected while `USE_GEE` is `False` or Earth Engine is not configured. |
| Colab session disconnects | Reconnect and rerun the notebook; downloaded data in the temporary runtime may need to be fetched again. |
