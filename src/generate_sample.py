"""
Generate sample datasets that mirror the schema of Seungbae Kim's
Instagram Influencer Dataset / Influencer and Brand Dataset.

These samples are synthetic but follow realistic distributions observed
in public Instagram influencer research. They are used for demonstration
purposes only. The full dataset is available at:
https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/OQAQWK

Usage:
    python src/generate_sample.py
"""

import pandas as pd
import numpy as np
import os

np.random.seed(42)

CATEGORIES = [
    "Fashion", "Beauty", "Fitness", "Travel", "Food",
    "Lifestyle", "Tech", "Parenting", "Gaming", "Music",
    "Photography", "Art", "Business", "Health", "Pets"
]

FOLLOWER_TIERS = {
    "nano": (1_000, 10_000),
    "micro": (10_000, 50_000),
    "mid": (50_000, 500_000),
    "macro": (500_000, 1_000_000),
    "mega": (1_000_000, 10_000_000),
}

TIER_WEIGHTS = [0.30, 0.30, 0.25, 0.10, 0.05]

N_CREATORS = 500
N_POSTS_PER_CREATOR = (20, 80)


def generate_creators(n=N_CREATORS):
    """Generate a sample creator dataset."""
    tiers = np.random.choice(list(FOLLOWER_TIERS.keys()), size=n, p=TIER_WEIGHTS)
    records = []
    for i, tier in enumerate(tiers):
        lo, hi = FOLLOWER_TIERS[tier]
        followers = int(np.random.lognormal(
            mean=np.log((lo + hi) / 2), sigma=0.3
        ))
        followers = max(lo, min(hi, followers))

        # Engagement rates inversely correlated with follower count
        base_er = {
            "nano": np.random.uniform(3.0, 8.0),
            "micro": np.random.uniform(2.0, 5.0),
            "mid": np.random.uniform(1.0, 3.5),
            "macro": np.random.uniform(0.8, 2.0),
            "mega": np.random.uniform(0.5, 1.5),
        }[tier]

        category = np.random.choice(CATEGORIES)
        avg_likes = int(followers * base_er / 100 * np.random.uniform(0.7, 1.0))
        avg_comments = int(avg_likes * np.random.uniform(0.02, 0.08))
        post_count = np.random.randint(*N_POSTS_PER_CREATOR)
        sponsored_rate = np.random.beta(2, 8)  # Most creators: 5-30% sponsored

        records.append({
            "creator_id": f"CR{i+1:05d}",
            "username": f"creator_{i+1}",
            "category": category,
            "follower_tier": tier,
            "followers": followers,
            "following": int(followers * np.random.uniform(0.01, 0.3)),
            "total_posts": post_count,
            "avg_likes": avg_likes,
            "avg_comments": avg_comments,
            "avg_engagement_rate": round(base_er, 2),
            "sponsored_post_rate": round(sponsored_rate, 3),
            "is_verified": np.random.random() < (0.02 if tier == "nano" else
                                                   0.05 if tier == "micro" else
                                                   0.15 if tier == "mid" else
                                                   0.40 if tier == "macro" else 0.70),
            "bio_has_email": np.random.random() < 0.55,
            "account_age_days": np.random.randint(365, 4000),
        })

    return pd.DataFrame(records)


def generate_posts(creators_df):
    """Generate a sample post dataset linked to creators."""
    all_posts = []
    post_id = 0
    for _, creator in creators_df.iterrows():
        n_posts = creator["total_posts"]
        sponsored_rate = creator["sponsored_post_rate"]

        for _ in range(n_posts):
            post_id += 1
            is_sponsored = np.random.random() < sponsored_rate

            # Sponsored posts: slight engagement penalty on average
            er_mult = np.random.uniform(0.70, 1.05) if is_sponsored else np.random.uniform(0.85, 1.20)
            likes = max(1, int(creator["avg_likes"] * er_mult * np.random.lognormal(0, 0.4)))
            comments = max(0, int(likes * np.random.uniform(0.02, 0.08)))
            engagement = likes + comments
            er = round(engagement / max(creator["followers"], 1) * 100, 3)

            # Posting date: random within last 2 years
            days_ago = np.random.randint(0, 730)
            post_date = pd.Timestamp("2025-03-01") - pd.Timedelta(days=days_ago)
            hour_probs = np.array([
                0.01, 0.01, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05,
                0.06, 0.07, 0.07, 0.07, 0.07, 0.06, 0.06, 0.05,
                0.05, 0.05, 0.06, 0.06, 0.05, 0.03, 0.02, 0.01
            ])
            hour_probs = hour_probs / hour_probs.sum()
            hour = np.random.choice(range(24), p=hour_probs)

            hashtag_count = np.random.randint(0, 30) if not is_sponsored else np.random.randint(3, 30)
            caption_length = int(np.random.lognormal(4.5, 0.8))

            all_posts.append({
                "post_id": f"P{post_id:07d}",
                "creator_id": creator["creator_id"],
                "category": creator["category"],
                "follower_tier": creator["follower_tier"],
                "followers_at_post": creator["followers"],
                "post_date": post_date.strftime("%Y-%m-%d"),
                "post_hour": hour,
                "post_weekday": post_date.day_name(),
                "is_sponsored": is_sponsored,
                "likes": likes,
                "comments": comments,
                "engagement": engagement,
                "engagement_rate": er,
                "hashtag_count": hashtag_count,
                "caption_length": min(caption_length, 2200),
                "has_brand_mention": is_sponsored or (np.random.random() < 0.08),
            })

    return pd.DataFrame(all_posts)


def main():
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample")
    os.makedirs(out_dir, exist_ok=True)

    print("Generating creator sample...")
    creators = generate_creators()
    creators.to_csv(os.path.join(out_dir, "creator_sample.csv"), index=False)
    print(f"  {len(creators)} creators saved.")

    print("Generating post sample...")
    posts = generate_posts(creators)
    posts.to_csv(os.path.join(out_dir, "post_sample.csv"), index=False)
    print(f"  {len(posts)} posts saved.")

    # Summary stats
    print("\n--- Sample Summary ---")
    print(f"Creators: {len(creators)}")
    print(f"Posts: {len(posts)}")
    print(f"Sponsored posts: {posts['is_sponsored'].sum()} ({posts['is_sponsored'].mean()*100:.1f}%)")
    print(f"Categories: {creators['category'].nunique()}")
    print(f"Tier distribution:\n{creators['follower_tier'].value_counts().to_string()}")


if __name__ == "__main__":
    main()
