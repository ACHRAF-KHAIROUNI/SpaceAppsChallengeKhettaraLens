# Written by Science4Elegance team for the NASA Space Apps Challenge
"""Generate scientific visualizations for the Merzouga (Morocco) datasets.

Reads every CSV in ``team_data/``, builds one or more purpose-chosen charts per
file in ``visualizations/individual/``, then cross-dataset comparison charts in
``visualizations/comparisons/``.

Run:  py visualize_data.py   (or: python visualize_data.py)
"""

from __future__ import annotations

import sys
import textwrap
from functools import lru_cache
from pathlib import Path

# Third-party imports: fail with an actionable message instead of a traceback,
# because the "python" on PATH may not be the interpreter with the packages.
try:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns
    from scipy.stats import pearsonr
except ImportError as exc:
    sys.exit(
        f"Missing package ({exc}).\n"
        "This script needs pandas, numpy, matplotlib, seaborn and scipy.\n"
        "  1) Install them:   py -m pip install -r requirements.txt\n"
        "     (or:            python -m pip install -r requirements.txt)\n"
        "  2) If they are already installed in another interpreter, run the\n"
        "     script with that one, e.g.:  py visualize_data.py"
    )

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "team_data"
OUT_DIR = BASE_DIR / "visualizations"
IND_DIR = OUT_DIR / "individual"
CMP_DIR = OUT_DIR / "comparisons"

FIGSIZE = (11, 6)
DPI = 300
FOOTER = "Science4Elegance | NASA Space Apps Challenge"

# Color-blind friendly (Okabe-Ito) palette, used everywhere
PALETTE = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#56B4E9", "#CC79A7", "#F0E442"]
BLUE, ORANGE, GREEN, RED, SKY, PINK, YELLOW = PALETTE
GRID_KW = dict(color="#D9D9D9", linewidth=0.7, alpha=0.9)

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def setup_theme() -> None:
    """Consistent scientific look across all figures."""
    sns.set_theme(style="whitegrid", context="notebook", palette=PALETTE)
    plt.rcParams.update({
        "figure.figsize": FIGSIZE,
        "font.size": 11,
        "axes.titlesize": 12,
        "axes.labelsize": 11,
        "axes.edgecolor": "#666666",
        "axes.linewidth": 0.9,
        "legend.fontsize": 9.5,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })


# --------------------------------------------------------------------------
# Loading / cleaning helpers
# --------------------------------------------------------------------------
def load_csv(name: str) -> pd.DataFrame:
    """Load a CSV and parse known date/time columns."""
    df = pd.read_csv(DATA_DIR / name)
    for col in ("date", "time"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df.dropna(how="all")


@lru_cache(maxsize=None)
def _cached(name: str) -> pd.DataFrame:
    return load_csv(name)


def break_gaps(series: pd.Series, max_gap: str = "60D") -> pd.Series:
    """Insert NaN where observations are far apart so lines do not bridge gaps."""
    s = series.sort_index()
    diff = s.index.to_series().diff()
    gap_idx = diff[diff > pd.Timedelta(max_gap)].index
    if len(gap_idx) == 0:
        return s
    filler = pd.Series(np.nan, index=gap_idx, name=s.name)
    return pd.concat([s, filler]).sort_index()


def monthly_mean(df: pd.DataFrame, date_col: str, cols: list[str]) -> pd.DataFrame:
    """Resample daily data to calendar-month means with a month-start index."""
    out = (df.set_index(date_col)[cols]
           .resample("ME").mean()
           .reset_index())
    out[date_col] = out[date_col].dt.to_period("M").dt.to_timestamp()
    return out.rename(columns={date_col: "month"})


# --------------------------------------------------------------------------
# Figure finishing helpers
# --------------------------------------------------------------------------
def finish(fig, title: str, subtitle: str, source: str, path: Path) -> None:
    """Title, subtitle, footer, layout and save at 300 dpi."""
    wrapped = textwrap.fill(subtitle, 150)
    n_lines = wrapped.count("\n") + 1
    fig.suptitle(title, fontsize=15, fontweight="bold", x=0.012, ha="left", y=0.975)
    fig.text(0.012, 0.915, wrapped,
             fontsize=9.5, color="#444444", ha="left", va="top")
    fig.text(0.012, 0.015, FOOTER, fontsize=8.5, color="#666666", ha="left")
    src_text = f"Source: {source}"
    if len(src_text) > 90:  # keep the footer from colliding with the left text
        src_text = "Source: " + source[:87] + "..."
    fig.text(0.988, 0.015, src_text, fontsize=8.5,
             color="#666666", ha="right")
    try:
        fig.tight_layout(rect=(0.005, 0.04, 0.995, 0.90 - 0.035 * n_lines))
    except Exception:
        pass
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def save_individual(fig, stem: str, chart: str, title: str,
                    subtitle: str, source: str) -> None:
    finish(fig, title, subtitle, source, IND_DIR / f"{stem}_{chart}.png")


def save_comparison(fig, name: str, title: str, subtitle: str, source: str) -> None:
    finish(fig, title, subtitle, source, CMP_DIR / f"{name}.png")


def tidy(ax, xlabel: str | None = None, ylabel: str | None = None) -> None:
    ax.grid(True, **GRID_KW)
    ax.set_axisbelow(True)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    sns.despine(ax=ax)


def annotate_peak(ax, x, y, text: str, color=RED, dx=12, dy=12) -> None:
    ax.annotate(text, xy=(x, y), xytext=(dx, dy), textcoords="offset points",
                fontsize=9, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.0))


def date_axis(ax) -> None:
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))


# --------------------------------------------------------------------------
# Per-file visualizations
# --------------------------------------------------------------------------
def plot_power_precipitation_daily(df: pd.DataFrame) -> list[str]:
    stem = "power_precipitation_daily"
    src = "power_precipitation_daily.csv"
    d = df.dropna(subset=["date"]).sort_values("date")
    charts = []

    # 1) time series: daily rain + 365-day rolling mean + flagged extremes
    fig, ax = plt.subplots()
    ax.plot(d["date"], d["rain_mm_day"], color=BLUE, lw=0.5, alpha=0.5,
            label="Daily rainfall")
    roll = (d.set_index("date")["rain_mm_day"]
            .rolling("365D", min_periods=30).mean())
    ax.plot(roll.index, roll.values, color=ORANGE, lw=2.2, label="365-day rolling mean")
    ext = d[d["extreme_rain_day"]]
    ax.scatter(ext["date"], ext["rain_mm_day"], s=34, color=RED, zorder=5,
               label="Extreme-rain day (flagged)")
    imax = d["rain_mm_day"].idxmax()
    annotate_peak(ax, d.loc[imax, "date"], d.loc[imax, "rain_mm_day"],
                   f"max {d.loc[imax, 'rain_mm_day']:.1f} mm\n"
                   f"{d.loc[imax, 'date']:%d %b %Y}")
    ax.set_ylim(bottom=0)
    date_axis(ax)
    tidy(ax, "Date", "Rainfall (mm day$^{-1}$)")
    ax.legend(loc="upper right", frameon=True)
    save_individual(fig, stem, "timeseries",
                    "Daily rainfall time series, NASA POWER (2001-2026)",
                    "Daily totals with a 365-day rolling mean; red points are days flagged "
                    "as extreme rainfall. Note the very skewed, event-driven desert regime.", src)
    charts.append("timeseries")

    # 2) distribution of wet-day amounts (log scale)
    wet = d.loc[d["rain_mm_day"] > 0, "rain_mm_day"].dropna()
    fig, ax = plt.subplots()
    ax.hist(wet, bins=np.logspace(np.log10(wet.min()), np.log10(wet.max()), 45),
            color=BLUE, edgecolor="white", lw=0.4)
    ax.set_xscale("log")
    for q, lab, col in [(0.5, "median", ORANGE), (0.95, "95th pct", GREEN)]:
        v = wet.quantile(q)
        ax.axvline(v, color=col, ls="--", lw=1.6)
        ax.text(v, ax.get_ylim()[1] * 0.92, f" {lab} = {v:.2f} mm",
                color=col, fontsize=9, rotation=90, va="top")
    tidy(ax, "Daily rainfall on wet days (mm, log scale)", "Number of days")
    save_individual(fig, stem, "distribution",
                    "Distribution of wet-day rainfall amounts",
                    f"{len(wet):,} days with rain > 0 out of {len(d):,} days total; "
                    "log-scale bins reveal the long tail of rare heavy events.", src)
    charts.append("distribution")

    # 3) monthly climatology (mean +- std of monthly totals)
    m = d.set_index("date")["rain_mm_day"].resample("ME").sum()
    clim = m.groupby(m.index.month).agg(["mean", "std"])
    fig, ax = plt.subplots()
    ax.bar(clim.index, clim["mean"], yerr=clim["std"], capsize=4,
           color=BLUE, edgecolor="white", alpha=0.9)
    wettest = clim["mean"].idxmax()
    annotate_peak(ax, wettest, clim.loc[wettest, "mean"],
                   f"wettest: {clim.loc[wettest, 'mean']:.1f} mm", color=RED, dy=18)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_LABELS)
    tidy(ax, "Calendar month", "Total rainfall per month (mm, mean $\\pm$ std)")
    save_individual(fig, stem, "monthly_climatology",
                    "Monthly rainfall climatology (2001-2026)",
                    "Mean monthly total rainfall and standard deviation by calendar month: "
                    "a weak, bimodal spring/autumn signal typical of the pre-Sahara.", src)
    charts.append("monthly_climatology")
    return charts


