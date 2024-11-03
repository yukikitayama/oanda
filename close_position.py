import os
import json
import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
TRADE_SPECIFIER = "35"
UNITS = "10000"


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def close_trade(trade_specifier, units, headers):
    payload = json.dumps({
        "units": units
    })
    r = requests.put(
        url=f"{API_URL}/v3/accounts/{ACCOUNT_ID}/trades/{trade_specifier}/close",
        headers=headers,
        data=payload
    )
    print(f"Status code: {r.status_code}")
    if r.status_code == 200:
        print(f"Successfully closed position of trade: {trade_specifier}, units: {units}")
    else:
        pprint.pprint(r.json())


def main():

    # Create header
    headers = make_headers()

    # Close trade
    close_trade(
        trade_specifier=TRADE_SPECIFIER,
        units=UNITS,
        headers=headers
    )


if __name__ == "__main__":
    main()
