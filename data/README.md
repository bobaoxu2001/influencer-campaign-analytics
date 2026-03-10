# Data Dictionary

## Overview

This project uses sample data that mirrors the schema of publicly available Instagram influencer research datasets. The full datasets are too large for a GitHub repository (37GB+ raw data), so we provide:

1. **A reproducible sampling script** (`src/generate_sample.py`) that generates realistic sample data
2. **Pre-generated sample CSVs** in `data/sample/` for immediate use
3. **A manually curated benchmark CSV** from public case studies

## Primary Data Source

**Seungbae Kim's Instagram Influencer Dataset / Influencer and Brand Dataset**
- Source: [Harvard Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OQAQWK)
- Original scope: 33,935 influencers, 10M+ Instagram posts
- Fields include: caption, hashtags, timestamp, sponsorship flag, likes, comments
- License: See original dataset for terms

## Sample Files

### `creator_sample.csv` — 500 creators

| Column | Type | Description |
|--------|------|-------------|
| `creator_id` | string | Unique creator identifier (CR00001–CR00500) |
| `username` | string | Placeholder username |
| `category` | string | Content category (Fashion, Beauty, Fitness, etc.) |
| `follower_tier` | string | Size tier: nano / micro / mid / macro / mega |
| `followers` | int | Follower count |
| `following` | int | Following count |
| `total_posts` | int | Number of posts in sample |
| `avg_likes` | int | Average likes per post |
| `avg_comments` | int | Average comments per post |
| `avg_engagement_rate` | float | Average engagement rate (%) |
| `sponsored_post_rate` | float | Proportion of posts that are sponsored (0–1) |
| `is_verified` | bool | Whether account is verified |
| `bio_has_email` | bool | Whether bio contains an email address |
| `account_age_days` | int | Days since account creation |

### `post_sample.csv` — ~25,000 posts

| Column | Type | Description |
|--------|------|-------------|
| `post_id` | string | Unique post identifier |
| `creator_id` | string | Foreign key to creator_sample |
| `category` | string | Creator's content category |
| `follower_tier` | string | Creator's follower tier at time of post |
| `followers_at_post` | int | Creator's follower count at time of post |
| `post_date` | date | Date of publication (YYYY-MM-DD) |
| `post_hour` | int | Hour of publication (0–23) |
| `post_weekday` | string | Day of week |
| `is_sponsored` | bool | Whether the post is sponsored content |
| `likes` | int | Number of likes |
| `comments` | int | Number of comments |
| `engagement` | int | Total engagement (likes + comments) |
| `engagement_rate` | float | Engagement rate (%) = engagement / followers * 100 |
| `hashtag_count` | int | Number of hashtags used |
| `caption_length` | int | Character length of caption |
| `has_brand_mention` | bool | Whether post mentions a brand |

### `case_study_benchmarks.csv` — 6 public case studies

| Column | Type | Description |
|--------|------|-------------|
| `campaign` | string | Campaign name |
| `brand` | string | Brand name |
| `agency` | string | Agency (Humanz / Ubiquitous) |
| `platform` | string | Social platform |
| `views` | int | Total views (where available) |
| `impressions` | int | Total impressions (where available) |
| `cpm_usd` | float | Cost per mille in USD |
| `engagements` | int | Total engagements |
| `paid_clicks` | int | Paid clicks (where available) |
| `conversions_new_users` | int | Conversions or new users (where available) |
| `engagement_rate_pct` | string | Engagement rate or benchmark note |
| `source_url` | string | Public URL where the data was found |
| `notes` | string | Additional context |

## Follower Tier Definitions

| Tier | Follower Range | Typical ER Range |
|------|---------------|------------------|
| Nano | 1K – 10K | 3.0% – 8.0% |
| Micro | 10K – 50K | 2.0% – 5.0% |
| Mid | 50K – 500K | 1.0% – 3.5% |
| Macro | 500K – 1M | 0.8% – 2.0% |
| Mega | 1M+ | 0.5% – 1.5% |

## Regenerating Sample Data

```bash
python src/generate_sample.py
```

This will overwrite the CSVs in `data/sample/` with a fresh sample. The random seed is fixed for reproducibility.
