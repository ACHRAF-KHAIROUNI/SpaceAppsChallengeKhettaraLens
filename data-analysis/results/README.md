# KhettaraLens analysis results

This folder is intended for small, shareable outputs exported by the trend-analysis notebook. The notebook currently writes its run outputs to `outputs_trends/` in Colab; use the notebook guide to download them.

## Expected outputs

| File | Description |
|---|---|
| `trend_results.csv` | Trend results by variable and site, including slope, p-value, and significance |
| `annual_series.csv` | Annual values used in the trend analysis |
| `trend_summary.png` | Summary of estimated change per decade |
| `variable_links.png` | Correlations between annual variables for the selected site |
| `team_bsi_vs_rain.png` | Team rainfall-anomaly and BSI comparison, when input files are available |
| `trend_dashboard.html` | Interactive dashboard for exploring variables and sites |
| `data_provenance.csv` | Source products, versions, periods, and notes for the run |
| Generated run report | Notebook-generated `README.md` documenting that run's methods, sources, results, and limitations |

The exact set of outputs depends on the data available and optional notebook sections enabled.

## Updating this folder

1. Run the notebook through its export step and download the generated archive.
2. Review the generated files and provenance information before sharing or presenting results.
3. Copy the relevant outputs into this folder. Rename the notebook-generated `README.md` to `run_README.md` (or another clearly dated filename) so it does not overwrite this folder's instructions.
4. Replace older result files only when the new run is complete and its period, data coverage, and method have been checked.

Results should be interpreted with the limitations described in the generated report. In particular, a trend does not establish a cause, and gridded climate data should not be used to select exact planting locations.
