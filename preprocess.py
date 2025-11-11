# preprocess.py
# Preprocessing pipeline for EEA E1a Parquet files based on official schema.

from __future__ import annotations
import pandas as pd
from pathlib import Path

RAW_DIR = Path("E1a")  # folder containing parquet files
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def load_raw_files() -> pd.DataFrame:
    print("=== DEBUG ===")
    print("Working directory:", Path().resolve())
    print("RAW_DIR resolved:", RAW_DIR.resolve())
    files = list(RAW_DIR.glob("*.parquet"))
    print("Files found:", files)
    print("==============")

    if not files:
        raise FileNotFoundError("No parquet files found in E1a/ folder.")

    dfs = []
    for file in files:
        try:
            df = pd.read_parquet(file)
            dfs.append(df)
        except Exception as e:
            print(f"ERROR reading file {file}: {e}")
            continue

    combined = pd.concat(dfs, ignore_index=True)
    return combined


def simplify_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only the relevant columns and rename them to standard names.
    Schema from documentation:
        Samplingpoint → station_id
        Pollutant → pollutant
        Start → datetime
        Value → value
    """
    rename_map = {
        "Samplingpoint": "station_id",
        "Pollutant": "pollutant",
        "Start": "datetime",
        "Value": "value",
    }

    df = df.rename(columns=rename_map)

    required = ["station_id", "pollutant", "datetime", "value"]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise ValueError(f"Missing columns from dataset: {missing}")

    return df[required]


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"])
    df["date"] = df["datetime"].dt.date
    return df


def aggregate_daily(df: pd.DataFrame) -> pd.DataFrame:
    # Solid daily mean per station/pollutant
    daily = df.groupby(["station_id", "pollutant", "date"], as_index=False).agg(
        value_daily=("value", "mean")
    )
    return daily


def aggregate_yearly(daily: pd.DataFrame) -> pd.DataFrame:
    daily["year"] = pd.to_datetime(daily["date"]).dt.year

    yearly = daily.groupby(["station_id", "pollutant", "year"], as_index=False).agg(
        mean=("value_daily", "mean"),
        median=("value_daily", "median"),
        p90=("value_daily", lambda x: x.quantile(0.9)),
        days=("value_daily", "size"),
    )
    return yearly


def build_minimal_station_metadata(df: pd.DataFrame) -> pd.DataFrame:
    stations = (
        df[["station_id"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return stations


def main():
    print("Loading raw parquet files...")
    raw = load_raw_files()

    print("Simplifying columns...")
    raw = simplify_columns(raw)

    print("Converting types...")
    raw = convert_types(raw)

    print("Aggregating daily data...")
    daily = aggregate_daily(raw)

    print("Aggregating yearly data...")
    yearly = aggregate_yearly(daily)

    print("Building minimal station metadata...")
    stations = build_minimal_station_metadata(raw)

    print("Saving parquet outputs...")
    daily.to_parquet(OUT_DIR / "daily.parquet", index=False)
    yearly.to_parquet(OUT_DIR / "yearly.parquet", index=False)
    stations.to_parquet(OUT_DIR / "stations.parquet", index=False)

    print("✅ Done. Processed parquet files saved.")


if __name__ == "__main__":
    main()
