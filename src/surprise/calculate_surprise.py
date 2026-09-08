import re

import json
from pathlib import Path

from surprise.surprise_indicators import (
    SURPRISE_WORDS,
    SURPRISE_PHRASES
)

def count_words(text):
    """Count number of words in a text block"""

    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)

def find_surprise_words(text):
    """Find 'surprise related' words in a text block"""

    text = text.lower()
    matches = []

    for word in SURPRISE_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"

        matches.extend(re.findall(pattern, text))

    return matches

def find_surprise_phrases(text):
    """Find 'surprise related' phrases in a text block"""

    text = text.lower()
    matches = []

    for phrase in SURPRISE_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"

        matches.extend(re.findall(pattern, text))

    return matches

def calculate_article_surprise(article):
    """Calculate surprise score for an article"""

    result = calculate_surprise(article["content"])

    analyzed = article.copy()

    analyzed["word_count"] = result["word_count"]
    analyzed["surprise_count"] = result["surprise_count"]
    analyzed["surprise_score"] = result["surprise_score"]
    analyzed["matched_words"] = result["matched_words"]
    analyzed["matched_phrases"] = result["matched_phrases"]

    return analyzed

def calculate_articles_surprise(articles):
    """Calculate surprise score for a list of articles"""

    return [calculate_article_surprise(article) for article in articles]

def calculate_surprise(text):
    """Calculate surprise score for an article"""

    word_count = count_words(text)

    surprise_words = find_surprise_words(text)
    surprise_phrases = find_surprise_phrases(text)

    surprise_count = len(surprise_words) + len(surprise_phrases)

    if word_count == 0:
        surprise_score = None
    else:
        surprise_score = surprise_count / word_count

    return {
        "word_count": word_count,
        "surprise_count": surprise_count,
        "surprise_score": surprise_score,
        "matched_words": surprise_words,
        "matched_phrases": surprise_phrases
    }

if __name__ == "__main__":
    print()