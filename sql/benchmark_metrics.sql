-- Benchmark Metrics — Real Public Case Study KPIs
-- Compatible with DuckDB. Run against case_study_benchmarks.csv.

-- 1. Full benchmark table
SELECT
    campaign,
    brand,
    agency,
    platform,
    views,
    impressions,
    cpm_usd,
    engagements,
    paid_clicks,
    conversions_new_users,
    source_url
FROM benchmarks
ORDER BY agency, campaign;


-- 2. CPM range by agency
SELECT
    agency,
    COUNT(*) AS campaigns,
    ROUND(MIN(cpm_usd), 2) AS min_cpm,
    ROUND(MAX(cpm_usd), 2) AS max_cpm,
    ROUND(AVG(cpm_usd), 2) AS avg_cpm
FROM benchmarks
WHERE cpm_usd IS NOT NULL
GROUP BY agency;


-- 3. Views and engagement summary
SELECT
    agency,
    ROUND(SUM(views), 0) AS total_views,
    ROUND(SUM(engagements), 0) AS total_engagements,
    ROUND(SUM(conversions_new_users), 0) AS total_conversions
FROM benchmarks
GROUP BY agency;


-- 4. Campaigns with engagement data
SELECT
    campaign,
    brand,
    views,
    engagements,
    ROUND(engagements * 100.0 / NULLIF(views, 0), 2) AS implied_engagement_rate_pct
FROM benchmarks
WHERE engagements IS NOT NULL
ORDER BY engagements DESC;
