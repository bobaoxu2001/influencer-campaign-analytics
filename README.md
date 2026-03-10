# Influencer Campaign Analytics Prototype

> **This repository is an earlier prototype exploring creator campaign analytics workflows.** My latest real-data portfolio version (YouTube Data API–based) is at [Creator Campaign Intelligence](https://github.com/bobaoxu2001/youtube_creator_data_pipeline).

---

## Why This Project Exists

If I were supporting the partnerships team at a creator-marketing platform like [Humanz](https://humanz.com) or [Ubiquitous](https://ubiquitousinfluence.com), how would I use public creator data to:

1. **Benchmark sponsored content performance** against organic baselines
2. **Identify high-fit creators** for different campaign objectives
3. **Summarize campaign-relevant insights** for client-facing teams

This project simulates that workflow. It uses a sampled subset of a public influencer dataset (see Data Sources) to benchmark creator cohorts, compare sponsored vs organic engagement, and generate shortlist recommendations for partnerships teams.

---

## Key Insights

### 1. Micro and mid-tier creators are the strongest partnership candidates

They deliver the best combination of engagement quality, sponsored content reliability, and posting consistency. Larger creators have reach but show steeper sponsored engagement drops.

### 2. Sponsored content doesn't always underperform

The engagement gap varies significantly by category and follower tier. Certain categories (Fitness, Food, Health) and certain creator profiles maintain near-organic engagement even with sponsorship disclosures.

### 3. Partnerships teams should shortlist by objective, not just by size

Our scoring framework segments creators into four cohorts:

| Cohort | Profile | Best For |
|--------|---------|----------|
| Star Creators | High reach + high engagement | Anchor placements |
| Engagement Specialists | Niche audiences + strong interaction | Community campaigns |
| Awareness Drivers | Large follower base + broad reach | Impression goals |
| Emerging Creators | Growing audiences + improving metrics | Early partnerships |

---

## Data Sources

### Primary Dataset

**Seungbae Kim's Instagram Influencer Dataset / Influencer and Brand Dataset**
- [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OQAQWK)
- Full dataset: 33,935 influencers, 10M+ Instagram posts
- Fields: caption, hashtags, timestamp, sponsorship flag, likes, comments
- **This repo uses pre-generated sample CSVs** (500 creators, ~25K posts) plus a reproducible sampling script. These samples are a subset of the public dataset — useful for prototyping, not production.

### Benchmark Layer

Public KPIs from official Humanz and Ubiquitous case studies:

| Campaign | Brand | Views | CPM | Engagements | Source |
|----------|-------|-------|-----|-------------|--------|
| Lyft TikTok | Lyft | 8.1M | $4.31 | — | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/lyft) |
| Zilla Body | Zilla | 9.1M | $11.00 | 253K | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/zilla) |
| Hers Campaign | Hers | — | $5.00 | — | [Ubiquitous](https://ubiquitousinfluence.com/case-studies/hers) |
| Absolut Vodka | Absolut | — | — | 225.8K | [Humanz](https://humanz.com/case-studies) |
| American Swiss | American Swiss | — | — | 6x industry standard | [Humanz](https://humanz.com/case-studies) |

All benchmark values are publicly available. No values were fabricated.

---

## Methodology

### Feature Engineering

| Feature | Description |
|---------|-------------|
| `engagement_rate` | (likes + comments) / followers x 100 |
| `sponsored_er` / `organic_er` | Engagement rate split by post type |
| `sponsored_lift` | % change in ER for sponsored vs organic |
| `consistency_score` | Inverse of posting cadence variability (0-100) |
| `creator_fit_score` | Composite: engagement quality + sponsored reliability + consistency + brand openness |
| `awareness_score` | Weighted: reach + volume + brand mention breadth |
| `engagement_suitability_score` | Weighted: ER + comment quality + consistency |

### Analysis Pipeline

1. **Data Audit** — Quality checks, distribution analysis, missing value assessment
2. **Feature Engineering** — Creator-level aggregations, sponsored/organic splits, derived metrics
3. **Sponsored vs Organic Analysis** — Tier-level and category-level comparisons, posting pattern analysis
4. **Creator Scoring & Shortlisting** — Composite scoring, quadrant segmentation, objective-driven shortlists

### SQL Metric Definitions

All key metrics are also defined as SQL queries in `sql/` for use with DuckDB or any SQL-compatible warehouse.

---

## Repo Structure

```
influencer-campaign-analytics/
├── README.md
├── LICENSE
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md                          # Data dictionary
│   └── sample/
│       ├── creator_sample.csv             # 500 creators
│       ├── post_sample.csv                # ~25K posts
│       └── case_study_benchmarks.csv      # Public benchmark KPIs
├── notebooks/
│   ├── 01_data_audit.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_sponsored_vs_organic.ipynb
│   └── 04_creator_scoring.ipynb
├── sql/
│   ├── creator_metrics.sql
│   ├── sponsored_benchmarks.sql
│   └── creator_shortlist.sql
├── src/
│   ├── __init__.py
│   ├── ingest.py                          # Data loading utilities
│   ├── clean.py                           # Cleaning and validation
│   ├── features.py                        # Feature engineering
│   ├── scoring.py                         # Creator scoring and shortlisting
│   ├── utils.py                           # Visualization helpers
│   └── generate_sample.py                 # Reproducible sample generation
├── dashboard/
│   ├── app.py                             # Streamlit dashboard (4 pages)
│   ├── awareness_vs_engagement_quadrant.png
│   ├── creator_leaderboard.png
│   ├── scores_by_tier.png
│   ├── sponsored_vs_organic_by_tier.png
│   ├── sponsored_lift_by_category.png
│   ├── sponsored_split.png
│   └── tier_distribution.png
└── deliverables/
    └── client_recap_sample.md             # Business-facing memo
```

---

## Quick Start

**Requirements:** Python 3.10+

```bash
git clone https://github.com/bobaoxu2001/influencer-campaign-analytics.git
cd influencer-campaign-analytics

# Install dependencies
pip install -r requirements.txt

# Regenerate sample data (optional — samples are included)
python src/generate_sample.py

# Run analysis notebooks
jupyter notebook notebooks/

# Launch dashboard
streamlit run dashboard/app.py
```

---

## Dashboard Pages

| Page | Purpose |
|------|---------|
| **Executive Overview** | KPIs, tier distributions, category benchmarks, public case study reference |
| **Sponsored Content Benchmarking** | Sponsored vs organic ER by tier and category, posting time analysis |
| **Creator Shortlisting** | Quadrant chart, fit scores, objective-driven shortlists |
| **Partnerships Recap** | Findings summary, creator mix recommendations, test ideas |

---

## Example Recommendations for a Partnerships Team

Based on this analysis, a partnerships team could:

1. **Prioritize micro and mid-tier creators** for engagement-focused campaigns — they deliver 2-3x the engagement rate of macro/mega creators at a fraction of the cost
2. **Use the quadrant chart** in client meetings to explain the tradeoff between reach and engagement, and why the recommended creator mix includes both profile types
3. **Set expectations around sponsored ER** — show clients the typical 10-15% engagement dip for sponsored content, but highlight categories and creator profiles where the gap is smaller
4. **Build longer-term creator relationships** — creators with 3+ sponsored posts show more stable engagement than one-off placements

---

## Prototype / Archived Status

This repo is retained as an **earlier concept version** of creator campaign analytics work. It uses sampled public data and demonstrates the methodology; it is not actively developed. The approach is preserved for reference.

---

## Limitations

- **Sample data, not proprietary campaigns.** This project uses a sampled subset of a public influencer dataset as a proxy. In a production setting, this pipeline would connect to live campaign data and creator APIs
- **No spend or conversion data.** The primary dataset does not include ad spend, clicks, or conversions. ROI calculations would require integration with ad platform data
- **Instagram only.** This analysis covers Instagram. A full partnerships analytics stack would include TikTok and YouTube
- **Benchmark directional, not definitive.** Public case study KPIs provide context but may not reflect current market rates

---

## Next Steps for a Real Production Setting

1. **Connect to live APIs** — Instagram Graph API, TikTok Creator Marketplace API, or platform-specific data feeds
2. **Add a spend and conversion layer** — Enable true ROI, CPM, and CPA calculations
3. **Automate scoring on a weekly cadence** — Surface emerging talent and flag performance shifts
4. **Build alerting** — Notify when a shortlisted creator's metrics change significantly
5. **Expand to multi-platform** — Unified creator profiles across Instagram, TikTok, and YouTube
6. **Integrate with CRM** — Link creator scores to partnership pipeline and campaign history

---

## LinkedIn / Email Summary

> **Influencer Campaign Analytics Prototype**
>
> Built an earlier prototype of a creator campaign analytics pipeline. Using a sampled public influencer dataset (500 creators, 25K+ posts from Harvard Dataverse), developed a scoring framework to benchmark sponsored content performance, segment creators by campaign objective, and generate shortlist recommendations — with methodology grounded in public benchmarks from companies like Humanz and Ubiquitous.
>
> Tech: Python, pandas, DuckDB, SQL, Streamlit, matplotlib, plotly

---

## Resume Bullets

- **Built an influencer campaign analytics prototype** using sampled public Instagram data (25K+ posts from Harvard Dataverse), developing composite scoring models to benchmark sponsored content performance and shortlist creators by campaign objective (awareness vs engagement)
- **Designed a 4-page partnerships dashboard** (Streamlit) with executive overview, sponsored content benchmarking, creator shortlisting, and client recap — grounded in public KPI benchmarks from Humanz and Ubiquitous case studies
- **Produced client-facing deliverables** including creator segmentation quadrant charts, objective-driven shortlists, and a business memo translating data findings into actionable recommendations for partnerships teams

---

*This is an archived prototype using sampled public data. It is not affiliated with Humanz, Ubiquitous, or any creator-marketing platform. All benchmark data is sourced from publicly available case studies with attribution.*
