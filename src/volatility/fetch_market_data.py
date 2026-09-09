import csv
import io
import requests

SP500_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id=SP500"
)

def fetch_sp500():
    """Fetch daily SP500 closing values from FRED"""

    response = requests.get(SP500_URL, timeout=30)

    response.raise_for_status()

    return response.text

def parse_sp500(csv_text):
    """Parse daily SP500 values into standard format"""

    # Allow csv.DictReader to handle the CSV data as a dictionary
    reader = csv.DictReader(io.StringIO(csv_text))

    records = []

    for row in reader:
        date = row["observation_date"]
        close = row["SP500"]

        if not close:
            continue

        records.append({
            "date": date,
            "close": float(close)
        })

    return records


if __name__ == "__main__":
    data = fetch_sp500()

    records = parse_sp500(data)

    print(f"Found {len(records)} records\n")

    for record in records[:10]:
        print(record)