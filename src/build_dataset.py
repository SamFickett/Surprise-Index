from scraping.fortune import scrape_fortune
from scraping.nasdaq import scrape_nasdaq
from scraping.cnbc import scrape_cnbc
from scraping.morningbrew import scrape_morningbrew

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FORTUNE_OUTPUT = (
    BASE_DIR / "data" / "raw" / "fortune" / "fortune_articles.json"
)

NASDAQ_OUTPUT = (
    BASE_DIR / "data" / "raw" / "nasdaq" / "nasdaq_articles.json"
)

CNBC_OUTPUT = (
    BASE_DIR / "data" / "raw" / "cnbc" / "cnbc_articles.json"
)

MORNINGBREW_OUTPUT = (
    BASE_DIR / "data" / "raw" / "morningbrew" / "morningbrew_articles.json"
)

MERGED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "merged_articles.json"
)

def build_dataset():
    """Build dataset from Fortune and NASDAQ articles"""

    fortune_articles = scrape_fortune()
    nasdaq_articles = scrape_nasdaq()
    cnbc_articles = scrape_cnbc()
    morningbrew_articles = scrape_morningbrew()

    save_articles(fortune_articles, FORTUNE_OUTPUT)
    save_articles(nasdaq_articles, NASDAQ_OUTPUT)
    save_articles(cnbc_articles, CNBC_OUTPUT)
    save_articles(morningbrew_articles, MORNINGBREW_OUTPUT)

    all_articles = fortune_articles + nasdaq_articles + cnbc_articles + morningbrew_articles

    seen = set()
    unique_articles = []

    """WORKS FOR SOURCES WITH "GUIDS" ONLY. POTENTIAL FIX LATER"""
    for article in all_articles:
        key = (article["source"], article["guid"])

        if key not in seen:
            seen.add(key)
            unique_articles.append(article)

    save_articles(unique_articles, MERGED_OUTPUT)

    return unique_articles

def save_articles(articles, fp):
    """Save articles to JSON file"""

    fp.parent.mkdir(
        parents = True,
        exist_ok = True
    )

    with fp.open("w", encoding="utf-8") as f:
        json.dump(
            articles,
            f,
            indent = 2,
            ensure_ascii = False
        )

if __name__ == "__main__":
    all_articles = build_dataset()

    print(f"Total articles: {len(all_articles)}")

    for article in all_articles[:5]:
        print(article["source"], "-", article["title"])