def plot_power_monthly_rain_anomalies(df: pd.DataFrame) -> list[str]:
    stem = "power_monthly_rain_anomalies"
    src = "power_monthly_rain_anomalies.csv"
    d = df.sort_values("date")
    charts = []

    # 1) anomaly bars coloured by status
    status_colors = {"above-normal / wet": GREEN, "below-normal / deficit": RED,
                     "near-normal": SKY}
    fig, ax = plt.subplots()
    ax.bar(d["date"], d["anomaly_mm"],
           color=[status_colors.get(s, SKY) for s in d["status"]], width=24)
    ax.axhline(0, color="#333333", lw=1.0)
    i_max = d["anomaly_mm"].idxmax()
    annotate_peak(ax, d.loc[i_max, "date"], d.loc[i_max, "anomaly_mm"],
                   f"+{d.loc[i_max, 'anomaly_mm']:.0f} mm "
                   f"({d.loc[i_max, 'date']:%b %Y})", color=GREEN, dy=10)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in status_colors.values()]
    ax.legend(handles, status_colors.keys(), title="Status", loc="upper right")
    date_axis(ax)
    tidy(ax, "Month", "Rainfall anomaly vs climatology (mm month$^{-1}$)")
    save_individual(fig, stem, "anomaly_bars",
                    "Monthly rainfall anomalies vs the local normal (2022-2026)",
                    "Difference between observed and climatological rainfall; blue = wetter, "
                    "red = deficit months, light blue = near normal.", src)
    charts.append("anomaly_bars")

    # 2) month x year z-score heatmap
    piv = d.pivot_table(index="month", columns="year", values="z_score")
    vals = piv.to_numpy(dtype=float)
    annot = [["" if np.isnan(v) else f"{v:.1f}" for v in row] for row in vals]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.heatmap(piv, annot=annot, fmt="", cmap="RdBu_r", center=0,
                cbar_kws={"label": "z-score (standard deviations from normal)"},
                linewidths=0.5, ax=ax, annot_kws={"fontsize": 8.5})
    ax.set_yticklabels(MONTH_LABELS, rotation=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Calendar month")
    save_individual(fig, stem, "zscore_heatmap",
                    "Rainfall z-score by month and year",
                    "Standardised monthly rainfall (wet = red, dry = blue). Empty cells are "
                    "months not covered by the dataset.", src)
    charts.append("zscore_heatmap")

    # 3) observed vs climatology with +/- 1 std band
    fig, ax = plt.subplots()
    ax.fill_between(d["date"],
                    d["climatology_mm"] - d["climatology_std_mm"],
                    d["climatology_mm"] + d["climatology_std_mm"],
                    color=ORANGE, alpha=0.22, label="Normal $\\pm$1 std")
    ax.plot(d["date"], d["climatology_mm"], color=ORANGE, lw=2.0,
            label="Climatology (normal)")
    ax.plot(d["date"], d["rain_mm"], color=BLUE, marker="o", ms=4.5, lw=1.4,
            label="Observed rainfall")
    i = d["rain_mm"].idxmax()
    annotate_peak(ax, d.loc[i, "date"], d.loc[i, "rain_mm"],
                   f"{d.loc[i, 'rain_mm']:.0f} mm ({d.loc[i, 'date']:%b %Y})", color=BLUE)
    date_axis(ax)
    tidy(ax, "Month", "Rainfall (mm month$^{-1}$)")
    ax.legend(loc="upper right")
    save_individual(fig, stem, "rain_vs_climatology",
                    "Observed rainfall against the monthly normal",
                    "Observed totals compared with the climatological mean and its "
                    "$\\pm$1 standard-deviation envelope (NASA POWER, 2022-2026).", src)
    charts.append("rain_vs_climatology")
    return charts


def plot_precip_extreme_rain_screening_days(df: pd.DataFrame) -> list[str]:
    stem = "precip_extreme_rain_screening_days"
    src = "precip_extreme_rain_screening_days.csv"
    d = df.dropna(subset=["date"]).sort_values("date")
    charts = []

    fig, ax = plt.subplots(figsize=(11, 6))
    x = np.arange(len(d))
    w = 0.38
    ax.bar(x - w / 2, d["rain_mm_day"], w, color=BLUE, label="1-day total (mm)")
    ax.bar(x + w / 2, d["rain_3day_mm"], w, color=ORANGE, label="3-day total (mm)")
    for xi, v in zip(x - w / 2, d["rain_mm_day"]):
        ax.text(xi, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=BLUE)
    for xi, v in zip(x + w / 2, d["rain_3day_mm"]):
        ax.text(xi, v + 1.5, f"{v:.0f}", ha="center", fontsize=8, color=ORANGE)
    ax.set_xticks(x)
    ax.set_xticklabels(d["date"].dt.strftime("%d %b %Y"), rotation=35, ha="right")
    tidy(ax, "Extreme-rain date", "Rainfall (mm)")
    ax.legend(loc="upper right")
    save_individual(fig, stem, "grouped_bars",
                    "Screened extreme-rain events (2002-2024)",
                    "The 9 days flagged by the extreme-rain screening: 1-day vs 3-day totals. "
                    "Only 5 of 9 also exceed the 3-day extreme threshold.", src)
    charts.append("grouped_bars")

    fig, ax = plt.subplots()
    ax.scatter(d["rain_mm_day"], d["rain_3day_mm"], s=70, color=BLUE,
               edgecolor="white", zorder=3)
    lim = max(d["rain_mm_day"].max(), d["rain_3day_mm"].max()) * 1.1
    ax.plot([0, lim], [0, lim], ls="--", lw=1.2, color="#888888", label="1:1 line")
    for _, r in d.iterrows():
        ax.annotate(r["date"].strftime("%Y-%m-%d"),
                    (r["rain_mm_day"], r["rain_3day_mm"]),
                    textcoords="offset points", xytext=(6, 4), fontsize=8, color="#444444")
    tidy(ax, "1-day rainfall total (mm)", "3-day rainfall total (mm)")
    ax.legend(loc="upper left")
    save_individual(fig, stem, "daily_vs_3day_scatter",
                    "1-day vs 3-day totals for screened extreme events",
                    "Points above the dashed line indicate events whose 3-day accumulation "
                    "exceeds the single-day peak (multi-day storms).", src)
    charts.append("daily_vs_3day_scatter")
    return charts


def plot_modis_sand_bsi_monthly(df: pd.DataFrame) -> list[str]:
    stem = "modis_sand_bsi_monthly"
    src = "modis_sand_bsi_monthly.csv"
    d = df.dropna(subset=["date"]).sort_values("date").set_index("date")
    charts = []

    # 1) time series with acquisition gap highlighted
    fig, ax = plt.subplots()
    s = break_gaps(d["bsi_mean"], "90D")
    ax.plot(s.index, s.values, color=BLUE, marker="o", ms=5, lw=1.4,
            label="Monthly BSI mean")
    roll = d["bsi_mean"].rolling(3, min_periods=1).mean()
    ax.plot(roll.index, roll.values, color=ORANGE, lw=2.0, label="3-month rolling mean")
    ax.axvspan(pd.Timestamp("2021-12-25"), pd.Timestamp("2022-05-25"),
               color="#BBBBBB", alpha=0.45, label="No acquisitions")
    i_max = d["bsi_mean"].idxmax()
    annotate_peak(ax, i_max, d.loc[i_max, "bsi_mean"],
                   f"most bare surface: {d.loc[i_max, 'bsi_mean']:.3f}", color=RED, dy=14)
    date_axis(ax)
    tidy(ax, "Date", "Bare Soil Index (BSI, -1 to 1)")
    ax.legend(loc="lower right")
    save_individual(fig, stem, "timeseries",
                    "MODIS Bare Soil Index, monthly (2021-2026)",
                    "Higher BSI = more bare/sand-exposed surface. Lines break across the "
                    "Dec 2021 - May 2022 acquisition gap; BSI is a change proxy only.", src)
    charts.append("timeseries")

    # 2) distribution
    fig, ax = plt.subplots()
    sns.histplot(d["bsi_mean"], bins=18, kde=True, color=BLUE, ax=ax,
                 edgecolor="white")
    ax.axvline(d["bsi_mean"].mean(), color=RED, ls="--", lw=1.6)
    ax.text(d["bsi_mean"].mean(), ax.get_ylim()[1] * 0.95,
            f" mean = {d['bsi_mean'].mean():.3f}", color=RED, fontsize=9, va="top")
    tidy(ax, "Bare Soil Index (BSI)", "Number of monthly snapshots")
    save_individual(fig, stem, "distribution",
                    "Distribution of monthly BSI values",
                    f"{len(d)} monthly snapshots; the narrow range around 0.23 confirms a "
                    "consistently bare surface with modest month-to-month change.", src)
    charts.append("distribution")

    # 3) seasonal pattern
    by_month = d.groupby(d.index.month)["bsi_mean"].agg(["mean", "std"])
    fig, ax = plt.subplots()
    ax.plot(by_month.index, by_month["mean"], marker="o", color=BLUE, lw=2.0)
    ax.fill_between(by_month.index, by_month["mean"] - by_month["std"],
                    by_month["mean"] + by_month["std"], color=BLUE, alpha=0.18,
                    label="$\\pm$1 std")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTH_LABELS)
    tidy(ax, "Calendar month", "Mean BSI (-)")
    ax.legend()
    save_individual(fig, stem, "seasonal_cycle",
                    "Seasonal cycle of the Bare Soil Index",
                    "Mean BSI by calendar month over 2021-2026, with $\\pm$1 standard "
                    "deviation: seasonal breathing of bare/sand-exposed surface.", src)
    charts.append("seasonal_cycle")
    return charts


