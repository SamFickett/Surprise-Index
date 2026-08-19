from scraping.fortune import scrape_fortune
from scraping.nasdaq import scrape_nasdaq

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

FORTUNE_OUTPUT = (
    BASE_DIR / "data" / "raw" / "fortune" / "fortune_articles.json"
)

NASDAQ_OUTPUT = (
    BASE_DIR / "data" / "raw" / "nasdaq" / "nasdaq_articles.json"
)

MERGED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "merged_articles.json"
)

def build_dataset():
    """Build dataset from Fortune and NASDAQ articles"""

    fortune_articles = scrape_fortune()
    nasdaq_articles = scrape_nasdaq()

    save_articles(fortune_articles, FORTUNE_OUTPUT)
    save_articles(nasdaq_articles, NASDAQ_OUTPUT)

    all_articles = fortune_articles + nasdaq_articles   

    save_articles(all_articles, MERGED_OUTPUT)

    return all_articles

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