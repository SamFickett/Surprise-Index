import json
import re
from pathlib import Path

from processing.relevance_indicators import TERMS

def is_relevant(article):
    """Is article relevant"""

    matches = get_relevance_terms(article)

    return len(matches) > 0

def get_relevance_terms(article):
    """Return # of terms found in an article"""

    text = get_relevance_text(article)

    matches = []

    for term in TERMS:
        pattern = r"\b" + re.escape(term) + r"\b"

        if re.search(pattern, text):
            matches.append(term)

    return matches

def get_relevance_text(article):
    """Build text used for relevance classification"""

    parts = [
        article.get("title", ""),
        article.get("description", ""),
        " ".join(article.get("categories", []))
    ]

    return " ".join(parts).lower()

def filter_relevant_articles(articles):
    """Return articles classified by relevance"""

    return [
        article
        for article in articles
        if is_relevant(article)
    ]

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    input_path = (
        BASE_DIR / "data" / "processed" / "normalized_articles.json"
    )

    with input_path.open("r", encoding="utf-8") as file:
        normalized_articles = json.load(file)

    m_count = 0

    for article in normalized_articles:
        matches = get_relevance_terms(article)

        status = (
            "RELEVANT"
            if matches
            else "NOT RELEVANT"
        )

        if matches:
            m_count += 1

        print(status)
        print(article["source"])
        print(article["title"])
        print("Matches:", matches)
        print("-" * 60)

    print(f"RELEVANT ARTICLES: {m_count}")