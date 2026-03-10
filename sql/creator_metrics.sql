-- Creator-Level Performance Metrics
-- Used by partnerships teams to evaluate creator baselines

-- Overall creator performance summary
SELECT
    c.creator_id,
    c.username,
    c.category,
    c.follower_tier,
    c.followers,
    c.avg_engagement_rate,
    c.sponsored_post_rate,
    COUNT(p.post_id) AS total_posts,
    SUM(CASE WHEN p.is_sponsored THEN 1 ELSE 0 END) AS sponsored_posts,
    SUM(CASE WHEN NOT p.is_sponsored THEN 1 ELSE 0 END) AS organic_posts,
    ROUND(AVG(p.engagement_rate), 2) AS overall_avg_er,
    ROUND(AVG(CASE WHEN p.is_sponsored THEN p.engagement_rate END), 2) AS sponsored_avg_er,
    ROUND(AVG(CASE WHEN NOT p.is_sponsored THEN p.engagement_rate END), 2) AS organic_avg_er,
    ROUND(AVG(p.likes), 0) AS avg_likes,
    ROUND(AVG(p.comments), 0) AS avg_comments,
    ROUND(AVG(p.comments) / NULLIF(AVG(p.likes), 0) * 100, 2) AS comment_to_like_ratio
FROM creators c
LEFT JOIN posts p ON c.creator_id = p.creator_id
GROUP BY c.creator_id, c.username, c.category, c.follower_tier,
         c.followers, c.avg_engagement_rate, c.sponsored_post_rate
ORDER BY c.followers DESC;


-- Category-level benchmarks
SELECT
    c.category,
    COUNT(DISTINCT c.creator_id) AS creators,
    ROUND(AVG(c.followers), 0) AS avg_followers,
    ROUND(AVG(c.avg_engagement_rate), 2) AS avg_er,
    ROUND(AVG(c.sponsored_post_rate) * 100, 1) AS avg_sponsored_pct,
    ROUND(AVG(CASE WHEN p.is_sponsored THEN p.engagement_rate END), 2) AS sponsored_er,
    ROUND(AVG(CASE WHEN NOT p.is_sponsored THEN p.engagement_rate END), 2) AS organic_er
FROM creators c
LEFT JOIN posts p ON c.creator_id = p.creator_id
GROUP BY c.category
ORDER BY avg_er DESC;


-- Follower tier benchmarks
SELECT
    c.follower_tier,
    COUNT(DISTINCT c.creator_id) AS creators,
    ROUND(AVG(c.followers), 0) AS avg_followers,
    ROUND(AVG(c.avg_engagement_rate), 2) AS avg_er,
    ROUND(PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY c.avg_engagement_rate), 2) AS er_p25,
    ROUND(PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY c.avg_engagement_rate), 2) AS er_median,
    ROUND(PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY c.avg_engagement_rate), 2) AS er_p75
FROM creators c
GROUP BY c.follower_tier
ORDER BY avg_followers;
