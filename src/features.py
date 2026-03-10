"""
Feature engineering for creator campaign intelligence.

Builds creator-level and post-level features used in scoring,
segmentation, and benchmarking analysis.
"""

import pandas as pd
import numpy as np


def add_post_features(posts_df):
    """Add derived features to the post dataset."""
    df = posts_df.copy()

    # Time features
    df["post_month"] = df["post_date"].dt.month
    df["post_quarter"] = df["post_date"].dt.quarter
    df["is_weekend"] = df["post_weekday"].isin(["Saturday", "Sunday"])

    # Content features
    df["high_hashtag"] = df["hashtag_count"] > 15
    df["long_caption"] = df["caption_length"] > 500

    # Engagement buckets
    df["er_bucket"] = pd.cut(
        df["engagement_rate"],
        bins=[0, 1, 2, 3, 5, 10, 100],
        labels=["<1%", "1-2%", "2-3%", "3-5%", "5-10%", "10%+"],
        right=False,
    )

    return df


def build_creator_features(posts_df, creators_df):
    """
    Build creator-level aggregate features from post data.
    Returns enriched creator DataFrame.
    """
    # Sponsored vs organic splits
    sponsored = posts_df[posts_df["is_sponsored"]]
    organic = posts_df[~posts_df["is_sponsored"]]

    # Sponsored engagement rate
    sp_er = sponsored.groupby("creator_id")["engagement_rate"].mean().rename("sponsored_er")
    org_er = organic.groupby("creator_id")["engagement_rate"].mean().rename("organic_er")

    # Sponsored post count
    sp_count = sponsored.groupby("creator_id").size().rename("sponsored_count")
    org_count = organic.groupby("creator_id").size().rename("organic_count")

    # Posting consistency: coefficient of variation of days between posts
    def posting_consistency(group):
        dates = group["post_date"].sort_values()
        if len(dates) < 3:
            return np.nan
        gaps = dates.diff().dt.days.dropna()
        if gaps.mean() == 0:
            return 0
        return gaps.std() / gaps.mean()

    consistency = posts_df.groupby("creator_id").apply(
        posting_consistency, include_groups=False
    ).rename("posting_cv")

    # Brand mention diversity
    brand_posts = posts_df[posts_df["has_brand_mention"]]
    brand_diversity = brand_posts.groupby("creator_id").size().rename("brand_mention_count")

    # Merge all features
    df = creators_df.copy()
    df = df.merge(sp_er, on="creator_id", how="left")
    df = df.merge(org_er, on="creator_id", how="left")
    df = df.merge(sp_count, on="creator_id", how="left")
    df = df.merge(org_count, on="creator_id", how="left")
    df = df.merge(consistency, on="creator_id", how="left")
    df = df.merge(brand_diversity, on="creator_id", how="left")

    # Fill NaN
    df["sponsored_er"] = df["sponsored_er"].fillna(0)
    df["organic_er"] = df["organic_er"].fillna(df["avg_engagement_rate"])
    df["sponsored_count"] = df["sponsored_count"].fillna(0).astype(int)
    df["organic_count"] = df["organic_count"].fillna(0).astype(int)
    df["posting_cv"] = df["posting_cv"].fillna(df["posting_cv"].median())
    df["brand_mention_count"] = df["brand_mention_count"].fillna(0).astype(int)

    # Derived features
    df["sponsored_lift"] = np.where(
        df["organic_er"] > 0,
        (df["sponsored_er"] - df["organic_er"]) / df["organic_er"] * 100,
        0
    )

    # Consistency score (lower CV = more consistent = higher score)
    max_cv = df["posting_cv"].quantile(0.95)
    df["consistency_score"] = (1 - df["posting_cv"].clip(0, max_cv) / max_cv) * 100

    return df
