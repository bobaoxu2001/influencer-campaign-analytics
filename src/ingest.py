"""
Data ingestion utilities.

For a production setting, this module would handle:
- Downloading raw data from Harvard Dataverse or an API
- Parsing large JSON/NDJSON files
- Loading into DuckDB or a cloud warehouse

For this portfolio project, we load pre-generated sample CSVs.
"""

import os
import pandas as pd
import duckdb

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "sample")


def load_creators(path=None):
    """Load creator sample dataset."""
    path = path or os.path.join(DATA_DIR, "creator_sample.csv")
    return pd.read_csv(path)


def load_posts(path=None):
    """Load post sample dataset."""
    path = path or os.path.join(DATA_DIR, "post_sample.csv")
    df = pd.read_csv(path, parse_dates=["post_date"])
    return df


def load_benchmarks(path=None):
    """Load case study benchmarks."""
    path = path or os.path.join(DATA_DIR, "case_study_benchmarks.csv")
    return pd.read_csv(path)


def create_duckdb_connection(db_path=":memory:"):
    """Create a DuckDB connection and register sample tables."""
    con = duckdb.connect(db_path)
    creators = load_creators()
    posts = load_posts()
    benchmarks = load_benchmarks()
    con.register("creators", creators)
    con.register("posts", posts)
    con.register("benchmarks", benchmarks)
    return con


if __name__ == "__main__":
    creators = load_creators()
    posts = load_posts()
    benchmarks = load_benchmarks()
    print(f"Creators: {len(creators)}")
    print(f"Posts: {len(posts)}")
    print(f"Benchmarks: {len(benchmarks)}")
