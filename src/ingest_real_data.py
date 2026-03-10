"""
Ingest YouTube channel data from the Global YouTube Statistics 2023 dataset.

Data source:
    Global YouTube Statistics 2023 by Nidula Elgiriyewithana
    https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023
    GitHub mirror: https://github.com/IrisMejuto/Global-YouTube-Statistics

Dataset: 995 YouTube channels with subscribers, views, uploads, categories,
countries, 30-day performance metrics, and estimated earnings.
"""

import os
import pandas as pd
import duckdb


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
RAW_PATH = os.path.join(DATA_DIR, "raw", "global_youtube_statistics.csv")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
BENCHMARKS_DIR = os.path.join(DATA_DIR, "benchmarks")


def load_raw_channels() -> pd.DataFrame:
    """Load the raw Global YouTube Statistics CSV."""
    if not os.path.exists(RAW_PATH):
        raise FileNotFoundError(
            f"Raw dataset not found at {RAW_PATH}. "
            "Download from: https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023"
        )
    df = pd.read_csv(RAW_PATH, encoding="latin-1")
    return df


def load_processed_channels() -> pd.DataFrame:
    """Load the cleaned and processed channel dataset."""
    path = os.path.join(PROCESSED_DIR, "channels_cleaned.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Processed dataset not found at {path}. Run clean_real_data.py first."
        )
    return pd.read_csv(path)


def load_scored_channels() -> pd.DataFrame:
    """Load the scored channel dataset with all features."""
    path = os.path.join(PROCESSED_DIR, "channels_scored.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Scored dataset not found at {path}. Run scoring.py first."
        )
    return pd.read_csv(path)


def load_benchmarks() -> pd.DataFrame:
    """Load the case study benchmark table."""
    path = os.path.join(BENCHMARKS_DIR, "case_study_benchmarks.csv")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Benchmark file not found at {path}. Run benchmark_loader.py first."
        )
    return pd.read_csv(path)


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Create a DuckDB in-memory connection with channel data loaded."""
    con = duckdb.connect()

    channels_path = os.path.join(PROCESSED_DIR, "channels_cleaned.csv")
    if os.path.exists(channels_path):
        con.execute(f"""
            CREATE TABLE channels AS
            SELECT * FROM read_csv_auto('{channels_path}')
        """)

    scored_path = os.path.join(PROCESSED_DIR, "channels_scored.csv")
    if os.path.exists(scored_path):
        con.execute(f"""
            CREATE TABLE channels_scored AS
            SELECT * FROM read_csv_auto('{scored_path}')
        """)

    benchmarks_path = os.path.join(BENCHMARKS_DIR, "case_study_benchmarks.csv")
    if os.path.exists(benchmarks_path):
        con.execute(f"""
            CREATE TABLE benchmarks AS
            SELECT * FROM read_csv_auto('{benchmarks_path}')
        """)

    return con


if __name__ == "__main__":
    df = load_raw_channels()
    print(f"Loaded {len(df)} real YouTube channels")
    print(f"Columns: {list(df.columns)}")
    print(f"Categories: {df['category'].nunique()} unique")
    print(f"Countries: {df['Country'].nunique()} unique")
