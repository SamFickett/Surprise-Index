import json
from pathlib import Path

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime


def clean_text(value):
    """Normalize whitespace in strings"""

    if value is None:
        return None

    return " ".join(value.split())

def clean_categories(categories):
    """Remove duplicate categories, preserve order"""

    if not categories:
        return []

    seen = set()
    cleaned = []

    for category in categories:
        category = clean_text(category)

        if category and (category not in seen):
            seen.add(category)
            cleaned.append(category)

    return cleaned

def normalize_date(value):
    """Convert pubDate to UTC ISO-8601 format"""
    """Ex:       2026-08-16T15:06:27+00:00"""

    if not value:
        return None

    value = value.strip()

    try:
        # RSS-style dates
        # Mon, 24 Aug 2026 08:10:47 GMT
        date = parsedate_to_datetime(value)

    except (TypeError, ValueError):
        try:
            # ISO-style dates
            # 2026-08-24T08:10:47.000Z
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    # If source gives a timezone-native date
    # Treat as UTC
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    date = date.astimezone(timezone.utc)

    return date.isoformat()

def norm_missing_values(article):
    """Consistent Missing values across article sources"""

    # None
    article["source"] = article.get("source") or None
    article["title"] = article.get("title") or None
    article["url"] = article.get("url") or None
    article["published"] = article.get("published") or None
    article["author"] = article.get("author") or None

    # ""
    article["description"] = article.get("description") or ""
    article["content"] = article.get("content") or ""

    # []
    article["categories"] = article.get("categories") or []

    # URL for giud
    article["guid"] = article.get("guid") or article.get("url") or None

    return article

def get_content_type(article):
    """Classify type of content represented"""

    url = article.get("url") or ""

    if "live-updates" in url:
        return "live_updates"

    return "article"

def normalize_article(article):
    """Normalize one article dictionary"""

    normalized = article.copy()

    normalized = norm_missing_values(normalized)

    normalized["title"] = clean_text(normalized.get("title"))
    normalized["description"] = clean_text(normalized.get("description"))
    normalized["content"] = clean_text(normalized.get("content"))
    normalized["author"] = clean_text(normalized.get("author"))
    normalized["published"] = normalize_date(normalized.get("published"))
    normalized["categories"] = clean_categories(normalized.get("categories"))
    normalized["content_type"] = get_content_type(normalized)

    return normalized

def normalize_articles(articles):
    """Normalize list of article dictionaries"""

    return [
        normalize_article(article)
        for article in articles
    ]

def validate_article(article):
    """Check that normalized articles follow the expected format"""

    required_fields = [
        "source",
        "title",
        "url",
        "guid",
        "published",
        "author",
        "categories",
        "description",
        "content",
        "content_type"
    ]

    for field in required_fields:
        if field not in article:
            return False

    if not isinstance(article["source"], str):
        return False

    if not isinstance(article["title"], str):
        return False

    if not isinstance(article["url"], str):
        return False

    if not isinstance(article["guid"], str):
        return False    

    if not isinstance(article["published"], str):
        return False

    if (article["author"] is not None) and (not isinstance(article["author"], str)):
        return False

    if not isinstance(article["categories"], list):
        return False

    if not isinstance(article["description"], str):
        return False

    if not isinstance(article["content"], str):
        return False    

    if article["content_type"] not in ["article", "live_updates"]:
        return False

    return True

def validate_articles(articles):
    """Return articles that fail format violations"""

    failures = []

    for article in articles:
        if not validate_article(article):
            failures.append(article)

    return failures

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    input_path = (BASE_DIR / "data" / "processed" / "merged_articles.json")

    with input_path.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    normalized_articles = normalize_articles(articles)

    failures = validate_articles(normalized_articles)

    print(f"Total articles: {len(normalized_articles)}")
    print(f"Validation Failures: {len(failures)}")

    for article in failures:
        print(article.get("source"))
        print(article.get("title"))
        print()