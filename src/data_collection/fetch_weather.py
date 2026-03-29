#!/usr/bin/env python3
"""
Weather Data Collection Service
================================
Fetches daily weather for every day from 2010-01-01 to 2030-12-31
using Open-Meteo — completely FREE, no API key required.

Two APIs are stitched together seamlessly
------------------------------------------
  Open-Meteo Archive API  (ERA5 reanalysis)
      URL   : https://archive-api.open-meteo.com/v1/archive
      Range : 2010-01-01  →  ~7 days ago          ← real observations
      Model : ERA5 (0.25° / ~25 km, 1940–present)

  Open-Meteo Climate API  (CMIP6 projections)
      URL   : https://climate-api.open-meteo.com/v1/climate
      Range : ~7 days ago  →  2030-12-31           ← model projection
      Model : MRI-AGCM3-2-S  (20 km, Japan MRI, full variable coverage)

Default location : New Delhi, India (28.6139°N, 77.2090°E)
  — matches the Indian festival calendar in data/calendar-events/

Variables fetched
------------------
  Archive                          Climate projection
  ──────────────────────────────   ──────────────────────────────────────
  temperature_2m_max (°C)          temperature_2m_max (°C)
  temperature_2m_min (°C)          temperature_2m_min (°C)
  temperature_2m_mean (°C)         temperature_2m_mean (°C)
  apparent_temperature_max (°C)    precipitation_sum (mm)
  apparent_temperature_min (°C)    rain_sum (mm)
  precipitation_sum (mm)           snowfall_sum (cm)
  rain_sum (mm)                    wind_speed_10m_max (km/h)
  snowfall_sum (cm)                wind_speed_10m_mean (km/h)
  wind_speed_10m_max (km/h)        shortwave_radiation_sum (MJ/m²)
  wind_gusts_10m_max (km/h)        relative_humidity_2m_mean (%)
  wind_direction_10m_dominant (°)  pressure_msl_mean (hPa)
  weather_code (WMO)
  daylight_duration (s)
  sunshine_duration (s)
  shortwave_radiation_sum (MJ/m²)
  et0_fao_evapotranspiration (mm)

Derived features added automatically
--------------------------------------
  temp_range            max - min  (diurnal variation)
  day_length_hours      daylight_duration / 3600
  sunshine_hours        sunshine_duration / 3600
  season_meteo          Meteorological season  (4 seasons, NH)
  season_india          Indian 6-season Ritu system
  is_rainy_day          precipitation_sum > 1 mm  (0/1)
  is_hot_day            temperature_2m_max > 35°C  (0/1)
  is_cold_day           temperature_2m_min < 10°C  (0/1)
  weather_category      Human-readable WMO code group
  uv_risk               Low / Moderate / High / Very High / Extreme
  data_source           "archive" or "climate_projection"

Output
-------
  data/weather_daily.csv   — one row per calendar day

Resume / incremental updates
------------------------------
  Re-running the script only fetches years not yet present in the CSV.
  Use --force to re-fetch everything from scratch.

Usage
------
  # Default: New Delhi, full 2010-2030 range
  python src/data_collection/fetch_weather.py

  # Mumbai
  python src/data_collection/fetch_weather.py --city mumbai

  # Custom coordinates (Varanasi)
  python src/data_collection/fetch_weather.py --lat 25.317 --lon 82.973

  # Subset of years
  python src/data_collection/fetch_weather.py --start 2020-01-01 --end 2025-12-31

  # Preview what would be fetched without making API calls
  python src/data_collection/fetch_weather.py --dry-run

  # Re-fetch everything
  python src/data_collection/fetch_weather.py --force

  # ALL cities / district HQs across India  (~150 locations)
  python src/data_collection/fetch_weather.py --all-india
  # output → data/weather_india/<city_slug>.csv  (one CSV per city)
  #           data/weather_india_combined.csv      (all cities merged)

  # All cities of a single state
  python src/data_collection/fetch_weather.py --state "Tamil Nadu"

  # Verify day-level completeness from 2010-01-01 to today and fill any gaps
  python src/data_collection/fetch_weather.py --verify
  python src/data_collection/fetch_weather.py --verify --all-india
  python src/data_collection/fetch_weather.py --verify --state "Tamil Nadu"
  python src/data_collection/fetch_weather.py --verify --dry-run   # report only

  The --verify flag operates at the individual DAY level (not year level).
  It scans every city CSV, finds any dates missing between 2010-01-01 and
  today, groups them into the fewest possible date ranges, fetches only those
  ranges, inserts the rows in the correct chronological position, and
  re-merges the combined CSV.  Safe to run at any time; idempotent.

Available --city presets
-------------------------
  delhi, mumbai, chennai, kolkata, bengaluru, hyderabad,
  jaipur, ahmedabad, pune, lucknow
"""

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import warnings
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

# Import the India location registry (same directory)
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from india_locations import INDIA_LOCATIONS, city_slug, get_locations_by_state
except ImportError:
    INDIA_LOCATIONS = []
    def city_slug(loc): return loc["city"].lower().replace(" ", "_")
    def get_locations_by_state(s): return []

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
OUTPUT_DIR   = PROJECT_ROOT / "data"
DEFAULT_OUT  = OUTPUT_DIR / "weather_daily.csv"
INDIA_DIR    = OUTPUT_DIR / "weather_india"          # per-city CSV directory
INDIA_COMBINED = OUTPUT_DIR / "weather_india_combined.csv"
BATCH_SIZE   = 50                                    # locations per API call

# ─────────────────────────────────────────────────────────────────────────────
# API endpoints
# ─────────────────────────────────────────────────────────────────────────────
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
CLIMATE_URL = "https://climate-api.open-meteo.com/v1/climate"

