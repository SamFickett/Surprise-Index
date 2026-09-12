import json
from pathlib import Path
from datetime import datetime, timedelta

from volatility.fetch_market_data import fetch_sp500, parse_sp500
from volatility.fetch_vix import fetch_vix, parse_vix
from volatility.calculate_realized import calculate_realized_volatility
from volatility.calculate_gap import calculate_volatility_gap

# TEMP, Maybe
from comparison.align_series import align_series

BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------- #
# Processed output paths

SP500_OUTPUT = (
    BASE_DIR / "data" / "raw" / "volatility" / "sp500.json"
)

VIX_OUTPUT = (
    BASE_DIR / "data" / "raw" / "volatility" / "vix.json"
)

REALIZED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "volatility" / "realized_volatility.json"
)
GAP_OUTPUT = (
    BASE_DIR / "data" / "processed" / "volatility" / "volatility_gap.json"
)

# TEMP, Maybe
DAILY_SURPRISE_INPUT = (
    BASE_DIR / "data" / "processed" / "daily_surprise.json"
)

ALIGNED_OUTPUT = (
    BASE_DIR / "data" / "processed" / "comparison" / "aligned_series.json"
)

ROLLING_OUTPUT = (
    BASE_DIR / "data" / "processed" / "comparison" / "rolling_3_months.json"
)

# ------------------------------------------------------------- #
# Dataset functions

def save_data(data, fp):
    """Save data to JSON file"""

    fp.parent.mkdir(parents=True, exist_ok=True)

    with fp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# TEMP, Maybe
def load_data(fp):
    with fp.open("r", encoding="utf-8") as file:
        return json.load(file)

def filter_rolling_window(data, days=90):
    if not data:
        return []

    latest_date = max(datetime.strptime(record["date"], "%Y-%m-%d") for record in data)

    start_date = latest_date - timedelta(days=days)

    filtered = []

    for record in data:
        record_date = datetime.strptime(record["date"], "%Y-%m-%d")

        if start_date <= record_date <= latest_date:
            filtered.append(record)

    return filtered

def build_volatility():
    """Fetch and save SP500 data"""

    sp500_csv = fetch_sp500()
    sp500_data = parse_sp500(sp500_csv)
    save_data(sp500_data, SP500_OUTPUT)

    vix_csv = fetch_vix()
    vix_data = parse_vix(vix_csv)
    save_data(vix_data, VIX_OUTPUT)

    realized_data = calculate_realized_volatility(sp500_data)
    save_data(realized_data, REALIZED_OUTPUT)

    gap_data = calculate_volatility_gap(vix_data, realized_data)
    save_data(gap_data, GAP_OUTPUT)

    surprise_data = load_data(DAILY_SURPRISE_INPUT)
    aligned_data = align_series(surprise_data, gap_data)
    save_data(aligned_data, ALIGNED_OUTPUT)

    rolling_data = filter_rolling_window(aligned_data)
    save_data(rolling_data, ROLLING_OUTPUT)

    return sp500_data, vix_data, realized_data, gap_data, aligned_data

if __name__ == "__main__":
    sp500_data, vix_data, realized_data, gap_data, aligned_data = build_volatility()

    print(f"Saved {len(sp500_data)} SP500 records")
    print(f"Saved {len(vix_data)} VIX records")
    print(f"Saved {len(realized_data)} realized volatility records")
    print(f"Saved {len(gap_data)} volatility gap records")
    print(f"Saved {len(aligned_data)} aligned records")
