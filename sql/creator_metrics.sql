-- Creator Metrics — Core KPIs for Partnerships Teams
-- Compatible with DuckDB. Run against channels_scored.csv.

-- 1. Channel overview with key performance metrics
SELECT
    channel_name,
    category,
    channel_type,
    country,
    follower_tier,
    subscribers,
    total_views,
    uploads,
    ROUND(avg_views_per_video, 0) AS avg_views_per_video,
    ROUND(views_per_subscriber, 2) AS views_per_sub,
    ROUND(views_last_30d, 0) AS views_last_30d,
    ROUND(subs_gained_last_30d, 0) AS subs_gained_30d,
    ROUND(est_monthly_earnings_mid, 0) AS est_monthly_earnings,
    channel_age_years
FROM channels
ORDER BY subscribers DESC;


-- 2. Category-level benchmarks
SELECT
    category,
    COUNT(*) AS channels,
    ROUND(AVG(subscribers), 0) AS avg_subscribers,
    ROUND(AVG(total_views), 0) AS avg_total_views,
    ROUND(AVG(avg_views_per_video), 0) AS avg_views_per_video,
    ROUND(AVG(views_per_subscriber), 2) AS avg_views_per_sub,
    ROUND(AVG(views_last_30d), 0) AS avg_30d_views,
    ROUND(AVG(uploads), 0) AS avg_uploads
FROM channels
WHERE category IS NOT NULL
GROUP BY category
HAVING COUNT(*) >= 5
ORDER BY avg_views_per_sub DESC;


-- 3. Tier-level benchmarks
SELECT
    follower_tier,
    COUNT(*) AS channels,
    ROUND(AVG(subscribers), 0) AS avg_subscribers,
    ROUND(AVG(total_views), 0) AS avg_total_views,
    ROUND(AVG(views_per_subscriber), 2) AS avg_views_per_sub,
    ROUND(AVG(posting_intensity), 1) AS avg_posting_intensity,
    ROUND(AVG(momentum_score), 1) AS avg_momentum_score,
    ROUND(AVG(consistency_score), 1) AS avg_consistency_score
FROM channels_scored
GROUP BY follower_tier
ORDER BY avg_subscribers;


-- 4. Country-level distribution
SELECT
    country,
    COUNT(*) AS channels,
    ROUND(AVG(subscribers), 0) AS avg_subscribers,
    ROUND(SUM(total_views), 0) AS total_views,
    ROUND(AVG(views_per_subscriber), 2) AS avg_views_per_sub
FROM channels
WHERE country IS NOT NULL
GROUP BY country
HAVING COUNT(*) >= 5
ORDER BY channels DESC;
