import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "comparison" / "rolling_3_months.json"
)

OUTPUT_PATH = (
    BASE_DIR / "outputs" / "daily_surprise.png"
)

def load_data(fp):
    with fp.open("r", encoding="utf-8") as file:
        return json.load(file)

def plot_daily_surprise(data):
    dates = [
        datetime.strptime(record["date"], "%Y-%m-%d") for record in data
    ]

    surprise = [record["surprise_per_1000"] for record in data]

    plt.figure(figsize=(10, 5))

    plt.plot(dates, surprise, marker="o")

    plt.xlabel("Date")
    plt.ylabel("Surprise occurences per 1,000 words")
    plt.title("Daily News Surprise")

    plt.grid(True)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_PATH)

    plt.show()

if __name__ == "__main__":
    data = load_data(DATA_PATH)

    plot_daily_surprise(data)