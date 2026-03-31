#!/usr/bin/env python3
"""
pipeline.py — Master orchestrator for the MLOps data pipeline
=============================================================
Runs the full pipeline or individual stages, with progress tracking,
timing, validation, and summary reporting.

Usage
-----
    # Full pipeline (all stages in order)
    python pipeline.py

    # Specific stages
    python pipeline.py --stages fetch_weather prepare_calendar
    python pipeline.py --stages merge_daily

    # List available stages
    python pipeline.py --list

    # Dry run (show what would execute)
    python pipeline.py --dry-run

    # Skip slow stages (e.g. weather fetch if data exists)
    python pipeline.py --skip fetch_weather

    # Verbose output
    python pipeline.py -v

Inside Docker
-------------
    docker compose run pipeline                         # full pipeline
    docker compose run pipeline --stages merge_daily    # single stage
"""
from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import yaml

# ── Paths ─────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent
PARAMS_FILE = PROJECT_ROOT / "params.yaml"
DATA_DIR = PROJECT_ROOT / "data"

# ── Load params ───────────────────────────────────────────────────────────────
def load_params() -> dict:
    with open(PARAMS_FILE, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ── Stage result tracking ─────────────────────────────────────────────────────
@dataclass
class StageResult:
    name: str
    status: str = "pending"      # pending | running | success | failed | skipped
    duration: float = 0.0
    output_files: list[str] = field(default_factory=list)
    row_counts: dict[str, int] = field(default_factory=dict)
    error: str = ""


# ── Stage definitions ─────────────────────────────────────────────────────────
# Each stage is a dict: name, description, function, deps (upstream stage names)

def run_fetch_weather(params: dict, verbose: bool = False) -> list[str]:
    """Stage 1: Fetch weather data from Open-Meteo."""
    wp = params["weather"]
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "data_collection" / "fetch_weather.py"),
        "--city", wp["city"],
        "--start", wp["start_date"],
        "--end", wp["end_date"],
    ]
    _run_cmd(cmd, verbose)
    return [wp["output_csv"]]


def run_ingest_calendar(params: dict, verbose: bool = False) -> list[str]:
    """Stage 2: Ingest calendar JSON files from GitHub."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "data_collection" / "ingest_calendar.py"),
    ]
    _run_cmd(cmd, verbose)
    return ["data/calendar-events"]


def run_prepare_calendar(params: dict, verbose: bool = False) -> list[str]:
    """Stage 3: Engineer calendar features."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "preprocessing" / "prepare_calendar_features.py"),
    ]
    _run_cmd(cmd, verbose)
    cp = params["calendar"]
    return [cp["output_events_csv"], cp["output_features_csv"]]


def run_merge_daily(params: dict, verbose: bool = False) -> list[str]:
    """Stage 4: Merge calendar + weather into daily_combined.csv."""
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "preprocessing" / "merge_daily_features.py"),
        "--params", str(PARAMS_FILE),
    ]
    _run_cmd(cmd, verbose)
    return [params["merge"]["output_csv"]]


def run_aggregate_zones(params: dict, verbose: bool = False) -> list[str]:
    """Stage 5 (optional): Aggregate weather by climate zone."""
    zp = params["zones"]
    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "src" / "preprocessing" / "aggregate_by_zone.py"),
        "--input", str(PROJECT_ROOT / zp["input_csv"]),
        "--out-dir", str(PROJECT_ROOT / zp["output_dir"]),
    ]
    _run_cmd(cmd, verbose)
    return [
        f"data/weather_zone_koppen.csv",
        f"data/weather_zone_monsoon.csv",
        f"data/weather_zone_imd.csv",
        f"data/weather_zone_agri.csv",
    ]