def plot_merra2_wind_daily_sites(df: pd.DataFrame) -> list[str]:
    stem = "merra2_wind_daily_sites"
    src = "merra2_wind_daily_sites.csv"
    charts = []

    # 1) per-site time series with 30-day rolling means
    fig, ax = plt.subplots()
    for i, (site, g) in enumerate(df.groupby("site")):
        g = g.sort_values("time")
        col = PALETTE[i % len(PALETTE)]
        s = break_gaps(g.set_index("time")["wspd_mean"], "14D")
        ax.plot(s.index, s.values, color=col, lw=0.5, alpha=0.45)
        roll = s.rolling("30D", min_periods=7).mean()
        ax.plot(roll.index, roll.values, color=col, lw=2.0, label=f"{site} (30-day mean)")
    ax.axvspan(pd.Timestamp("2002-01-01"), pd.Timestamp("2024-12-31"),
               color="#EEEEEE", zorder=0)
    ax.text(pd.Timestamp("2013-06-01"), ax.get_ylim()[1] * 0.5,
            "no wind data\n2002-2024", ha="center", fontsize=10, color="#777777")
    date_axis(ax)
    tidy(ax, "Date", "10 m wind speed (m s$^{-1}$)")
    ax.legend(loc="upper left")
    save_individual(fig, stem, "timeseries",
                    "Daily MERRA-2 wind speed at two sites (2000-2026)",
                    "Daily 10 m wind speed with 30-day rolling means for Merzouga and "
                    "Hassilabied. The extract only covers 2000-2001 and 2025-2026.", src)
    charts.append("timeseries")

    # 2) distribution by site
    fig, ax = plt.subplots()
    sns.violinplot(data=df, x="site", y="wspd_mean", inner="quartile",
                   cut=0, ax=ax, saturation=0.9)
    means = df.groupby("site")["wspd_mean"].mean()
    for i, site in enumerate(means.index):
        ax.scatter(i, means[site], marker="D", s=45, color=RED, zorder=5,
                   label="mean" if i == 0 else None)
    tidy(ax, "Site", "Mean wind speed (m s$^{-1}$)")
    ax.legend()
    save_individual(fig, stem, "distribution",
                    "Wind speed distributions by site",
                    "Violin plots of daily mean wind speed (quartiles inside); red diamonds "
                    "mark the site means. Both sites share a similar wind regime.", src)
    charts.append("distribution")

    # 3) wind rose per site (strong-wind hours by direction)
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    cols = [f"strong_from_{d}" for d in dirs]
    fig, axes = plt.subplots(1, 2, figsize=(12, 6),
                             subplot_kw={"projection": "polar"})
    for ax, (site, g) in zip(axes, df.groupby("site")):
        vals = g[cols].sum().to_numpy()
        theta = np.linspace(0, 2 * np.pi, len(dirs), endpoint=False)
        ax.bar(theta, vals, width=0.72, color=BLUE, edgecolor="white", alpha=0.9)
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.degrees(theta), dirs)
        ax.set_title(f"{site}", pad=18)
        ax.grid(True, **GRID_KW)
    fig.text(0.5, 0.03,
             "Bar length = total hours of strong wind coming from each direction",
             ha="center", fontsize=10, color="#444444")
    save_individual(fig, stem, "wind_rose",
                    "Wind roses: strong-wind hours by direction",
                    "Directional exposure of the two sites from MERRA-2 strong-wind hours; "
                    "both are dominated by NE-SW flow, the Saharan trade axis.", src)
    charts.append("wind_rose")
    return charts


