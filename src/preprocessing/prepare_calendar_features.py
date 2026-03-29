#!/usr/bin/env python3
"""
Calendar Events Feature Engineering for ML
==========================================
Loads calendar-events JSON files (2010–2030) and formulates them as
ML-ready features while preserving temporal relations.

Key Design Decisions
--------------------
1. Full date-range backbone  : one row per calendar day so the model sees
                               both event *and* non-event days.
2. Cyclical (sin/cos) encoding: periodic features (month, day-of-week,
                               day-of-year) wrap correctly at boundaries
                               (Dec→Jan, Sun→Mon) — no ordinal bias.
3. Multi-hot event aggregation: days with several events are represented
                               as multi-hot vectors + a raw count.
4. Calendar-system tagging   : extras field → Gregorian / Hindu / Islamic /
                               Parsi / Astronomy / …  as dummy features.
5. Rolling & proximity windows: recent event density (7 / 14 / 30-day
                               windows) and days-to/since the nearest event.
6. Temporal train/test split : walk-forward split to prevent data leakage.

Output files (saved to  data/ )
---------------------------------
  calendar_events_parsed.csv   – one row per raw event occurrence
  calendar_features_daily.csv  – one row per calendar day (ML-ready)

Three ready-to-use target vectors
----------------------------------
  y_binary      – is there any event today?          (0/1)
  y_multiclass  – dominant event type (4 classes)    (0-3)
  y_count       – total events on the day            (int)

Usage
-----
  python src/preprocessing/prepare_calendar_features.py
"""

import json
import re
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Path configuration ────────────────────────────────────────────────────────
SCRIPT_DIR  = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR    = PROJECT_ROOT / "data" / "calendar-events"
OUTPUT_DIR  = PROJECT_ROOT / "data"

# ── Constants ─────────────────────────────────────────────────────────────────
EVENT_TYPES = ["Religional Festival", "Government Holiday", "Good to know"]

# Priority order for resolving a single dominant label per day
TYPE_PRIORITY = {
    "Government Holiday":  3,
    "Religional Festival": 2,
    "Good to know":        1,
    "No Event":            0,
}
TYPE_LABEL_MAP = {k: v for k, v in TYPE_PRIORITY.items()}

# Regex patterns to detect which calendar system governs the event
CALENDAR_PATTERNS = {
    "gregorian_fixed": r"fixed day in Gregorian|first day of Gregorian",
    "islamic":         r"based on Islamic calendar",
    "parsi":           r"based on Parsi calendar",
    "astronomy":       r"Astronomy Event",
    "nanakshahi":      r"Nanakshahi",
    "hindu_lunar": (
        r"(Pausha|Magha|Phalguna|Chaitra|Vaishakha|Jyeshtha|Ashadha"
        r"|Shravana|Bhadrapada|Ashwina|Kartika|Margashirsha)"
        r",\s*(Shukla|Krishna)"
    ),
    "day_relative":    r"day before|day after",
}
CALENDAR_SYSTEMS = list(CALENDAR_PATTERNS.keys()) + ["other"]

# ─────────────────────────────────────────────────────────────────────────────
# Step 1 – Parse all JSON files into a flat DataFrame
# ─────────────────────────────────────────────────────────────────────────────

def parse_calendar_files(data_dir: Path) -> pd.DataFrame:
    """
    Walk every calendar-YYYY.json file and return a flat DataFrame with
    columns: [raw_date_str, event, type, extras]
    """
    records = []
    for fp in sorted(data_dir.glob("calendar-*.json")):
        with open(fp, encoding="utf-8") as fh:
            root = json.load(fh)
        year_key = next(iter(root))  # e.g. "2012"
        for _month_label, month_data in root[year_key].items():
            for date_str, ev in month_data.items():
                records.append(
                    {
                        "raw_date_str": date_str,
                        "event":  ev.get("event",  ""),
                        "type":   ev.get("type",   ""),
                        "extras": ev.get("extras", ""),
                    }
                )
    return pd.DataFrame(records)


