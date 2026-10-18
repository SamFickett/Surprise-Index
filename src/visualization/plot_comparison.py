import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "comparison" / "rolling_3_months.json"
)

OUTPUT_PATH = (
    BASE_DIR / "outputs" / "comparison.png"
)

def load_data(fp):
    with fp.open("r", encoding="utf-8") as file:
        return json.load(file)

def plot_comparison(data):
    dates = [datetime.strptime(record["date"], "%Y-%m-%d") for record in data]

    surprise = [record["surprise_per_1000"] for record in data]

    volatility_gap = [record["volatility_gap"] for record in data]

    figs, axes = plt.subplots(2, 1, figsize=(10,8), sharex=True)

    # Surprise Graph
    axes[0].plot(dates, surprise, marker = "o")
    axes[0].set_title("Daily News Surprise")
    axes[0].set_ylabel("Surprise occurences \n per 1,000 words")
    axes[0].grid(True)

    # Volatility Graph
    axes[1].plot(dates, volatility_gap, marker = "o")
    axes[1].axhline(y = 0, linestyle = "--")
    axes[1].set_title("Expected vs. Realized Volatility Gap")
    axes[1].set_ylabel("VIX - Realized Volatility")
    axes[1].set_xlabel("Date")
    axes[1].grid(True)

    plt.xticks(rotation = 45, ha = "right")
    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_PATH)

    plt.show()

if __name__ == "__main__":
    data = load_data(DATA_PATH)

    plot_comparison(data)