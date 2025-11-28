from numbers import Number

import pandas as pd

from .config import VALID_IDEOLOGIES


def resolve_regions(selection):
    if not selection or "all" in selection:
        return None
    return selection


def resolve_ideologies(selection):
    return [ide for ide in selection or [] if ide in VALID_IDEOLOGIES]


def apply_multi_filter(frame, column, values):
    if values is None:
        return frame
    if not values:
        return frame.iloc[0:0]
    return frame[frame[column].isin(values)]


def is_one(value) -> bool:
    if pd.isna(value):
        return False
    try:
        return float(value) == 1.0
    except (TypeError, ValueError):
        return bool(value)


def safe_text(value, fallback="Unknown"):
    if value is None:
        return fallback
    if isinstance(value, str):
        return value.strip() or fallback
    if isinstance(value, Number):
        if pd.isna(value):
            return fallback
        if float(value).is_integer():
            return str(int(value))
        return str(value)
    if pd.isna(value):
        return fallback
    return str(value)


def format_democracy(row):
    value = row.get("democracy_flag")
    if value in (None, "no data"):
        value = row.get("democracy")
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "Unknown"
    normalized = str(value).strip().lower()
    if normalized in {"1", "yes", "democracy", "true"}:
        return "Democracy"
    if normalized in {"0", "no", "non-democracy", "false"}:
        return "Non-democracy"
    return "Unknown"


def political_leaning(row):
    if is_one(row.get("hog_left")):
        return "Left"
    if is_one(row.get("hog_center")):
        return "Center"
    if is_one(row.get("hog_right")):
        return "Right"
    ideology = row.get("hog_ideology")
    if isinstance(ideology, str) and ideology:
        return ideology.capitalize()
    return "Unknown"


def pref_value(row, primary, fallback):
    value = row.get(primary)
    if value is None or (isinstance(value, str) and not value.strip()):
        value = row.get(fallback)
    return safe_text(value)


def extract_summary_row(map_frame, country, year):
    if not country or year is None:
        return None
    country_lower = str(country).strip().lower()
    matches = map_frame[
        map_frame["country_name"].fillna("").str.lower().eq(country_lower)
        & map_frame["year"].eq(year)
    ]
    if matches.empty:
        return None
    return matches.iloc[0]


def compute_stage(has_region, regimes, ideologies, year_selected):
    stage = 0
    for idx, ready in enumerate([has_region, regimes, ideologies, year_selected], start=1):
        if not ready:
            return stage
        stage = idx
    return 4


def prepare_stage_highlight(stage, map_frame, regions, regimes, ideologies, has_region_selection):
    if stage == 0 or not has_region_selection:
        return pd.DataFrame()

    subset = map_frame
    if regions:
        subset = subset[subset["region"].isin(regions)]
    if stage >= 2:
        subset = apply_multi_filter(subset, "democracy_flag", regimes)
    if stage >= 3:
        subset = apply_multi_filter(subset, "hog_ideology", ideologies)
    return subset.drop_duplicates(subset=["country_name"])