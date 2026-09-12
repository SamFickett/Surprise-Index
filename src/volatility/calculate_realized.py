import math
import statistics

TRADING_DAYS = 252
WINDOW_SIZE = 21

def calculate_log_returns(market_data):
    """Calculate daily log returns from S&P closing prices"""

    market_data = sorted(market_data, key=lambda record: record["date"])

    returns = []

    for i in range(1, len(market_data)):
        prev_close = market_data[i - 1]["close"]
        curr_close = market_data[i]["close"]

        log_return = math.log(curr_close / prev_close)

        returns.append({
            "date": market_data[i]["date"],
            "return": log_return
        })

    return returns

"""

Added an extra factor of 100 to have it scale alongside the VIX data

"""
def calculate_realized_volatility(market_data, window_size=WINDOW_SIZE):
    """Calculate rolling annualized realized volatility"""

    returns = calculate_log_returns(market_data)

    results = []

    for i in range(window_size - 1, len(returns)):
        window = returns[i - window_size + 1:i + 1]

        values = [record["return"] for record in window]

        daily_std = statistics.stdev(values)

        realized_volatility = daily_std * math.sqrt(TRADING_DAYS) * 100

        results.append({
            "date": returns[i]["date"],
            "realized_volatility": realized_volatility
        })

    return results
