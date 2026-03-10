"""
Creator scoring and shortlisting framework.

Scoring dimensions:
1. Creator Fit Score — overall suitability for brand partnerships
2. Awareness Suitability Score — optimized for reach and impressions
3. Engagement Suitability Score — optimized for interaction quality
4. Risk / Data Quality Flags — caveats for partnerships teams

All scores are derived from observed metrics in the Global YouTube Statistics 2023 dataset.
"""

import os
import pandas as pd
import numpy as np
from ingest_real_data import PROCESSED_DIR


def _percentile_score(series: pd.Series) -> pd.Series:
    """Convert a series to 0-100 percentile scores."""
    return series.rank(pct=True, na_option="keep") * 100


def compute_creator_fit_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Creator Fit Score (0-100): composite measure of overall partnership suitability.

    Components:
    - Engagement proxy (25%): views per subscriber
    - Posting intensity (20%): content volume relative to age
    - Momentum (25%): recent growth trajectory
    - Consistency (20%): stability and maturity
    - Upload volume (10%): content library depth
    """
    engagement = _percentile_score(df["engagement_proxy"]) * 0.25
    posting = _percentile_score(df["posting_intensity"]) * 0.20
    momentum = _percentile_score(df["momentum_score"]) * 0.25
    consistency = _percentile_score(df["consistency_score"]) * 0.20
    uploads = _percentile_score(df["uploads"]) * 0.10

    df["creator_fit_score"] = (engagement + posting + momentum + consistency + uploads).round(1)
    return df


def compute_awareness_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Awareness Suitability Score (0-100): optimized for reach campaigns.

    Components:
    - Subscriber count (35%): audience size
    - Total views (30%): lifetime reach
    - Recent views momentum (20%): current visibility
    - Upload volume (15%): content surface area
    """
    subs = _percentile_score(df["subscribers"]) * 0.35
    views = _percentile_score(df["total_views"]) * 0.30
    recent = _percentile_score(df["views_last_30d"]) * 0.20
    uploads = _percentile_score(df["uploads"]) * 0.15

    df["awareness_score"] = (subs + views + recent + uploads).round(1)
    return df


def compute_engagement_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engagement Suitability Score (0-100): optimized for interaction quality.

    Components:
    - Engagement proxy (35%): views per subscriber
    - Avg views per video (25%): per-content performance
    - Subscriber momentum (20%): audience growth signal
    - Consistency (20%): reliability
    """
    engagement = _percentile_score(df["engagement_proxy"]) * 0.35
    avg_views = _percentile_score(df["avg_views_per_video"]) * 0.25
    sub_mom = _percentile_score(df["subscriber_momentum"]) * 0.20
    consistency = _percentile_score(df["consistency_score"]) * 0.20

    df["engagement_suitability_score"] = (engagement + avg_views + sub_mom + consistency).round(1)
    return df


def add_risk_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add data quality and risk flags for partnerships teams.

    Flags:
    - missing_30d_data: No recent 30-day metrics available
    - low_upload_volume: Fewer than 50 uploads (thin content history)
    - negative_growth: Losing subscribers in the last 30 days
    - earnings_data_missing: No earnings estimate available
    - very_high_upload_rate: Potentially a network/compilation channel
    """
    df["flag_missing_30d_data"] = df["views_last_30d"].isna()
    df["flag_low_upload_volume"] = df["uploads"] < 50
    df["flag_negative_growth"] = df["subs_gained_last_30d"] < 0
    df["flag_earnings_missing"] = df["est_monthly_earnings_mid"].isna() | (df["est_monthly_earnings_mid"] == 0)
    df["flag_very_high_uploads"] = df["uploads"] > 50000

    # Composite risk count
    flag_cols = [c for c in df.columns if c.startswith("flag_")]
    df["risk_flag_count"] = df[flag_cols].sum(axis=1).astype(int)

    return df


def generate_shortlist(
    df: pd.DataFrame,
    objective: str = "balanced",
    top_n: int = 30,
) -> pd.DataFrame:
    """
    Generate a creator shortlist ranked by the specified objective.

    Objectives:
    - balanced: creator_fit_score
    - awareness: awareness_score
    - engagement: engagement_suitability_score
    """
    score_col = {
        "balanced": "creator_fit_score",
        "awareness": "awareness_score",
        "engagement": "engagement_suitability_score",
    }.get(objective, "creator_fit_score")

    # Filter out high-risk channels
    eligible = df[df["risk_flag_count"] <= 2].copy()

    shortlist = eligible.nlargest(top_n, score_col).copy()
    shortlist["rank"] = range(1, len(shortlist) + 1)
    shortlist["objective"] = objective

    # Add recommendation label
    def _recommend(row):
        if row["awareness_score"] > 70 and row["engagement_suitability_score"] > 70:
            return "Star Creator — strong on both reach and engagement"
        elif row["awareness_score"] > 70:
            return "Awareness Driver — prioritize for reach campaigns"
        elif row["engagement_suitability_score"] > 70:
            return "Engagement Specialist — prioritize for interaction goals"
        else:
            return "Solid Performer — versatile for mixed campaigns"

    shortlist["recommendation"] = shortlist.apply(_recommend, axis=1)

    return shortlist


def score_all(df: pd.DataFrame) -> pd.DataFrame:
    """Run the full scoring pipeline."""
    df = compute_creator_fit_score(df)
    df = compute_awareness_score(df)
    df = compute_engagement_score(df)
    df = add_risk_flags(df)
    return df


def main():
    print("Loading featured data...")
    path = os.path.join(PROCESSED_DIR, "channels_featured.csv")
    df = pd.read_csv(path)
    print(f"  {len(df)} channels loaded")

    print("Computing scores...")
    df = score_all(df)

    out_path = os.path.join(PROCESSED_DIR, "channels_scored.csv")
    df.to_csv(out_path, index=False)
    print(f"  Saved to {out_path}")

    # Summary
    score_cols = ["creator_fit_score", "awareness_score", "engagement_suitability_score"]
    print("\n--- Score Summary ---")
    print(df[score_cols].describe().round(1).to_string())

    print("\n--- Top 10 by Creator Fit Score ---")
    top = df.nlargest(10, "creator_fit_score")[
        ["channel_name", "category", "follower_tier", "subscribers",
         "creator_fit_score", "awareness_score", "engagement_suitability_score"]
    ]
    print(top.to_string(index=False))

    # Generate shortlists
    for obj in ["balanced", "awareness", "engagement"]:
        sl = generate_shortlist(df, objective=obj, top_n=15)
        sl_path = os.path.join(PROCESSED_DIR, f"shortlist_{obj}.csv")
        sl.to_csv(sl_path, index=False)
        print(f"\n  Shortlist ({obj}): {len(sl)} creators → {sl_path}")


if __name__ == "__main__":
    main()
