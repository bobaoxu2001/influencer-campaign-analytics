# Creator Campaign Intelligence for Partnerships Teams

> **Prototype project.** This repo demonstrates creator analytics workflow using public data. It is not a production system and does not use proprietary campaign data. See [Limitations](#limitations) for details.

A data analytics prototype that scores, segments, and shortlists YouTube creators by campaign objective — built to show how a data analyst supports partnerships teams at companies like [Humanz](https://humanz.com) and [Ubiquitous](https://ubiquitousinfluence.com).

- **990 real YouTube channels** scored across three composite dimensions (overall fit, awareness, engagement suitability)
- **Tier-based segmentation** reveals how creator size relates to engagement efficiency and momentum
- **Objective-driven shortlists** with risk-flag filtering for awareness, engagement, and balanced campaigns
- **Benchmarked against public campaign KPIs** from Humanz and Ubiquitous case studies (CPM $4–$11 range)
- **Client-ready deliverables** including quadrant charts, leaderboards, and a recap memo

---

## Dashboard Screenshots

| Awareness vs Engagement Quadrant | Creator Leaderboard |
|---|---|
| ![Awareness vs Engagement](dashboard/screenshots/awareness_vs_engagement.png) | ![Creator Leaderboard](dashboard/screenshots/creator_leaderboard.png) |

| Composite Scores by Tier | Tier Segmentation |
|---|---|
| ![Scores by Tier](dashboard/screenshots/scores_by_tier.png) | ![Tier Segmentation](dashboard/screenshots/tier_segmentation.png) |

---

## Why This Project Exists

Creator marketing platforms like Humanz and Ubiquitous help brands select creators, track campaign performance, and optimize spend. The data analyst supporting these teams needs to:

1. **Benchmark creator cohorts** — Which tiers and categories perform best for different objectives?
2. **Score and shortlist creators** — Who should a partnerships team recommend, and why?
3. **Translate metrics into business language** — Client-facing teams need clear, defensible recommendations, not raw data tables.

This project prototypes that workflow using publicly available data.

---

## Data Sources and Provenance

### What's in this repo

| Dataset | Source | Records | Type |
|---------|--------|---------|------|
| YouTube channel data | [Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023) (Kaggle) | 990 channels | Real public data |
| Campaign benchmarks | [Humanz](https://humanz.com/case-studies) and [Ubiquitous](https://ubiquitousinfluence.com/case-studies) case studies | 6 campaigns | Real public KPIs, source-attributed |

The primary dataset was collected from public YouTube channel data and published on Kaggle by Nidula Elgiriyewithana. It contains the top ~1,000 YouTube channels globally by subscriber count, with metrics including subscribers, total views, uploads, 30-day trailing performance, and estimated earnings.

A [GitHub mirror](https://github.com/IrisMejuto/Global-YouTube-Statistics) of the dataset is also available.

### What's NOT in this repo

- Per-video engagement (likes, comments on individual videos)
- Sponsored vs organic content flags
- Ad spend, click-through rates, or conversion data
- Audience demographics or brand safety scores

These would be available through the YouTube Data API or proprietary campaign platforms. This is a known limitation — see [Limitations](#limitations) below.

### Tier definitions

Because this dataset contains only the top ~1,000 global channels, all channels have 12M+ subscribers. The tier labels used in this project (mid, macro_low, macro, mega, mega_plus) reflect the distribution *within this dataset* and do not correspond to the standard nano/micro/macro taxonomy used in typical influencer marketing. This is documented throughout the analysis.

---

## Methodology

### Pipeline

```
raw data → cleaning → feature engineering → scoring → shortlisting → dashboard
```

1. **Ingestion:** Load raw CSV, validate schema and row counts
2. **Cleaning:** Remove platform-owned placeholders, standardize columns, handle nulls
3. **Feature Engineering:** Derive engagement proxy, posting intensity, momentum, consistency, earnings efficiency
4. **Scoring:** Compute Creator Fit Score, Awareness Score, Engagement Suitability Score (all 0–100, percentile-based composites)
5. **Shortlisting:** Generate objective-driven shortlists with risk flags and recommendation labels
6. **Dashboard:** 5-page Streamlit app for interactive exploration

### Feature Definitions

| Feature | Formula | What It Measures |
|---------|---------|-----------------|
| `engagement_proxy` | total_views / subscribers | Audience engagement depth (channel-level proxy) |
| `posting_intensity` | uploads / channel_age_years | Content production cadence |
| `momentum_score` | Weighted: 60% views momentum + 40% subscriber momentum | Recent growth trajectory |
| `consistency_score` | Weighted: 30% age + 40% posting + 30% growth stability | Reliability and maturity |
| `creator_fit_score` | 25% engagement + 20% posting + 25% momentum + 20% consistency + 10% uploads | Overall partnership suitability |
| `awareness_score` | 35% subscribers + 30% views + 20% recent views + 15% uploads | Reach/impression potential |
| `engagement_suitability_score` | 35% engagement proxy + 25% avg views/video + 20% sub momentum + 20% consistency | Interaction quality |

### SQL Definitions

All key metrics are also defined as SQL queries in `sql/` for use with DuckDB or any SQL-compatible warehouse.

---

## Key Findings

Based on scoring 990 real YouTube channels across the three composite dimensions:

**1. Star Creators are rare — most channels specialize in either awareness or engagement, not both.**
The awareness vs engagement quadrant chart shows that channels scoring in the top quartile on *both* dimensions are a small minority. Most high-subscriber channels score well on awareness but have below-median engagement suitability scores, while high-engagement channels tend to have smaller (within this dataset) subscriber bases. This tradeoff is the core insight for partnerships teams building multi-creator rosters.

**2. Mid-tier channels (12–30M subscribers) show stronger momentum than mega channels (100M+).**
The momentum score, which weights 60% recent views growth and 40% subscriber growth over the trailing 30-day window, is higher on average for the mid and macro_low tiers than for mega_plus channels. This suggests that partnerships teams scouting for rising talent should look beyond raw subscriber count.

**3. Category matters more for engagement efficiency than for reach.**
Entertainment and Music categories dominate total view volume, but Education, How-To, and People/Lifestyle categories show higher engagement proxy values (views/subscribers) relative to their audience size. The scores-by-tier analysis confirms that engagement suitability scores are more evenly distributed across categories than awareness scores.

**4. Risk flags meaningfully improve shortlist quality.**
Channels with 3+ risk flags (missing 30-day data, negative subscriber growth, very high upload volume suggesting network/compilation channels) score lower on the Creator Fit composite even when their raw metrics look strong. Filtering these out before shortlisting reduces false positives in creator recommendations.

---

## Creator Shortlisting Framework

The scoring framework produces three shortlists:

| Shortlist | Optimized For | Key Signals |
|-----------|---------------|-------------|
| **Balanced** | Overall fit | Composite of all dimensions |
| **Awareness** | Reach campaigns | Subscriber count, total views, 30-day views |
| **Engagement** | Interaction campaigns | Views/subscriber, avg views/video, sub momentum |

Each shortlist filters out channels with 3+ risk flags and adds a recommendation label:
- **Star Creator** — high on both awareness and engagement
- **Awareness Driver** — prioritize for reach campaigns
- **Engagement Specialist** — prioritize for interaction goals
- **Solid Performer** — versatile for mixed campaigns

---

## Benchmark Context

Public KPIs from Humanz and Ubiquitous case studies:

| Campaign | Brand | CPM | Views | Engagements | Source |
|----------|-------|-----|-------|-------------|--------|
| Lyft TikTok | Lyft | $4.31 | 8.1M | — | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/lyft) |
| Zilla Body | Zilla | $11.00 | 9.1M | 253K | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/zilla) |
| Hers | Hers | $5.00 | — | — | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/hers) |
| Absolut Vodka | Absolut | — | — | 225.8K | [Humanz](https://humanz.com/case-studies) |
| American Swiss | American Swiss | — | — | 6x industry avg | [Humanz](https://humanz.com/case-studies) |

These provide directional context for campaign planning. All values are publicly available and source-attributed.

---

## Repo Structure

```
influencer-campaign-analytics/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md                    # Data dictionary and provenance
│   ├── raw/                         # Original unmodified dataset
│   ├── processed/                   # Cleaned, featured, and scored CSVs
│   └── benchmarks/                  # Case study benchmark table
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_cleaning_and_feature_engineering.ipynb
│   ├── 03_creator_segmentation.ipynb
│   ├── 04_benchmarking.ipynb
│   └── 05_shortlisting_and_recommendations.ipynb
├── sql/
│   ├── creator_metrics.sql
│   ├── benchmark_metrics.sql
│   └── shortlist_logic.sql
├── src/
│   ├── ingest_real_data.py          # Data loading and DuckDB setup
│   ├── clean_real_data.py           # Cleaning and validation
│   ├── feature_engineering.py       # Feature derivation
│   ├── scoring.py                   # Composite scoring and shortlisting
│   ├── benchmark_loader.py          # Benchmark table creation
│   └── utils.py                     # Visualization helpers
├── dashboard/
│   ├── app.py                       # 5-page Streamlit dashboard
│   └── screenshots/                 # 10 exported chart PNGs
└── deliverables/
    ├── client_recap_sample.md       # Business-facing memo
    ├── recruiter_share_summary.md   # Project summary + email snippet
    └── resume_bullets.md            # Resume-ready bullet points
```

---

## Quick Start

**Requirements:** Python 3.10+

```bash
git clone https://github.com/bobaoxu2001/influencer-campaign-analytics.git
cd influencer-campaign-analytics

# Install dependencies
pip install -r requirements.txt

# Run the pipeline (data is already included)
cd src && python clean_real_data.py && python feature_engineering.py && python benchmark_loader.py && python scoring.py && cd ..

# Explore analysis
jupyter notebook notebooks/

# Launch dashboard
streamlit run dashboard/app.py
```

---

## Limitations

This project is a **public-data prototype**, not a production campaign analytics system.

- **Sample data from a public dataset.** The underlying CSVs are derived from the [Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023) Kaggle dataset. They are not proprietary campaign data.
- **No spend, click, or conversion data.** ROI, CPM, and CPA calculations require ad platform integration that is not available in this dataset. The benchmark KPIs are from publicly available case studies, not from internal campaign reporting.
- **Channel-level data only.** The dataset provides channel aggregates, not per-video metrics. The engagement proxy (views/subscribers) is directional but not equivalent to per-post engagement rates.
- **Top-of-market bias.** All 990 channels have 12M+ subscribers. The analysis does not cover nano, micro, or small mid-tier creators that are common in influencer marketing campaigns.
- **Snapshot data.** Metrics reflect a 2023 point-in-time snapshot. A production system would use live API data.
- **Benchmark context is directional.** Public case study KPIs provide reference points but may not reflect current market rates.

---

## What This Would Look Like in Production

| This Prototype | Production System |
|----------------|-------------------|
| Public Kaggle dataset | YouTube Data API v3 + platform APIs |
| Channel-level aggregates | Per-video engagement metrics |
| Estimated earnings | Actual campaign spend data |
| Manual benchmark table | Live campaign performance feeds |
| Static scoring | Automated weekly scoring with alerts |
| Single-platform | Multi-platform (YouTube + TikTok + Instagram) |

---

*This is a portfolio project using publicly available data. It is not affiliated with Humanz, Ubiquitous, or any creator marketing platform. All benchmark data is sourced from publicly available case studies with attribution.*
