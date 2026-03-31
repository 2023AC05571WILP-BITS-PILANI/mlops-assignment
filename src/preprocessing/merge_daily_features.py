#!/usr/bin/env python3
"""
merge_daily_features.py
========================
Joins calendar features and weather observations into a single daily CSV.

The calendar backbone (one row per day, 2010-2030) is always the LEFT side
of the join.  Weather data is joined ON `date`.  Days without weather
observations keep NaN in the weather columns — downstream models can decide
how to handle missingness (impute, drop, or use a mask).

Controlled entirely by ``params.yaml`` at the project root:

    merge:
      calendar_csv : data/calendar_features_daily.csv
      weather_csv  : data/weather_daily.csv
      output_csv   : data/daily_combined.csv
      join_type    : left        # left | inner
      drop_duplicate_cols:       # columns present in BOTH CSVs to drop
        - year_norm              #   from the weather side

Usage
-----
    python src/preprocessing/merge_daily_features.py
    python src/preprocessing/merge_daily_features.py --params params.yaml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PARAMS = PROJECT_ROOT / "params.yaml"


def load_params(params_path: Path) -> dict:
    """Load the ``merge`` section from params.yaml."""
    with open(params_path, encoding="utf-8") as fh:
        all_params = yaml.safe_load(fh)
    return all_params.get("merge", {})


def merge(
    calendar_path: Path,
    weather_path: Path,
    output_path: Path,
    join_type: str = "left",
    drop_dup_cols: list[str] | None = None,
) -> pd.DataFrame:
    """
    Merge calendar and weather CSVs on ``date``.

    Parameters
    ----------
    calendar_path : path to calendar_features_daily.csv
    weather_path  : path to weather_daily.csv
    output_path   : where to write the merged CSV
    join_type     : 'left' keeps every calendar day; 'inner' keeps only days
                    where weather exists
    drop_dup_cols : columns to drop from the weather side before merging
                    (avoids duplicate columns like year_norm that exist in both)
    """
    print(f"[merge] Loading calendar : {calendar_path}")
    cal = pd.read_csv(calendar_path, parse_dates=["date"])
    print(f"        → {len(cal):,} rows  ×  {len(cal.columns)} cols  "
          f"({cal['date'].min().date()} → {cal['date'].max().date()})")

    print(f"[merge] Loading weather  : {weather_path}")
    wx = pd.read_csv(weather_path, parse_dates=["date"])
    print(f"        → {len(wx):,} rows  ×  {len(wx.columns)} cols  "
          f"({wx['date'].min().date()} → {wx['date'].max().date()})")

    # Drop columns from weather that already exist in calendar
    drop_dup_cols = drop_dup_cols or []
    # Also auto-detect any overlapping columns (besides 'date') and warn
    overlap = set(cal.columns) & set(wx.columns) - {"date"}
    if overlap:
        auto_drop = overlap - set(drop_dup_cols)
        if auto_drop:
            print(f"[merge] ⚠  Overlapping columns auto-dropped from weather: {sorted(auto_drop)}")
            drop_dup_cols = list(set(drop_dup_cols) | auto_drop)

    wx = wx.drop(columns=[c for c in drop_dup_cols if c in wx.columns], errors="ignore")

    print(f"[merge] Join type: {join_type}")
    merged = cal.merge(wx, on="date", how=join_type, suffixes=("", "_weather"))

    # Report coverage
    weather_cols = [c for c in merged.columns if c in wx.columns or c.endswith("_weather")]
    if weather_cols:
        filled = merged[weather_cols[0]].notna().sum()
        total = len(merged)
        print(f"[merge] Weather coverage: {filled:,}/{total:,} days "
              f"({100*filled/total:.1f}%)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(output_path, index=False)
    print(f"[merge] Saved → {output_path}  "
          f"({len(merged):,} rows × {len(merged.columns)} cols)")
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge calendar + weather into daily_combined.csv")
    parser.add_argument("--params", default=str(DEFAULT_PARAMS), help="Path to params.yaml")
    args = parser.parse_args()

    params = load_params(Path(args.params))
    if not params:
        print("[merge] ERROR: No 'merge' section found in params.yaml", file=sys.stderr)
        sys.exit(1)

    merge(
        calendar_path=PROJECT_ROOT / params["calendar_csv"],
        weather_path=PROJECT_ROOT / params["weather_csv"],
        output_path=PROJECT_ROOT / params["output_csv"],
        join_type=params.get("join_type", "left"),
        drop_dup_cols=params.get("drop_duplicate_cols", []),
    )


if __name__ == "__main__":
    main()