# ─────────────────────────────────────────────────────────────────────────────
# Step 2 – Parse date strings  "January 1, 2012, Sunday" → pd.Timestamp
# ─────────────────────────────────────────────────────────────────────────────

def parse_date(date_str: str) -> pd.Timestamp:
    """
    Remove the trailing weekday then parse.
    E.g. "January 1, 2012, Sunday" → "January 1, 2012" → 2012-01-01
    """
    clean = re.sub(r",\s*\w+$", "", date_str.strip())
    return pd.to_datetime(clean, format="%B %d, %Y")


# ─────────────────────────────────────────────────────────────────────────────
# Step 3 – Detect calendar system from the extras field
# ─────────────────────────────────────────────────────────────────────────────

def classify_calendar_system(extras: str) -> str:
    for sys_name, pattern in CALENDAR_PATTERNS.items():
        if re.search(pattern, extras, re.IGNORECASE):
            return sys_name
    return "other"


# ─────────────────────────────────────────────────────────────────────────────
# Step 4 – Cyclical (sin / cos) encoding helper
# ─────────────────────────────────────────────────────────────────────────────

def cyclical_encode(series: pd.Series, period: float):
    """
    Maps a periodic feature to the unit circle.
    Ensures distance(Dec, Jan) == distance(Jan, Feb) etc.
    Returns (sin_series, cos_series).
    """
    angle = 2 * np.pi * series / period
    return np.sin(angle), np.cos(angle)


# ─────────────────────────────────────────────────────────────────────────────
# Step 5 – Build the full date-range backbone with temporal features
# ─────────────────────────────────────────────────────────────────────────────

def build_temporal_backbone(start: str = "2010-01-01",
                             end:   str = "2030-12-31") -> pd.DataFrame:
    """
    Create one row for every calendar day in [start, end].

    Raw temporal features
    ─────────────────────
      year, month, day, day_of_week, day_of_year,
      week_of_year, quarter, is_weekend, is_leap_year

    Cyclical features  (preserves periodic wrap-around)
    ────────────────────────────────────────────────────
      month_sin / month_cos      (period = 12)
      day_sin   / day_cos        (period = 31)
      dow_sin   / dow_cos        (period = 7)
      doy_sin   / doy_cos        (period = 366)
      week_sin  / week_cos       (period = 53)

    Linear trend feature
    ─────────────────────
      year_norm  ∈ [0, 1]   –  captures long-term trend without ordinal gap
    """
    dates = pd.date_range(start, end, freq="D")
    df = pd.DataFrame({"date": dates})

    # ── Raw / ordinal features ────────────────────────────────────────────────
    df["year"]        = df["date"].dt.year
    df["month"]       = df["date"].dt.month
    df["day"]         = df["date"].dt.day
    df["day_of_week"] = df["date"].dt.dayofweek          # 0 = Mon, 6 = Sun
    df["day_of_year"] = df["date"].dt.dayofyear
    df["week_of_year"]= df["date"].dt.isocalendar().week.astype(int)
    df["quarter"]     = df["date"].dt.quarter
    df["is_weekend"]  = (df["day_of_week"] >= 5).astype(int)
    df["is_leap_year"]= df["date"].dt.is_leap_year.astype(int)

    # ── Cyclical encoding ─────────────────────────────────────────────────────
    df["month_sin"],  df["month_cos"]  = cyclical_encode(df["month"],       12)
    df["day_sin"],    df["day_cos"]    = cyclical_encode(df["day"],          31)
    df["dow_sin"],    df["dow_cos"]    = cyclical_encode(df["day_of_week"],   7)
    df["doy_sin"],    df["doy_cos"]    = cyclical_encode(df["day_of_year"], 366)
    df["week_sin"],   df["week_cos"]   = cyclical_encode(df["week_of_year"], 53)

    # ── Linear trend (year) ───────────────────────────────────────────────────
    df["year_norm"] = (df["year"] - 2010) / (2030 - 2010)

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Step 6 – Aggregate per-day: multi-hot event types + calendar systems
# ─────────────────────────────────────────────────────────────────────────────

