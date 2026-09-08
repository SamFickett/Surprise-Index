from scraping.fortune import scrape_fortune
from scraping.nasdaq import scrape_nasdaq
from scraping.cnbc import scrape_cnbc
from scraping.morningbrew import scrape_morningbrew
from processing.normalize_article import normalize_articles
from processing.filter_relevance import filter_relevant_articles
from surprise.calculate_surprise import calculate_articles_surprise
from surprise.aggregate_daily import aggregate_daily_surprise

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

#------------------------------------------------------------- #
# Source output paths

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

# ------------------------------------------------------------- #
# Processed output paths

MERGED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "merged_articles.json"
)

PROCESSED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "normalized_articles.json"
)

RELEVANT_OUTPUT = (
    BASE_DIR / "data" / "processed" / "relevant_articles.json"
)

SURPRISE_OUTPUT = (
    BASE_DIR / "data" / "processed" / "surprise_articles.json"
)

DAILY_SURPRISE_OUTPUT = (
    BASE_DIR / "data" / "processed" / "daily_surprise.json"
)

# ------------------------------------------------------------- #
# Dataset functions

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

    normalized_articles = normalize_articles(unique_articles)
    save_articles(normalized_articles, PROCESSED_OUTPUT)

    relevant_articles = filter_relevant_articles(normalized_articles)
    save_articles(relevant_articles, RELEVANT_OUTPUT)

    surprise_articles = calculate_articles_surprise(relevant_articles)
    save_articles(surprise_articles, SURPRISE_OUTPUT)

    daily_surprise = aggregate_daily_surprise(surprise_articles)
    save_articles(daily_surprise, DAILY_SURPRISE_OUTPUT)

    return relevant_articles

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

    print(len(all_articles))