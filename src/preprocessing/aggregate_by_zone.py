"""
aggregate_by_zone.py
=====================
Aggregates per-city daily weather data into climate-zone–level daily summaries.

Reduces 165-city × N-day noise into 5-zone × N-day signal using four grouping
schemes:

    koppen       5 zones   Arid_West / Humid_Subtropical_N / Mountain_N /
                           Tropical_Wet_E / Tropical_WetDry_S
    monsoon_zone 5 zones   Early_SW / Central_SW / Late_SW / Arid_Late /
                           NE_Monsoon
    imd_zone    24 zones   IMD meteorological subdivisions
    agri_zone    6 zones   Kharif_Dom / Rabi_Dom / Kharif_Rabi /
                           Year_Round / Arid_Irrigated / Mountain

For each (date, zone) group the aggregation computes:
  mean, median, std for every numeric weather variable
  count   = number of cities that contributed
  city_list = comma-joined city names in that zone × day

Usage
-----
    python src/preprocessing/aggregate_by_zone.py
    python src/preprocessing/aggregate_by_zone.py --input data/weather_india_combined.csv
    python src/preprocessing/aggregate_by_zone.py --zones koppen monsoon_zone
    python src/preprocessing/aggregate_by_zone.py --out-dir data/zone_summaries

Outputs (default: data/)
-----------------------
    data/weather_zone_koppen.csv
    data/weather_zone_monsoon.csv
    data/weather_zone_imd.csv
    data/weather_zone_agri.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Make sure project src is importable when running as a script
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_PROJECT_ROOT / "src" / "data_collection"))

import pandas as pd
import numpy as np
from india_locations import INDIA_LOCATIONS, as_dataframe as locations_df

# ── Config ────────────────────────────────────────────────────────────────────

DEFAULT_INPUT     = _PROJECT_ROOT / "data" / "weather_india_combined.csv"
DEFAULT_OUT_DIR   = _PROJECT_ROOT / "data"

ZONE_FIELDS: dict[str, str] = {
    "koppen":       "weather_zone_koppen.csv",
    "monsoon_zone": "weather_zone_monsoon.csv",
    "imd_zone":     "weather_zone_imd.csv",
    "agri_zone":    "weather_zone_agri.csv",
}

# Columns that are NOT numeric weather variables
NON_WEATHER_COLS = {
    "date", "city", "state", "state_code", "district",
    "latitude", "longitude", "season_meteo", "season_india",
    "weather_category", "data_source",
    # zone cols added during join
    "koppen", "monsoon_zone", "imd_zone", "agri_zone",
}

# ── Core helpers ──────────────────────────────────────────────────────────────

def load_weather(path: Path) -> pd.DataFrame:
    """Load the combined weather CSV; parse date column."""
    print(f"[load] Reading {path} …")
    df = pd.read_csv(path, parse_dates=["date"], low_memory=False)
    print(f"       {len(df):,} rows | {df['date'].min().date()} → {df['date'].max().date()}")
    print(f"       Cities: {sorted(df['city'].unique())}")
    return df


def join_zone_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """
    Left-join zone metadata from india_locations onto the weather DataFrame.
    Matching key: lowercase(city).
    """
    meta = locations_df()[["city", "koppen", "monsoon_zone", "imd_zone", "agri_zone"]].copy()
    meta["_city_key"] = meta["city"].str.lower().str.strip()
    df["_city_key"]   = df["city"].str.lower().str.strip()

    before = len(df)
    df = df.merge(meta.drop(columns="city"), on="_city_key", how="left")
    df.drop(columns="_city_key", inplace=True)

    unmatched = df[df["koppen"].isna()]["city"].unique()
    if len(unmatched):
        print(f"[warn] {len(unmatched)} cities had no zone metadata: {list(unmatched)}")
    print(f"[join] Zone metadata joined  ({before:,} rows preserved)")
    return df


def get_numeric_vars(df: pd.DataFrame, zone_col: str) -> list[str]:
    """Return numeric weather variable names (excluding group keys + metadata)."""
    skip = NON_WEATHER_COLS | {zone_col}
    return [
        c for c in df.select_dtypes(include=[np.number]).columns
        if c not in skip
    ]


def aggregate_zone(
    df: pd.DataFrame,
    zone_col: str,
    out_path: Path,
) -> pd.DataFrame:
    """
    Group by (date, zone_col) and compute mean/median/std for all numeric vars.
    Also keeps count and city_list columns.
    """
    print(f"\n[agg]  Zone: {zone_col}  →  {out_path.name}")

    # drop rows without zone info
    valid = df.dropna(subset=[zone_col])
    dropped = len(df) - len(valid)
    if dropped:
        print(f"       Dropped {dropped} rows with null {zone_col}")

    num_vars = get_numeric_vars(valid, zone_col)
    print(f"       Numeric vars: {len(num_vars)}")

    grouped = valid.groupby(["date", zone_col])

    # -- aggregations for numeric columns ------
    agg_dict: dict[str, list] = {v: ["mean", "median", "std"] for v in num_vars}
    result = grouped.agg(agg_dict)

    # flatten multi-level column names: temp_2m_max_mean, temp_2m_max_std …
    result.columns = ["_".join(col).strip() for col in result.columns]
    result.reset_index(inplace=True)

    # -- count + city_list ----------------------
    extra = grouped.agg(
        city_count=("city", "count"),
        city_list=("city", lambda x: ",".join(sorted(x.unique()))),
    ).reset_index()

    result = result.merge(extra, on=["date", zone_col])

    # -- categorical mode for string weather cols ----
    def _safe_mode(x):
        m = x.dropna().mode()
        return m.iloc[0] if len(m) > 0 else pd.NA

    for cat_col in ("season_meteo", "season_india", "weather_category"):
        if cat_col in valid.columns:
            mode_df = (
                valid.groupby(["date", zone_col])[cat_col]
                .agg(_safe_mode)
                .reset_index()
                .rename(columns={cat_col: f"{cat_col}_mode"})
            )
            result = result.merge(mode_df, on=["date", zone_col], how="left")

    result.sort_values(["date", zone_col], inplace=True)

    zones_found = result[zone_col].nunique()
    print(f"       Output : {len(result):,} rows  |  {zones_found} zones  |  "
          f"{result['date'].min().date()} → {result['date'].max().date()}")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_path, index=False)
    print(f"       Saved  → {out_path}")
    return result


def add_zone_onset_features(
    df: pd.DataFrame,
    zone_col: str = "monsoon_zone",
) -> pd.DataFrame:
    """
    For the monsoon_zone aggregated frame, append boolean flags:
        in_monsoon_onset_window, in_monsoon_withdrawal_window
    based on MONSOON_ONSET_WINDOW and MONSOON_WITHDRAWAL_WINDOW dicts.
    """
    try:
        from india_locations import MONSOON_ONSET_WINDOW, MONSOON_WITHDRAWAL_WINDOW
    except ImportError:
        return df

    if zone_col not in df.columns:
        return df

    df = df.copy()
    df["_doy"] = pd.to_datetime(df["date"]).dt.day_of_year

    def _in_window(row, windows: dict) -> bool:
        w = windows.get(row[zone_col])
        if w is None:
            return False
        return w[0] <= row["_doy"] <= w[1]

    df["in_monsoon_onset_window"]      = df.apply(_in_window, axis=1, windows=MONSOON_ONSET_WINDOW)
    df["in_monsoon_withdrawal_window"] = df.apply(_in_window, axis=1, windows=MONSOON_WITHDRAWAL_WINDOW)
    df.drop(columns="_doy", inplace=True)
    return df


# ── Pipeline ─────────────────────────────────────────────────────────────────

def run(
    input_path: Path,
    out_dir: Path,
    zones: list[str],
) -> dict[str, pd.DataFrame]:
    """Full pipeline: load → join zones → aggregate each zone type → save."""

    df = load_weather(input_path)
    df = join_zone_metadata(df)

    results: dict[str, pd.DataFrame] = {}
    for zone_col in zones:
        out_file = ZONE_FIELDS.get(zone_col, f"weather_zone_{zone_col}.csv")
        out_path = out_dir / out_file
        agg_df   = aggregate_zone(df, zone_col, out_path)

        # add monsoon window flags for monsoon_zone aggregation
        if zone_col == "monsoon_zone":
            agg_df = add_zone_onset_features(agg_df, zone_col)
            agg_df.to_csv(out_path, index=False)
            print(f"       (+ monsoon window flags, re-saved)")

        results[zone_col] = agg_df

    print("\n✅  All done.")
    return results


# ── CLI ───────────────────────────────────────────────────────────────────────

def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Aggregate per-city weather data into climate-zone summaries."
    )
    p.add_argument(
        "--input",
        default=str(DEFAULT_INPUT),
        help=f"Combined city weather CSV (default: {DEFAULT_INPUT})",
    )
    p.add_argument(
        "--zones",
        nargs="+",
        default=list(ZONE_FIELDS.keys()),
        choices=list(ZONE_FIELDS.keys()),
        help="Which zone types to aggregate (default: all four)",
    )
    p.add_argument(
        "--out-dir",
        default=str(DEFAULT_OUT_DIR),
        help=f"Output directory (default: {DEFAULT_OUT_DIR})",
    )
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(
        input_path=Path(args.input),
        out_dir=Path(args.out_dir),
        zones=args.zones,
    )
