# mlops-assignment

A **DVC-managed MLOps data pipeline** that collects, processes, and merges
Indian weather data and calendar/festival events into a single ML-ready
daily feature dataset.

**GitHub repo:** https://github.com/2023AC05571WILP-BITS-PILANI/mlops-assignment

---

## What This Project Does

```
Open-Meteo APIs ──→ fetch_weather.py ──→ weather_daily.csv ──┐
                                                              ├─→ merge ──→ daily_combined.csv
GitHub calendar ──→ calendar-events/*.json ──→                │     (7,670 rows × 73 columns)
                    prepare_calendar_features.py ─────────────┘     one row per day, 2010–2030
```

| Dataset | Rows | Columns | Description |
|---------|------|---------|-------------|
| Weather | 7,670 | 31 | Daily temp, rain, wind, UV, seasons for Delhi (2010–2030) |
| Calendar | 7,670 | 44 | Event flags, cyclical time encoding, rolling windows |
| **Combined** | **7,670** | **73** | All features merged on `date` — ML-ready |

---

## Quick Start

### 3 Ways to Run

#### Option A: Docker (recommended — no local deps needed)

```bash
# Full pipeline
./run.sh

# Skip slow fetch stages when data already exists
./run.sh --skip fetch_weather ingest_calendar

# Single stage
docker compose run --rm validate
docker compose run --rm merge

# Rebuild image after code changes
./run.sh --build
```

#### Option B: Local Python

```bash
pip install -r requirements.txt

# Full pipeline
python pipeline.py -v

# Skip stages / pick stages
python pipeline.py --skip fetch_weather ingest_calendar -v
python pipeline.py --stages merge_daily validate -v

# Dry run (show plan without executing)
python pipeline.py --dry-run

# List all stages
python pipeline.py --list
```

#### Option C: DVC

```bash
pip install -r requirements.txt
dvc repro                     # full pipeline (skip unchanged)
dvc repro merge_daily         # single stage
dvc repro --force             # re-run everything
dvc dag                       # view pipeline DAG
```

### Pipeline Stages

| # | Stage | Description |
|---|-------|-------------|
| 1 | **fetch_weather** | Fetches daily weather from Open-Meteo (free, no API key) |
| 2 | **ingest_calendar** | Clones calendar JSONs from GitHub |
| 3 | **prepare_calendar** | Parses JSONs → temporal features + event encoding |
| 4 | **merge_daily** | Left-joins calendar + weather → `daily_combined.csv` |
| 5 | **aggregate_zones** | Multi-city zone summaries (optional) |
| 6 | **validate** | Checks row count, date range, duplicates, coverage |

---

## Project Structure

```
mlops-assignment/
├── pipeline.py              ← master orchestrator (6 stages)
├── Dockerfile               ← containerized pipeline image
├── docker-compose.yml       ← service shortcuts (validate, merge, etc.)
├── run.sh                   ← convenience wrapper (--local / --build)
├── dvc.yaml                 ← DVC pipeline definition
├── dvc.lock                 ← auto-generated reproducibility lock
├── params.yaml              ← all configurable parameters
├── requirements.txt         ← Python dependencies
├── README.md
├── DVC_PIPELINE_README.md   ← detailed pipeline + "add new source" guide
├── .gitignore
├── .dockerignore            ← keeps Docker context small
├── .dvcignore               ← excludes junk from DVC scans
├── .github/workflows/
│   └── pipeline.yml         ← CI/CD: lint → build → run
│
├── src/
│   ├── __init__.py
│   ├── data_collection/
│   │   ├── __init__.py
│   │   ├── fetch_weather.py         ← weather from Open-Meteo API
│   │   ├── fetch_missing_years.py   ← targeted retry for gaps
│   │   ├── india_locations.py       ← ~165 city registry with zones
│   │   ├── ingest_calendar.py       ← clone calendar JSONs from GitHub
│   │   └── README.md
│   │
│   └── preprocessing/
│       ├── __init__.py
│       ├── prepare_calendar_features.py  ← calendar → ML features
│       ├── aggregate_by_zone.py          ← multi-city → zone summaries
│       └── merge_daily_features.py       ← calendar + weather → combined
│
├── data/
│   ├── calendar-events/             ← raw JSONs (2010–2030, git-tracked)
│   ├── weather_india/               ← per-city weather CSVs (generated)
│   ├── weather_daily.csv            ← single-city weather (generated)
│   ├── weather_india_combined.csv   ← all-India combined weather (generated)
│   ├── calendar_events_parsed.csv   ← parsed calendar events (generated)
│   ├── calendar_features_daily.csv  ← ML-ready calendar features (generated)
│   ├── daily_combined.csv           ← FINAL merged dataset (generated)
│   ├── weather_zone_*.csv           ← zone aggregates (generated, optional)
│   ├── WEATHER_DATA_README.md       ← weather data dictionary
│   └── CALENDAR_FEATURES_README.md  ← calendar features data dictionary
│
└── .dvc/                            ← DVC configuration
```

---

## Configuration

All parameters live in **params.yaml**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `weather.city` | `delhi` | City preset for weather collection |
| `weather.start_date` | `2010-01-01` | Start of date range |
| `weather.end_date` | `2030-12-31` | End of date range |
| `merge.join_type` | `left` | `left` (keep all days) or `inner` (only overlap) |

Change a value → `dvc repro` re-runs only the affected stages.

---

## Adding a New Data Source

See [DVC_PIPELINE_README.md](DVC_PIPELINE_README.md) for the full guide.

**TL;DR:**
1. Write a collection script in `src/data_collection/` with a `date` column
2. Add its config to `params.yaml`
3. Add a stage to `dvc.yaml`
4. Wire it as a dependency of `merge_daily`
5. Run `dvc repro`

---

## Data Sources

- **Weather:** [Open-Meteo](https://open-meteo.com/) — free, no API key
  - Archive: ERA5 reanalysis (2010 → ~7 days ago)
  - Projections: CMIP6 MRI-AGCM3-2-S (~7 days ago → 2030)
- **Calendar:** [calendar-bharat](https://github.com/jayantur13/calendar-bharat) — Indian festivals & holidays

---

## Useful Commands

| Command | Description |
|---------|-------------|
| `./run.sh` | Full pipeline in Docker |
| `./run.sh --local -v` | Full pipeline locally (verbose) |
| `python pipeline.py --list` | Show all stages & dependencies |
| `python pipeline.py --dry-run` | Preview execution plan |
| `docker compose run --rm validate` | Run just validation |
| `dvc repro` | Run full DVC pipeline (skip unchanged) |
| `dvc status` | Show which stages are out of date |
| `dvc dag` | Visualize pipeline graph |
| `dvc params diff` | Show param changes since last run |
