"""
Data cleaning and validation utilities.

Handles missing values, type enforcement, outlier flagging,
and data quality checks for creator and post datasets.
"""

import pandas as pd
import numpy as np


def clean_creators(df):
    """Clean and validate creator dataset."""
    df = df.copy()

    # Enforce types
    df["followers"] = pd.to_numeric(df["followers"], errors="coerce").fillna(0).astype(int)
    df["following"] = pd.to_numeric(df["following"], errors="coerce").fillna(0).astype(int)
    df["avg_likes"] = pd.to_numeric(df["avg_likes"], errors="coerce").fillna(0).astype(int)
    df["avg_comments"] = pd.to_numeric(df["avg_comments"], errors="coerce").fillna(0).astype(int)

    # Remove creators with zero followers (unusable for ER calculations)
    df = df[df["followers"] > 0].reset_index(drop=True)

    # Cap engagement rate at reasonable bounds
    df["avg_engagement_rate"] = df["avg_engagement_rate"].clip(0, 30)

    # Standardize category names
    df["category"] = df["category"].str.strip().str.title()

    # Flag potential outliers
    df["is_outlier_er"] = df["avg_engagement_rate"] > df["avg_engagement_rate"].quantile(0.99)

    return df


def clean_posts(df):
    """Clean and validate post dataset."""
    df = df.copy()

    # Enforce types
    df["likes"] = pd.to_numeric(df["likes"], errors="coerce").fillna(0).astype(int)
    df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0).astype(int)
    df["engagement"] = df["likes"] + df["comments"]

    # Parse dates
    df["post_date"] = pd.to_datetime(df["post_date"], errors="coerce")
    df = df.dropna(subset=["post_date"]).reset_index(drop=True)

    # Recalculate engagement rate
    df["engagement_rate"] = np.where(
        df["followers_at_post"] > 0,
        (df["engagement"] / df["followers_at_post"]) * 100,
        0
    )

    # Cap extreme ERs
    df["engagement_rate"] = df["engagement_rate"].clip(0, 50)

    # Ensure boolean fields
    df["is_sponsored"] = df["is_sponsored"].astype(bool)
    df["has_brand_mention"] = df["has_brand_mention"].astype(bool)

    return df


def data_quality_report(creators_df, posts_df):
    """Generate a data quality summary."""
    report = {
        "creators_total": len(creators_df),
        "creators_with_zero_followers": (creators_df["followers"] == 0).sum(),
        "creators_missing_category": creators_df["category"].isna().sum(),
        "posts_total": len(posts_df),
        "posts_missing_date": posts_df["post_date"].isna().sum(),
        "posts_zero_engagement": (posts_df["engagement"] == 0).sum(),
        "sponsored_posts": posts_df["is_sponsored"].sum(),
        "organic_posts": (~posts_df["is_sponsored"]).sum(),
        "date_range": f"{posts_df['post_date'].min()} to {posts_df['post_date'].max()}",
        "categories": creators_df["category"].nunique(),
    }
    return report
