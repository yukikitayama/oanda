import os
import pprint
import json

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = "https://api-fxpractice.oanda.com"  # Demo account
# API_URL = "https://api-fxtrade.oanda.com"  # Live account


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_account_id(headers):
    # Check account info
    res = requests.get(
        url=f"{API_URL}/v3/accounts",
        headers=headers
    )
    account = res.json()["accounts"][0]
    account_id = account["id"]

    print("get_account_id()")
    print(f"Status code: {res.status_code}")
    print(f"Account ID: {account_id}")

    return account_id


def open_position(headers, account_id):
    # Create an order
    payload = json.dumps({
        "order": {
            "type": "MARKET",
            "instrument": "USD_JPY",
            "units": "1000",
            "timeInForce": "FOK",
            "positionFill": "DEFAULT"
        }
    })
    res = requests.post(
        url=f"{API_URL}/v3/accounts/{account_id}/orders",
        headers=headers,
        data=payload
    )
    print(f"open_position()")
    print(f"Status code: {res.status_code}")
    print(f"Response:")
    pprint.pprint(res.json())


def main():
    # Create headers
    headers = make_headers()

    # Get account ID
    account_id = get_account_id(headers)

    # Open a position
    open_position(headers, account_id)


if __name__ == "__main__":
    main()
