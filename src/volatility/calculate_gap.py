def calculate_volatility_gap(vix_data, realized_data):
    """Match VIX and realized volatility by date. Calculate expected minus realized"""

    realized_by_date = {record["date"]: record["realized_volatility"] for record in realized_data}

    results = []

    for vix_record in vix_data:
        date = vix_record["date"]

        if date not in realized_by_date:
            continue

        vix = vix_record["vix"]
        realized = realized_by_date[date]

        gap = vix - realized
        results.append({
            "date": date,
            "vix": vix,
            "realized_volatility": realized,
            "volatility_gap": gap
        })

    return results