# ─────────────────────────────────────────────────────────────────────────────
# Defaults
# ─────────────────────────────────────────────────────────────────────────────
DATASET_START   = date(2010, 1, 1)
DATASET_END     = date(2030, 12, 31)
DEFAULT_LAT     = 28.6139      # New Delhi
DEFAULT_LON     = 77.2090
ARCHIVE_LAG     = 7            # ERA5 has ~5-day publishing lag; use 7 to be safe
CLIMATE_MODEL   = "MRI_AGCM3_2_S"   # 20 km, full variable coverage (Japan MRI)
REQUEST_DELAY   = 0.5          # seconds between API calls (respectful of free tier)

# ─────────────────────────────────────────────────────────────────────────────
# City presets (lat, lon)
# ─────────────────────────────────────────────────────────────────────────────
CITY_PRESETS: dict[str, tuple[float, float]] = {
    "delhi":      (28.6139,  77.2090),
    "mumbai":     (19.0760,  72.8777),
    "chennai":    (13.0827,  80.2707),
    "kolkata":    (22.5726,  88.3639),
    "bengaluru":  (12.9716,  77.5946),
    "hyderabad":  (17.3850,  78.4867),
    "jaipur":     (26.9124,  75.7873),
    "ahmedabad":  (23.0225,  72.5714),
    "pune":       (18.5204,  73.8567),
    "lucknow":    (26.8467,  80.9462),
}

# ─────────────────────────────────────────────────────────────────────────────
# Variable lists
# ─────────────────────────────────────────────────────────────────────────────
ARCHIVE_VARS = [
    # Temperature
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "apparent_temperature_max",
    "apparent_temperature_min",
    # Rain / precipitation
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    # Weather code — kept only to derive weather_category label; raw col dropped after
    "weather_code",
]

CLIMATE_VARS = [
    # Temperature
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    # Rain / precipitation
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
]

# WMO weather code → human-readable category
WMO_CATEGORIES = [
    (range(0,  4),   "Clear / Partly Cloudy"),
    (range(4,  10),  "Unusual Meteorology"),
    (range(10, 20),  "Mist / Fog"),
    (range(20, 30),  "Recent Precipitation"),
    (range(30, 40),  "Dust / Sand Storm"),
    (range(40, 50),  "Fog"),
    (range(50, 60),  "Drizzle"),
    (range(60, 70),  "Rain"),
    (range(70, 80),  "Snow / Ice"),
    (range(80, 83),  "Rain Showers"),
    (range(83, 87),  "Snow Showers"),
    (range(87, 95),  "Ice / Hail Showers"),
    (range(95, 100), "Thunderstorm"),
]

# Indian 6-season Ritu system (month → season)
RITU_MAP = {
    1:  "Shishira (Winter)",
    2:  "Shishira (Winter)",
    3:  "Vasanta (Spring)",
    4:  "Vasanta (Spring)",
    5:  "Grishma (Summer)",
    6:  "Grishma (Summer)",
    7:  "Varsha (Monsoon)",
    8:  "Varsha (Monsoon)",
    9:  "Sharad (Autumn)",
    10: "Sharad (Autumn)",
    11: "Hemanta (Pre-winter)",
    12: "Hemanta (Pre-winter)",
}

# Meteorological season (NH) by month
METEO_SEASON = {
    12: "Winter", 1: "Winter",  2: "Winter",
    3:  "Spring", 4: "Spring",  5: "Spring",
    6:  "Summer", 7: "Summer",  8: "Summer",
    9:  "Autumn", 10: "Autumn", 11: "Autumn",
}


# ─────────────────────────────────────────────────────────────────────────────
# HTTP helper
# ─────────────────────────────────────────────────────────────────────────────

def _get_json(url: str, params: dict, retries: int = 6) -> dict:
    """
    HTTP GET → JSON with exponential back-off retry.
    Raises RuntimeError after all retries are exhausted.
    """
    query    = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(full_url, timeout=90) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:          # rate-limited
                wait = 30
            else:
                wait = 2 ** attempt
            print(f"    ⚠  HTTP {exc.code} on attempt {attempt + 1}/{retries}. "
                  f"Waiting {wait}s …")
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError) as exc:
            wait = 2 ** attempt
            print(f"    ⚠  Network error ({exc}) on attempt {attempt + 1}/{retries}. "
                  f"Waiting {wait}s …")
            time.sleep(wait)
    raise RuntimeError(f"Failed after {retries} attempts: {full_url}")


# ─────────────────────────────────────────────────────────────────────────────
# Archive API  (historical observations via ERA5)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_archive_chunk(start: date, end: date,
                        lat: float, lon: float) -> pd.DataFrame:
    """
    Fetch one chunk from the Archive API (ERA5 reanalysis).
    Returns a DataFrame with one row per day.
    """
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
        "daily":      ",".join(ARCHIVE_VARS),
        "timezone":   "Asia/Kolkata",
        "models":     "era5",          # ERA5 for long-term consistency
    }
    data = _get_json(ARCHIVE_URL, params)
    df = pd.DataFrame(data["daily"])
    df.rename(columns={"time": "date"}, inplace=True)
    df["data_source"] = "archive_era5"
    # stamp the resolved grid-cell coordinates returned by the API
    df["latitude"]  = data.get("latitude",  lat)
    df["longitude"] = data.get("longitude", lon)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Climate API  (CMIP6 projections for future dates)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_climate_chunk(start: date, end: date,
                        lat: float, lon: float) -> pd.DataFrame:
    """
    Fetch one chunk from the Climate Change API (CMIP6 / MRI-AGCM3-2-S).
    Returns a DataFrame with one row per day.

    The Climate API appends the model name as a suffix to each variable
    (e.g. temperature_2m_max_MRI_AGCM3_2_S).  This function strips those
    suffixes so the schema matches the archive output.
    """
    params = {
        "latitude":   lat,
        "longitude":  lon,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
        "daily":      ",".join(CLIMATE_VARS),
        "models":     CLIMATE_MODEL,
        "timezone":   "Asia/Kolkata",
    }
    data  = _get_json(CLIMATE_URL, params)
    daily = dict(data.get("daily", {}))   # copy to avoid mutation

    # Build DataFrame, stripping the model-name suffix from column names
    records: dict[str, list] = {}
    model_suffix = f"_{CLIMATE_MODEL}"
    for key, values in daily.items():
        clean_key = key.replace(model_suffix, "") if key != "time" else "date"
        records[clean_key] = values

    df = pd.DataFrame(records)

    # Normalise wind: climate API provides wind_speed_10m_mean; rename to match
    # archive schema so downstream code is uniform.
    if "wind_speed_10m_mean" in df.columns and "wind_speed_10m_max" not in df.columns:
        df.rename(columns={"wind_speed_10m_mean": "wind_speed_10m_max"}, inplace=True)

    df["data_source"] = "climate_mri_agcm3"
    # stamp the resolved grid-cell coordinates returned by the API
    df["latitude"]  = data.get("latitude",  lat)
    df["longitude"] = data.get("longitude", lon)
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Batch multi-location fetch helpers
# ─────────────────────────────────────────────────────────────────────────────

