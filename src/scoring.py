"""
Creator scoring and shortlisting for campaign partnerships.

Generates composite scores to help partnerships teams quickly
identify high-fit creators for different campaign objectives.
"""

import pandas as pd
import numpy as np


def _normalize(series, lower=0, upper=100):
    """Min-max normalize a series to [lower, upper]."""
    s_min, s_max = series.min(), series.max()
    if s_max == s_min:
        return pd.Series(50, index=series.index)
    return lower + (series - s_min) / (s_max - s_min) * (upper - lower)


def compute_creator_fit_score(df):
    """
    Composite creator fit score for brand partnerships.

    Components (equally weighted):
    - Engagement quality: organic engagement rate
    - Sponsored reliability: sponsored ER relative to organic
    - Posting consistency: regularity of posting cadence
    - Brand openness: willingness to do sponsored content
    """
    df = df.copy()

    # Component 1: Engagement quality (organic ER, normalized)
    df["_engagement_quality"] = _normalize(df["organic_er"])

    # Component 2: Sponsored reliability (how well sponsored posts perform vs organic)
    # Creators whose sponsored ER is close to or above organic ER score higher
    df["_sponsored_reliability"] = _normalize(
        df["sponsored_lift"].clip(-100, 100) + 100  # shift to positive range
    )

    # Component 3: Posting consistency
    df["_consistency"] = _normalize(df["consistency_score"])

    # Component 4: Brand openness (sponsored post rate, but not too high)
    # Optimal range: 10-40% sponsored — too low means unproven, too high means oversaturated
    optimal_rate = df["sponsored_post_rate"].clip(0, 1)
    df["_brand_openness"] = _normalize(
        1 - np.abs(optimal_rate - 0.25) * 4  # peaks at 25%
    )

    # Composite score
    df["creator_fit_score"] = (
        df["_engagement_quality"] * 0.30
        + df["_sponsored_reliability"] * 0.25
        + df["_consistency"] * 0.25
        + df["_brand_openness"] * 0.20
    ).round(1)

    # Clean up temp columns
    df = df.drop(columns=[c for c in df.columns if c.startswith("_")])

    return df


def compute_awareness_score(df):
    """
    Awareness suitability score.
    Prioritizes reach (follower count) and posting volume.
    """
    df = df.copy()
    df["awareness_score"] = (
        _normalize(np.log1p(df["followers"])) * 0.50
        + _normalize(df["total_posts"]) * 0.25
        + _normalize(df["brand_mention_count"]) * 0.25
    ).round(1)
    return df


def compute_engagement_score(df):
    """
    Engagement suitability score.
    Prioritizes engagement rate and comment quality.
    """
    df = df.copy()
    comment_ratio = df["avg_comments"] / df["avg_likes"].clip(1)
    df["engagement_suitability_score"] = (
        _normalize(df["avg_engagement_rate"]) * 0.40
        + _normalize(comment_ratio) * 0.30
        + _normalize(df["consistency_score"]) * 0.30
    ).round(1)
    return df


def generate_shortlist(df, top_n=30, objective="balanced"):
    """
    Generate a creator shortlist for partnerships teams.

    Parameters
    ----------
    df : DataFrame with scoring columns
    top_n : number of creators to shortlist
    objective : 'awareness', 'engagement', or 'balanced'

    Returns
    -------
    DataFrame of shortlisted creators with rankings
    """
    if objective == "awareness":
        sort_col = "awareness_score"
    elif objective == "engagement":
        sort_col = "engagement_suitability_score"
    else:
        sort_col = "creator_fit_score"

    shortlist = (
        df.nlargest(top_n, sort_col)
        .reset_index(drop=True)
    )
    shortlist["rank"] = range(1, len(shortlist) + 1)
    shortlist["recommendation"] = shortlist.apply(_recommendation_label, axis=1)

    return shortlist


def _recommendation_label(row):
    """Generate a human-readable recommendation for a creator."""
    labels = []
    if row.get("awareness_score", 0) > 70:
        labels.append("Strong reach")
    if row.get("engagement_suitability_score", 0) > 70:
        labels.append("High engagement")
    if row.get("consistency_score", 0) > 70:
        labels.append("Consistent poster")
    if row.get("sponsored_lift", 0) > -10:
        labels.append("Sponsored content holds up")
    return " | ".join(labels) if labels else "Review needed"
