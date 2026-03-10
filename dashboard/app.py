"""
Creator Campaign Intelligence Dashboard

A 5-page Streamlit dashboard for partnerships teams.
Built on real YouTube channel data (Global YouTube Statistics 2023).

Usage:
    streamlit run dashboard/app.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from ingest_real_data import load_scored_channels, load_benchmarks
from scoring import generate_shortlist
from utils import COLORS, TIER_ORDER, TIER_LABELS, format_number, format_currency

# --- Page Config ---
st.set_page_config(
    page_title="Creator Campaign Intelligence",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Load Data ---
@st.cache_data
def load_data():
    channels = load_scored_channels()
    benchmarks = load_benchmarks()
    return channels, benchmarks

channels, benchmarks = load_data()
scored = channels[channels["creator_fit_score"].notna()].copy()

# --- Sidebar ---
st.sidebar.title("Creator Campaign Intelligence")
st.sidebar.caption(
    "A public-data prototype for creator marketing analytics. "
    "Built on the Global YouTube Statistics 2023 dataset (990 real channels)."
)
page = st.sidebar.radio(
    "Navigate",
    [
        "Executive Overview",
        "Creator Cohort Benchmarking",
        "Creator Shortlist",
        "Campaign Benchmarks",
        "Client-Facing Recap",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "**Data:** [Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023)  \n"
    "**Benchmarks:** [Humanz](https://humanz.com) / [Ubiquitous](https://ubiquitousinfluence.com) case studies"
)


# ============================================================
# PAGE 1: Executive Overview
# ============================================================
if page == "Executive Overview":
    st.title("Executive Overview")
    st.caption("Key metrics across 990 real YouTube channels")

    # KPI cards
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Channels Analyzed", f"{len(channels):,}")
    c2.metric("With Complete Scores", f"{len(scored):,}")
    c3.metric("Categories", f"{channels['category'].nunique()}")
    c4.metric("Countries", f"{channels['country'].nunique()}")
    c5.metric(
        "Median Fit Score",
        f"{scored['creator_fit_score'].median():.1f}",
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Channels by Category")
        cat_counts = (
            channels["category"]
            .value_counts()
            .head(12)
            .reset_index()
        )
        cat_counts.columns = ["Category", "Count"]
        fig = px.bar(
            cat_counts,
            x="Count",
            y="Category",
            orientation="h",
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Channels by Follower Tier")
        tier_counts = (
            channels["follower_tier"]
            .value_counts()
            .reindex(TIER_ORDER)
            .reset_index()
        )
        tier_counts.columns = ["Tier", "Count"]
        tier_counts["Label"] = tier_counts["Tier"].map(TIER_LABELS)
        fig = px.bar(
            tier_counts,
            x="Label",
            y="Count",
            color_discrete_sequence=[COLORS["secondary"]],
        )
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 15 Countries")
    country_counts = (
        channels["country"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    country_counts.columns = ["Country", "Channels"]
    fig = px.bar(
        country_counts,
        x="Channels",
        y="Country",
        orientation="h",
        color_discrete_sequence=[COLORS["accent"]],
    )
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=10, b=0), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE 2: Creator Cohort Benchmarking
# ============================================================
elif page == "Creator Cohort Benchmarking":
    st.title("Creator Cohort Benchmarking")
    st.caption("Performance comparisons by tier, category, and geography")

    st.subheader("Scores by Follower Tier")
    tier_scores = (
        scored.groupby("follower_tier")[
            ["creator_fit_score", "awareness_score", "engagement_suitability_score"]
        ]
        .mean()
        .reindex(TIER_ORDER)
        .round(1)
        .reset_index()
    )
    tier_scores["Label"] = tier_scores["follower_tier"].map(TIER_LABELS)
    fig = go.Figure()
    for col, name, color in [
        ("creator_fit_score", "Fit Score", COLORS["primary"]),
        ("awareness_score", "Awareness", COLORS["secondary"]),
        ("engagement_suitability_score", "Engagement", COLORS["success"]),
    ]:
        fig.add_trace(
            go.Bar(x=tier_scores["Label"], y=tier_scores[col], name=name, marker_color=color)
        )
    fig.update_layout(barmode="group", height=400, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.subheader("Engagement Proxy by Category")
    cat_eng = (
        scored[scored["category"].notna()]
        .groupby("category")
        .agg(
            channels=("channel_name", "count"),
            avg_engagement=("engagement_proxy", "mean"),
            avg_momentum=("momentum_score", "mean"),
        )
        .sort_values("avg_engagement", ascending=False)
        .round(1)
        .reset_index()
    )
    cat_eng = cat_eng[cat_eng["channels"] >= 5]
    fig = px.scatter(
        cat_eng,
        x="avg_engagement",
        y="avg_momentum",
        size="channels",
        text="category",
        color_discrete_sequence=[COLORS["primary"]],
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(
        height=500,
        xaxis_title="Avg Engagement Proxy (Views/Sub)",
        yaxis_title="Avg Momentum Score",
        margin=dict(l=0, r=0, t=30, b=0),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# PAGE 3: Creator Shortlist
# ============================================================
elif page == "Creator Shortlist":
    st.title("Creator Shortlist")
    st.caption("Objective-driven shortlists for partnerships teams")

    objective = st.selectbox(
        "Campaign Objective",
        ["balanced", "awareness", "engagement"],
        format_func=lambda x: {
            "balanced": "Balanced (overall fit)",
            "awareness": "Awareness (reach-focused)",
            "engagement": "Engagement (interaction-focused)",
        }[x],
    )
    top_n = st.slider("Number of creators", 10, 50, 20)

    shortlist = generate_shortlist(scored, objective=objective, top_n=top_n)

    # Quadrant chart
    st.subheader("Awareness vs Engagement Quadrant")
    fig = px.scatter(
        scored,
        x="awareness_score",
        y="engagement_suitability_score",
        color="follower_tier",
        category_orders={"follower_tier": TIER_ORDER},
        opacity=0.5,
        hover_data=["channel_name", "category", "subscribers"],
    )
    # Highlight shortlisted
    fig.add_trace(
        go.Scatter(
            x=shortlist["awareness_score"],
            y=shortlist["engagement_suitability_score"],
            mode="markers",
            marker=dict(size=12, color=COLORS["danger"], symbol="star"),
            name="Shortlisted",
            text=shortlist["channel_name"],
            hoverinfo="text",
        )
    )
    fig.update_layout(height=550, margin=dict(l=0, r=0, t=30, b=0))
    st.plotly_chart(fig, use_container_width=True)

    # Table
    st.subheader(f"Shortlist ({objective.title()}) — Top {top_n}")
    display_cols = [
        "rank",
        "channel_name",
        "category",
        "follower_tier",
        "subscribers",
        "creator_fit_score",
        "awareness_score",
        "engagement_suitability_score",
        "risk_flag_count",
        "recommendation",
    ]
    st.dataframe(
        shortlist[display_cols].reset_index(drop=True),
        use_container_width=True,
        height=min(len(shortlist) * 40 + 40, 600),
    )


# ============================================================
# PAGE 4: Campaign Benchmarks
# ============================================================
elif page == "Campaign Benchmarks":
    st.title("Campaign Benchmarks")
    st.caption(
        "Public KPIs from official Humanz and Ubiquitous case studies. "
        "Every value is source-attributed."
    )

    st.dataframe(
        benchmarks[
            [
                "campaign",
                "brand",
                "agency",
                "platform",
                "views",
                "impressions",
                "cpm_usd",
                "engagements",
                "paid_clicks",
                "conversions_new_users",
                "source_url",
            ]
        ],
        use_container_width=True,
    )

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("CPM Benchmarks")
        cpm_data = benchmarks[benchmarks["cpm_usd"].notna()].sort_values("cpm_usd")
        fig = px.bar(
            cpm_data,
            x="cpm_usd",
            y="campaign",
            orientation="h",
            color="cpm_usd",
            color_continuous_scale=["#10B981", "#F59E0B", "#EF4444"],
            text="cpm_usd",
        )
        fig.update_traces(texttemplate="$%{text:.2f}", textposition="outside")
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Views Benchmarks")
        views_data = benchmarks[benchmarks["views"].notna()].sort_values(
            "views", ascending=False
        )
        fig = px.bar(
            views_data,
            x="views",
            y="campaign",
            orientation="h",
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=10, b=0),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info(
        "These benchmarks are from official public case study pages. "
        "They provide directional context for campaign planning, not guaranteed outcomes."
    )


# ============================================================
# PAGE 5: Client-Facing Recap
# ============================================================
elif page == "Client-Facing Recap":
    st.title("Client-Facing Recap")
    st.caption("A summary a partnerships team could share with stakeholders")

    st.markdown("""
    ### What We Analyzed

    We evaluated **{channels} YouTube channels** from the Global YouTube Statistics 2023 dataset
    across **{categories} content categories** and **{countries} countries** to identify high-fit
    creators for brand partnership campaigns.

    ### Key Findings

    **1. The dataset's top-performing channels cluster in Entertainment and Music.**
    These categories dominate both subscriber counts and total view volume. However,
    categories like Education and How-To show higher engagement proxies relative to
    their audience size, making them strong candidates for engagement-focused campaigns.

    **2. Momentum and size are not strongly correlated.**
    Some mid-tier channels (12–30M subscribers) are growing faster than mega channels (100M+).
    Partnerships teams should weight recent momentum alongside absolute size when shortlisting.

    **3. Star Creators — those scoring high on both awareness and engagement — are rare.**
    Most channels specialize in one dimension. A well-constructed campaign brief should
    specify whether the goal is reach or interaction, then select creators accordingly.

    **4. Risk flags matter.**
    {risk_count} channels in this dataset have 3+ risk flags (missing data, negative growth,
    or potential network/compilation channels). These should be reviewed manually before
    inclusion in any shortlist.

    ### What We Recommend

    - **For awareness campaigns:** Prioritize channels in the macro/mega tiers with strong
      30-day views momentum and high upload volume.
    - **For engagement campaigns:** Look at mid-tier channels with high views-per-subscriber
      ratios, positive subscriber momentum, and consistent posting history.
    - **For balanced campaigns:** Use the Creator Fit Score to surface well-rounded channels
      that perform across multiple dimensions.

    ### Benchmark Context

    Public case studies from Humanz and Ubiquitous show that real campaigns achieve:
    - CPMs ranging from **$1.47 to $11.00**
    - Campaign views of **5M–9M+**
    - Engagement results of **225K+ interactions** and **6x industry-standard rates**

    These provide directional guidance for client expectations.

    ### Limitations

    - This analysis uses **public channel-level data**, not proprietary campaign exports
    - **Per-video engagement** (likes, comments per video) is not available in this dataset
    - **Spend, click, and conversion data** are not included — true ROI requires ad platform integration
    - Tier labels in this dataset reflect the top ~1,000 global channels (all 12M+ subscribers),
      not the standard nano/micro/macro taxonomy used in typical influencer marketing

    ---

    *Analysis produced as part of the Creator Campaign Intelligence portfolio project.*
    """.format(
        channels=len(channels),
        categories=channels["category"].nunique(),
        countries=channels["country"].nunique(),
        risk_count=len(scored[scored["risk_flag_count"] >= 3]),
    ))
