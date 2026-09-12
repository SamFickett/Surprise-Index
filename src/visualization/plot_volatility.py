import json
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt


BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_PATH = (
    BASE_DIR / "data" / "processed" / "comparison"/ "rolling_3_months.json"
)

OUTPUT_PATH = ( 
    BASE_DIR / "outputs" / "volatility_gap.png"
)

def load_data(file_path):
    with file_path.open( "r", encoding="utf-8") as file:
        return json.load(file)


def plot_volatility_gap(data):
    dates = [
        datetime.strptime(record["date"], "%Y-%m-%d") for record in data
        ]

    gaps = [
        record["volatility_gap"]
        for record in data
    ]

    plt.figure(figsize=(10, 5))

    plt.plot(dates, gaps, marker="o")

    plt.axhline(y=0, linestyle="--")

    plt.xlabel("Date")
    plt.ylabel("VIX - Realized Volatility")
    plt.title("Expected vs. Realized Volatility Gap")

    plt.grid(True)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    plt.savefig(OUTPUT_PATH)

    plt.show()


if __name__ == "__main__":
    data = load_data(DATA_PATH)

    plot_volatility_gap(data)