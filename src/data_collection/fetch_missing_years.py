"""
fetch_missing_years.py
======================
Targeted retry script: fetches only the years missing from each city CSV,
one city at a time with a longer inter-request delay to avoid HTTP 429s.

Usage
-----
    python src/data_collection/fetch_missing_years.py
    python src/data_collection/fetch_missing_years.py --years 2010 2011 2012 2013 2014
    python src/data_collection/fetch_missing_years.py --state "Tamil Nadu" --years 2010 2014
    python src/data_collection/fetch_missing_years.py --delay 5
"""
from __future__ import annotations

import argparse
import sys
import time
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src" / "data_collection"))

import pandas as pd
from fetch_weather import (
    INDIA_DIR, INDIA_COMBINED,
    fetch_archive_batch, add_derived_features, _merge_india_csvs,
)
from india_locations import INDIA_LOCATIONS, get_locations_by_state, city_slug


def _complete_years(fp: Path) -> set[int]:
    """Return set of years with a full 365/366 days in the CSV."""
    if not fp.exists():
        return set()
    df = pd.read_csv(fp, usecols=["date"], parse_dates=["date"])
    counts = df["date"].dt.year.value_counts()
    complete = set()
    for yr, cnt in counts.items():
        expected = 366 if (yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)) else 365
        if cnt >= expected:
            complete.add(int(yr))
    return complete


def fetch_missing(
    locations: list[dict],
    years: list[int],
    delay: float = 3.0,
) -> None:
    INDIA_DIR.mkdir(parents=True, exist_ok=True)

    for loc in locations:
        slug = city_slug(loc)
        fp   = INDIA_DIR / f"{slug}.csv"
        print(f"\n── {loc['city']} ({loc['state']}) ──")

        existing       = pd.read_csv(fp, parse_dates=["date"]) if fp.exists() else pd.DataFrame()
        complete_yrs   = _complete_years(fp)
        to_fetch       = [y for y in years if y not in complete_yrs]

        if not to_fetch:
            print(f"  All requested years already complete, skip.")
            continue

        print(f"  Missing years: {to_fetch}")
        new_chunks: list[pd.DataFrame] = []

        for yr in to_fetch:
            start = date(yr, 1, 1)
            end   = date(yr, 12, 31)
            print(f"  {yr} … ", end="", flush=True)
            try:
                chunk = fetch_archive_batch([loc], start, end)
                if len(chunk):
                    chunk = add_derived_features(chunk)
                    new_chunks.append(chunk)
                    print(f"✓  {len(chunk)} rows")
                else:
                    print("empty response")
            except RuntimeError as exc:
                print(f"✗  {exc}")
            time.sleep(delay)

        if new_chunks:
            merged = pd.concat(
                ([existing] if len(existing) else []) + new_chunks,
                ignore_index=True,
            )
            id_cols = ["date", "city", "state", "state_code", "district", "latitude", "longitude"]
            merged = (
                merged
                .drop_duplicates(subset=["date", "city"])
                .sort_values("date")
                .reset_index(drop=True)
            )
            other_cols = [c for c in merged.columns if c not in id_cols]
            merged = merged[[c for c in id_cols if c in merged.columns] + other_cols]
            merged.to_csv(fp, index=False)
            print(f"  → saved {len(merged):,} total rows to {fp.name}")

    print("\nMerging all city CSVs …")
    _merge_india_csvs(INDIA_DIR, INDIA_COMBINED)
    print("✅  Done.")


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fetch only missing years for city CSVs.")
    p.add_argument("--years",  nargs="+", type=int, default=list(range(2010, 2031)),
                   help="Years to check/fetch (default: 2010-2030)")
    p.add_argument("--state",  default=None, help="Limit to one state (default: all)")
    p.add_argument("--delay",  type=float, default=3.0,
                   help="Seconds to wait between API calls (default: 3)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    locs = get_locations_by_state(args.state) if args.state else INDIA_LOCATIONS
    if not locs:
        print(f"No locations found for state: {args.state!r}")
        sys.exit(1)
    print(f"Locations : {len(locs)}  |  Years to check: {args.years}  |  Delay: {args.delay}s")
    fetch_missing(locs, args.years, delay=args.delay)
