import json
from pathlib import Path

from volatility.fetch_market_data import fetch_sp500, parse_sp500
from volatility.fetch_vix import fetch_vix, parse_vix

BASE_DIR = Path(__file__).resolve().parent.parent


# ------------------------------------------------------------- #
# Processed output paths

SP500_OUTPUT = (
    BASE_DIR / "data" / "raw" / "volatility" / "sp500.json"
)

VIX_OUTPUT = (
    BASE_DIR / "data" / "raw" / "volatility" / "vix.json"
)

# ------------------------------------------------------------- #
# Dataset functions

def save_data(data, fp):
    """Save data to JSON file"""

    fp.parent.mkdir(parents=True, exist_ok=True)

    with fp.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def build_volatility():
    """Fetch and save SP500 data"""

    sp500_csv = fetch_sp500()
    sp500_data = parse_sp500(sp500_csv)
    save_data(sp500_data, SP500_OUTPUT)

    vix_csv = fetch_vix()
    vix_data = parse_vix(vix_csv)
    save_data(vix_data, VIX_OUTPUT)

    return sp500_data, vix_data

if __name__ == "__main__":
    sp500_data, vix_data = build_volatility()

    print(f"Saved {len(sp500_data)} SP500 records")
    print(f"Saved {len(vix_data)} VIX records")