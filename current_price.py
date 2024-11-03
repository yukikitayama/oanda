import os
import json
import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
INSTRUMENT = "USD_JPY"


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_recent_price():
    headers = make_headers()
    payload = {
        "price": "M",
        "granularity": "S5",
        "count": "1",
        "alignmentTimezone": "UTC"
    }
    r = requests.get(
        url=f"{API_URL}/v3/instruments/{INSTRUMENT}/candles",
        headers=headers,
        params=payload
    )
    print("get_trades()")
    print(f"Status code: {r.status_code}")
    # pprint.pprint(r.json())
    return float(r.json()["candles"][0]["mid"]["c"])

def main():

    # Get most recent price
    price = get_recent_price()

    print(f"Most recent price: {price}")


if __name__ == "__main__":
    main()