def plot_merra2_wind_daily_box_mean(df: pd.DataFrame) -> list[str]:
    stem = "merra2_wind_daily_box_mean"
    src = "merra2_wind_daily_box_mean.csv"
    d = df.dropna(subset=["time"]).sort_values("time").set_index("time")
    charts = []

    # 1) time series: mean and max wind
    fig, ax = plt.subplots()
    mean_s = break_gaps(d["wspd_mean"], "14D")
    max_s = break_gaps(d["wspd_max"], "14D")
    ax.fill_between(max_s.index, mean_s.values, max_s.values,
                    color=SKY, alpha=0.35, label="daily gust envelope (max)")
    ax.plot(mean_s.index, mean_s.values, color=BLUE, lw=0.7, alpha=0.7,
            label="daily mean")
    roll = mean_s.rolling("30D", min_periods=7).mean()
    ax.plot(roll.index, roll.values, color=ORANGE, lw=2.2, label="30-day rolling mean")
    i = d["wspd_max"].idxmax()
    annotate_peak(ax, i, d.loc[i, "wspd_max"],
                   f"peak gust {d.loc[i, 'wspd_max']:.1f} m s$^{{-1}}$", color=RED, dy=10)
    ax.axvspan(pd.Timestamp("2002-01-01"), pd.Timestamp("2024-12-31"),
               color="#EEEEEE", zorder=0)
    date_axis(ax)
    tidy(ax, "Date", "Wind speed (m s$^{-1}$)")
    ax.legend(loc="upper right")
    save_individual(fig, stem, "timeseries",
                    "Daily MERRA-2 wind speed, box mean (2000-2026)",
                    "Daily mean wind with the gust (daily-max) envelope and a 30-day rolling "
                    "mean. Coverage: 2000-2001 and 2025-2026 only.", src)
    charts.append("timeseries")

    # 2) distribution of mean vs max wind
    fig, ax = plt.subplots()
    ax.hist(d["wspd_mean"], bins=40, alpha=0.75, color=BLUE, edgecolor="white",
            label=f"Daily mean (median {d['wspd_mean'].median():.1f})")
    ax.hist(d["wspd_max"], bins=40, alpha=0.65, color=ORANGE, edgecolor="white",
            label=f"Daily max (median {d['wspd_max'].median():.1f})")
    ax.axvline(d["wspd_mean"].mean(), color=BLUE, ls="--", lw=1.4)
    ax.axvline(d["wspd_max"].mean(), color=ORANGE, ls="--", lw=1.4)
    ax.annotate(f"strong-wind threshold region\nabove {d['wspd_mean'].quantile(0.95):.1f} m s$^{{-1}}$ "
                "(95th pct of daily means)",
                xy=(d["wspd_mean"].quantile(0.95), ax.get_ylim()[1] * 0.75),
                xytext=(40, 0), textcoords="offset points", fontsize=9, color=RED,
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.0))
    tidy(ax, "Wind speed (m s$^{-1}$)", "Number of days")
    ax.legend(loc="upper right")
    save_individual(fig, stem, "distribution",
                    "Wind speed distributions, box mean",
                    "Daily mean vs daily-max wind speeds; dashed lines are the means and the "
                    "annotation marks the strong-wind tail relevant to sand transport.", src)
    charts.append("distribution")

    # 3) strong hours by calendar month (storminess seasonality)
    tmp = d.reset_index()
    tmp["month"] = tmp["time"].dt.month
    fig, ax = plt.subplots()
    sns.boxplot(data=tmp, x="month", y="strong_hours", color=BLUE,
                fliersize=2, ax=ax)
    ax.set_xticks(range(12))
    ax.set_xticklabels(MONTH_LABELS)
    tidy(ax, "Calendar month", "Strong-wind hours per day (h)")
    save_individual(fig, stem, "strong_hours_seasonality",
                    "Seasonality of strong-wind hours",
                    "Distribution of daily strong-wind hours by calendar month: when the "
                    "windiest, most sand-mobile part of the year falls.", src)
    charts.append("strong_hours_seasonality")
    return charts