def _parse_multi_response(raw: list | dict, locations: list[dict],
                          source_tag: str,
                          model_suffix: str = "") -> list[pd.DataFrame]:
    """
    Parse Open-Meteo multi-location response.

    When multiple lat/lon are passed, the API returns a JSON *list*, one
    element per location, in the same order as the request.
    Returns a list of DataFrames, one per location.
    """
    if isinstance(raw, dict):        # single-location fallback
        raw = [raw]

    frames: list[pd.DataFrame] = []
    for idx, (payload, loc) in enumerate(zip(raw, locations)):
        daily = dict(payload.get("daily", {}))
        records: dict[str, list] = {}
        for key, values in daily.items():
            clean = key.replace(model_suffix, "") if key != "time" else "date"
            records[clean] = values
        if not records:
            continue
        df = pd.DataFrame(records)
        # stamp identity
        df["city"]       = loc["city"]
        df["state"]      = loc["state"]
        df["state_code"] = loc["state_code"]
        df["district"]   = loc["district"]
        df["latitude"]   = round(payload.get("latitude",  loc["lat"]), 4)
        df["longitude"]  = round(payload.get("longitude", loc["lon"]), 4)
        df["data_source"] = source_tag
        frames.append(df)
    return frames


def fetch_archive_batch(locations: list[dict], start: date, end: date) -> list[pd.DataFrame]:
    """
    Fetch archive data for a batch of locations in a single API call.
    Returns a list of DataFrames, one per location.
    """
    lats = ",".join(str(loc["lat"]) for loc in locations)
    lons = ",".join(str(loc["lon"]) for loc in locations)
    params = {
        "latitude":   lats,
        "longitude":  lons,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
        "daily":      ",".join(ARCHIVE_VARS),
        "timezone":   "Asia/Kolkata",
        "models":     "era5",
    }
    raw = _get_json(ARCHIVE_URL, params)
    return _parse_multi_response(raw, locations, "archive_era5")


def fetch_climate_batch(locations: list[dict], start: date, end: date) -> list[pd.DataFrame]:
    """
    Fetch climate projection data for a batch of locations in a single API call.
    Returns a list of DataFrames, one per location.
    """
    lats = ",".join(str(loc["lat"]) for loc in locations)
    lons = ",".join(str(loc["lon"]) for loc in locations)
    model_suffix = f"_{CLIMATE_MODEL}"
    params = {
        "latitude":   lats,
        "longitude":  lons,
        "start_date": start.isoformat(),
        "end_date":   end.isoformat(),
        "daily":      ",".join(CLIMATE_VARS),
        "models":     CLIMATE_MODEL,
        "timezone":   "Asia/Kolkata",
    }
    raw = _get_json(CLIMATE_URL, params)
    frames = _parse_multi_response(raw, locations, "climate_mri_agcm3", model_suffix)
    # normalise wind column name (climate returns wind_speed_10m_mean)
    for df in frames:
        if "wind_speed_10m_mean" in df.columns and "wind_speed_10m_max" not in df.columns:
            df.rename(columns={"wind_speed_10m_mean": "wind_speed_10m_max"}, inplace=True)
    return frames


# ─────────────────────────────────────────────────────────────────────────────
# All-India multi-city collection pipeline
# ─────────────────────────────────────────────────────────────────────────────

