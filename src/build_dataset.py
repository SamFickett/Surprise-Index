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
# Dataset functions

def build_dataset():
    """Build dataset from source articles"""

    # Search for existing articles, filter out previously seen
    # for faster result time
    existing_fortune = load_articles(FORTUNE_OUTPUT)
    existing_nasdaq = load_articles(NASDAQ_OUTPUT)
    existing_cnbc = load_articles(CNBC_OUTPUT)
    existing_morningbrew = load_articles(MORNINGBREW_OUTPUT)

    fortune_keys = get_known_keys(existing_fortune)
    nasdaq_keys = get_known_keys(existing_nasdaq)
    cnbc_keys = get_known_keys(existing_cnbc)
    morningbrew_keys = get_known_keys(existing_morningbrew)

    new_fortune = scrape_fortune(fortune_keys)
    new_nasdaq = scrape_nasdaq(nasdaq_keys)
    new_cnbc = scrape_cnbc(cnbc_keys)
    new_morningbrew = scrape_morningbrew(morningbrew_keys)

    fortune_articles = merge_articles(existing_fortune, new_fortune)
    nasdaq_articles = merge_articles(existing_nasdaq, new_nasdaq)
    cnbc_articles = merge_articles(existing_cnbc, new_cnbc)
    morningbrew_articles = merge_articles(existing_morningbrew, new_morningbrew)

    all_articles = (fortune_articles + nasdaq_articles + cnbc_articles + morningbrew_articles)

    # ---------- Testing ---------- #
    print(f"Old Fortune: {len(existing_fortune)}")
    print(f"New Fortune: {len(new_fortune)}")
    print(f"Total Fortune: {len(fortune_articles)}")

    print(f"Old Nasdaq: {len(existing_nasdaq)}")
    print(f"New Nasdaq: {len(new_nasdaq)}")
    print(f"Total Nasdaq: {len(nasdaq_articles)}")

    print(f"Old CNBC: {len(existing_cnbc)}")
    print(f"New CNBC: {len(new_cnbc)}")
    print(f"Total CNBC: {len(cnbc_articles)}")

    print(f"Old Morning Brew: {len(existing_morningbrew)}")
    print(f"New Morning Brew: {len(new_morningbrew)}")
    print(f"Total Morning Brew: {len(morningbrew_articles)}")

    print(f"All Articles: {len(all_articles)}")

    save_articles(fortune_articles, FORTUNE_OUTPUT)
    save_articles(nasdaq_articles, NASDAQ_OUTPUT)
    save_articles(cnbc_articles, CNBC_OUTPUT)
    save_articles(morningbrew_articles, MORNINGBREW_OUTPUT)

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