def run_validate(params: dict, verbose: bool = False) -> list[str]:
    """Stage 6: Validate the final merged dataset."""
    import pandas as pd

    output = params["merge"]["output_csv"]
    path = PROJECT_ROOT / output
    if not path.exists():
        raise FileNotFoundError(f"Merged dataset not found: {path}")

    df = pd.read_csv(path, parse_dates=["date"])
    issues = []

    # Check row count
    if len(df) < 7000:
        issues.append(f"Row count too low: {len(df)} (expected ~7670)")

    # Check date range
    min_date = df["date"].min()
    max_date = df["date"].max()
    if min_date.year > 2010:
        issues.append(f"Start date too late: {min_date.date()} (expected 2010-01-01)")
    if max_date.year < 2030:
        issues.append(f"End date too early: {max_date.date()} (expected 2030-12-31)")

    # Check for duplicate dates
    dupes = df["date"].duplicated().sum()
    if dupes > 0:
        issues.append(f"Found {dupes} duplicate dates")

    # Check weather coverage
    weather_col = "temperature_2m_max"
    if weather_col in df.columns:
        coverage = df[weather_col].notna().sum()
        pct = 100 * coverage / len(df)
        print(f"  Weather coverage: {coverage:,}/{len(df):,} days ({pct:.1f}%)")
        if pct < 50:
            issues.append(f"Weather coverage only {pct:.1f}% (expected >90%)")

    # Check calendar coverage
    cal_col = "event_count"
    if cal_col in df.columns:
        events = (df[cal_col] > 0).sum()
        print(f"  Event days: {events:,}/{len(df):,}")

    if issues:
        print(f"  ⚠️  Validation warnings:")
        for issue in issues:
            print(f"     - {issue}")
    else:
        print(f"  ✅ All validation checks passed")

    print(f"  Shape: {df.shape[0]:,} rows × {df.shape[1]} cols")
    print(f"  Date range: {min_date.date()} → {max_date.date()}")
    return [output]


# ── Stage registry ────────────────────────────────────────────────────────────
STAGES = [
    {
        "name": "fetch_weather",
        "desc": "Fetch daily weather from Open-Meteo API",
        "func": run_fetch_weather,
        "deps": [],
    },
    {
        "name": "ingest_calendar",
        "desc": "Ingest calendar JSONs from GitHub",
        "func": run_ingest_calendar,
        "deps": [],
    },
    {
        "name": "prepare_calendar",
        "desc": "Engineer calendar features (temporal + events)",
        "func": run_prepare_calendar,
        "deps": ["ingest_calendar"],
    },
    {
        "name": "merge_daily",
        "desc": "Merge calendar + weather → daily_combined.csv",
        "func": run_merge_daily,
        "deps": ["fetch_weather", "prepare_calendar"],
    },
    {
        "name": "aggregate_zones",
        "desc": "Aggregate weather by climate zone (optional)",
        "func": run_aggregate_zones,
        "deps": ["fetch_weather"],
    },
    {
        "name": "validate",
        "desc": "Validate final merged dataset",
        "func": run_validate,
        "deps": ["merge_daily"],
    },
]

STAGE_MAP = {s["name"]: s for s in STAGES}

# Default pipeline: the core stages (not aggregate_zones which needs --all-india)
DEFAULT_STAGES = [
    "fetch_weather",
    "ingest_calendar",
    "prepare_calendar",
    "merge_daily",
    "validate",
]


def _run_cmd(cmd: list[str], verbose: bool = False) -> None:
    """Run a subprocess and stream output."""
    proc = subprocess.run(
        cmd,
        cwd=str(PROJECT_ROOT),
        capture_output=not verbose,
        text=True,
    )
    if not verbose and proc.stdout:
        # Print last 20 lines of output as summary
        lines = proc.stdout.strip().split("\n")
        for line in lines[-20:]:
            print(f"  {line}")
    if proc.returncode != 0:
        err = proc.stderr if not verbose else ""
        raise RuntimeError(
            f"Command failed (exit {proc.returncode}): {' '.join(cmd)}\n{err}"
        )


def _resolve_stages(
    requested: list[str],
    skip: list[str],
) -> list[str]:
    """Topologically order requested stages, resolving dependencies."""
    to_run = set(requested) - set(skip)
    ordered = []

    def _add(name: str):
        if name in ordered or name in skip:
            return
        stage = STAGE_MAP.get(name)
        if not stage:
            raise ValueError(f"Unknown stage: {name}")
        for dep in stage["deps"]:
            if dep in to_run:
                _add(dep)
        ordered.append(name)

    for name in requested:
        _add(name)
    return ordered