def collect_all_india(
    locations: list[dict] | None = None,
    start: date = DATASET_START,
    end:   date = DATASET_END,
    out_dir: Path = INDIA_DIR,
    combined_path: Path = INDIA_COMBINED,
    force: bool = False,
    dry_run: bool = False,
    batch_size: int = BATCH_SIZE,
) -> None:
    """
    Fetch weather for every location in `locations` (default: all of India)
    using batched multi-location API calls.

    Output
    ------
    data/weather_india/<city_slug>.csv    — one CSV per city
    data/weather_india_combined.csv       — all cities in one file

    The function is fully resumable: cities whose CSV already has all expected
    days are skipped (unless force=True).
    """
    if locations is None:
        locations = INDIA_LOCATIONS
    if not locations:
        print("  ❌  No locations loaded. Check india_locations.py")
        return

    today          = date.today()
    archive_cutoff = today - timedelta(days=ARCHIVE_LAG)
    climate_start  = archive_cutoff + timedelta(days=1)
    all_years      = list(range(start.year, end.year + 1))

    sep = "─" * 62
    print(sep)
    print("  🗺️   All-India Weather Data Collection")
    print(sep)
    print(f"  Locations       : {len(locations)}")
    print(f"  Date range      : {start}  →  {end}")
    print(f"  Batch size      : {batch_size} locations/call")
    print(f"  Archive cutoff  : ≤ {archive_cutoff}")
    print(f"  Climate from    : ≥ {climate_start}")
    n_batches = (len(locations) - 1) // batch_size + 1
    est_calls = n_batches * (len(all_years) + 5)     # rough estimate
    print(f"  Est. API calls  : ~{est_calls}  (free tier limit = 10,000/day)")
    print(f"  Output dir      : {out_dir}")
    print(sep)

    if dry_run:
        print("  🔍  DRY RUN — no API calls made.")
        for i, loc in enumerate(locations[:5]):
            print(f"     [{i+1}] {loc['city']:<20} {loc['state']:<25} "
                  f"{loc['lat']:.4f}°N {loc['lon']:.4f}°E")
        if len(locations) > 5:
            print(f"     … and {len(locations)-5} more locations")
        return

    # ── Determine which cities still need data ────────────────────────────────
    out_dir.mkdir(parents=True, exist_ok=True)

    def _needs_fetch(loc: dict) -> bool:
        if force:
            return True
        fp = out_dir / f"{city_slug(loc)}.csv"
        if not fp.exists():
            return True
        done = already_fetched_years(fp)
        return bool(set(all_years) - done)

    pending = [loc for loc in locations if _needs_fetch(loc)]
    done_count = len(locations) - len(pending)
    print(f"  Already complete: {done_count} cities")
    print(f"  To fetch        : {len(pending)} cities")

    if not pending:
        print("  ✅  All cities already fetched.  Use --force to re-fetch.")
        _merge_india_csvs(out_dir, combined_path)
        return

    # Accumulate per-city DataFrames across all batches
    city_frames: dict[str, list[pd.DataFrame]] = {loc["city"]: [] for loc in pending}

    # ── Process year by year ──────────────────────────────────────────────────
    for yr in all_years:
        y_start = max(start, date(yr, 1, 1))
        y_end   = min(end,   date(yr, 12, 31))

        needs_archive = y_start <= archive_cutoff
        needs_climate = y_end   >= climate_start

        # Split pending into batches
        for b_start in range(0, len(pending), batch_size):
            batch = pending[b_start: b_start + batch_size]
            b_num = b_start // batch_size + 1
            b_total = (len(pending) - 1) // batch_size + 1

            # ── Archive batch ─────────────────────────────────────────────────
            if needs_archive:
                arch_end = min(y_end, archive_cutoff)
                tag = f"{yr} archive  batch {b_num}/{b_total}"
                print(f"  📥  {tag} ({len(batch)} cities) {y_start}→{arch_end} … ",
                      end="", flush=True)
                try:
                    frames = fetch_archive_batch(batch, y_start, arch_end)
                    for df in frames:
                        df = add_derived_features(df)
                        city_frames[df["city"].iloc[0]].append(df)
                    print(f"✓  ({sum(len(f) for f in frames)} rows)")
                except Exception as exc:
                    print(f"✗  {exc}")
                time.sleep(REQUEST_DELAY)

            # ── Climate batch ─────────────────────────────────────────────────
            if needs_climate:
                clim_start_y = max(y_start, climate_start)
                tag = f"{yr} climate  batch {b_num}/{b_total}"
                print(f"  📥  {tag} ({len(batch)} cities) {clim_start_y}→{y_end} … ",
                      end="", flush=True)
                try:
                    frames = fetch_climate_batch(batch, clim_start_y, y_end)
                    for df in frames:
                        df = add_derived_features(df)
                        city_frames[df["city"].iloc[0]].append(df)
                    print(f"✓  ({sum(len(f) for f in frames)} rows)")
                except Exception as exc:
                    print(f"✗  {exc}")
                time.sleep(REQUEST_DELAY)

    # ── Save per-city CSVs, merging with any existing data ────────────────────
    id_cols = ["date", "city", "state", "state_code", "district", "latitude", "longitude"]
    print()
    saved_cities = 0
    for loc in pending:
        cname = loc["city"]
        chunks = city_frames.get(cname, [])
        if not chunks:
            continue
        fp = out_dir / f"{city_slug(loc)}.csv"
        new_df = pd.concat(chunks, ignore_index=True)
        if fp.exists() and not force:
            existing = pd.read_csv(fp, parse_dates=["date"])
            new_df = pd.concat([existing, new_df], ignore_index=True)
        new_df = (
            new_df.drop_duplicates(subset=["date"])
                  .sort_values("date")
                  .reset_index(drop=True)
        )
        other_cols = [c for c in new_df.columns if c not in id_cols]
        new_df = new_df[[c for c in id_cols if c in new_df.columns] + other_cols]
        new_df.to_csv(fp, index=False)
        saved_cities += 1

    print(f"  💾  Saved {saved_cities} city CSV files  →  {out_dir}")

    # ── Merge all cities into one big CSV ─────────────────────────────────────
    _merge_india_csvs(out_dir, combined_path)


def _merge_india_csvs(out_dir: Path, combined_path: Path) -> None:
    """Concatenate all per-city CSVs into one combined file."""
    files = sorted(out_dir.glob("*.csv"))
    if not files:
        return
    print(f"  🔗  Merging {len(files)} city CSVs … ", end="", flush=True)
    frames = [pd.read_csv(f, parse_dates=["date"]) for f in files]
    combined = (
        pd.concat(frames, ignore_index=True)
          .sort_values(["city", "date"])
          .reset_index(drop=True)
    )
    combined.to_csv(combined_path, index=False)
    print(f"✓  {len(combined):,} rows  →  {combined_path}")


# ─────────────────────────────────────────────────────────────────────────────
# Derived feature engineering
# ─────────────────────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────────────────────
# Day-level verification & gap-filling
# ─────────────────────────────────────────────────────────────────────────────

