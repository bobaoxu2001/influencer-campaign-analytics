-- Sponsored Content Benchmarking Queries
-- Compares sponsored vs organic performance across segments

-- Sponsored vs Organic engagement by follower tier
SELECT
    follower_tier,
    is_sponsored,
    COUNT(*) AS post_count,
    ROUND(AVG(engagement_rate), 2) AS avg_er,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY engagement_rate), 2) AS median_er,
    ROUND(AVG(likes), 0) AS avg_likes,
    ROUND(AVG(comments), 0) AS avg_comments,
    ROUND(AVG(hashtag_count), 1) AS avg_hashtags
FROM posts
GROUP BY follower_tier, is_sponsored
ORDER BY follower_tier, is_sponsored;


-- Sponsored engagement lift/drop by category
SELECT
    category,
    ROUND(AVG(CASE WHEN is_sponsored THEN engagement_rate END), 2) AS sponsored_er,
    ROUND(AVG(CASE WHEN NOT is_sponsored THEN engagement_rate END), 2) AS organic_er,
    ROUND(
        (AVG(CASE WHEN is_sponsored THEN engagement_rate END)
         - AVG(CASE WHEN NOT is_sponsored THEN engagement_rate END))
        / NULLIF(AVG(CASE WHEN NOT is_sponsored THEN engagement_rate END), 0) * 100,
        1
    ) AS er_lift_pct
FROM posts
GROUP BY category
HAVING COUNT(CASE WHEN is_sponsored THEN 1 END) >= 10
ORDER BY er_lift_pct DESC;


-- Top-performing sponsored posts
SELECT
    p.post_id,
    p.creator_id,
    p.category,
    p.follower_tier,
    p.likes,
    p.comments,
    p.engagement,
    p.engagement_rate,
    p.hashtag_count,
    p.post_date
FROM posts p
WHERE p.is_sponsored = true
ORDER BY p.engagement_rate DESC
LIMIT 50;


-- Posting time analysis for sponsored content
SELECT
    post_hour,
    is_sponsored,
    COUNT(*) AS posts,
    ROUND(AVG(engagement_rate), 2) AS avg_er
FROM posts
GROUP BY post_hour, is_sponsored
ORDER BY post_hour;