def aggregate_events(df_events: pd.DataFrame) -> pd.DataFrame:
    """
    Collapse multiple events on the same day into a single row.

    Adds
    ────
      event_count          – total events on the day
      events_list          – pipe-separated event names  (human-readable)
      has_religional_festival / has_government_holiday / has_good_to_know
      cal_<system>         – multi-hot calendar-system flags
      primary_event_type   – highest-priority type on the day
    """
    agg = (
        df_events
        .groupby("date")
        .agg(
            event_count       =("event",           "count"),
            events_list       =("event",           lambda x: "|".join(x)),
            types_list        =("type",            lambda x: "|".join(x)),
            cal_systems_list  =("calendar_system", lambda x: "|".join(x)),
        )
        .reset_index()
    )

    # Multi-hot: event types
    for et in EVENT_TYPES:
        col = "has_" + et.lower().replace(" ", "_")
        agg[col] = agg["types_list"].str.contains(et, regex=False).astype(int)

    # Multi-hot: calendar systems
    for cs in CALENDAR_SYSTEMS:
        agg[f"cal_{cs}"] = agg["cal_systems_list"].str.contains(cs, regex=False).astype(int)

    # Primary (dominant) event type for single-label tasks
    def _primary_type(types_str: str) -> str:
        best, best_pri = "Good to know", 1
        for et in EVENT_TYPES:
            if et in types_str and TYPE_PRIORITY[et] > best_pri:
                best, best_pri = et, TYPE_PRIORITY[et]
        return best

    agg["primary_event_type"] = agg["types_list"].apply(_primary_type)
    return agg


# ─────────────────────────────────────────────────────────────────────────────
# Step 7 – Rolling windows and temporal proximity features
# ─────────────────────────────────────────────────────────────────────────────