def plot_gldas_soil_monthly_sites(df: pd.DataFrame) -> list[str]:
    stem = "gldas_soil_monthly_sites"
    src = "gldas_soil_monthly_sites.csv"
    charts = []

    # 1) per-site time series
    fig, ax = plt.subplots()
    for i, (site, g) in enumerate(df.groupby("site")):
        g = g.sort_values("time")
        col = PALETTE[i % len(PALETTE)]
        ax.plot(g["time"], g["vol_m3m3_approx"], color=col, lw=1.0, alpha=0.75,
                label=f"{site} (monthly)")
        roll = g.set_index("time")["vol_m3m3_approx"].rolling(12, min_periods=3).mean()
        ax.plot(roll.index, roll.values, color=col, lw=2.2,
                label=f"{site} (12-month mean)")
    date_axis(ax)
    tidy(ax, "Date", "Volumetric soil moisture 0-10 cm (m$^3$ m$^{-3}$)")
    ax.legend(loc="upper right", ncol=2)
    save_individual(fig, stem, "timeseries",
                    "Root-zone soil moisture at two sites, GLDAS (2010-2026)",
                    "Monthly 0-10 cm soil moisture for Merzouga and Hassilabied with "
                    "12-month rolling means; both track the same regional water balance.", src)
    charts.append("timeseries")

    # 2) distribution by site
    fig, ax = plt.subplots()
    sns.boxplot(data=df, x="site", y="vol_m3m3_approx", color=BLUE, ax=ax,
                fliersize=2.5, width=0.5)
    sns.stripplot(data=df, x="site", y="vol_m3m3_approx", color="#333333",
                  size=2.5, alpha=0.35, ax=ax)
    tidy(ax, "Site", "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)")
    save_individual(fig, stem, "distribution",
                    "Soil moisture distributions by site",
                    "Box plots with individual monthly values overlaid: the two sites are "
                    "nearly identical, so the box mean is representative.", src)
    charts.append("distribution")

    # 3) month x year heatmap for Merzouga
    mer = df[df["site"] == "Merzouga"].copy()
    mer["month"] = mer["time"].dt.month
    mer["year"] = mer["time"].dt.year
    piv = mer.pivot_table(index="month", columns="year", values="vol_m3m3_approx")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.heatmap(piv, cmap="YlGnBu", linewidths=0.4,
                cbar_kws={"label": "Soil moisture (m$^3$ m$^{-3}$)"}, ax=ax)
    ax.set_yticklabels(MONTH_LABELS, rotation=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Calendar month")
    save_individual(fig, stem, "heatmap_month_year",
                    "Soil moisture by month and year - Merzouga",
                    "Seasonal wetting (yellow) and drying (dark blue) of the 0-10 cm layer, "
                    "month by year from 2010 to 2026.", src)
    charts.append("heatmap_month_year")
    return charts


def plot_gldas_soil_monthly_box_mean(df: pd.DataFrame) -> list[str]:
    stem = "gldas_soil_monthly_box_mean"
    src = "gldas_soil_monthly_box_mean.csv"
    d = df.dropna(subset=["time"]).sort_values("time")
    charts = []

    # 1) time series with seasonal climatology band
    fig, ax = plt.subplots()
    ax.plot(d["time"], d["vol_m3m3_approx"], color=BLUE, lw=1.1,
            label="Monthly box mean")
    roll = d.set_index("time")["vol_m3m3_approx"].rolling(12, min_periods=3).mean()
    ax.plot(roll.index, roll.values, color=ORANGE, lw=2.4, label="12-month mean")
    i = d["vol_m3m3_approx"].idxmax()
    annotate_peak(ax, d.loc[i, "time"], d.loc[i, "vol_m3m3_approx"],
                   f"wettest {d.loc[i, 'vol_m3m3_approx']:.2f} "
                   f"({d.loc[i, 'time']:%b %Y})", color=GREEN, dy=12)
    j = d["vol_m3m3_approx"].idxmin()
    annotate_peak(ax, d.loc[j, "time"], d.loc[j, "vol_m3m3_approx"],
                   f"driest {d.loc[j, 'vol_m3m3_approx']:.2f}",
                   color=RED, dx=-60, dy=-22)
    date_axis(ax)
    tidy(ax, "Date", "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)")
    ax.legend(loc="upper right")
    save_individual(fig, stem, "timeseries",
                    "GLDAS soil moisture, box mean (2010-2026)",
                    "Monthly volumetric soil moisture with a 12-month mean and annotated "
                    "extremes: a clear annual wet-dry cycle over a dry baseline.", src)
    charts.append("timeseries")

    # 2) month x year heatmap
    tmp = d.copy()
    tmp["month"] = tmp["time"].dt.month
    tmp["year"] = tmp["time"].dt.year
    piv = tmp.pivot_table(index="month", columns="year", values="vol_m3m3_approx")
    fig, ax = plt.subplots(figsize=(10, 5.5))
    sns.heatmap(piv, cmap="YlGnBu", linewidths=0.4,
                cbar_kws={"label": "Soil moisture (m$^3$ m$^{-3}$)"}, ax=ax)
    ax.set_yticklabels(MONTH_LABELS, rotation=0)
    ax.set_xlabel("Year")
    ax.set_ylabel("Calendar month")
    save_individual(fig, stem, "heatmap_month_year",
                    "Soil moisture by month and year, box mean",
                    "Month-by-year matrix of root-zone moisture: seasonal structure dominates "
                    "and no long-term drying trend is obvious by eye.", src)
    charts.append("heatmap_month_year")

    # 3) distribution
    fig, ax = plt.subplots()
    sns.histplot(d["vol_m3m3_approx"], bins=25, kde=True, color=GREEN, ax=ax,
                 edgecolor="white")
    med = d["vol_m3m3_approx"].median()
    ax.axvline(med, color=RED, ls="--", lw=1.6)
    ax.text(med, ax.get_ylim()[1] * 0.95, f" median = {med:.2f} m$^3$ m$^{{-3}}$",
            color=RED, fontsize=9, va="top")
    tidy(ax, "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)", "Number of months")
    save_individual(fig, stem, "distribution",
                    "Distribution of monthly soil moisture",
                    f"{len(d)} months of box-mean soil moisture: bimodal shape reflecting "
                    "the wet and dry seasons of the Merzouga region.", src)
    charts.append("distribution")
    return charts


# Plant trait keyword table (derived by scanning the documented adaptation text)
PLANT_TRAITS = {
    "Deep roots /\ngroundwater": ["taproot", "deep water", "groundwater",
                                  "water table", "root system", "root network"],
    "Reduced leaf\narea": ["bipinnate leaflets", "scale-like", "minute leaves",
                           "rudimentary", "reduced to tiny", "small, leathery",
                           "very small"],
    "Waxy / reflective\nsurface": ["waxy", "glaucous", "reflect", "cuticle"],
    "Salt tolerance": ["salt", "saline", "alkaline"],
    "Succulence / C4": ["succulen", "c4 ", "cladodes", "photosynthetic stems"],
    "Drought-deciduous /\ndefence": ["sheds leaves", "thorn", "spine", "toxic latex"],
    "Wind / sand\nanchoring": ["high winds", "binds loose sandy soil", "sandy soil"],
}


def _plant_trait_matrix(df: pd.DataFrame) -> pd.DataFrame:
    text = (df["Specific Adaptations"].fillna("") + " " +
            df["Leaf Structure"].fillna("")).str.lower()
    labels = df["Common Name"].str.split(" / ").str[0]
    rows = []
    for t in text:
        rows.append([int(any(k in t for k in keys)) for keys in PLANT_TRAITS.values()])
    return pd.DataFrame(rows, index=labels, columns=list(PLANT_TRAITS))


def plot_morocco_merzouga_plant_adaptations(df: pd.DataFrame) -> list[str]:
    stem = "morocco_merzouga_plant_adaptations"
    src = "morocco_merzouga_plant_adaptations.csv"
    charts = []

    # 1) species x trait keyword matrix
    mat = _plant_trait_matrix(df)
    ann = [[("●" if v else "") for v in row] for row in mat.to_numpy()]
    fig, ax = plt.subplots(figsize=(10.5, 5.5))
    sns.heatmap(mat, cmap=sns.color_palette(["#EEEEEE", BLUE], as_cmap=True),
                cbar=False, linewidths=1.0, linecolor="white",
                annot=ann, fmt="", ax=ax, annot_kws={"fontsize": 14},
                xticklabels=True, yticklabels=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha="right")
    ax.set_xlabel("Documented adaptive trait (keyword scan of the source text)")
    ax.set_ylabel("Species")
    save_individual(fig, stem, "trait_matrix",
                    "Adaptive trait matrix of Merzouga flora (6 species)",
                    "Blue = trait explicitly documented in the species description: a compact "
                    "view of the survival strategies present in the Merzouga plant list.", src)
    charts.append("trait_matrix")

    # 2) adaptation categories with family information
    fig, ax = plt.subplots(figsize=(11, 6))
    cats = df["Adaptation Category"].value_counts().sort_values()
    ax.barh(range(len(cats)), cats.values, color=PALETTE[0], edgecolor="white")
    for y, (cat, n) in enumerate(cats.items()):
        fams = ", ".join(df.loc[df["Adaptation Category"] == cat, "Family"])
        ax.text(n + 0.05, y, f"{int(n)} species - {fams}", va="center", fontsize=9,
                color="#333333")
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels([textwrap.fill(c, 34) for c in cats.index])
    ax.set_xlim(0, cats.max() * 2.6)
    tidy(ax, "Number of species", "Adaptation category")
    save_individual(fig, stem, "adaptation_categories",
                    "Plant adaptation categories - Merzouga species list",
                    "One species per strategy (families in grey): xerophyte, phreatophyte, "
                    "halophyte, oasis palm, C4 succulent and drought-deciduous.", src)
    charts.append("adaptation_categories")
    return charts


def plot_extracted_pdf_plant_adaptations(df: pd.DataFrame) -> list[str]:
    stem = "extracted_pdf_plant_adaptations"
    src = "extracted_pdf_plant_adaptations.csv"
    charts = []

    # 1) suitability class counts
    short = df["Merzouga Suitability"].str.split(" (", regex=False).str[0]
    counts = short.value_counts()
    fig, ax = plt.subplots()
    bars = ax.bar(counts.index, counts.values,
                  color=[GREEN if "Excellent" in i else ORANGE for i in counts.index],
                  edgecolor="white", width=0.55)
    for b, n in zip(bars, counts.values):
        ax.text(b.get_x() + b.get_width() / 2, n + 0.06, f"{int(n)} species",
                ha="center", fontsize=10, fontweight="bold")
    ax.set_ylim(0, counts.max() * 1.25)
    ax.tick_params(axis="x", labelsize=10)
    tidy(ax, "Merzouga suitability class", "Number of species")
    save_individual(fig, stem, "suitability_counts",
                    "Merzouga suitability of the extracted plant list",
                    "Species classified as excellent target species vs species needing oasis "
                    "or microclimate control (extracted from the team PDF).", src)
    charts.append("suitability_counts")

    # 2) every species coloured by suitability
    order = short.map({"Excellent": 0, "Requires Oasis / Microclimate Control": 1})
    fig, ax = plt.subplots(figsize=(11, 6))
    y = np.arange(len(df))[::-1]
    colors = [GREEN if "Excellent" in s else ORANGE for s in short]
    ax.scatter([0] * len(df), y, s=140, c=colors, zorder=3, edgecolor="white")
    for yi, (_, r) in zip(y, df.iterrows()):
        ax.text(0.06, yi, f"{r['Common Name']}  ({r['Scientific Name']})",
                va="center", fontsize=10)
        ax.text(0.62, yi, r["Merzouga Suitability"].split(" (")[0],
                va="center", fontsize=9, color="#555555")
    ax.set_xlim(-0.05, 1.0)
    ax.set_ylim(-0.7, len(df) - 0.3)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)
    handles = [plt.Line2D([], [], marker="o", ls="", color=GREEN, markersize=10,
                          label="Excellent (target species)"),
               plt.Line2D([], [], marker="o", ls="", color=ORANGE, markersize=10,
                          label="Requires oasis / microclimate control")]
    ax.legend(handles=handles, loc="lower right", frameon=True)
    save_individual(fig, stem, "species_suitability",
                    "Species-by-species Merzouga suitability",
                    "All 7 extracted species with their suitability rating: 2 ready for "
                    "direct planting, 5 needing protected, wetter microsites.", src)
    charts.append("species_suitability")
    return charts


