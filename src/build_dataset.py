from scraping.fortune import scrape_fortune
from scraping.nasdaq import scrape_nasdaq
from scraping.cnbc import scrape_cnbc
from scraping.morningbrew import scrape_morningbrew
from processing.normalize_article import normalize_articles
from processing.filter_relevance import filter_relevant_articles
from surprise.calculate_surprise import calculate_articles_surprise
from surprise.aggregate_daily import aggregate_daily_surprise
from scraping.common import make_article_key

import json
import time
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
# Source Registry

SOURCES = [
    {
        "name": "Fortune",
        "scraper": scrape_fortune,
        "output": FORTUNE_OUTPUT
    },
    {
        "name": "Nasdaq",
        "scraper": scrape_nasdaq,
        "output": NASDAQ_OUTPUT
    },
    {
        "name": "CNBC",
        "scraper": scrape_cnbc,
        "output": CNBC_OUTPUT
    },
    {
        "name": "Morning Brew",
        "scraper": scrape_morningbrew,
        "output": MORNINGBREW_OUTPUT
    }
]

# ------------------------------------------------------------- #
# Dataset functions

def build_dataset():
    """Build dataset from source articles"""
    all_articles = []

    for source in SOURCES:
        source_articles = process_source(source)

        all_articles.extend(source_articles)

    all_articles = dedup_articles(all_articles)

    save_articles(all_articles, MERGED_OUTPUT)

    normalized_articles = normalize_articles(all_articles)
    save_articles(normalized_articles, PROCESSED_OUTPUT)

    relevant_articles = filter_relevant_articles(normalized_articles)
    save_articles(relevant_articles, RELEVANT_OUTPUT)

    surprise_articles = calculate_articles_surprise(relevant_articles)
    save_articles(surprise_articles, SURPRISE_OUTPUT)

    daily_surprise = aggregate_daily_surprise(surprise_articles)
    save_articles(daily_surprise, DAILY_SURPRISE_OUTPUT)

    return relevant_articles

def process_source(source):
    name = source["name"]
    scraper = source["scraper"]
    output = source["output"]

    existing_articles = load_articles(output)
    known_keys = get_known_keys(existing_articles)

    start_time = time.perf_counter()
    new_articles = scraper(known_keys)
    elapsed = time.perf_counter() - start_time

    merged_articles = merge_articles(existing_articles, new_articles)
    save_articles(merged_articles, output)

    print(f"{name}: {len(existing_articles)} existing, {len(new_articles)} new, {len(merged_articles)} total, {elapsed:.2f}s")

    return merged_articles

def load_articles(path):
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def get_known_keys(articles):
    keys = set()

    for article in articles:
        key = make_article_key(article.get("source"), guid=article.get("guid"), url=article.get("url"))

        if key is not None:
            keys.add(key)

    return keys

def merge_articles(existing_articles, new_articles):
    return dedup_articles(existing_articles + new_articles)

def dedup_articles(articles):
    dedup = []
    seen = set()

    for index, article in enumerate(articles):
        if not isinstance(article, dict):
            print(f"BAD ARTICLE AT INDEX {index}")
            print(f"Type: {type(article)}")
            print(f"Value: {article}")
            raise TypeError("Expected article dictionary")

        key = make_article_key(article.get("source"), guid=article.get("guid"), url=article.get("url"))

        if key is None:
            continue

        if key in seen:
            continue

        seen.add(key)
        dedup.append(article)

    return dedup

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
    start_time = time.perf_counter()

    all_articles = build_dataset()

    end_time = time.perf_counter()

    print("-" * 10)
    print(f"Total relevant articles: {len(all_articles)}")

    elapsed = end_time - start_time
    print("-" * 10)
    print(f"Build completed in {elapsed:.2f} seconds")
