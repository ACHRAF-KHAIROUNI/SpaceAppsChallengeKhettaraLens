# KhettaraLens data analysis

This Science4Elegance project folder contains KhettaraLens' climate-data analysis and visualization materials. It includes a Google Colab notebook for downloading and analysing NASA data, a Python script for plotting the checked-in team CSV files, and the resulting charts.

## Two analysis workflows

### 1. Trend analysis notebook

[`notebooks/dune_detective_trends_EN.ipynb`](notebooks/dune_detective_trends_EN.ipynb) downloads MERRA-2 and GLDAS data after NASA Earthdata authentication. It can optionally query MODIS data through Google Earth Engine and can load three team CSVs (daily POWER rainfall, monthly rainfall anomalies, and monthly MODIS BSI) when those files are provided in Colab's `team_data/` folder.

The notebook calculates annual means for complete years, applies Sen's slope and the Mann-Kendall test, and creates a dashboard, figures, result tables, and a provenance report. See the [notebook guide](notebooks/README.md) for setup and run instructions.

### 2. Dataset visualization script

[`data/visualize_data.py`](data/visualize_data.py) reads CSV files from `data/team_data/` and writes PNG charts to `data/visualizations/individual/` and `data/visualizations/comparisons/`. It makes individual charts for known datasets, uses a general chart fallback for unrecognized CSVs, and skips designated reference tables.

From `data-analysis/data/`, install the listed packages and run the script:

```bash
python -m pip install -r requirements.txt
python visualize_data.py
```

The script uses pandas, NumPy, Matplotlib, Seaborn, and SciPy. It prints a warning when a dataset cannot be plotted; inspect the terminal output if an expected chart is missing.

## Folder map

| Path | Purpose |
|---|---|
| [`notebooks/`](notebooks/) | Trend-analysis notebook and its guide |
| [`data/team_data/`](data/team_data/) | Checked-in CSV datasets |
| [`data/visualizations/`](data/visualizations/) | PNG charts produced by the visualization script |
| [`data/requirements.txt`](data/requirements.txt) | Python dependencies for the visualization script |
| [`results/`](results/) | Instructions for sharing notebook-generated outputs |
| [`docs/`](docs/) | Contribution guidance and roadmap |

## Interpretation notes

- MERRA-2 and GLDAS are gridded products. Their values describe regional conditions, not precise planting locations.
- A statistically significant trend is evidence of a trend in the tested series; it does not identify a cause.
- BSI is a bare-surface proxy, not a direct measurement of sand movement. Monthly observations may have gaps and are not independent.
- Verify the geographic coverage of the team-provided rainfall and BSI datasets before using them to describe a specific site.
- Treat correlations as exploratory associations, not proof of a physical relationship.

## Data documentation

See the [data guide](data/README.md) for the available CSV files, their fields, and dataset limitations. After a notebook run, use the generated provenance file to verify the products, versions, and periods used for that run.
