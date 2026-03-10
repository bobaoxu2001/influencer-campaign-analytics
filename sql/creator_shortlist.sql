-- Creator Shortlisting Queries
-- Used by partnerships teams to identify campaign-ready creators

-- High-engagement creators with proven sponsored performance
SELECT
    c.creator_id,
    c.username,
    c.category,
    c.follower_tier,
    c.followers,
    c.avg_engagement_rate,
    sp.sponsored_er,
    sp.organic_er,
    ROUND((sp.sponsored_er - sp.organic_er) / NULLIF(sp.organic_er, 0) * 100, 1) AS sponsored_lift_pct,
    sp.sponsored_count,
    sp.total_posts
FROM creators c
INNER JOIN (
    SELECT
        creator_id,
        ROUND(AVG(CASE WHEN is_sponsored THEN engagement_rate END), 2) AS sponsored_er,
        ROUND(AVG(CASE WHEN NOT is_sponsored THEN engagement_rate END), 2) AS organic_er,
        SUM(CASE WHEN is_sponsored THEN 1 ELSE 0 END) AS sponsored_count,
        COUNT(*) AS total_posts
    FROM posts
    GROUP BY creator_id
) sp ON c.creator_id = sp.creator_id
WHERE sp.sponsored_count >= 3
  AND sp.sponsored_er >= 1.0
  AND c.avg_engagement_rate >= 2.0
ORDER BY sp.sponsored_er DESC
LIMIT 30;


-- Awareness-focused shortlist (high reach, decent engagement)
SELECT
    c.creator_id,
    c.username,
    c.category,
    c.follower_tier,
    c.followers,
    c.avg_engagement_rate,
    c.total_posts,
    ROUND(c.sponsored_post_rate * 100, 1) AS sponsored_pct
FROM creators c
WHERE c.followers >= 50000
  AND c.avg_engagement_rate >= 1.0
  AND c.sponsored_post_rate BETWEEN 0.05 AND 0.50
ORDER BY c.followers DESC
LIMIT 30;


-- Engagement-focused shortlist (high ER, comment quality)
SELECT
    c.creator_id,
    c.username,
    c.category,
    c.follower_tier,
    c.followers,
    c.avg_engagement_rate,
    ROUND(c.avg_comments::FLOAT / NULLIF(c.avg_likes, 0) * 100, 2) AS comment_ratio_pct,
    c.total_posts
FROM creators c
WHERE c.avg_engagement_rate >= 3.0
  AND c.total_posts >= 20
ORDER BY c.avg_engagement_rate DESC
LIMIT 30;


-- Creator cohort summary for client deck
SELECT
    follower_tier,
    category,
    COUNT(*) AS creators,
    ROUND(AVG(avg_engagement_rate), 2) AS cohort_avg_er,
    ROUND(AVG(sponsored_post_rate) * 100, 1) AS cohort_sponsored_pct,
    ROUND(AVG(followers), 0) AS cohort_avg_followers
FROM creators
GROUP BY follower_tier, category
HAVING COUNT(*) >= 3
ORDER BY cohort_avg_er DESC;
