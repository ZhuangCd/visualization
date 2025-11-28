import pandas as pd

from .config import DATA_FILE, SUMMARY_COLUMNS, VALID_IDEOLOGIES


def normalize_democracy(series: pd.Series) -> pd.Series:
    normalized = series.astype(str).str.strip().str.lower()
    return normalized.where(normalized.isin(["yes", "no"]), "no data")


raw_df = pd.read_csv(DATA_FILE)

df = raw_df.reindex(columns=["year", "hog_ideology", "region", "democracy", *SUMMARY_COLUMNS]).copy()
df["hog_ideology"] = df["hog_ideology"].str.lower()
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["region"] = df["region"].fillna("Unknown")
df["democracy_flag"] = normalize_democracy(df["democracy"])

map_df = raw_df.reindex(
    columns=["country_name", "hog_ideology", "year", "region", "democracy", *SUMMARY_COLUMNS]
).copy()
map_df["hog_ideology"] = map_df["hog_ideology"].str.lower()
map_df["year"] = pd.to_numeric(map_df["year"], errors="coerce").astype("Int64")
map_df = map_df[map_df["hog_ideology"].isin(VALID_IDEOLOGIES)]
map_df["democracy_flag"] = normalize_democracy(map_df["democracy"])
map_df = map_df.drop_duplicates(subset=["country_name", "year"], keep="last")

available_years = sorted(map_df["year"].dropna().unique())
min_year = int(available_years[0]) if available_years else None
max_year = int(available_years[-1]) if available_years else None


def build_year_marks(years):
    if not years:
        return {}
    first, last = years[0], years[-1]
    return {
        int(year): str(int(year))
        for year in years
        if year in (first, last) or int(year) % 10 == 0
    }


year_marks = build_year_marks(available_years)