def find_missing_days(output_path: Path, start: date, end: date) -> list[date]:
    """
    Return a sorted list of calendar dates absent from the city CSV.

    Only dates up to yesterday are checked — today's ERA5 data is not yet
    published and future climate-projection dates are not "missing".
    """
    check_end = min(end, date.today() - timedelta(days=1))
    all_days  = {start + timedelta(days=i)
                 for i in range((check_end - start).days + 1)}
    if not output_path.exists():
        return sorted(all_days)
    df      = pd.read_csv(output_path, usecols=["date"], parse_dates=["date"])
    present = {d.date() for d in pd.to_datetime(df["date"])}
    return sorted(all_days - present)


def _group_into_ranges(days: list[date]) -> list[tuple[date, date]]:
    """Group a sorted list of dates into contiguous (start, end) pairs."""
    if not days:
        return []
    ranges: list[tuple[date, date]] = []
    r_start = r_end = days[0]
    for d in days[1:]:
        if (d - r_end).days == 1:
            r_end = d
        else:
            ranges.append((r_start, r_end))
            r_start = r_end = d
    ranges.append((r_start, r_end))
    return ranges


def fill_missing_days(
    missing:     list[date],
    lat:         float,
    lon:         float,
    city_name:   str,
    output_path: Path,
    loc_meta:    dict | None = None,
    dry_run:     bool = False,
) -> int:
    """
    Fetch and insert missing days into the city CSV.

    Consecutive missing days are grouped into the fewest contiguous date
    ranges to minimise API calls.  Each range is split at the archive/climate
    boundary if it spans it.  The updated rows are merged back into the
    existing CSV in chronological order.

    Returns the number of days successfully filled (0 on dry-run).
    """
    if not missing:
        return 0

    today          = date.today()
    archive_cutoff = today - timedelta(days=ARCHIVE_LAG)
    climate_start  = archive_cutoff + timedelta(days=1)
    ranges         = _group_into_ranges(missing)

    print(f"    ⚠  {len(missing)} missing day(s) in {len(ranges)} range(s)")
    if dry_run:
        for r_start, r_end in ranges:
            n = (r_end - r_start).days + 1
            print(f"       {r_start} → {r_end}  ({n}d)")
        return 0

    new_chunks: list[pd.DataFrame] = []
    filled = 0

    for r_start, r_end in ranges:
        segments: list[tuple[str, date, date]] = []
        if r_start <= archive_cutoff:
            segments.append(("archive", r_start, min(r_end, archive_cutoff)))
        if r_end >= climate_start:
            segments.append(("climate", max(r_start, climate_start), r_end))

        for src, s_start, s_end in segments:
            n = (s_end - s_start).days + 1
            print(f"    📥  {src:<8}  {s_start} → {s_end}  ({n}d) … ",
                  end="", flush=True)
            try:
                if src == "archive":
                    chunk = fetch_archive_chunk(s_start, s_end, lat, lon)
                else:
                    chunk = fetch_climate_chunk(s_start, s_end, lat, lon)
                chunk = add_derived_features(chunk)
                # stamp full location identity
                chunk["city"]      = city_name
                chunk["latitude"]  = round(lat, 4)
                chunk["longitude"] = round(lon, 4)
                if loc_meta:
                    for fld in ("state", "state_code", "district"):
                        if fld in loc_meta:
                            chunk[fld] = loc_meta[fld]
                new_chunks.append(chunk)
                filled += len(chunk)
                print(f"✓  ({len(chunk)} rows)")
            except Exception as exc:
                print(f"✗  {exc}")
            time.sleep(REQUEST_DELAY)

    if not new_chunks:
        return 0

    existing = (
        pd.read_csv(output_path, parse_dates=["date"])
        if output_path.exists() else pd.DataFrame()
    )
    all_frames = ([existing] if not existing.empty else []) + new_chunks
    combined = (
        pd.concat(all_frames, ignore_index=True)
          .drop_duplicates(subset=["date"])
          .sort_values("date")
          .reset_index(drop=True)
    )
    id_cols    = ["date", "city", "state", "state_code", "district",
                  "latitude", "longitude"]
    other_cols = [c for c in combined.columns if c not in id_cols]
    combined   = combined[[c for c in id_cols if c in combined.columns] + other_cols]
    combined.to_csv(output_path, index=False)
    print(f"    💾  {output_path.name}  →  {len(combined):,} rows total")
    return filled


def verify_all_india(
    locations:     list[dict],
    start:         date,
    out_dir:       Path,
    combined_path: Path,
    dry_run:       bool = False,
) -> None:
    """
    Scan every per-city CSV for missing days between *start* and yesterday.

    For each city:
      1. Compute the full expected date range  [start, yesterday].
      2. Subtract dates already present in the CSV.
      3. Group remaining gaps into the fewest contiguous ranges.
      4. Fetch and insert each gap range, splitting at the archive/climate
         boundary as needed.
      5. Re-merge all city CSVs into the combined file.

    Safe to run repeatedly — it is fully idempotent.
    """
    today     = date.today()
    check_end = today - timedelta(days=1)

    sep = "─" * 62
    print(sep)
    print("  🔍  VERIFY MODE — day-level completeness check")
    print(f"  Period checked  : {start}  →  {check_end}")
    print(f"  Cities          : {len(locations)}")
    print(sep)

    total_missing = 0
    any_filled    = False

    for loc in locations:
        slug    = city_slug(loc)
        fp      = out_dir / f"{slug}.csv"
        city    = loc["city"]
        missing = find_missing_days(fp, start, check_end)

        if not missing:
            print(f"  ✅  {city:<25} complete")
            continue

        print(f"  ⚠   {city:<25} {len(missing)} missing day(s)")
        total_missing += len(missing)
        filled = fill_missing_days(
            missing     = missing,
            lat         = loc["lat"],
            lon         = loc["lon"],
            city_name   = city,
            output_path = fp,
            loc_meta    = loc,
            dry_run     = dry_run,
        )
        if filled:
            any_filled = True

    print(sep)
    if total_missing == 0:
        print("  ✅  All cities complete — no missing days found.")
    elif dry_run:
        print(f"  🔍  DRY RUN — would fill {total_missing} missing city-day(s).")
    else:
        print(f"  ✅  Filled {total_missing} missing day(s) across all cities.")
        if any_filled:
            _merge_india_csvs(out_dir, combined_path)
    print(sep)


