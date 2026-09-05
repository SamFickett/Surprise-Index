import re

import json
from pathlib import Path

from surprise_indicators import (
    SURPRISE_WORDS,
    SURPRISE_PHRASES
)

def count_words(text):
    """Count number of words in a text block"""

    words = re.findall(r"\b[\w'-]+\b", text)
    return len(words)

def count_surprise_words(text):
    """Count 'surprise related' words in a text block"""

    text = text.lower()

    count = 0

    for word in SURPRISE_WORDS:
        pattern = r"\b" + re.escape(word) + r"\b"

        matches = re.findall(pattern, text)
        count += len(matches)

    return count

def count_surprise_phrases(text):
    """Count 'surprise related' phrases in a text block"""

    text = text.lower()

    count = 0

    for phrase in SURPRISE_PHRASES:
        pattern = r"\b" + re.escape(phrase) + r"\b"

        matches = re.findall(pattern, text)
        count += len(matches)

    return count

def calculate_surprise(text):
    """Calculate surprise score for an article"""

    word_count = count_words(text)

    surprise_word_count = count_surprise_words(text)
    surprise_phrase_count = count_surprise_phrases(text)

    surprise_count = surprise_word_count + surprise_phrase_count

    if word_count == 0:
        surprise_score = None
    else:
        surprise_score = surprise_count / word_count

    return {
        "word_count": word_count,
        "surprise_count": surprise_count,
        "surprise_score": surprise_score
    }

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    input_path = (
        BASE_DIR / "data" / "processed" / "relevant_articles.json"
    )

    with input_path.open("r", encoding="utf-8") as file:
        articles = json.load(file)

    article = articles[0]

    result = calculate_surprise(article["content"])

    print("Title: ", article["title"])
    print("Word count: ", result["word_count"])
    print("Surprise count: ", result["surprise_count"])
    print("Surprise score: ", result["surprise_score"])