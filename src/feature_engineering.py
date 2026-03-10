"""
Feature engineering for YouTube channel data.

All features are derived from observed metrics in the Global YouTube
Statistics 2023 dataset.

Features computed:
- engagement_proxy: views per subscriber (closest available proxy for ER)
- posting_intensity: uploads relative to channel age
- recent_momentum: 30-day views as share of lifetime views
- subscriber_momentum: 30-day sub growth rate
- consistency_score: composite of posting regularity and growth stability
- earnings_efficiency: estimated earnings per 1K views
"""

import os
import pandas as pd
import numpy as np
from ingest_real_data import PROCESSED_DIR


def add_engagement_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engagement proxy = total views / subscribers.
    This is the best available proxy for engagement using channel-level data.
    NOT the same as per-post engagement rate (which requires video-level data).
    """
    df["engagement_proxy"] = np.where(
        df["subscribers"] > 0,
        (df["total_views"] / df["subscribers"]).round(2),
        np.nan,
    )
    return df


def add_posting_intensity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Posting intensity = uploads / channel age in years.
    Higher values indicate more active content production.
    """
    df["posting_intensity"] = np.where(
        df["channel_age_years"] > 0,
        (df["uploads"] / df["channel_age_years"]).round(1),
        np.nan,
    )
    return df


def add_momentum_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Momentum features capture recent performance relative to lifetime.
    - recent_views_momentum: 30-day views / total views * 100
    - subscriber_momentum: 30-day sub gain / total subs * 100
    - momentum_score: normalized composite (0-100)
    """
    # Views momentum
    df["recent_views_momentum"] = np.where(
        df["total_views"] > 0,
        (df["views_last_30d"] / df["total_views"] * 100).round(3),
        np.nan,
    )

    # Subscriber momentum
    df["subscriber_momentum"] = np.where(
        df["subscribers"] > 0,
        (df["subs_gained_last_30d"] / df["subscribers"] * 100).round(4),
        np.nan,
    )

    # Composite momentum score (0-100 scale)
    views_mom = df["recent_views_momentum"].rank(pct=True, na_option="keep") * 100
    subs_mom = df["subscriber_momentum"].rank(pct=True, na_option="keep") * 100
    df["momentum_score"] = ((views_mom * 0.6 + subs_mom * 0.4)).round(1)

    return df


def add_efficiency_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Earnings efficiency = estimated monthly earnings per 1K average views.
    Uses the midpoint of estimated earnings range.
    """
    df["avg_views_per_30d"] = df["views_last_30d"]

    df["earnings_per_1k_views"] = np.where(
        df["views_last_30d"] > 0,
        (df["est_monthly_earnings_mid"] / (df["views_last_30d"] / 1000)).round(2),
        np.nan,
    )

    return df


def add_consistency_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Consistency score (0-100) based on:
    - Channel age (mature channels score higher)
    - Posting intensity (regular uploaders score higher)
    - Positive momentum (growing channels score higher)

    This is a proxy. True consistency scoring requires time-series video data.
    """
    # Age component (0-1): channels 5+ years score max
    age_score = (df["channel_age_years"].clip(upper=15) / 15).fillna(0)

    # Posting component (0-1): percentile rank of posting intensity
    post_score = df["posting_intensity"].rank(pct=True, na_option="keep").fillna(0)

    # Growth stability (0-1): positive 30d growth signals stability
    growth_positive = (df["subs_gained_last_30d"] > 0).astype(float)
    views_positive = (df["views_last_30d"] > 0).astype(float)
    growth_score = (growth_positive * 0.5 + views_positive * 0.5)

    df["consistency_score"] = ((age_score * 30 + post_score * 40 + growth_score * 30)).round(1)

    return df


def add_category_labels(df: pd.DataFrame) -> pd.DataFrame:
    """Map categories to influencer-marketing-relevant labels."""
    marketing_categories = {
        "Entertainment": "Entertainment",
        "Music": "Music",
        "People": "Lifestyle / People",
        "Games": "Gaming",
        "Comedy": "Comedy",
        "Education": "Education",
        "Film": "Film & Media",
        "Howto": "How-To & Style",
        "News": "News & Current Affairs",
        "Tech": "Tech",
        "Sports": "Sports",
        "Autos": "Autos & Vehicles",
        "Animals": "Pets & Animals",
        "Nonprofit": "Nonprofit",
    }
    df["marketing_category"] = df["channel_type"].map(marketing_categories).fillna("Other")
    return df


def engineer_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full feature engineering pipeline."""
    df = add_engagement_proxy(df)
    df = add_posting_intensity(df)
    df = add_momentum_features(df)
    df = add_efficiency_features(df)
    df = add_consistency_score(df)
    df = add_category_labels(df)
    return df


def main():
    print("Loading cleaned data...")
    path = os.path.join(PROCESSED_DIR, "channels_cleaned.csv")
    df = pd.read_csv(path)
    print(f"  {len(df)} channels loaded")

    print("Engineering features...")
    df = engineer_all_features(df)

    out_path = os.path.join(PROCESSED_DIR, "channels_featured.csv")
    df.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")

    # Summary
    feature_cols = [
        "engagement_proxy", "posting_intensity", "recent_views_momentum",
        "subscriber_momentum", "momentum_score", "earnings_per_1k_views",
        "consistency_score",
    ]
    print("\n--- Feature Summary ---")
    print(df[feature_cols].describe().round(2).to_string())


if __name__ == "__main__":
    main()
