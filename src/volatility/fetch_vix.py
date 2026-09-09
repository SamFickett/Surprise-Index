import csv
import io
import requests

VIX_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?id=VIXCLS"
)

def fetch_vix():
    """Fetch daily VIX closing values from FRED"""

    response = requests.get(VIX_URL, timeout=30)

    response.raise_for_status()

    return response.text

def parse_vix(csv_text):
    """Parse daily VIX values into standard format"""

    # Allow csv.DictReader to handle the CSV data as a dictionary
    reader = csv.DictReader(io.StringIO(csv_text))

    records = []

    for row in reader:
        date = row["observation_date"]
        vix = row["VIXCLS"]

        if not vix:
            continue

        records.append({
            "date": date,
            "vix": float(vix)
        })

    return records


if __name__ == "__main__":
    data = fetch_vix()

    records = parse_vix(data)

    print(f"Found {len(records)} records\n")

    for record in records[:10]:
        print(record)