def _count_rows(filepath: str) -> int:
    """Quick line-count of a CSV (minus header)."""
    path = PROJECT_ROOT / filepath
    if not path.exists() or path.is_dir():
        return -1
    with open(path) as f:
        return sum(1 for _ in f) - 1


def run_pipeline(
    stages: list[str],
    skip: list[str],
    dry_run: bool = False,
    verbose: bool = False,
) -> list[StageResult]:
    """Execute the pipeline stages in order."""
    params = load_params()
    ordered = _resolve_stages(stages, skip)

    print("=" * 65)
    print("  📊  MLOps Data Pipeline")
    print("=" * 65)
    print(f"  Stages  : {' → '.join(ordered)}")
    print(f"  Skipped : {', '.join(skip) if skip else 'none'}")
    print(f"  Params  : {PARAMS_FILE}")
    print(f"  Data dir: {DATA_DIR}")
    print(f"  Time    : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    if dry_run:
        print("\n  🏃 DRY RUN — no stages will execute\n")
        for name in ordered:
            s = STAGE_MAP[name]
            print(f"  [{name}] {s['desc']}")
        return []

    results: list[StageResult] = []

    for i, name in enumerate(ordered, 1):
        stage = STAGE_MAP[name]
        result = StageResult(name=name)
        results.append(result)

        print(f"\n{'─' * 65}")
        print(f"  [{i}/{len(ordered)}] {name} — {stage['desc']}")
        print(f"{'─' * 65}")

        result.status = "running"
        t0 = time.time()

        try:
            output_files = stage["func"](params, verbose=verbose)
            result.status = "success"
            result.output_files = output_files
            for f in output_files:
                rc = _count_rows(f)
                if rc >= 0:
                    result.row_counts[f] = rc
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            if verbose:
                traceback.print_exc()
            print(f"\n  ❌ FAILED: {e}")
            break
        finally:
            result.duration = time.time() - t0

        print(f"  ✅ {name} completed in {result.duration:.1f}s")
        for f, rc in result.row_counts.items():
            print(f"     → {f} ({rc:,} rows)")

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 65}")
    print("  PIPELINE SUMMARY")
    print(f"{'=' * 65}")
    total_time = sum(r.duration for r in results)
    for r in results:
        icon = {"success": "✅", "failed": "❌", "skipped": "⏭️"}.get(r.status, "⏳")
        print(f"  {icon}  {r.name:<25} {r.duration:>6.1f}s  {r.status}")
    print(f"{'─' * 65}")
    print(f"  Total: {total_time:.1f}s")

    failed = [r for r in results if r.status == "failed"]
    if failed:
        print(f"\n  ❌ Pipeline FAILED at stage: {failed[0].name}")
        print(f"     Error: {failed[0].error}")
        sys.exit(1)
    else:
        print(f"\n  🎉 Pipeline completed successfully!")

    return results


# ── CLI ───────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="MLOps Data Pipeline — master orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python pipeline.py                                    # full pipeline
  python pipeline.py --stages fetch_weather merge_daily # specific stages
  python pipeline.py --skip fetch_weather               # skip slow stages
  python pipeline.py --list                             # show available stages
  python pipeline.py --dry-run                          # preview execution plan
        """,
    )
    parser.add_argument(
        "--stages", nargs="+", default=None,
        help="Stages to run (default: full pipeline). Use --list to see options.",
    )
    parser.add_argument(
        "--skip", nargs="+", default=[],
        help="Stages to skip",
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all available stages and exit",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show execution plan without running",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Stream full output from each stage",
    )
    args = parser.parse_args()

    if args.list:
        print("\nAvailable pipeline stages:\n")
        for s in STAGES:
            deps = f" (depends on: {', '.join(s['deps'])})" if s["deps"] else ""
            default = " ⭐" if s["name"] in DEFAULT_STAGES else "   "
            print(f"  {default} {s['name']:<25} {s['desc']}{deps}")
        print(f"\n  ⭐ = included in default pipeline")
        print(f"\n  Use: python pipeline.py --stages <name1> <name2> ...\n")
        return

    stages = args.stages or DEFAULT_STAGES
    run_pipeline(stages, args.skip, args.dry_run, args.verbose)


if __name__ == "__main__":
    main()
