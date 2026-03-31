# DVC Data Pipeline — Combined Daily Features

## What This Is

A **DVC-managed pipeline** that collects, processes, and merges multiple data
sources into a single ML-ready CSV: **`data/daily_combined.csv`**.

Every row = one calendar day (2010-01-01 → 2030-12-31) with columns from:

| Source | Columns | Description |
|--------|---------|-------------|
| Calendar features | 44 | Temporal encoding, event flags, rolling windows, proximity |
| Weather observations | ~28 | Temperature, precipitation, wind, derived flags |

```
data/daily_combined.csv   →   7,670 rows  ×  ~70 columns
```

---

## Pipeline DAG

```
 ┌──────────────────┐      ┌───────────────────┐
 │  ingest_calendar │      │   fetch_weather    │
 │  (GitHub clone)  │      │   (Open-Meteo API) │
 └────────┬─────────┘      └─────────┬──────────┘
          │                           │
   data/calendar-events/       data/weather_daily.csv
          │                           │
 ┌────────▼──────────┐               │
 │ prepare_calendar   │               │
 │ (feature engineer) │               │
 └────────┬──────────┘               │
          │                           │
  data/calendar_features_daily.csv    │
          │                           │
          └──────────┬────────────────┘
                     │
              ┌──────▼───────┐
              │  merge_daily  │
              └──────┬───────┘
                     │
           data/daily_combined.csv
```

Optional side-branch (for multi-city weather):

```
  fetch_weather --all-india  →  data/weather_india_combined.csv
                                         │
                              ┌──────────▼──────────┐
                              │   aggregate_zones    │
                              └──────────┬──────────┘
                                         │
                              data/weather_zone_*.csv
```

View it live:
```bash
dvc dag
```

---

## Quick Start

### Prerequisites

```bash
pip install dvc pyyaml pandas
```

DVC is already initialized in this project (`.dvc/` exists).

### Run the full pipeline

```bash
cd mlops-assignment
dvc repro
```

DVC will execute stages in dependency order, **skipping any stage whose
inputs haven't changed** since the last run.

### Run a single stage

```bash
dvc repro fetch_weather       # only re-fetch weather
dvc repro prepare_calendar    # only re-generate calendar features
dvc repro merge_daily         # only re-merge (if upstream CSVs exist)
```

### Force re-run everything

```bash
dvc repro --force
```

---

## Configuration — `params.yaml`

All pipeline parameters live in one file at the project root.
Change a value → `dvc repro` detects it and re-runs only the affected stages.

```yaml
# Weather collection
weather:
  city: delhi                    # delhi|mumbai|chennai|kolkata|bengaluru|...
  start_date: "2010-01-01"
  end_date: "2030-12-31"
  output_csv: data/weather_daily.csv

# Calendar feature engineering
calendar:
  data_dir: data/calendar-events
  output_events_csv: data/calendar_events_parsed.csv
  output_features_csv: data/calendar_features_daily.csv

# Final merge
merge:
  calendar_csv: data/calendar_features_daily.csv
  weather_csv: data/weather_daily.csv
  output_csv: data/daily_combined.csv
  join_type: left                # left | inner
  drop_duplicate_cols:
    - year_norm
```

### Common config changes

| Want to... | Change in params.yaml |
|---|---|
| Switch city | `weather.city: mumbai` |
| Only keep days with weather | `merge.join_type: inner` |
| Narrow date range | `weather.start_date: "2020-01-01"` |
| Change output path | `merge.output_csv: data/my_dataset.csv` |

---

## Pipeline Stages Explained

### Stage 1 — `fetch_weather`

- **Script:** `src/data_collection/fetch_weather.py`
- **What:** Fetches daily weather from Open-Meteo (free, no API key)
  - Historical data (ERA5 reanalysis) up to ~7 days ago
  - Climate projections (CMIP6) for future dates
- **Output:** `data/weather_daily.csv`
- **Resume-safe:** Only fetches years not already in the CSV

### Stage 2 — `ingest_calendar`

- **Script:** `src/data_collection/ingest_calendar.py`
- **What:** Clones the `calendar-bharat` GitHub repo and copies JSON files
- **Output:** `data/calendar-events/*.json`
- **Note:** The JSONs are already checked into git — this stage rarely needs re-running

### Stage 3 — `prepare_calendar`

- **Script:** `src/preprocessing/prepare_calendar_features.py`
- **What:** Parses calendar JSONs → temporal backbone → cyclical encoding → rolling windows → target labels
- **Output:** `data/calendar_features_daily.csv` (7,670 rows × 44 cols)

### Stage 4 — `merge_daily`

- **Script:** `src/preprocessing/merge_daily_features.py`
- **What:** Left-joins calendar features + weather on `date`
- **Output:** `data/daily_combined.csv`
- **Handles:** Duplicate column detection, configurable join type

### Stage 5 — `aggregate_zones` (optional)

- **Script:** `src/preprocessing/aggregate_by_zone.py`
- **What:** Aggregates multi-city weather into zone-level summaries
- **Output:** `data/weather_zone_*.csv`
- **When:** Only after `fetch_weather --all-india`

---

## How to Add a New Data Source

This is the step-by-step guide to plug in any new dataset.

### Example: Adding air quality (AQI) data

#### Step 1 — Write the collection script

