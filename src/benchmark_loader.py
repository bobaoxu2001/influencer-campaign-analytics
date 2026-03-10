"""
Load and validate the benchmark table from Humanz / Ubiquitous case studies.

Every row comes from a publicly available case study page with source URL.
"""

import os
import pandas as pd
from ingest_real_data import BENCHMARKS_DIR


BENCHMARKS = [
    {
        "campaign": "Lyft TikTok Campaign",
        "brand": "Lyft",
        "agency": "Ubiquitous",
        "platform": "TikTok",
        "views": 8_100_000,
        "impressions": None,
        "cpm_usd": 4.31,
        "engagements": None,
        "paid_clicks": None,
        "conversions_new_users": None,
        "engagement_rate_pct": None,
        "source_url": "https://ubiquitousinfluence.com/case-studies/lyft",
        "notes": "Target was 800K-1M impressions with ideal CPM < $15. Actual delivery far exceeded target.",
    },
    {
        "campaign": "Zilla Body Campaign",
        "brand": "Zilla",
        "agency": "Ubiquitous",
        "platform": "TikTok",
        "views": 9_100_000,
        "impressions": None,
        "cpm_usd": 11.00,
        "engagements": 253_000,
        "paid_clicks": 58_826,
        "conversions_new_users": None,
        "engagement_rate_pct": None,
        "source_url": "https://ubiquitousinfluence.com/case-studies/zilla",
        "notes": "",
    },
    {
        "campaign": "Hers Campaign",
        "brand": "Hers",
        "agency": "Ubiquitous",
        "platform": "TikTok",
        "views": None,
        "impressions": 5_000_000,
        "cpm_usd": 5.00,
        "engagements": None,
        "paid_clicks": None,
        "conversions_new_users": 11_000,
        "engagement_rate_pct": None,
        "source_url": "https://ubiquitousinfluence.com/case-studies/hers",
        "notes": "11K+ new users attributed to campaign.",
    },
    {
        "campaign": "Ubiquitous Platform Demo",
        "brand": "Various",
        "agency": "Ubiquitous",
        "platform": "TikTok",
        "views": 5_500_000,
        "impressions": None,
        "cpm_usd": 1.47,
        "engagements": None,
        "paid_clicks": None,
        "conversions_new_users": None,
        "engagement_rate_pct": None,
        "source_url": "https://ubiquitousinfluence.com",
        "notes": "Shown on How It Works page as platform capability example.",
    },
    {
        "campaign": "Absolut Vodka Campaign",
        "brand": "Absolut Vodka",
        "agency": "Humanz",
        "platform": "Instagram",
        "views": None,
        "impressions": 2_940_000,
        "cpm_usd": None,
        "engagements": 225_770,
        "paid_clicks": None,
        "conversions_new_users": None,
        "engagement_rate_pct": None,
        "source_url": "https://humanz.com/case-studies",
        "notes": "",
    },
    {
        "campaign": "American Swiss Campaign",
        "brand": "American Swiss",
        "agency": "Humanz",
        "platform": "Instagram",
        "views": None,
        "impressions": None,
        "cpm_usd": None,
        "engagements": None,
        "paid_clicks": None,
        "conversions_new_users": None,
        "engagement_rate_pct": None,
        "source_url": "https://humanz.com/case-studies",
        "notes": "Achieved 6x industry-standard engagement rate.",
    },
]


def create_benchmark_table() -> pd.DataFrame:
    """Create the benchmark DataFrame from hardcoded real public data."""
    return pd.DataFrame(BENCHMARKS)


def validate_benchmarks(df: pd.DataFrame) -> None:
    """Validate that every benchmark row has a source URL."""
    missing_sources = df[df["source_url"].isna() | (df["source_url"] == "")]
    if len(missing_sources) > 0:
        raise ValueError(
            f"{len(missing_sources)} benchmark rows are missing source URLs. "
            "Every benchmark must have verifiable public attribution."
        )
    print(f"  All {len(df)} benchmark rows have source attribution. ✓")


def main():
    os.makedirs(BENCHMARKS_DIR, exist_ok=True)

    print("Creating benchmark table from real public case studies...")
    benchmarks = create_benchmark_table()

    print("Validating...")
    validate_benchmarks(benchmarks)

    out_path = os.path.join(BENCHMARKS_DIR, "case_study_benchmarks.csv")
    benchmarks.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")

    print("\n--- Benchmark Summary ---")
    print(f"  Campaigns: {len(benchmarks)}")
    print(f"  Agencies: {benchmarks['agency'].nunique()}")
    print(f"  With views: {benchmarks['views'].notna().sum()}")
    print(f"  With CPM: {benchmarks['cpm_usd'].notna().sum()}")
    print(f"  With engagements: {benchmarks['engagements'].notna().sum()}")
    print(f"  CPM range: ${benchmarks['cpm_usd'].min():.2f} – ${benchmarks['cpm_usd'].max():.2f}")


if __name__ == "__main__":
    main()