def add_temporal_context(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds look-back rolling sums and nearest-event proximity features.

    Rolling windows (lagged by 1 day – no leakage)
    ────────────────────────────────────────────────
      events_last_7d, events_last_14d, events_last_30d

    Proximity to events
    ─────────────────────
      days_since_last_event  – backward distance to previous event day
      days_to_next_event     – forward  distance to next     event day
    """
    df = df.sort_values("date").reset_index(drop=True)

    # Rolling event density (shift(1) ensures today is not included)
    for window in [7, 14, 30]:
        df[f"events_last_{window}d"] = (
            df["event_count"]
            .rolling(window, min_periods=1)
            .sum()
            .shift(1)
            .fillna(0)
            .astype(int)
        )

    # ── Proximity to nearest event – vectorised using searchsorted ────────────
    event_indices = df.index[df["event_count"] > 0].to_numpy()

    # days_since_last_event
    def _days_since(idx: int) -> int:
        pos = np.searchsorted(event_indices, idx, side="left")
        if pos == 0:
            return -1                        # no prior event in the dataset
        prev_idx = event_indices[pos - 1]
        return int(idx - prev_idx)

    # days_to_next_event
    def _days_to_next(idx: int) -> int:
        pos = np.searchsorted(event_indices, idx, side="right")
        if pos >= len(event_indices):
            return -1                        # no future event in the dataset
        next_idx = event_indices[pos]
        return int(next_idx - idx)

    df["days_since_last_event"] = [_days_since(i) for i in df.index]
    df["days_to_next_event"]    = [_days_to_next(i) for i in df.index]

    # Replace sentinel –1 with the median (boundary rows only)
    for col in ["days_since_last_event", "days_to_next_event"]:
        median_val = df.loc[df[col] >= 0, col].median()
        df[col] = df[col].replace(-1, int(median_val))

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Step 8 – Encode target labels
# ─────────────────────────────────────────────────────────────────────────────

def encode_targets(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creates three target columns:
      is_event_day       0 / 1           binary classification
      event_type_label   0–3             multi-class classification
      event_count        int             regression / Poisson modelling
    """
    df["is_event_day"] = (df["event_count"] > 0).astype(int)
    df["event_type_label"] = df.apply(
        lambda r: (
            TYPE_LABEL_MAP[r["primary_event_type"]]
            if r["event_count"] > 0
            else TYPE_LABEL_MAP["No Event"]
        ),
        axis=1,
    )
    return df


# ─────────────────────────────────────────────────────────────────────────────
# Step 9 – Temporal (walk-forward) train / test split
# ─────────────────────────────────────────────────────────────────────────────

def temporal_train_test_split(df: pd.DataFrame, test_years: int = 3):
    """
    Splits the dataset chronologically so that the test set is always in the
    future relative to training — the only correct approach for time-series.

    Parameters
    ----------
    df         : the full daily feature DataFrame
    test_years : how many years to reserve for testing (default = 3)

    Returns
    -------
    df_train, df_test
    """
    cutoff = df["date"].max() - pd.DateOffset(years=test_years)
    df_train = df[df["date"] <= cutoff].copy()
    df_test  = df[df["date"] >  cutoff].copy()
    return df_train, df_test


# ─────────────────────────────────────────────────────────────────────────────
# Step 10 – Main pipeline
# ─────────────────────────────────────────────────────────────────────────────

def build_dataset(
    data_dir: Path = DATA_DIR,
) -> tuple:
    """
    Full pipeline: parse → join → feature-engineer → encode labels.

    Returns
    -------
    df_events : pd.DataFrame   raw event records
    df_daily  : pd.DataFrame   ML-ready daily feature matrix
    """
    # ── 1. Parse raw events ───────────────────────────────────────────────────
    print("📅  Parsing calendar JSON files …")
    df_events = parse_calendar_files(data_dir)
    df_events["date"] = df_events["raw_date_str"].apply(parse_date)
    df_events["calendar_system"] = df_events["extras"].apply(classify_calendar_system)
    df_events.drop(columns=["raw_date_str"], inplace=True)
    print(f"    → {len(df_events):,} event records  |  "
          f"{df_events['date'].dt.year.nunique()} years  |  "
          f"{df_events['event'].nunique()} unique events")

    # ── 2. Temporal backbone ──────────────────────────────────────────────────
    print("📆  Building temporal backbone (2010-01-01 → 2030-12-31) …")
    backbone = build_temporal_backbone()

    # ── 3. Aggregate events per day ───────────────────────────────────────────
    print("📊  Aggregating events per day …")
    daily_events = aggregate_events(df_events)

    # ── 4. Left-join: keep every day, including non-event days ────────────────
    df = backbone.merge(daily_events, on="date", how="left")

    # Fill non-event-day columns
    df["event_count"]       = df["event_count"].fillna(0).astype(int)
    df["events_list"]       = df["events_list"].fillna("")
    df["types_list"]        = df["types_list"].fillna("")
    df["cal_systems_list"]  = df["cal_systems_list"].fillna("")
    df["primary_event_type"]= df["primary_event_type"].fillna("No Event")

    # Only cast the actual multi-hot boolean columns, not the list strings
    multihot_cols = [c for c in df.columns
                     if (c.startswith("has_") or c.startswith("cal_"))
                     and c != "cal_systems_list"]
    for col in multihot_cols:
        df[col] = df[col].fillna(0).astype(int)

    # ── 5. Temporal context (rolling / proximity) ─────────────────────────────
    print("🔄  Computing rolling windows & event proximity features …")
    df = add_temporal_context(df)

    # ── 6. Target labels ──────────────────────────────────────────────────────
    print("🏷️   Encoding target labels …")
    df = encode_targets(df)

    print(f"\n✅  Final dataset : {len(df):,} rows  ×  {len(df.columns)} columns")
    return df_events, df


# ─────────────────────────────────────────────────────────────────────────────
# CLI entry-point
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    df_events, df_daily = build_dataset()

    # ── Summaries ─────────────────────────────────────────────────────────────
    sep = "─" * 55

    print(f"\n{sep}")
    print("EVENT TYPE DISTRIBUTION")
    print(sep)
    print(df_events["type"].value_counts().to_string())

    print(f"\n{sep}")
    print("CALENDAR SYSTEM DISTRIBUTION")
    print(sep)
    print(df_events["calendar_system"].value_counts().to_string())

    print(f"\n{sep}")
    print("DAILY TARGET DISTRIBUTION  (primary_event_type)")
    print(sep)
    vc = df_daily["primary_event_type"].value_counts()
    for k, v in vc.items():
        print(f"  {k:<25}  {v:>5}  ({100*v/len(df_daily):.1f} %)")

    # ── Feature matrix ────────────────────────────────────────────────────────
    DROP_COLS = [
        "date", "events_list", "types_list", "cal_systems_list",
        "primary_event_type", "is_event_day", "event_type_label",
    ]
    X = df_daily.drop(columns=DROP_COLS)
    y_binary     = df_daily["is_event_day"]
    y_multiclass = df_daily["event_type_label"]
    y_count      = df_daily["event_count"]

    print(f"\n{sep}")
    print("ML-READY FEATURE MATRIX")
    print(sep)
    print(f"  X shape         : {X.shape}")
    print(f"  y_binary        : {dict(y_binary.value_counts().sort_index())}")
    print(f"  y_multiclass    : {dict(y_multiclass.value_counts().sort_index())}")
    print(f"  y_count         : mean={y_count.mean():.3f}  max={int(y_count.max())}")

    print(f"\n  Feature columns ({len(X.columns)}):")
    #  Group by category for readability
    groups = {
        "Raw temporal":    [c for c in X.columns if c in
                            ["year","month","day","day_of_week","day_of_year",
                             "week_of_year","quarter","is_weekend","is_leap_year"]],
        "Cyclical":        [c for c in X.columns if any(c.endswith(s) for s in
                            ["_sin","_cos"])],
        "Year trend":      [c for c in X.columns if c == "year_norm"],
        "Event multi-hot": [c for c in X.columns if c.startswith("has_")],
        "Calendar multi-hot":[c for c in X.columns if c.startswith("cal_")],
        "Rolling windows": [c for c in X.columns if c.startswith("events_last_")],
        "Proximity":       [c for c in X.columns if "since" in c or "to_next" in c],
        "Count":           [c for c in X.columns if c == "event_count"],
    }
    for grp, cols in groups.items():
        if cols:
            print(f"\n    [{grp}]")
            for c in cols:
                print(f"      {c}")

    # ── Temporal train / test split ───────────────────────────────────────────
    df_train, df_test = temporal_train_test_split(df_daily, test_years=3)
    print(f"\n{sep}")
    print("TEMPORAL TRAIN / TEST SPLIT  (test = last 3 years)")
    print(sep)
    print(f"  Train : {df_train['date'].min().date()}  →  "
          f"{df_train['date'].max().date()}  ({len(df_train):,} days)")
    print(f"  Test  : {df_test['date'].min().date()}  →  "
          f"{df_test['date'].max().date()}  ({len(df_test):,} days)")
    print(f"\n  ⚠️  Always use a temporal split — never random shuffle for")
    print(f"     time-series data (avoids future-leakage into training).")

    # ── Save ──────────────────────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    events_out = OUTPUT_DIR / "calendar_events_parsed.csv"
    daily_out  = OUTPUT_DIR / "calendar_features_daily.csv"
    df_events.to_csv(events_out, index=False)
    df_daily.to_csv(daily_out,   index=False)
    print(f"\n{sep}")
    print("SAVED")
    print(sep)
    print(f"  {events_out}")
    print(f"  {daily_out}")


if __name__ == "__main__":
    main()