def plot_generic(df: pd.DataFrame, stem: str) -> list[str]:
    """Fallback for any CSV without a dedicated routine."""
    src = f"{stem}.csv"
    num = df.select_dtypes("number").columns
    date_col = next((c for c in ("date", "time") if c in df.columns), None)
    charts = []
    if date_col and len(num):
        fig, ax = plt.subplots()
        for i, c in enumerate(num[:4]):
            ax.plot(df[date_col], df[c], lw=1.2, label=c,
                    color=PALETTE[i % len(PALETTE)])
        date_axis(ax)
        tidy(ax, "Date", "Value")
        ax.legend()
        save_individual(fig, stem, "timeseries", f"{stem} - time series",
                        "Automatic chart: numeric columns plotted against the date column.", src)
        charts.append("timeseries")
    elif len(num):
        fig, ax = plt.subplots(figsize=FIGSIZE)
        df[num].hist(ax=ax, color=BLUE, edgecolor="white")
        fig.tight_layout(rect=(0.005, 0.04, 0.995, 0.87))
        save_individual(fig, stem, "histograms", f"{stem} - distributions",
                        "Automatic chart: histogram of each numeric column.", src)
        charts.append("histograms")
    return charts


# Files deliberately not plotted (reference/descriptive tables)
SKIP_FILES = {"regions_africa_table1"}

# Dispatch: file stem -> plot functions (files themselves are auto-discovered)
CHART_ROUTINES = {    "power_precipitation_daily": [plot_power_precipitation_daily],
    "power_monthly_rain_anomalies": [plot_power_monthly_rain_anomalies],
    "precip_extreme_rain_screening_days": [plot_precip_extreme_rain_screening_days],
    "modis_sand_bsi_monthly": [plot_modis_sand_bsi_monthly],
    "merra2_wind_daily_sites": [plot_merra2_wind_daily_sites],
    "merra2_wind_daily_box_mean": [plot_merra2_wind_daily_box_mean],
    "gldas_soil_monthly_sites": [plot_gldas_soil_monthly_sites],
    "gldas_soil_monthly_box_mean": [plot_gldas_soil_monthly_box_mean],
    "morocco_merzouga_plant_adaptations": [plot_morocco_merzouga_plant_adaptations],
    "extracted_pdf_plant_adaptations": [plot_extracted_pdf_plant_adaptations],
}

CHART_REASON = {
    "power_precipitation_daily":
        "event-driven daily series -> time series + skewed distribution + monthly climatology",
    "power_monthly_rain_anomalies":
        "anomaly time series, month x year heat pattern, observed vs normal band",
    "precip_extreme_rain_screening_days":
        "few labelled events -> grouped bars + 1-day vs 3-day scatter",
    "modis_sand_bsi_monthly":
        "sparse monthly index -> broken time series + distribution + seasonal cycle",
    "merra2_wind_daily_sites":
        "two sites, daily wind -> per-site series, violin distributions, wind roses",
    "merra2_wind_daily_box_mean":
        "gusty daily wind -> series with gust envelope, distributions, storminess season",
    "gldas_soil_monthly_sites":
        "two sites, monthly moisture -> series, box plots, month x year heatmap",
    "gldas_soil_monthly_box_mean":
        "long monthly record -> series with extremes, heatmap, distribution",
    "morocco_merzouga_plant_adaptations":
        "categorical trait text -> species x trait matrix + category bars",
    "extracted_pdf_plant_adaptations":
        "two-class suitability rating -> counts bar + species-by-species dot plot",
    "regions_africa_table1":
        "reference/descriptive table - no visualization requested, skipped",
}


# --------------------------------------------------------------------------
# Comparison visualizations
# --------------------------------------------------------------------------
def _monthly_frame() -> pd.DataFrame:
    """Outer-join the four environmental datasets on calendar month."""
    rain = _cached("power_monthly_rain_anomalies.csv")[
        ["date", "rain_mm", "anomaly_mm"]].rename(columns={"date": "month"})
    wind = monthly_mean(_cached("merra2_wind_daily_box_mean.csv"), "time",
                        ["wspd_mean", "wspd_max", "strong_hours"])
    soil = _cached("gldas_soil_monthly_box_mean.csv")[
        ["time", "vol_m3m3_approx"]].rename(columns={"time": "month"})
    bsi = _cached("modis_sand_bsi_monthly.csv")[
        ["date", "bsi_mean"]].rename(columns={"date": "month"})
    # normalise every month key to the 1st of the month (BSI snapshots sit mid-month)
    out = []
    for part in (rain, wind, soil, bsi):
        part = part.copy()
        part["month"] = pd.to_datetime(part["month"]).dt.to_period("M").dt.to_timestamp()
        out.append(part)
    rain, wind, soil, bsi = out
    m = rain.merge(soil, on="month", how="outer")
    m = m.merge(wind, on="month", how="outer")
    m = m.merge(bsi, on="month", how="outer")
    return m.sort_values("month").reset_index(drop=True)


def _scatter_fit(ax, d: pd.DataFrame, x: str, y: str, xlabel: str, ylabel: str,
                 color=BLUE) -> None:
    d = d.dropna(subset=[x, y])
    sns.regplot(data=d, x=x, y=y, ax=ax, ci=95, scatter_kws={"s": 48, "alpha": 0.8,
                "color": color, "edgecolor": "white"},
                line_kws={"color": RED, "lw": 2.0})
    r, p = pearsonr(d[x], d[y])
    ax.text(0.04, 0.93, f"r = {r:+.2f}   p = {p:.3g}   n = {len(d)}",
            transform=ax.transAxes, fontsize=11, fontweight="bold",
            color="#222222", va="top",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#BBBBBB", alpha=0.9))
    tidy(ax, xlabel, ylabel)


def compare_rain_vs_soil() -> None:
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "rain_mm", "vol_m3m3_approx",
                 "Monthly rainfall (mm month$^{-1}$)",
                 "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)")
    save_comparison(fig, "rain_vs_soil_moisture_scatter",
                    "Rainfall vs root-zone soil moisture (monthly, 2022-2026)",
                    "Each point is one month; the fitted line carries a 95% confidence band "
                    "and the Pearson correlation is shown in the box.", 
                    "power_monthly_rain_anomalies.csv + gldas_soil_monthly_box_mean.csv")


def compare_rain_vs_bsi() -> None:
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "rain_mm", "bsi_mean", "Monthly rainfall (mm month$^{-1}$)",
                 "Bare Soil Index (BSI, -)", color=ORANGE)
    save_comparison(fig, "rain_vs_sand_bsi_scatter",
                    "Rainfall vs bare-surface (sand) signal, monthly",
                    "Weak rain-BSI coupling is expected in a hyper-arid site (about -0.15 in "
                    "the team's first check): treat as a lead, not a proof.",
                    "power_monthly_rain_anomalies.csv + modis_sand_bsi_monthly.csv")


def compare_soil_vs_bsi() -> None:
    """Soil moisture vs vegetation/bare-ground proxy."""
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "vol_m3m3_approx", "bsi_mean",
                 "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)",
                 "Bare Soil Index (BSI, -) - inverse vegetation cover", color=GREEN)
    save_comparison(fig, "soil_moisture_vs_vegetation_bsi_scatter",
                    "Soil moisture vs vegetation cover proxy (BSI)",
                    "BSI rises as bare ground increases, so it acts as the inverse of green "
                    "cover: wetter months should sit toward lower BSI.",
                    "gldas_soil_monthly_box_mean.csv + modis_sand_bsi_monthly.csv")


def compare_wind_vs_bsi() -> None:
    """Wind vs sand movement proxy."""
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "wspd_mean", "bsi_mean",
                 "Mean wind speed (m s$^{-1}$)",
                 "Bare Soil Index / sand-movement proxy (BSI, -)", color=SKY)
    save_comparison(fig, "wind_vs_sand_movement_bsi_scatter",
                    "Wind speed vs sand-movement proxy (monthly means)",
                    "Months with stronger mean wind are tested against the MODIS bare-soil "
                    "signal; only the overlapping 2025-2026 months exist for both series.",
                    "merra2_wind_daily_box_mean.csv + modis_sand_bsi_monthly.csv")


