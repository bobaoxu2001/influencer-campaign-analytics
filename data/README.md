# Data Dictionary

## Data Provenance

All data in this project comes from publicly available sources. See below for details on each dataset.

### Primary Dataset: Global YouTube Statistics 2023

- **Source:** [Kaggle — Global YouTube Statistics 2023](https://www.kaggle.com/datasets/nelgiriyewithana/global-youtube-statistics-2023) by Nidula Elgiriyewithana
- **GitHub Mirror:** [IrisMejuto/Global-YouTube-Statistics](https://github.com/IrisMejuto/Global-YouTube-Statistics)
- **Records:** 995 real YouTube channels (990 after removing platform-owned placeholders)
- **Scope:** Top YouTube channels globally by subscriber count
- **Collection method:** Aggregated from public YouTube channel data
- **Time period:** Snapshot as of 2023 with 30-day trailing metrics

### Benchmark Dataset: Humanz / Ubiquitous Case Studies

- **Source:** Official public case study pages from [Humanz](https://humanz.com/case-studies) and [Ubiquitous](https://ubiquitousinfluence.com/case-studies)
- **Records:** 6 campaigns with publicly disclosed KPIs
- **Every row has a source URL** for verification

---

## File Reference

### `raw/global_youtube_statistics.csv`
Original unmodified dataset as downloaded. 995 rows, 28 columns.

### `processed/channels_cleaned.csv`
Cleaned dataset after removing placeholders, standardizing columns, and adding derived metrics.

| Column | Type | Description |
|--------|------|-------------|
| `rank` | int | Global rank by subscriber count |
| `channel_name` | str | YouTube channel name |
| `subscribers` | int | Total subscriber count |
| `total_views` | int | Lifetime total views |
| `category` | str | YouTube category (Music, Entertainment, etc.) |
| `channel_title` | str | Channel display title |
| `uploads` | int | Total video uploads |
| `country` | str | Channel country |
| `country_code` | str | ISO country code |
| `channel_type` | str | Channel type classification |
| `views_last_30d` | float | Views in the last 30 days |
| `est_monthly_earnings_low` | float | Estimated monthly earnings (low) |
| `est_monthly_earnings_high` | float | Estimated monthly earnings (high) |
| `est_monthly_earnings_mid` | float | Midpoint of earnings estimate |
| `subs_gained_last_30d` | float | Subscribers gained in last 30 days |
| `created_year` | float | Year channel was created |
| `avg_views_per_video` | float | Total views / uploads |
| `channel_age_years` | float | Years since channel creation |
| `views_per_subscriber` | float | Total views / subscribers (engagement proxy) |
| `views_30d_pct_of_total` | float | 30-day views as % of lifetime views |
| `sub_growth_rate_30d` | float | 30-day sub growth as % of total subs |
| `follower_tier` | str | Tier assignment based on subscriber count |

### `processed/channels_scored.csv`
Full scored dataset with all engineered features and composite scores.

Additional columns beyond `channels_cleaned.csv`:

| Column | Type | Description |
|--------|------|-------------|
| `engagement_proxy` | float | Views per subscriber (best available engagement proxy) |
| `posting_intensity` | float | Uploads per year of channel age |
| `recent_views_momentum` | float | 30-day views / total views * 100 |
| `subscriber_momentum` | float | 30-day sub growth / total subs * 100 |
| `momentum_score` | float | Composite momentum (0–100) |
| `earnings_per_1k_views` | float | Est. monthly earnings per 1K 30-day views |
| `consistency_score` | float | Composite consistency (0–100) |
| `marketing_category` | str | Influencer-marketing-relevant category label |
| `creator_fit_score` | float | Overall partnership suitability (0–100) |
| `awareness_score` | float | Reach/awareness suitability (0–100) |
| `engagement_suitability_score` | float | Interaction quality suitability (0–100) |
| `flag_missing_30d_data` | bool | No 30-day metrics available |
| `flag_low_upload_volume` | bool | Fewer than 50 uploads |
| `flag_negative_growth` | bool | Losing subscribers |
| `flag_earnings_missing` | bool | No earnings estimate |
| `flag_very_high_uploads` | bool | 50K+ uploads (possible network channel) |
| `risk_flag_count` | int | Number of active risk flags |

### `benchmarks/case_study_benchmarks.csv`
Real public campaign KPIs from Humanz and Ubiquitous.

| Column | Type | Description |
|--------|------|-------------|
| `campaign` | str | Campaign name |
| `brand` | str | Brand name |
| `agency` | str | Agency (Humanz or Ubiquitous) |
| `platform` | str | Platform (TikTok, Instagram) |
| `views` | float | Total views (if disclosed) |
| `impressions` | float | Total impressions (if disclosed) |
| `cpm_usd` | float | Cost per mille in USD (if disclosed) |
| `engagements` | float | Total engagements (if disclosed) |
| `paid_clicks` | float | Paid clicks (if disclosed) |
| `conversions_new_users` | float | Conversions / new users (if disclosed) |
| `source_url` | str | Public source URL for verification |
| `notes` | str | Additional context |

### Follower Tiers

| Tier | Subscriber Range | Count in Dataset |
|------|-----------------|------------------|
| `mid` | 12M–15M | 302 |
| `macro_low` | 15M–30M | 520 |
| `macro` | 30M–60M | 142 |
| `mega` | 60M–100M | 18 |
| `mega_plus` | 100M+ | 8 |

**Note:** This dataset contains only the top ~1,000 YouTube channels globally. All channels have 12M+ subscribers. The tier labels reflect the distribution within *this dataset*, not standard influencer-marketing tier definitions (which typically start at nano = 1K–10K). This is a known limitation documented in the README.

---

## What Data Is NOT Available

The following metrics are **not present** in this dataset and should not be fabricated:

- Per-post engagement (likes, comments on individual videos)
- Sponsored vs organic content flags
- Ad spend or campaign cost data
- Click-through rates or conversion rates
- Audience demographics
- Content-level sentiment or brand safety scores

These would be available through the YouTube Data API v3 or proprietary campaign platforms.
