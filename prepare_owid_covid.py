# prepare_owid_covid.py
# Downloads OWID CSV, keeps essential columns, cleans, writes full_cleaned.csv + splits
import sys
from pathlib import Path
import requests
import pandas as pd

URL = "covid_19_clean_complete.csv"
OUT_DIR = Path("covid_output")
OUT_DIR.mkdir(exist_ok=True)
DEST = OUT_DIR / "covid_19_clean_complete.csv"
KEEP_COLS = [
    "iso_code","continent","location","date",
    "total_cases","new_cases","total_deaths","new_deaths",
    "total_vaccinations","people_vaccinated","people_fully_vaccinated",
    "new_vaccinations","total_tests","new_tests","positive_rate",
    "population","median_age","population_density","aged_65_older","gdp_per_capita","stringency_index"
]

def download_csv(url, dest):
    print("Downloading OWID CSV. This can take a minute...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=8_000_000):
            if chunk:
                f.write(chunk)
    print("Downloaded:", dest)

def load_clean(dest):
    print("Reading CSV...")
    df = pd.read_csv(dest, parse_dates=["date"], low_memory=False)
    # keep only relevant columns if available
    cols = [c for c in KEEP_COLS if c in df.columns] + ["date","location"]
    cols = list(dict.fromkeys(cols))
    df = df[cols].copy()
    # basic cleaning
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.sort_values(["location","date"]).drop_duplicates(["location","date"], keep="last")
    # forward/backward fill numeric per country for smoother visuals
    num_cols = df.select_dtypes(include=["float64","int64"]).columns.tolist()
    df[num_cols] = df.groupby("location")[num_cols].apply(lambda g: g.ffill().bfill())
    return df

def export(df):
    out_full = OUT_DIR / "full_cleaned.csv"
    df.to_csv(out_full, index=False)
    print("Wrote:", out_full)
    # splits
    cases_cols = [c for c in ["iso_code","continent","location","date","total_cases","new_cases","population"] if c in df.columns]
    (OUT_DIR / "cases.csv").write_text("")
    df[cases_cols].to_csv(OUT_DIR / "cases.csv", index=False)
    deaths_cols = [c for c in ["iso_code","continent","location","date","total_deaths","new_deaths","population"] if c in df.columns]
    df[deaths_cols].to_csv(OUT_DIR / "deaths.csv", index=False)
    vacc_cols = [c for c in ["iso_code","continent","location","date","total_vaccinations","people_vaccinated","people_fully_vaccinated","new_vaccinations","population"] if c in df.columns]
    df[vacc_cols].to_csv(OUT_DIR / "vaccinations.csv", index=False)
    static_cols = [c for c in ["iso_code","location","continent","population","median_age","population_density","aged_65_older","gdp_per_capita"] if c in df.columns]
    latest = df.sort_values("date").groupby("location").tail(1)[static_cols]
    latest.to_csv(OUT_DIR / "population.csv", index=False)
    df.head(500).to_csv(OUT_DIR / "sample_head.csv", index=False)
    print("Exported split CSVs in folder:", OUT_DIR)

def main():
    if not DEST.exists():
        try:
            download_csv(URL, DEST)
        except Exception as e:
            print("Download failed:", e)
            sys.exit(1)
    df = load_clean(DEST)
    export(df)
    print("All done. Use file:", OUT_DIR / "full_cleaned.csv")

if __name__ == "__main__":
    main()