def compare_wind_vs_rain() -> None:
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "wspd_mean", "rain_mm",
                 "Mean wind speed (m s$^{-1}$)",
                 "Monthly rainfall (mm month$^{-1}$)", color=SKY)
    save_comparison(fig, "wind_vs_rain_scatter",
                    "Wind speed vs rainfall (monthly means)",
                    "Tests whether windier months are wetter or drier; only the 2025-2026 "
                    "overlap of the two records is available for the fit.",
                    "merra2_wind_daily_box_mean.csv + power_monthly_rain_anomalies.csv")


def compare_correlation_heatmap() -> None:
    m = _monthly_frame()
    cols = {"rain_mm": "Rainfall (mm)",
            "anomaly_mm": "Rain anomaly (mm)",
            "vol_m3m3_approx": "Soil moisture (m3/m3)",
            "wspd_mean": "Wind speed (m/s)",
            "wspd_max": "Gust (m/s)",
            "strong_hours": "Strong-wind hours",
            "bsi_mean": "Bare Soil Index"}
    sub = m[list(cols)].rename(columns=cols)
    corr = sub.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(9.5, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="RdBu_r", center=0, vmin=-1, vmax=1,
                square=True, linewidths=0.6, cbar_kws={"label": "Pearson r"},
                annot_kws={"fontsize": 10}, ax=ax)
    ax.set_title("")
    save_comparison(fig, "environment_correlation_matrix",
                    "Multi-variable correlation matrix (monthly)",
                    "Pearson correlations between rain, wind, soil moisture and the bare-soil "
                    "proxy on their month overlap; sample sizes differ per pair.",
                    "power_monthly_rain_anomalies.csv, merra2_wind_daily_box_mean.csv, "
                    "gldas_soil_monthly_box_mean.csv, modis_sand_bsi_monthly.csv")


def compare_dual_axis_timeseries() -> None:
    m = _monthly_frame().dropna(subset=["rain_mm", "vol_m3m3_approx"])
    fig, ax = plt.subplots()
    ax.bar(m["month"], m["rain_mm"], width=24, color=SKY, alpha=0.85,
           label="Rainfall (mm month$^{-1}$, left)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Rainfall (mm month$^{-1}$)")
    ax.set_ylim(bottom=0)
    date_axis(ax)
    ax2 = ax.twinx()
    ax2.plot(m["month"], m["vol_m3m3_approx"], color=RED, lw=2.2, marker="o", ms=4,
             label="Soil moisture (m$^3$ m$^{-3}$, right)")
    ax2.set_ylabel("Soil moisture (m$^3$ m$^{-3}$)")
    ax2.grid(False)
    r, p = pearsonr(m["rain_mm"], m["vol_m3m3_approx"])
    ax.text(0.02, 0.93, f"Pearson r = {r:+.2f}  (n = {len(m)} months)",
            transform=ax.transAxes, fontsize=10.5, fontweight="bold", va="top",
            bbox=dict(boxstyle="round,pad=0.35", fc="white", ec="#BBBBBB", alpha=0.9))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper right")
    tidy(ax)
    save_comparison(fig, "rain_soil_moisture_dual_axis_timeseries",
                    "Dual-axis time series: rainfall and soil moisture",
                    "Rain bars (left axis) against root-zone soil moisture (right axis), "
                    "2022-2026: spikes of rain are followed by a visible moisture response.",
                    "power_monthly_rain_anomalies.csv + gldas_soil_monthly_box_mean.csv")


def compare_small_multiples() -> None:
    rain = _cached("power_monthly_rain_anomalies.csv")
    wind = monthly_mean(_cached("merra2_wind_daily_box_mean.csv"), "time",
                        ["wspd_mean"])
    soil = _cached("gldas_soil_monthly_box_mean.csv")
    bsi = _cached("modis_sand_bsi_monthly.csv")

    fig, axes = plt.subplots(4, 1, figsize=(12, 12), sharex=True)
    specs = [
        (rain, "date", "rain_mm", "Rainfall (mm month$^{-1}$)", BLUE, "bar"),
        (wind, "month", "wspd_mean", "Wind speed (m s$^{-1}$)", ORANGE, "line"),
        (soil, "time", "vol_m3m3_approx", "Soil moisture (m$^3$ m$^{-3}$)", GREEN, "line"),
        (bsi, "date", "bsi_mean", "Bare Soil Index (-)", RED, "line"),
    ]
    for ax, (d, xc, yc, ylabel, col, kind) in zip(axes, specs):
        if kind == "bar":
            ax.bar(d[xc], d[yc], width=24, color=col, alpha=0.85)
        else:
            s = d.set_index(xc)[yc].sort_index()
            s = break_gaps(s, "120D")
            ax.plot(s.index, s.values, color=col, marker="o", ms=3.5, lw=1.3)
            roll = s.rolling(6, min_periods=1).mean()
            ax.plot(roll.index, roll.values, color="#333333", lw=1.6, alpha=0.8,
                    label="6-month mean")
            ax.legend(loc="upper right", fontsize=8)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.grid(True, **GRID_KW)
        sns.despine(ax=ax)
    axes[0].set_title("Rainfall", loc="left", fontsize=10, fontweight="bold")
    axes[1].set_title("Wind speed", loc="left", fontsize=10, fontweight="bold")
    axes[2].set_title("Soil moisture", loc="left", fontsize=10, fontweight="bold")
    axes[3].set_title("Bare Soil Index (sand/vegetation proxy)", loc="left",
                      fontsize=10, fontweight="bold")
    date_axis(axes[-1])
    axes[-1].set_xlabel("Date")
    fig.subplots_adjust(hspace=0.25)
    save_comparison(fig, "aligned_small_multiples_environment",
                    "Four environmental series on one aligned time axis",
                    "Small multiples sharing the same x-axis so rain, wind, soil moisture and "
                    "bare surface can be read together; gaps show missing coverage.",
                    "power_monthly_rain_anomalies.csv, merra2_wind_daily_box_mean.csv, "
                    "gldas_soil_monthly_box_mean.csv, modis_sand_bsi_monthly.csv")


WATER_STRATEGY = {
    "Phreatophyte / Physical Protection": "Deep-water access (phreatophyte)",
    "Oasis Phreatophyte": "Deep-water access (phreatophyte)",
    "Xerophytic / Drought Resistance": "Drought conservation (xerophyte)",
    "Succulence / C4 Photosynthesis": "Drought conservation (xerophyte)",
    "Drought Deciduous": "Drought conservation (xerophyte)",
    "Halophytic / Salt Excretion": "Salt tolerance (halophyte)",
}


def compare_plant_vs_soil_moisture() -> None:
    plants = _cached("morocco_merzouga_plant_adaptations.csv")
    soil = _cached("gldas_soil_monthly_box_mean.csv")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6),
                                   gridspec_kw={"width_ratios": [1, 1.1]})

    # left: the moisture regime the plants must survive
    sns.histplot(soil["vol_m3m3_approx"], bins=25, kde=True, color=GREEN, ax=ax1,
                 edgecolor="white")
    mean_v = soil["vol_m3m3_approx"].mean()
    ax1.axvline(mean_v, color=RED, ls="--", lw=1.6)
    ax1.text(mean_v, ax1.get_ylim()[1] * 0.95,
             f" mean {mean_v:.2f}", color=RED, fontsize=9, va="top")
    tidy(ax1, "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)", "Months")
    ax1.set_title("A. Root-zone moisture regime (GLDAS, 2010-2026)", loc="left",
                  fontsize=11, fontweight="bold")

    # right: species grouped by water-uptake strategy
    plants = plants.copy()
    plants["strategy"] = plants["Adaptation Category"].map(WATER_STRATEGY)
    groups = plants.groupby("strategy")["Common Name"].apply(list)
    colors = {"Deep-water access (phreatophyte)": BLUE,
              "Drought conservation (xerophyte)": ORANGE,
              "Salt tolerance (halophyte)": GREEN}
    ypos = np.arange(len(groups))[::-1]
    ax2.barh(ypos, [len(v) for v in groups.values],
             color=[colors.get(k, SKY) for k in groups.index], edgecolor="white")
    for y, (k, sp) in zip(ypos, groups.items()):
        ax2.text(len(sp) + 0.06, y, "; ".join(sp), va="center", fontsize=8.5,
                 color="#333333")
    ax2.set_yticks(ypos)
    ax2.set_yticklabels([textwrap.fill(k, 26) for k in groups.index], fontsize=9)
    ax2.set_xlim(0, 3.6)
    tidy(ax2, "Number of species", "Water-uptake strategy")
    ax2.set_title("B. Species per water-uptake strategy (plant list)", loc="left",
                  fontsize=11, fontweight="bold")
    save_comparison(fig, "plant_adaptation_vs_soil_moisture",
                    "Plant adaptation strategies vs soil moisture regime",
                    "Panel A: the 0-10 cm moisture distribution the flora lives in. Panel B: "
                    "how the documented species are split between deep-water access, "
                    "drought conservation and salt tolerance. Qualitative linkage - no "
                    "per-species numeric soil data exists, so the panels are compared by "
                    "regime, not by correlation.",
                    "morocco_merzouga_plant_adaptations.csv + gldas_soil_monthly_box_mean.csv")