Create `src/data_collection/fetch_aqi.py`:

```python
#!/usr/bin/env python3
"""Fetch daily AQI data and save to CSV."""
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

def fetch_aqi(city: str, start: str, end: str, output: str) -> None:
    # ... your API logic here ...
    df = pd.DataFrame(...)  # must have a 'date' column
    out_path = PROJECT_ROOT / output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows → {out_path}")

if __name__ == "__main__":
    import yaml
    params = yaml.safe_load(open(PROJECT_ROOT / "params.yaml"))["aqi"]
    fetch_aqi(params["city"], params["start_date"], params["end_date"], params["output_csv"])
```

#### Step 2 — Add parameters to `params.yaml`

```yaml
# ── NEW: Air quality ─────────────────────────────────────────────────────────
aqi:
  city: delhi
  start_date: "2010-01-01"
  end_date: "2030-12-31"
  output_csv: data/aqi_daily.csv
```

#### Step 3 — Add the stage to `dvc.yaml`

Add this block **before** the `merge_daily` stage:

```yaml
  fetch_aqi:
    cmd: python src/data_collection/fetch_aqi.py
    deps:
      - src/data_collection/fetch_aqi.py
    params:
      - aqi
    outs:
      - data/aqi_daily.csv:
          cache: true
```

#### Step 4 — Wire it into the merge

Update `merge_daily` deps in `dvc.yaml` to include the new CSV:

```yaml
  merge_daily:
    cmd: python src/preprocessing/merge_daily_features.py --params params.yaml
    deps:
      - src/preprocessing/merge_daily_features.py
      - data/calendar_features_daily.csv
      - data/weather_daily.csv
      - data/aqi_daily.csv              # ← ADD THIS
    params:
      - merge
    outs:
      - data/daily_combined.csv:
          cache: true
```

Then update `merge_daily_features.py` to accept a list of extra CSVs
(or update `params.yaml` `merge.extra_csvs` — the merge script supports this).

#### Step 5 — Add to `.gitignore`

```gitignore
data/aqi_daily.csv
```

#### Step 6 — Run

```bash
dvc repro
```

DVC will detect the new stage, run `fetch_aqi`, then re-run `merge_daily`.

### Checklist for any new data source

- [ ] Script in `src/data_collection/` with a `date` column in output
- [ ] Parameters in `params.yaml` under a new top-level key
- [ ] Stage in `dvc.yaml` with correct `deps`, `params`, `outs`
- [ ] Wire as a dependency of `merge_daily` in `dvc.yaml`
- [ ] Update merge script if the join key is not `date`
- [ ] Add output CSV to `.gitignore`
- [ ] Run `dvc repro` to verify

---

## File Layout

```
mlops-assignment/
├── dvc.yaml                 ← pipeline definition (stages, deps, outs)
├── params.yaml              ← all configurable parameters
├── dvc.lock                 ← auto-generated lock file (commit to git)
│
├── src/
│   ├── data_collection/
│   │   ├── fetch_weather.py        ← Stage 1
│   │   ├── india_locations.py      ← location registry
│   │   ├── fetch_missing_years.py  ← retry helper
│   │   └── ingest_calendar.py      ← Stage 2
│   │
│   └── preprocessing/
│       ├── prepare_calendar_features.py  ← Stage 3
│       ├── aggregate_by_zone.py          ← Stage 5 (optional)
│       ├── merge_daily_features.py       ← Stage 4 (final merge)
│       └── aggregate_by_zone.py          ← Stage 5 (optional)
│
└── data/
    ├── calendar-events/        ← raw JSONs (Stage 2 output)
    ├── weather_daily.csv       ← single-city weather (Stage 1 output)
    ├── calendar_features_daily.csv   ← ML-ready calendar (Stage 3 output)
    ├── daily_combined.csv      ← FINAL merged dataset (Stage 4 output)
    └── weather_zone_*.csv      ← zone aggregates (Stage 5 output)
```

---

## Useful DVC Commands

| Command | What it does |
|---------|-------------|
| `dvc repro` | Run the full pipeline (only changed stages) |
| `dvc repro merge_daily` | Run only the merge stage + its dependencies |
| `dvc repro --force` | Force re-run everything |
| `dvc dag` | Print the pipeline DAG |
| `dvc dag --md` | Print DAG in Mermaid markdown format |
| `dvc status` | Show which stages are out of date |
| `dvc params diff` | Show parameter changes since last run |
| `dvc metrics show` | Show metrics (when training stages added) |
| `dvc push` | Push cached data to remote storage |
| `dvc pull` | Pull cached data from remote storage |

---

## Design Decisions

1. **Left join on calendar backbone** — Every day gets a row even without weather data.
   Models can learn from the missingness pattern itself.

2. **params.yaml as single source of truth** — No hardcoded paths or magic numbers.
   DVC tracks param changes automatically.

3. **persist: true on weather** — Weather fetching is slow (API rate limits).
   `persist` prevents DVC from deleting the CSV when it invalidates the cache.

4. **aggregate_zones is separate** — It depends on `--all-india` data which is
   a different (much larger) collection run. Kept as an opt-in stage.

5. **Merge script auto-detects duplicate columns** — If both CSVs have
   `year_norm`, it's silently dropped from the weather side with a warning.
