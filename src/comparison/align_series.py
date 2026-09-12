import json
from pathlib import Path

def align_series(surprise_data, volatility_data):
    """Match surprise and volatility by date. Only dates that exist in both sets are included"""

    volatility_by_date = {record["date"]: record for record in volatility_data}

    results = []

    for surprise_record in surprise_data:
        date = surprise_record["date"]

        if date not in volatility_by_date:
            continue

        volatility_record = volatility_by_date[date]

        results.append({
            "date": date,
            "article_count": surprise_record["article_count"],
            "word_count": surprise_record["word_count"],
            "surprise_count": surprise_record["surprise_count"],
            "surprise_score": surprise_record["surprise_score"],
            "surprise_per_1000": surprise_record["surprise_per_1000"],
            "vix": volatility_record["vix"],
            "realized_volatility": volatility_record["realized_volatility"],
            "volatility_gap": volatility_record["volatility_gap"]
        })

    results.sort(key=lambda record: record["date"])

    return results

if __name__ == "__main__":
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

#   -------------------- FILE PATHS --------------------

    surprise_path = (
        BASE_DIR / "data" / "processed" / "daily_surprise.json"
    )

    volatility_path = (
        BASE_DIR / "data" / "processed" / "volatility" / "volatility_gap.json"
    )

#   -------------------- LOAD FILES --------------------

    with surprise_path.open("r", encoding="utf-8") as file:
        surprise_data = json.load(file)

    with volatility_path.open("r", encoding="utf-8") as file:
        volatility_data = json.load(file)

#   -------------------- ALIGN --------------------

    aligned = align_series(surprise_data, volatility_data)

    print(f"Surprise dates: {len(surprise_data)}")
    print(f"Volatility dates: {len(volatility_data)}")
    print(f"Aligned dates: {len(aligned)}")

    for record in aligned:
        print(record)