import csv
import random
from datetime import date, timedelta
from pathlib import Path

CAMPAIGNS_DIR = Path(__file__).parent.parent.parent.parent / "data" / "campaigns"

PRODUCT_SKUS = [
    "SKU-LAPTOP-PRO", "SKU-LAPTOP-AIR", "SKU-KEYBOARD-MECH", "SKU-MOUSE-GAMING",
    "SKU-HEADPHONES-BT", "SKU-MONITOR-27", "SKU-WEBCAM-HD", "SKU-CHAIR-ERGO",
    "SKU-DESK-STAND", "SKU-HUB-USBC", "SKU-GPU-RTX4070", "SKU-CPU-I9",
    "SKU-RAM-32GB", "SKU-SSD-1TB", "SKU-TABLET-PRO", "SKU-WATCH-SMART",
    "SKU-BACKPACK-TECH", "SKU-SPEAKER-BT", "SKU-CABLE-USBC", "SKU-PAD-MOUSE-XL",
]

OWNERS = ["Alice Martin", "Lucas Dupont", "Thomas Girard", "Sophie Bernard"]

PLATFORMS = {
    "meta": {
        "file": "meta_campaigns.csv",
        "prefix": "META",
        "names": [
            "Spring Sale", "Summer Push", "Product Launch", "Flash Deal",
            "Retargeting Wave", "Awareness Drive", "Creator Campaign",
        ],
    },
    "tiktok": {
        "file": "tiktok_campaigns.csv",
        "prefix": "TK",
        "names": [
            "Viral Unbox", "Trending Challenge", "ASMR Review", "Day in My Life",
            "Desk Setup Tour", "Life Hack", "Whats in My Bag",
        ],
    },
    "google_ads": {
        "file": "google_campaigns.csv",
        "prefix": "GGL",
        "names": [
            "Best Price", "Buy Now", "Compare Deals", "Top Rated",
            "Limited Offer", "Search Intent", "Performance Max",
        ],
    },
}

FIELDNAMES = [
    "campaign_id", "campaign_name", "platform", "owner", "product_sku",
    "start_date", "end_date", "budget_eur", "impressions", "clicks",
    "conversions", "spend_eur", "revenue_eur", "status",
]


def _last_id(rows: list[dict], prefix: str) -> int:
    ids = [
        int(r["campaign_id"].replace(f"{prefix}-", ""))
        for r in rows
        if r["campaign_id"].startswith(f"{prefix}-")
    ]
    return max(ids, default=0)


def _random_campaign(campaign_id: str, platform: str, name_suffix: str) -> dict:
    sku = random.choice(PRODUCT_SKUS)
    product_label = sku.replace("SKU-", "").replace("-", " ").title()
    budget = round(random.uniform(200, 5000), 2)
    spend = round(budget * random.uniform(0.85, 1.0), 2)

    if platform == "tiktok":
        impressions = random.randint(100_000, 700_000)
    elif platform == "meta":
        impressions = random.randint(80_000, 350_000)
    else:
        impressions = random.randint(5_000, 20_000)

    clicks = int(impressions * random.uniform(0.008, 0.015))
    conversions = int(clicks * random.uniform(0.02, 0.06))
    revenue = round(conversions * random.uniform(20, 1300), 2)

    start = date.today() - timedelta(days=random.randint(0, 30))
    end = start + timedelta(days=random.randint(14, 60))
    status = "active" if end >= date.today() else "completed"

    return {
        "campaign_id": campaign_id,
        "campaign_name": f"{product_label} {name_suffix}",
        "platform": platform,
        "owner": random.choice(OWNERS),
        "product_sku": sku,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "budget_eur": budget,
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "spend_eur": spend,
        "revenue_eur": revenue,
        "status": status,
    }


def generate(n: int = 5) -> None:
    for platform, config in PLATFORMS.items():
        path = CAMPAIGNS_DIR / config["file"]
        rows = []
        if path.exists():
            with open(path, newline="") as f:
                rows = list(csv.DictReader(f))

        next_id = _last_id(rows, config["prefix"]) + 1
        new_rows = [
            _random_campaign(
                f"{config['prefix']}-{str(next_id + i).zfill(3)}",
                platform,
                random.choice(config["names"]),
            )
            for i in range(n)
        ]

        is_new = not path.exists() or path.stat().st_size == 0
        with open(path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            if is_new:
                writer.writeheader()
            writer.writerows(new_rows)

        print(f"✅ {platform}: added {n} campaigns → {path.name}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Append new campaign rows to CSV files")
    parser.add_argument("--n", type=int, default=5, help="Number of new campaigns per platform (default: 5)")
    args = parser.parse_args()
    generate(args.n)
