-- Creator Shortlisting Queries for Partnerships Teams
-- Compatible with DuckDB. Run against channels_scored.csv.

-- 1. Balanced shortlist — top 30 overall creators
SELECT
    channel_name,
    category,
    channel_type,
    country,
    follower_tier,
    subscribers,
    total_views,
    ROUND(creator_fit_score, 1) AS fit_score,
    ROUND(awareness_score, 1) AS awareness,
    ROUND(engagement_suitability_score, 1) AS engagement,
    ROUND(consistency_score, 1) AS consistency,
    ROUND(momentum_score, 1) AS momentum,
    risk_flag_count
FROM channels_scored
WHERE risk_flag_count <= 2
ORDER BY creator_fit_score DESC
LIMIT 30;


-- 2. Awareness-focused shortlist — high reach creators
SELECT
    channel_name,
    category,
    country,
    follower_tier,
    subscribers,
    total_views,
    ROUND(views_last_30d, 0) AS views_30d,
    ROUND(awareness_score, 1) AS awareness,
    ROUND(engagement_suitability_score, 1) AS engagement,
    risk_flag_count
FROM channels_scored
WHERE risk_flag_count <= 2
ORDER BY awareness_score DESC
LIMIT 20;


-- 3. Engagement-focused shortlist — high interaction creators
SELECT
    channel_name,
    category,
    country,
    follower_tier,
    subscribers,
    ROUND(engagement_proxy, 2) AS views_per_sub,
    ROUND(avg_views_per_video, 0) AS avg_video_views,
    ROUND(engagement_suitability_score, 1) AS engagement,
    ROUND(consistency_score, 1) AS consistency,
    risk_flag_count
FROM channels_scored
WHERE risk_flag_count <= 2
ORDER BY engagement_suitability_score DESC
LIMIT 20;


-- 4. Star creators — high on BOTH awareness and engagement
SELECT
    channel_name,
    category,
    country,
    followers AS subscribers,
    ROUND(awareness_score, 1) AS awareness,
    ROUND(engagement_suitability_score, 1) AS engagement,
    ROUND(creator_fit_score, 1) AS fit_score,
    CASE
        WHEN awareness_score > 70 AND engagement_suitability_score > 70
            THEN 'Star Creator'
        WHEN awareness_score > 70
            THEN 'Awareness Driver'
        WHEN engagement_suitability_score > 70
            THEN 'Engagement Specialist'
        ELSE 'Solid Performer'
    END AS creator_segment
FROM channels_scored
WHERE risk_flag_count <= 2
  AND awareness_score > 60
  AND engagement_suitability_score > 60
ORDER BY creator_fit_score DESC;


-- 5. Risk flagged creators — channels to investigate before recommending
SELECT
    channel_name,
    category,
    country,
    subscribers,
    risk_flag_count,
    flag_missing_30d_data,
    flag_low_upload_volume,
    flag_negative_growth,
    flag_very_high_uploads
FROM channels_scored
WHERE risk_flag_count >= 3
ORDER BY risk_flag_count DESC;