def _wmo_category(code) -> str:
    if pd.isna(code):
        return "Unknown"
    code = int(code)
    for code_range, label in WMO_CATEGORIES:
        if code in code_range:
            return label
    return "Unknown"


def _uv_risk(uv) -> str:
    if pd.isna(uv):
        return "Unknown"
    uv = float(uv)
    if uv < 3:   return "Low"
    if uv < 6:   return "Moderate"
    if uv < 8:   return "High"
    if uv < 11:  return "Very High"
    return "Extreme"


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds category and grouping features derived from temperature and rain columns.

    Kept columns (raw)
    ──────────────────
    temperature_2m_max/min/mean   °C
    apparent_temperature_max/min  °C (feels-like; archive only)
    precipitation_sum             mm
    rain_sum                      mm
    snowfall_sum                  cm

    Derived categories / groupings (new)
    ─────────────────────────────────────
    temp_range       diurnal temperature range (max − min), °C
    is_rainy_day     1 if precipitation_sum > 1 mm, else 0
    is_hot_day       1 if temperature_2m_max > 35 °C, else 0
    is_cold_day      1 if temperature_2m_min < 10 °C, else 0
    season_meteo     standard 4-season meteorological label (NH)
    season_india     Indian 6-season Ritu label
    weather_category plain-language WMO weather group (archive only)
    year_norm        year normalised to [0, 1] over 2010–2030

    Note: raw weather_code is dropped after deriving weather_category.
    """
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    month = df["date"].dt.month

    # ── Temperature derived ───────────────────────────────────────────────────
    if "temperature_2m_max" in df.columns and "temperature_2m_min" in df.columns:
        df["temp_range"] = (
            df["temperature_2m_max"] - df["temperature_2m_min"]
        ).round(2)

    # ── Binary flags ──────────────────────────────────────────────────────────
    if "precipitation_sum" in df.columns:
        df["is_rainy_day"] = (df["precipitation_sum"].fillna(0) > 1.0).astype(int)
    if "temperature_2m_max" in df.columns:
        df["is_hot_day"]   = (df["temperature_2m_max"].fillna(0) > 35.0).astype(int)
    if "temperature_2m_min" in df.columns:
        df["is_cold_day"]  = (df["temperature_2m_min"].fillna(50) < 10.0).astype(int)

    # ── Season groupings ──────────────────────────────────────────────────────
    df["season_meteo"] = month.map(METEO_SEASON)
    df["season_india"] = month.map(RITU_MAP)

    # ── Weather category (derive from code, then drop the raw numeric code) ───
    if "weather_code" in df.columns:
        df["weather_category"] = df["weather_code"].apply(_wmo_category)
        df.drop(columns=["weather_code"], inplace=True)

    # ── Normalised year ───────────────────────────────────────────────────────
    df["year_norm"] = ((df["date"].dt.year - 2010) / (2030 - 2010)).round(4)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Determine already-fetched years  (for resumable downloads)
# ─────────────────────────────────────────────────────────────────────────────

def already_fetched_years(output_path: Path) -> set[int]:
    """
    Return the set of calendar years that are fully present in the output CSV.
    A year is considered complete only if all 365/366 days are present.
    """
    if not output_path.exists():
        return set()
    try:
        df   = pd.read_csv(output_path, usecols=["date"], parse_dates=["date"])
        counts = df["date"].dt.year.value_counts()
        complete = set()
        for yr, cnt in counts.items():
            expected = 366 if (yr % 4 == 0 and (yr % 100 != 0 or yr % 400 == 0)) else 365
            if cnt >= expected:
                complete.add(int(yr))
        return complete
    except Exception:
        return set()


# ─────────────────────────────────────────────────────────────────────────────
# Main collection pipeline
# ─────────────────────────────────────────────────────────────────────────────

def collect_weather(
    lat: float = DEFAULT_LAT,
    lon: float = DEFAULT_LON,
    city_name: str = "New Delhi",
    start: date = DATASET_START,
    end:   date = DATASET_END,
    output_path: Path = DEFAULT_OUT,
    force: bool = False,
    dry_run: bool = False,
) -> pd.DataFrame:
    """
    Fetch daily weather data for [start, end] and save to output_path.

    Strategy
    --------
    archive  →  2010-01-01  to  (today − ARCHIVE_LAG days)
    climate  →  (today − ARCHIVE_LAG + 1 days)  to  2030-12-31

    Data is fetched year-by-year for reliability and progress visibility.
    Already-downloaded years are skipped (unless force=True).

    Returns the full DataFrame.
    """
    today          = date.today()
    archive_cutoff = today - timedelta(days=ARCHIVE_LAG)     # last reliable ERA5 day
    climate_start  = archive_cutoff + timedelta(days=1)       # first climate-projection day

    # Years to process
    all_years      = list(range(start.year, end.year + 1))
    done_years     = set() if force else already_fetched_years(output_path)
    pending_years  = [y for y in all_years if y not in done_years]

    # ── Summary header ────────────────────────────────────────────────────────
    sep = "─" * 62
    print(sep)
    print("  🌤  Open-Meteo Weather Data Collection Service")
    print(sep)
    print(f"  Location        : {city_name}  (lat={lat:.4f}  lon={lon:.4f})")
    print(f"  Date range      : {start}  →  {end}")
    print(f"  Archive cutoff  : ≤ {archive_cutoff}  (ERA5 reanalysis)")
    print(f"  Climate from    : ≥ {climate_start}  (MRI-AGCM3-2-S projection)")
    print(f"  Total years     : {len(all_years)}")
    print(f"  Already done    : {sorted(done_years) or 'none'}")
    print(f"  Pending         : {pending_years or 'none'}")
    print(f"  Output          : {output_path}")
    print(sep)

    if not pending_years:
        print("  ✅  All years already fetched.  Use --force to re-fetch.")
        return pd.read_csv(output_path, parse_dates=["date"])

    if dry_run:
        print("  🔍  DRY RUN — no API calls made.")
        for yr in pending_years:
            y_start = max(start, date(yr, 1, 1))
            y_end   = min(end,   date(yr, 12, 31))
            src     = "archive" if y_end <= archive_cutoff else (
                      "climate" if y_start >= climate_start else "archive+climate")
            print(f"     {yr}: {y_start} → {y_end}  [{src}]")
        return pd.DataFrame()

    # ── Fetch year by year ────────────────────────────────────────────────────
    new_chunks: list[pd.DataFrame] = []

    for yr in pending_years:
        y_start = max(start, date(yr, 1, 1))
        y_end   = min(end,   date(yr, 12, 31))

        # Determine which API(s) cover this year
        needs_archive = y_start <= archive_cutoff
        needs_climate = y_end   >= climate_start

        year_frames: list[pd.DataFrame] = []

        # ── Archive segment ───────────────────────────────────────────────────
        if needs_archive:
            arch_end = min(y_end, archive_cutoff)
            print(f"  📥  {yr}  archive  {y_start} → {arch_end} … ", end="", flush=True)
            try:
                chunk = fetch_archive_chunk(y_start, arch_end, lat, lon)
                chunk = add_derived_features(chunk)
                year_frames.append(chunk)
                print(f"✓  ({len(chunk)} days)")
            except Exception as exc:
                print(f"✗  ERROR: {exc}")
            time.sleep(REQUEST_DELAY)

        # ── Climate segment ───────────────────────────────────────────────────
        if needs_climate:
            clim_start = max(y_start, climate_start)
            print(f"  📥  {yr}  climate  {clim_start} → {y_end} … ", end="", flush=True)
            try:
                chunk = fetch_climate_chunk(clim_start, y_end, lat, lon)
                chunk = add_derived_features(chunk)
                year_frames.append(chunk)
                print(f"✓  ({len(chunk)} days)")
            except Exception as exc:
                print(f"✗  ERROR: {exc}")
            time.sleep(REQUEST_DELAY)

        if year_frames:
            new_chunks.append(pd.concat(year_frames, ignore_index=True))

    # ── Merge with any existing data ──────────────────────────────────────────
    if output_path.exists() and not force:
        existing = pd.read_csv(output_path, parse_dates=["date"])
        all_frames = [existing] + new_chunks
    else:
        all_frames = new_chunks

    if not all_frames:
        print("  ⚠  No data collected.")
        return pd.DataFrame()

    df_final = (
        pd.concat(all_frames, ignore_index=True)
        .drop_duplicates(subset=["date"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Ensure location identity columns are always present
    df_final["city"]      = city_name
    df_final["latitude"]  = df_final["latitude"].fillna(lat).round(4)
    df_final["longitude"] = df_final["longitude"].fillna(lon).round(4)

    # Move identity columns to the front for readability
    id_cols    = ["date", "city", "latitude", "longitude"]
    other_cols = [c for c in df_final.columns if c not in id_cols]
    df_final   = df_final[id_cols + other_cols]

    # ── Save ──────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(output_path, index=False)

    return df_final


# ─────────────────────────────────────────────────────────────────────────────
# Summary report
# ─────────────────────────────────────────────────────────────────────────────

def print_summary(df: pd.DataFrame) -> None:
    if df.empty:
        return

    sep = "─" * 62
    print(f"\n{sep}")
    print("  📊  DATASET SUMMARY")
    print(sep)
    print(f"  Rows            : {len(df):,}")
    print(f"  Columns         : {len(df.columns)}")
    print(f"  Date range      : {df['date'].min().date()}  →  {df['date'].max().date()}")
    print(f"  Missing days    : {(len(df) / ((df['date'].max() - df['date'].min()).days + 1) - 1) * -len(df):.0f}")

    if "data_source" in df.columns:
        print(f"\n  Data source breakdown:")
        for src, cnt in df["data_source"].value_counts().items():
            print(f"    {src:<30} {cnt:>5} days  ({100*cnt/len(df):.1f} %)")

    if "temperature_2m_max" in df.columns:
        print(f"\n  Temperature (max)  :")
        print(f"    Mean  : {df['temperature_2m_max'].mean():.1f} °C")
        print(f"    Min   : {df['temperature_2m_max'].min():.1f} °C")
        print(f"    Max   : {df['temperature_2m_max'].max():.1f} °C")

    if "precipitation_sum" in df.columns:
        print(f"\n  Precipitation      :")
        print(f"    Rainy days: {df.get('is_rainy_day', pd.Series(dtype=int)).sum():,} "
              f"({100 * df.get('is_rainy_day', pd.Series(dtype=int)).mean():.1f} %)")

    if "season_india" in df.columns:
        print(f"\n  Days per Indian season:")
        for season, cnt in df["season_india"].value_counts().sort_index().items():
            print(f"    {season:<30} {cnt:>5}")

    if "weather_category" in df.columns:
        print(f"\n  Weather categories (archive days only):")
        for cat, cnt in df["weather_category"].value_counts().head(6).items():
            print(f"    {cat:<30} {cnt:>5}")

    print(f"\n  Columns:\n   {list(df.columns)}")
    print(sep)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def build_cli() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="fetch_weather.py",
        description="Collect daily weather data (Open-Meteo, free, no API key).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # ── Location scope (mutually exclusive) ───────────────────────────────────
    scope = p.add_mutually_exclusive_group()
    scope.add_argument(
        "--all-india", action="store_true",
        help="Fetch all ~150 Indian cities/district HQs",
    )
    scope.add_argument(
        "--state", metavar="STATE",
        help='Fetch all cities for one state, e.g. --state "Tamil Nadu"',
    )
    scope.add_argument(
        "--city", choices=list(CITY_PRESETS.keys()), metavar="CITY",
        help=f"Single city preset: {', '.join(CITY_PRESETS)}",
    )
    scope.add_argument(
        "--lat", type=float, default=None,
        help="Custom latitude (use with --lon)",
    )

    p.add_argument("--lon",  type=float, default=None, help="Custom longitude")
    p.add_argument(
        "--start", default=DATASET_START.isoformat(),
        help=f"Start date YYYY-MM-DD  (default: {DATASET_START})",
    )
    p.add_argument(
        "--end", default=DATASET_END.isoformat(),
        help=f"End date   YYYY-MM-DD  (default: {DATASET_END})",
    )
    p.add_argument(
        "--output", default=str(DEFAULT_OUT),
        help=f"Single-city output CSV (default: {DEFAULT_OUT})",
    )
    p.add_argument(
        "--out-dir", default=str(INDIA_DIR),
        help=f"Per-city output directory for --all-india / --state (default: {INDIA_DIR})",
    )
    p.add_argument(
        "--batch-size", type=int, default=BATCH_SIZE,
        help=f"Locations per API call for multi-city mode (default: {BATCH_SIZE})",
    )
    p.add_argument(
        "--list-locations", action="store_true",
        help="Print all available India locations and exit",
    )
    p.add_argument("--force",   action="store_true", help="Re-fetch all data")
    p.add_argument("--dry-run", action="store_true", help="Plan only, no API calls")
    p.add_argument(
        "--verify", action="store_true",
        help=(
            "Scan every city CSV for missing days (2010-01-01 → yesterday) and "
            "fetch only the gaps.  Combine with --all-india / --state / --city. "
            "Use --dry-run to report gaps without fetching."
        ),
    )
    return p


def main() -> None:
    args = build_cli().parse_args()

    # ── List locations mode ───────────────────────────────────────────────────
    if args.list_locations:
        print(f"{'#':<4} {'City':<22} {'State':<25} {'District':<25} {'Lat':>8} {'Lon':>9}")
        print("-" * 95)
        for i, loc in enumerate(INDIA_LOCATIONS, 1):
            print(f"{i:<4} {loc['city']:<22} {loc['state']:<25} "
                  f"{loc['district']:<25} {loc['lat']:>8.4f} {loc['lon']:>9.4f}")
        all_states = sorted({l["state"] for l in INDIA_LOCATIONS})
        print(f"\nTotal: {len(INDIA_LOCATIONS)} locations across {len(all_states)} states/UTs")
        return

    start = date.fromisoformat(args.start)
    end   = date.fromisoformat(args.end)

    # ── Multi-city modes  (--all-india / --state) ─────────────────────────────
    if args.all_india or args.state:
        if args.state:
            locs = get_locations_by_state(args.state)
            if not locs:
                all_states = sorted({l["state"] for l in INDIA_LOCATIONS})
                print(f"  ❌  State '{args.state}' not found.")
                print(f"  Available states: {', '.join(all_states)}")
                return
        else:
            locs = INDIA_LOCATIONS

        if args.verify:
            verify_all_india(
                locations     = locs,
                start         = DATASET_START,
                out_dir       = Path(args.out_dir),
                combined_path = INDIA_COMBINED,
                dry_run       = args.dry_run,
            )
        else:
            collect_all_india(
                locations     = locs,
                start         = start,
                end           = end,
                out_dir       = Path(args.out_dir),
                combined_path = INDIA_COMBINED,
                force         = args.force,
                dry_run       = args.dry_run,
                batch_size    = args.batch_size,
            )
        return

    # ── Single-city mode  (default / --city / --lat) ──────────────────────────
    if args.city:
        lat, lon   = CITY_PRESETS[args.city]
        city_label = args.city.title()
        out_path   = Path(args.output)
    elif args.lat is not None:
        lat, lon   = args.lat, (args.lon or DEFAULT_LON)
        city_label = f"Custom ({lat:.4f}°N, {lon:.4f}°E)"
        out_path   = Path(args.output)
    else:
        lat, lon   = DEFAULT_LAT, DEFAULT_LON
        city_label = "New Delhi"
        out_path   = Path(args.output)

    if args.verify:
        missing = find_missing_days(out_path, DATASET_START,
                                    date.today() - timedelta(days=1))
        sep = "─" * 62
        print(sep)
        print(f"  🔍  VERIFY — {city_label}")
        print(f"  CSV         : {out_path}")
        print(f"  Period      : {DATASET_START}  →  {date.today() - timedelta(days=1)}")
        print(sep)
        if not missing:
            print("  ✅  Complete — no missing days.")
        else:
            print(f"  ⚠  {len(missing)} missing day(s)")
            fill_missing_days(
                missing     = missing,
                lat         = lat,
                lon         = lon,
                city_name   = city_label,
                output_path = out_path,
                dry_run     = args.dry_run,
            )
        print(sep)
        return

    df = collect_weather(
        lat=lat, lon=lon, city_name=city_label,
        start=start, end=end,
        output_path=out_path,
        force=args.force, dry_run=args.dry_run,
    )
    if not df.empty:
        print_summary(df)
        print(f"\n  💾  Saved → {args.output}\n")


if __name__ == "__main__":
    main()