def compare_plant_vs_wind() -> None:
    plants = _cached("morocco_merzouga_plant_adaptations.csv")
    wind = _cached("merra2_wind_daily_box_mean.csv").dropna(subset=["time"])
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 6),
                                   gridspec_kw={"width_ratios": [1.1, 1]})

    # left: wind regime by calendar month
    tmp = wind.copy()
    tmp["month"] = tmp["time"].dt.month
    by = tmp.groupby("month")["wspd_mean"].agg(["mean", lambda s: s.quantile(0.95)])
    by.columns = ["mean", "p95"]
    ax1.plot(by.index, by["mean"], marker="o", color=ORANGE, lw=2.2,
             label="Mean wind speed")
    ax1.plot(by.index, by["p95"], marker="s", color=BLUE, lw=1.8, ls="--",
             label="95th percentile")
    ax1.fill_between(by.index, by["mean"], by["p95"], color=SKY, alpha=0.25)
    ax1.set_xticks(range(1, 13))
    ax1.set_xticklabels(MONTH_LABELS)
    tidy(ax1, "Calendar month", "Wind speed (m s$^{-1}$)")
    ax1.legend(loc="upper right")
    ax1.set_title("A. Wind regime at Merzouga (MERRA-2)", loc="left",
                  fontsize=11, fontweight="bold")

    # right: wind/sand-relevant traits found in the plant descriptions
    text = (plants["Specific Adaptations"].fillna("") + " " +
            plants["Leaf Structure"].fillna("")).str.lower()
    wind_keys = {
        "Wind / sand anchoring": ["high winds", "sandy soil", "binds loose"],
        "Reduced leaf area (less drag)": ["bipinnate leaflets", "scale-like",
                                          "minute leaves", "rudimentary", "very small"],
        "Flexible / tough leaves": ["tough", "fibrous", "waxy cuticle", "leathery"],
    }
    counts = {k: int(sum(any(w in t for w in ws) for t in text))
              for k, ws in wind_keys.items()}
    ypos = np.arange(len(counts))[::-1]
    ax2.barh(ypos, counts.values(), color=[RED, BLUE, GREEN],
             edgecolor="white", height=0.55)
    for y, (k, n) in zip(ypos, counts.items()):
        ax2.text(n + 0.05, y, f"{n} species", va="center", fontsize=9.5,
                 color="#333333")
    ax2.set_yticks(ypos)
    ax2.set_yticklabels(list(counts.keys()), fontsize=9.5)
    ax2.set_xlim(0, max(counts.values()) + 1.6)
    tidy(ax2, "Number of species", "Wind-relevant documented trait")
    ax2.set_title("B. Wind-relevant traits in the plant list", loc="left",
                  fontsize=11, fontweight="bold")
    save_comparison(fig, "plant_adaptation_vs_wind",
                    "Plant adaptations vs the Merzouga wind regime",
                    "Panel A: monthly mean and 95th-percentile wind speed. Panel B: how many "
                    "documented species carry wind/sand-relevant traits (keyword scan). "
                    "Qualitative linkage - trait keyword counts are read against the measured "
                    "wind regime: small/tough leaves and sand-anchoring roots match the windy "
                    "season.",
                    "morocco_merzouga_plant_adaptations.csv + merra2_wind_daily_box_mean.csv")


def compare_wind_vs_soil_moisture() -> None:
    m = _monthly_frame()
    fig, ax = plt.subplots()
    _scatter_fit(ax, m, "wspd_mean", "vol_m3m3_approx",
                 "Mean wind speed (m s$^{-1}$)",
                 "Soil moisture 0-10 cm (m$^3$ m$^{-3}$)", color=SKY)
    save_comparison(fig, "wind_vs_soil_moisture_scatter",
                    "Wind speed vs soil moisture (monthly means)",
                    "Windier months are checked against root-zone moisture (wind-driven "
                    "evaporation link); only the 2025-2026 overlap is available.",
                    "merra2_wind_daily_box_mean.csv + gldas_soil_monthly_box_mean.csv")


COMPARISON_ROUTINES = [
    compare_rain_vs_soil,
    compare_rain_vs_bsi,
    compare_soil_vs_bsi,
    compare_wind_vs_bsi,
    compare_wind_vs_rain,
    compare_wind_vs_soil_moisture,
    compare_correlation_heatmap,
    compare_dual_axis_timeseries,
    compare_small_multiples,
    compare_plant_vs_soil_moisture,
    compare_plant_vs_wind,
]


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------
def main() -> None:
    setup_theme()
    IND_DIR.mkdir(parents=True, exist_ok=True)
    CMP_DIR.mkdir(parents=True, exist_ok=True)

    csv_files = sorted(DATA_DIR.glob("*.csv"))
    if not csv_files:
        print(f"No CSV files found in {DATA_DIR}")
        return

    print(f"Found {len(csv_files)} CSV files in {DATA_DIR.name}/\n")
    print("=" * 78)
    print("INDIVIDUAL VISUALIZATIONS")
    print("=" * 78)

    for path in csv_files:
        stem = path.stem
        if stem in SKIP_FILES:
            print(f"  {path.name}")
            print(f"      charts : (none)")
            print(f"      why    : {CHART_REASON[stem]}")
            continue
        try:
            df = load_csv(path.name)
        except Exception as exc:  # keep going with the other files
            print(f"[skip] {path.name}: could not load ({exc})")
            continue
        routines = CHART_ROUTINES.get(stem)
        if routines is None:
            print(f"[info] {path.name}: no dedicated routine -> generic chart")
            routines = [lambda d, s=stem: plot_generic(d, s)]
        made = []
        for fn in routines:
            try:
                made.extend(fn(df))
            except Exception as exc:
                print(f"[warn] {path.name}: {fn.__name__} failed ({exc})")
        reason = CHART_REASON.get(stem, "generic fallback chart")
        if not made:
            print(f"[skip] {path.name}: no chart produced")
            continue
        print(f"  {path.name}")
        print(f"      charts : {', '.join(made)}")
        print(f"      why    : {reason}")

    print()
    print("=" * 78)
    print("COMPARISON VISUALIZATIONS")
    print("=" * 78)
    done = []
    for fn in COMPARISON_ROUTINES:
        try:
            fn()
            done.append(fn.__name__.replace("compare_", "").replace("_", " "))
        except Exception as exc:
            print(f"[warn] comparison {fn.__name__} failed ({exc})")
    for name in done:
        print(f"  - {name}")
    print(f"\nSaved to:\n  {IND_DIR}\n  {CMP_DIR}")
    print(f"\nTotal PNGs: {len(list(IND_DIR.glob('*.png')))} individual, "
          f"{len(list(CMP_DIR.glob('*.png')))} comparisons")


if __name__ == "__main__":
    main()
