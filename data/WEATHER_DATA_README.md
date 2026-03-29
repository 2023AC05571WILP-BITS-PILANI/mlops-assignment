# Weather Data — Collection & Aggregation Guide

This document explains the full pipeline that produces the weather datasets in
`data/`, from raw API calls all the way to ML-ready zone-level summaries.

---

## Table of Contents

1. [Overview](#overview)
2. [Data Sources](#data-sources)
3. [Collection Pipeline](#collection-pipeline)
   - [Single City](#single-city)
   - [All-India Multi-City Batch](#all-india-multi-city-batch)
4. [Variables Collected](#variables-collected)
5. [Derived Features](#derived-features)
6. [Location Registry (`india_locations.py`)](#location-registry)
7. [Zone Classification Scheme](#zone-classification-scheme)
8. [Aggregation Pipeline](#aggregation-pipeline)
   - [Step-by-step walkthrough](#step-by-step-walkthrough)
   - [Output columns explained](#output-columns-explained)
9. [Output Files Reference](#output-files-reference)
10. [How to Run](#how-to-run)
11. [Design Decisions & Trade-offs](#design-decisions--trade-offs)

---

## Overview

```
Open-Meteo Archive API  ──┐
(ERA5, 2010 → ~7 days ago) │
                           ├─► fetch_weather.py ──► data/weather_india/<city>.csv
Open-Meteo Climate API  ──┘                      ──► data/weather_india_combined.csv
(CMIP6, future → 2030)                                          │
                                                                ▼
                                                  aggregate_by_zone.py
                                                                │
                           ┌────────────────────────────────────┤
                           ▼            ▼            ▼          ▼
                   koppen.csv   monsoon.csv   imd.csv   agri.csv
```

**Goal**: Cover every calendar day 2010–2030 for 165 Indian cities, then reduce
that 165-city noise down to a small set of climate-zone summaries that an ML
model can train on without over-fitting to city-specific quirks.

---

## Data Sources

### Open-Meteo Archive API — Historical Observations

| Property | Value |
|---|---|
| URL | `https://archive-api.open-meteo.com/v1/archive` |
| Coverage | 2010-01-01 → ~7 days before today |
| Underlying dataset | **ERA5** reanalysis (ECMWF, 0.25° / ~25 km grid) |
| Cost | Free, no API key |
| Reliability | Gold standard — ERA5 is used in climate science worldwide |

### Open-Meteo Climate API — Future Projections

| Property | Value |
|---|---|
| URL | `https://climate-api.open-meteo.com/v1/climate` |
| Coverage | ~7 days ago → 2030-12-31 |
| Underlying dataset | **MRI-AGCM3-2-S** (Japan Meteorological Research Institute, 20 km) |
| Cost | Free, no API key |
| Reliability | CMIP6-class model; good for multi-year trends, not exact daily forecasts |

The two APIs are **stitched seamlessly** at the `ARCHIVE_LAG` boundary (7 days
before today) so the final CSV has no gaps across the 2010–2030 range.

---

## Collection Pipeline

### Single City

`fetch_weather.py` calls the Archive API year-by-year (to stay inside URL
length limits), then calls the Climate API for the remaining future period.

```
2010        archive boundary         today+7d        2030
 ├───── fetch_archive_chunk() ──────┤├─ fetch_climate_chunk() ─┤
```

**Incremental resume**: On re-run, `already_fetched_years()` reads the existing
CSV and skips years already present. Use `--force` to re-fetch from scratch.

**Retry logic**: Every HTTP call uses exponential back-off (up to 6 attempts).
Rate-limit responses (HTTP 429) trigger a 30-second wait.

### All-India Multi-City Batch

When `--all-india` or `--state STATE` is used, the script uses the **batch
multi-location** feature of Open-Meteo — up to 50 locations are passed as
comma-separated `latitude` / `longitude` lists in a single request.

```
165 cities  ÷  50 per batch  =  4 batches per year-chunk
4 batches × 21 years × 2 APIs ≈ ~168 total API calls (for all cities, all years)
```

Each city writes its own CSV to `data/weather_india/<city_slug>.csv`. At the
end, all CSVs are merged into `data/weather_india_combined.csv`. Cities that
already have a complete CSV are skipped automatically.

---

## Variables Collected

Only temperature and rain variables are fetched. Wind, radiation, humidity,
pressure and sunshine are excluded to keep the dataset lean and focused.

### Archive (ERA5) — 9 variables fetched

| Variable | Unit | Description |
|---|---|---|
| `temperature_2m_max` | °C | Daily maximum air temperature at 2 m |
| `temperature_2m_min` | °C | Daily minimum air temperature at 2 m |
| `temperature_2m_mean` | °C | Daily mean air temperature at 2 m |
| `apparent_temperature_max` | °C | Feels-like max (heat index / wind chill) |
| `apparent_temperature_min` | °C | Feels-like min |
| `precipitation_sum` | mm | Total precipitation (rain + snow water equivalent) |
| `rain_sum` | mm | Liquid precipitation only |
| `snowfall_sum` | cm | Snowfall accumulation |
| `weather_code` | WMO | WMO code — used to derive `weather_category` label, then dropped |

### Climate Projection (MRI-AGCM3-2-S) — 6 variables fetched

| Variable | Unit |
|---|---|
| `temperature_2m_max/min/mean` | °C |
| `precipitation_sum` | mm |
| `rain_sum` | mm |
| `snowfall_sum` | cm |

> `apparent_temperature` and `weather_code` are not available in the climate
> API; those columns are `NaN` for future projection rows.
> `data_source = "climate_projection"` marks all such rows.

---

## Derived Features

Added automatically after fetching, regardless of API source:

| Feature | Logic | Notes |
|---|---|---|
| `temp_range` | `max − min` | Diurnal variation; high = arid/continental |
| `is_rainy_day` | `precipitation_sum > 1 mm` → 0/1 | Binary rain flag |
| `is_hot_day` | `temperature_2m_max > 35 °C` → 0/1 | Binary heat flag |
| `is_cold_day` | `temperature_2m_min < 10 °C` → 0/1 | Binary cold flag |
| `season_meteo` | Month → Winter/Spring/Summer/Autumn (NH) | Standard 4-season label |
| `season_india` | Month → 6-season Ritu system | Culturally relevant seasons |
| `weather_category` | WMO code → human label (archive only) | e.g. `Rain`, `Thunderstorm`, `Clear / Partly Cloudy`; `NaN` for climate rows |
| `year_norm` | `(year − 2010) / 20` → [0, 1] | Normalised temporal position |
| `data_source` | `"archive_era5"` or `"climate_projection"` | Provenance flag for ML |

**Removed from previous version:** `day_length_hours`, `sunshine_hours`, `uv_risk`, and raw `weather_code` number are no longer in the output. `weather_code` is decoded to `weather_category` string then dropped.

Identity columns stamped on every row (front of DataFrame):

| Column | Example |
|---|---|
| `city` | `Chennai` |
| `state` | `Tamil Nadu` |
| `state_code` | `TN` |
| `district` | `Chennai` |
| `latitude` | `13.0827` |
| `longitude` | `80.2707` |

---

## Location Registry

**File**: `src/data_collection/india_locations.py`

Contains 165 Indian cities / district headquarters across all 36 states and
Union Territories. Each entry has:

```python
{
    "state":       "Tamil Nadu",
    "state_code":  "TN",
    "city":        "Chennai",
    "district":    "Chennai",
    "lat":         13.0827,
    "lon":         80.2707,

    # Zone classifications (see next section)
    "koppen":      "Tropical_WetDry_S",
    "monsoon_zone":"NE_Monsoon",
    "imd_zone":    "Tamil_Nadu_Puducherry",
    "agri_zone":   "Year_Round",
}
```

Helper functions available:

```python
from india_locations import (
    get_locations_by_state,   # filter by state name
    get_locations_by_koppen,  # filter by Köppen zone
    get_locations_by_monsoon, # filter by monsoon zone
    get_locations_by_imd,     # filter by IMD subdivision
    get_locations_by_agri,    # filter by agricultural zone
    get_all_states,           # list all 36 states/UTs
    get_zone_summary,         # dict of zone → [city, city, …]
    as_dataframe,             # returns pandas DataFrame
    city_slug,                # "New Delhi" → "new_delhi"
)
```

---

## Zone Classification Scheme

Each city belongs to **four independent zone systems**. These are used to group
cities for noise-reduced ML features.

### 1. Köppen Climate Zone (`koppen`) — 5 zones

| Zone | States | Climate character |
|---|---|---|
| `Arid_West` | Rajasthan, Gujarat | Hot/cold desert; <300 mm/yr rainfall |
| `Humid_Subtropical_N` | UP, Bihar, Delhi, Haryana, MP, Punjab | Hot summers, cool dry winters |
| `Tropical_Wet_E` | WB, Odisha, Assam, NE states | High humidity, heavy monsoon |
| `Mountain_N` | HP, Uttarakhand, J&K, Ladakh, Sikkim | Alpine; snow winters |
| `Tropical_WetDry_S` | Kerala, KA, TN, AP, TG, MH, Goa | Distinct wet/dry seasons |

### 2. Monsoon Zone (`monsoon_zone`) — 5 zones

Describes **when** the SW or NE monsoon arrives and departs:

| Zone | Onset (day of year) | Withdrawal | States |
|---|---|---|---|
| `Early_SW` | 152–165 (Jun 1–14) | 274–305 | Kerala, Goa, coastal KA, NE |
| `Central_SW` | 162–180 (Jun 11–29) | 274–290 | MH, MP, CG, Odisha, WB, AP, TG |
| `Late_SW` | 176–196 (Jun 25–Jul 15) | 258–274 | Bihar, JH, UP, Delhi, HR, PB, UK, HP |
| `Arid_Late` | 185–210 (Jul 4–29) | 244–265 | Rajasthan, Gujarat |
| `NE_Monsoon` | 274–335 (Oct 1–Dec 1) | 335–365 | Tamil Nadu, SE coast, Puducherry |

The aggregated `monsoon_zone` CSV additionally contains two boolean columns:
- `in_monsoon_onset_window` — is this date within the typical monsoon arrival window for the zone?
- `in_monsoon_withdrawal_window` — is this date within the typical retreat window?

### 3. IMD Meteorological Subdivision (`imd_zone`) — 24 zones

Closely follows the India Meteorological Department's official subdivisions:

`Kerala`, `Tamil_Nadu_Puducherry`, `Coastal_AP`, `Rayalaseema`, `Telangana`,
`Interior_Karnataka`, `Coastal_Karnataka`, `Konkan_Goa`, `Maharashtra_Interior`,
`Vidarbha`, `MP`, `Chhattisgarh`, `Odisha`, `West_Bengal`, `Bihar_Jharkhand`,
`UP`, `Haryana_Delhi_Punjab`, `Rajasthan`, `Gujarat_Saurashtra`, `NE_India`,
`Uttarakhand_HP`, `JK_Ladakh`, `Andaman_Nicobar`, `Lakshadweep`

### 4. Agricultural Zone (`agri_zone`) — 6 zones

| Zone | Dominant cropping | States |
|---|---|---|
| `Kharif_Dom` | SW-monsoon crop (Jun–Sep) | NE India, Odisha, coastal regions |
| `Rabi_Dom` | Winter crop (Oct–Mar) | Punjab, Haryana, W-UP (wheat belt) |
| `Kharif_Rabi` | Both seasons | AP, TG, MH, KA, MP, E-UP |
| `Year_Round` | Multi-crop perennial | Kerala, TN, Andaman |
| `Arid_Irrigated` | Canal / drip irrigation | Rajasthan, Gujarat |
| `Mountain` | Subsistence / terrace farming | HP, Uttarakhand, J&K, Ladakh |

---

## Aggregation Pipeline

**File**: `src/preprocessing/aggregate_by_zone.py`

### Step-by-step walkthrough

#### Step 1 — Load combined city data

Reads `data/weather_india_combined.csv`. At full scale this is:

```
165 cities × 7,670 days (2010–2030) = ~1.26 million rows
```

Each row is one city on one day with ~30 weather columns.

#### Step 2 — Join zone labels

A left-join on `lowercase(city)` stamps 4 zone columns (`koppen`,
`monsoon_zone`, `imd_zone`, `agri_zone`) from `india_locations.py` onto every
row. Cities not found in the registry are flagged with a warning; their rows
are dropped from that zone's aggregation.

```
Before join:  date | city | temp_max | precip | …
After join:   date | city | temp_max | precip | … | koppen | monsoon_zone | imd_zone | agri_zone
```

#### Step 3 — Group and aggregate (done 4× independently)

For each zone type the data is grouped by `(date, zone_label)`:

```python
grouped = df.groupby(["date", "koppen"])
```

For **every numeric weather variable** (23 variables), three statistics are
computed:

| Suffix | Statistic | ML meaning |
|---|---|---|
| `_mean` | Arithmetic mean across cities in zone | Typical condition that day |
| `_median` | Median across cities in zone | Robust central value (outlier-resistant) |
| `_std` | Standard deviation across cities in zone | Internal variability within zone |

So `temperature_2m_max` becomes `temperature_2m_max_mean`,
`temperature_2m_max_median`, and `temperature_2m_max_std` — giving **69
numeric feature columns** (23 × 3) per zone per day.

#### Step 4 — Append metadata columns

| Column | Content |
|---|---|
| `city_count` | Number of cities that contributed to this zone on this date |
| `city_list` | Comma-separated sorted city names (e.g. `"Chennai,Coimbatore,Madurai"`) |
| `season_meteo_mode` | Most common meteorological season among cities in the group |
| `season_india_mode` | Most common Indian Ritu season |
| `weather_category_mode` | Most common WMO weather type |

#### Step 5 — Monsoon window flags (monsoon_zone only)

Two boolean columns are appended to `weather_zone_monsoon.csv` based on
day-of-year windows from `MONSOON_ONSET_WINDOW` and
`MONSOON_WITHDRAWAL_WINDOW`:

```
in_monsoon_onset_window       True if today's DOY falls within the typical
                              arrival window for this zone
in_monsoon_withdrawal_window  True if today's DOY falls within the typical
                              retreat window for this zone
```

These let a model learn "is today anomalously wet/dry for the expected monsoon
stage?" without needing to hard-code calendar knowledge.

### Output columns explained

A sample row from `weather_zone_koppen.csv` (2015-01-01, Tropical_WetDry_S — 9 Tamil Nadu cities):

```
date                          2015-01-01
koppen                        Tropical_WetDry_S
temperature_2m_max_mean       30.4 °C
temperature_2m_max_median     30.9 °C
temperature_2m_max_std         1.5 °C   ← spread across 9 cities
precipitation_sum_mean         1.7 mm
precipitation_sum_median       1.0 mm   ← median < mean → a few cities had heavier rain
precipitation_sum_std          2.1 mm   ← high variability within zone
temp_range_mean                6.8 °C
is_rainy_day_mean              0.44     ← 44% of cities had rain that day
is_hot_day_mean                0.0      ← none exceeded 35 °C
is_cold_day_mean               0.0
season_meteo_mode              Winter
season_india_mode              Shishira (Winter)
weather_category_mode          Drizzle
city_count                     9
city_list                      Chennai,Coimbatore,Erode,…
```

`weather_zone_monsoon.csv` additionally contains:
```
in_monsoon_onset_window        False   (Jan 1 is outside Jun onset window)
in_monsoon_withdrawal_window   False
```

### Dimension reduction summary

| Dataset | Rows | Date coverage |
|---|---|---|
| Raw city-level combined CSV | 45,288 (9 cities × 5,032 days) | 2015–2030 (partial — see note) |
| **`weather_zone_koppen.csv`** | **5,032** (1 zone × 5,032 days) | 2015–2030 |
| **`weather_zone_monsoon.csv`** | **5,032** (1 zone × 5,032 days) | 2015–2030 |
| **`weather_zone_imd.csv`** | **5,032** (1 zone × 5,032 days) | 2015–2030 |
| **`weather_zone_agri.csv`** | **5,032** (1 zone × 5,032 days) | 2015–2030 |

> **Current data**: Tamil Nadu only (9 cities). Years 2010–2014 and 2024–2025
> were skipped due to Open-Meteo API rate limiting (HTTP 429) during the
> initial fetch run. Re-run `fetch_weather.py --state "Tamil Nadu"` (without
> `--force`) to fill in the missing years automatically — the resume logic
> will only fetch what is absent. Run `--all-india` to expand to all 165 cities.

At full scale (165 cities, 2010–2030):

| Dataset | Rows |
|---|---|
| Raw combined CSV | ~1.27 M (165 × 7,670 days) |
| **`weather_zone_koppen.csv`** | **~38 K** (5 zones × 7,670 days) |
| **`weather_zone_monsoon.csv`** | **~38 K** (5 zones × 7,670 days) |
| **`weather_zone_imd.csv`** | **~184 K** (24 zones × 7,670 days) |
| **`weather_zone_agri.csv`** | **~46 K** (6 zones × 7,670 days) |

---

## Output Files Reference

```
data/
├── weather_daily.csv               Single-city daily weather (New Delhi default)
├── weather_india_combined.csv      All 165 cities merged, one row per city per day
├── weather_india/
│   ├── new_delhi.csv               Per-city CSV (2010-2030, ~7670 rows each)
│   ├── mumbai.csv
│   └── …  (165 files)
├── weather_zone_koppen.csv         5-zone Köppen summary (mean/median/std)
├── weather_zone_monsoon.csv        5-zone monsoon summary + onset/withdrawal flags
├── weather_zone_imd.csv            24-zone IMD summary
└── weather_zone_agri.csv           6-zone agricultural summary
```

### Column naming pattern for zone CSVs

```
<variable>_mean              — zone mean for that day
<variable>_median            — zone median for that day
<variable>_std               — zone standard deviation for that day
city_count                   — number of cities aggregated
city_list                    — comma-separated city names
season_meteo_mode            — most common meteorological season (NH 4-season)
season_india_mode            — most common Indian Ritu season
weather_category_mode        — most common WMO weather category (NaN for future rows)
```

For `weather_zone_monsoon.csv` only:
```
in_monsoon_onset_window       boolean — date within typical SW/NE monsoon arrival window
in_monsoon_withdrawal_window  boolean — date within typical retreat window
```

**Numeric variables aggregated (13 per zone):**

| Variable | Type |
|---|---|
| `temperature_2m_max/min/mean` | raw °C |
| `apparent_temperature_max/min` | raw °C (archive only; NaN for climate rows) |
| `precipitation_sum`, `rain_sum`, `snowfall_sum` | raw mm/cm |
| `temp_range` | derived °C |
| `is_rainy_day`, `is_hot_day`, `is_cold_day` | derived 0/1 flags |
| `year_norm` | derived [0,1] |

---

## How to Run

### Verify completeness and auto-fill any missing days (recommended first step)

The `--verify` flag checks **every individual day** from `2010-01-01` to
yesterday against what is in the CSV, then fetches and inserts only the
missing date ranges — no full re-fetch needed.

```bash
# Check + fill all Tamil Nadu cities
python src/data_collection/fetch_weather.py --verify --state "Tamil Nadu"

# Check + fill all 165 India cities
python src/data_collection/fetch_weather.py --verify --all-india

# Report gaps only, make no API calls
python src/data_collection/fetch_weather.py --verify --state "Tamil Nadu" --dry-run

# Single city
python src/data_collection/fetch_weather.py --verify --city mumbai
```

**How `--verify` works internally:**

1. Builds the full expected date set `[2010-01-01, yesterday]`
2. Reads the dates already in the CSV
3. Computes `missing = expected − present`
4. Groups consecutive missing dates into the fewest contiguous ranges
   (e.g. `2010-01-01 → 2014-12-31` rather than 1,826 individual requests)
5. Splits each range at the archive/climate boundary if it spans it
6. Fetches only those ranges, inserts the rows at the correct position, saves
7. Re-merges the combined CSV

Safe to run at any time — fully **idempotent**.

### Collect weather for all Indian cities (full 2010–2030)

```bash
python src/data_collection/fetch_weather.py --all-india
```

### Collect weather for a single state

```bash
python src/data_collection/fetch_weather.py --state "Tamil Nadu"
```

### Collect weather for a single city preset

```bash
python src/data_collection/fetch_weather.py --city mumbai
```

### Aggregate into zone summaries (all four zone types)

```bash
python src/preprocessing/aggregate_by_zone.py
```

### Aggregate only specific zone types

```bash
python src/preprocessing/aggregate_by_zone.py --zones koppen monsoon_zone
```

### Use a different input file or output directory

```bash
python src/preprocessing/aggregate_by_zone.py \
    --input data/weather_india_combined.csv \
    --out-dir data/zone_summaries
```

### Preview what would be fetched without making API calls

```bash
python src/data_collection/fetch_weather.py --dry-run --all-india
```

### Force re-fetch (ignore existing CSVs)

```bash
python src/data_collection/fetch_weather.py --all-india --force
```

---

## Design Decisions & Trade-offs

| Decision | Reason |
|---|---|
| **Temperature + rain only** | Wind, radiation, humidity and pressure removed to keep features focused; temperature and rain are the primary drivers of agricultural and calendar-event patterns |
| **`weather_category` string instead of raw WMO code** | The raw integer code (0–99) is hard for a model to use directly; the decoded label is a clean categorical feature. Raw code is dropped after decoding |
| **ERA5 + MRI-AGCM3-2-S stitching** | ERA5 is the most accurate historical reanalysis; MRI-AGCM3-2-S is the highest-resolution (20 km) CMIP6 model available on Open-Meteo for India |
| **Batch API (50 cities/call)** | Reduces API calls from ~3,465 (165 × 21 years) to ~168; respects free-tier rate limits |
| **Per-city CSV + combined merge** | Allows resuming interrupted runs; easy to re-fetch only one city |
| **mean + median + std per zone** | Mean for typical value; median for outlier robustness; std for within-zone diversity — all three are informative ML features |
| **4 independent zone systems** | Different ML tasks benefit from different groupings: Köppen for climate modelling, monsoon_zone for agricultural timing, IMD for weather forecasting, agri_zone for crop yield prediction |
| **`_std` column as a feature** | High std signals that the zone is internally divided on that day (e.g., a storm hit one end of the zone) — this is itself an ML-useful signal, not just noise |
| **Monsoon window boolean flags** | Encodes domain knowledge about the expected monsoon stage without requiring a model to learn calendar patterns from scratch |
| **`data_source` column** | Lets a model distinguish ERA5-observed rows from CMIP6-projected rows, which differ systematically in variance |
