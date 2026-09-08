from collections import defaultdict

def aggregate_daily_surprise(articles):
    """Aggregate surprise data by publication date"""

    daily = defaultdict(
        lambda: {
            "article_count": 0,
            "word_count": 0,
            "surprise_count": 0,
        }
    )

    for article in articles:
        published = article.get("published")

        if not published:
            continue

        date = published.split("T")[0]

        daily[date]["article_count"] += 1
        daily[date]["word_count"] += article.get("word_count", 0)
        daily[date]["surprise_count"] += article.get("surprise_count", 0)

    results = []

    for date, values in daily.items():
        word_count = values["word_count"]
        surprise_count = values["surprise_count"]

        if word_count == 0:
            surprise_score = None
            surprise_per_1000 = None
        else:
            surprise_score = surprise_count / word_count
            surprise_per_1000 = surprise_score * 1000

        results.append({
            "date": date,
            "article_count": values["article_count"],
            "word_count": word_count,
            "surprise_count": surprise_count,
            "surprise_score": surprise_score,
            "surprise_per_1000": surprise_per_1000
        })

    results.sort(
        key=lambda item: item["date"]
    )

    return results