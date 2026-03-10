"""
Creator Campaign Intelligence Dashboard
========================================

A 4-page Streamlit dashboard for partnerships teams.

Run: streamlit run dashboard/app.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from src.ingest import load_creators, load_posts, load_benchmarks
from src.clean import clean_creators, clean_posts
from src.features import add_post_features, build_creator_features
from src.scoring import (
    compute_creator_fit_score,
    compute_awareness_score,
    compute_engagement_score,
    generate_shortlist,
)
from src.utils import format_number

# --- Page Config ---
st.set_page_config(
    page_title="Creator Campaign Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load & Process Data ---
@st.cache_data
def load_data():
    creators = clean_creators(load_creators())
    posts = add_post_features(clean_posts(load_posts()))
    benchmarks = load_benchmarks()
    creators_enriched = build_creator_features(posts, creators)
    scored = compute_creator_fit_score(creators_enriched)
    scored = compute_awareness_score(scored)
    scored = compute_engagement_score(scored)
    return scored, posts, benchmarks

scored, posts, benchmarks = load_data()

# --- Sidebar ---
st.sidebar.title("Creator Campaign Intelligence")
st.sidebar.markdown("*Partnerships Analytics Demo*")
page = st.sidebar.radio(
    "Navigate",
    ["Executive Overview", "Sponsored Content Benchmarking",
     "Creator Shortlisting", "Partnerships Recap"],
)
st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data:** Sample based on Seungbae Kim's Instagram Influencer Dataset schema"
)
st.sidebar.markdown(
    "**Benchmarks:** Public case studies from Humanz / Ubiquitous"
)

# === PAGE 1: EXECUTIVE OVERVIEW ===
if page == "Executive Overview":
    st.title("Executive Overview")
    st.markdown("High-level metrics for the partnerships team.")

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Creators Analyzed", format_number(len(scored)))
    col2.metric("Posts Analyzed", format_number(len(posts)))
    col3.metric("Sponsored Share", f"{posts['is_sponsored'].mean()*100:.1f}%")
    col4.metric("Avg Engagement Rate", f"{posts['engagement_rate'].mean():.2f}%")
    col5.metric("Content Categories", str(scored['category'].nunique()))

    st.markdown("---")

    # Two columns
    left, right = st.columns(2)

    with left:
        st.subheader("Creators by Follower Tier")
        tier_order = ["nano", "micro", "mid", "macro", "mega"]
        tier_counts = scored["follower_tier"].value_counts().reindex(tier_order).reset_index()
        tier_counts.columns = ["Tier", "Count"]
        fig = px.bar(tier_counts, x="Tier", y="Count",
                     color="Tier", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Engagement Rate by Tier")
        tier_er = scored.groupby("follower_tier")["avg_engagement_rate"].median().reindex(tier_order).reset_index()
        tier_er.columns = ["Tier", "Median ER (%)"]
        fig = px.bar(tier_er, x="Tier", y="Median ER (%)",
                     color="Tier", color_discrete_sequence=px.colors.sequential.Blues_r)
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    # Category table
    st.subheader("Category Benchmarks")
    cat_summary = scored.groupby("category").agg(
        creators=("creator_id", "count"),
        avg_followers=("followers", "mean"),
        avg_er=("avg_engagement_rate", "mean"),
        avg_sponsored_rate=("sponsored_post_rate", "mean"),
    ).round(2).sort_values("avg_er", ascending=False)
    cat_summary["avg_followers"] = cat_summary["avg_followers"].apply(format_number)
    cat_summary["avg_sponsored_rate"] = (cat_summary["avg_sponsored_rate"] * 100).round(1).astype(str) + "%"
    st.dataframe(cat_summary, use_container_width=True)

    # Benchmark snippets
    st.subheader("Industry Benchmarks (Public Case Studies)")
    st.dataframe(
        benchmarks[["campaign", "brand", "agency", "views", "impressions", "cpm_usd", "engagements"]],
        use_container_width=True,
    )

# === PAGE 2: SPONSORED CONTENT BENCHMARKING ===
elif page == "Sponsored Content Benchmarking":
    st.title("Sponsored Content Benchmarking")
    st.markdown("How does sponsored content perform compared to organic?")

    # Overall comparison
    col1, col2, col3 = st.columns(3)
    sp = posts[posts["is_sponsored"]]
    org = posts[~posts["is_sponsored"]]
    col1.metric("Sponsored Avg ER", f"{sp['engagement_rate'].mean():.2f}%")
    col2.metric("Organic Avg ER", f"{org['engagement_rate'].mean():.2f}%")
    delta = sp["engagement_rate"].mean() - org["engagement_rate"].mean()
    col3.metric("ER Gap", f"{delta:+.2f}%")

    st.markdown("---")

    # By tier
    st.subheader("Sponsored vs Organic ER by Follower Tier")
    tier_comp = posts.groupby(["follower_tier", "is_sponsored"])["engagement_rate"].mean().reset_index()
    tier_comp["Type"] = tier_comp["is_sponsored"].map({True: "Sponsored", False: "Organic"})
    fig = px.bar(tier_comp, x="follower_tier", y="engagement_rate", color="Type",
                 barmode="group", category_orders={"follower_tier": ["nano", "micro", "mid", "macro", "mega"]},
                 color_discrete_map={"Organic": "#2563EB", "Sponsored": "#F59E0B"})
    fig.update_layout(height=400, yaxis_title="Avg Engagement Rate (%)")
    st.plotly_chart(fig, use_container_width=True)

    # By category
    st.subheader("Sponsored ER Lift by Category")
    cat_comp = posts.groupby(["category", "is_sponsored"])["engagement_rate"].mean().unstack()
    cat_comp.columns = ["Organic", "Sponsored"]
    cat_comp["Lift (%)"] = ((cat_comp["Sponsored"] - cat_comp["Organic"]) / cat_comp["Organic"] * 100).round(1)
    cat_comp = cat_comp.sort_values("Lift (%)", ascending=False)
    fig = px.bar(cat_comp.reset_index(), x="Lift (%)", y="category", orientation="h",
                 color="Lift (%)", color_continuous_scale=["#EF4444", "#F59E0B", "#10B981"])
    fig.update_layout(height=500, yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

    # Posting frequency
    st.subheader("Engagement by Posting Hour")
    time_er = posts.groupby(["post_hour", "is_sponsored"])["engagement_rate"].mean().reset_index()
    time_er["Type"] = time_er["is_sponsored"].map({True: "Sponsored", False: "Organic"})
    fig = px.line(time_er, x="post_hour", y="engagement_rate", color="Type",
                  color_discrete_map={"Organic": "#2563EB", "Sponsored": "#F59E0B"})
    fig.update_layout(height=350, xaxis_title="Hour of Day", yaxis_title="Avg ER (%)")
    st.plotly_chart(fig, use_container_width=True)

# === PAGE 3: CREATOR SHORTLISTING ===
elif page == "Creator Shortlisting":
    st.title("Creator Shortlisting")
    st.markdown("Identify high-fit creators for brand campaigns.")

    # Objective selector
    objective = st.selectbox("Campaign Objective", ["Balanced", "Awareness", "Engagement"])
    top_n = st.slider("Shortlist Size", 10, 50, 30)

    obj_map = {"Balanced": "balanced", "Awareness": "awareness", "Engagement": "engagement"}
    shortlist = generate_shortlist(scored, top_n=top_n, objective=obj_map[objective])

    # KPIs
    col1, col2, col3 = st.columns(3)
    col1.metric("Shortlisted Creators", len(shortlist))
    col2.metric("Avg Fit Score", f"{shortlist['creator_fit_score'].mean():.1f}")
    col3.metric("Avg ER", f"{shortlist['avg_engagement_rate'].mean():.2f}%")

    # Quadrant chart
    st.subheader("Awareness vs Engagement Quadrant")
    fig = px.scatter(
        scored, x="awareness_score", y="engagement_suitability_score",
        color="follower_tier", size="creator_fit_score",
        hover_data=["creator_id", "category", "followers"],
        category_orders={"follower_tier": ["nano", "micro", "mid", "macro", "mega"]},
        color_discrete_sequence=px.colors.sequential.Blues_r,
        opacity=0.6,
    )
    aw_med = scored["awareness_score"].median()
    en_med = scored["engagement_suitability_score"].median()
    fig.add_hline(y=en_med, line_dash="dash", line_color="gray", opacity=0.4)
    fig.add_vline(x=aw_med, line_dash="dash", line_color="gray", opacity=0.4)
    fig.update_layout(height=500, xaxis_title="Awareness Score", yaxis_title="Engagement Score")
    st.plotly_chart(fig, use_container_width=True)

    # Shortlist table
    st.subheader(f"Top {top_n} Creators — {objective} Objective")
    display_cols = [
        "rank", "creator_id", "category", "follower_tier", "followers",
        "avg_engagement_rate", "sponsored_er", "creator_fit_score",
        "awareness_score", "engagement_suitability_score", "recommendation",
    ]
    st.dataframe(shortlist[display_cols], use_container_width=True, hide_index=True)

    # Tier distribution in shortlist
    st.subheader("Shortlist Tier Mix")
    tier_mix = shortlist["follower_tier"].value_counts().reset_index()
    tier_mix.columns = ["Tier", "Count"]
    fig = px.pie(tier_mix, values="Count", names="Tier",
                 color_discrete_sequence=px.colors.sequential.Blues_r)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# === PAGE 4: PARTNERSHIPS RECAP ===
elif page == "Partnerships Recap":
    st.title("Partnerships Recap")
    st.markdown("Summary insights for client-facing teams — what to tell the client.")

    st.markdown("---")

    st.subheader("1. Key Findings")
    st.markdown("""
    - **Micro and mid-tier creators** deliver the strongest combination of engagement quality and
      sponsored content reliability across our dataset of 500 creators and ~25K posts
    - **Sponsored content shows a moderate engagement dip on average**, but specific categories
      and creator profiles maintain strong performance — the gap is not universal
    - **Posting consistency** is a reliable predictor of sustained engagement quality
    """)

    st.subheader("2. Recommended Creator Mix")
    col1, col2, col3 = st.columns(3)
    col1.markdown("""
    **Awareness Plays**
    - Macro/mega creators for reach
    - Focus on categories with broad appeal
    - Target 50K+ followers
    """)
    col2.markdown("""
    **Engagement Plays**
    - Micro/nano creators for interaction
    - Niche categories with loyal audiences
    - Prioritize high comment-to-like ratios
    """)
    col3.markdown("""
    **Balanced Campaigns**
    - Mid-tier creators as anchors
    - Mix 2-3 categories for diversity
    - Weight consistency in selection
    """)

    st.subheader("3. KPI Focus Areas")
    st.markdown("""
    | KPI | Benchmark Range | Source |
    |-----|----------------|--------|
    | CPM | $1.47 – $11.00 | Ubiquitous case studies |
    | Engagement Rate | 0.5% – 8.0% | Varies by tier |
    | Sponsored ER Lift | -15% to +5% typical | Dataset analysis |
    | Impressions per campaign | 2.9M – 8.1M | Humanz / Ubiquitous cases |
    """)

    st.subheader("4. What to Monitor")
    st.markdown("""
    - **Sponsored engagement decay:** Track whether individual creators' sponsored ER drops over
      successive brand collaborations
    - **Category saturation:** Some categories show diminishing sponsored engagement returns as
      sponsored post rates increase
    - **Posting cadence changes:** Creators who shift from consistent to irregular posting may
      signal disengagement
    """)

    st.subheader("5. What to Test Next")
    st.markdown("""
    - **A/B test creator tiers:** Run parallel micro vs mid-tier campaigns for the same brand to
      quantify the engagement vs reach tradeoff
    - **Hashtag optimization:** Moderate hashtag counts (5-15) correlate with better sponsored ER — test
      this as a content guideline
    - **Time-of-day scheduling:** Sponsored and organic posts show different hourly engagement
      patterns — test optimized posting windows
    """)

    st.markdown("---")
    st.markdown(
        "*This dashboard uses sample data based on the schema of Seungbae Kim's Instagram "
        "Influencer Dataset. Benchmarks are sourced from public Humanz / Ubiquitous case studies. "
        "For a production deployment, this pipeline would connect to live campaign data and "
        "real-time creator APIs.*"
    )
