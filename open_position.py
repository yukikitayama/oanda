import os
import pprint
import json

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = "https://api-fxpractice.oanda.com"  # Demo account
# API_URL = "https://api-fxtrade.oanda.com"  # Live account
ORDER = {
    "type": "MARKET",
    "instrument": "USD_JPY",
    "units": "100000",  # Positive is long, negative is short
    "timeInForce": "FOK",
    "positionFill": "DEFAULT",
    "stopLossOnFill": {
        "distance": "0.5"  # In USD/JPY, if position is 150, 149.5 is stop loss
    },
    "takeProfitOnFill": {
        # distance doesn't exist in API documentation (https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitDetails),
        # but worked
        "distance": "1.0"  # In USD/JPY, if position is 150, 150.5 is take profit
    }
}
TRADE_INFO = "trade_info.json"


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
        "order": ORDER
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

    # Save trade info to close it later
    save_trade_info(res.json())


def save_trade_info(response_json):
    with open(TRADE_INFO, "w") as f:
        json.dump(response_json, f)
    print("Saved trade information")


def main():
    # Create headers
    headers = make_headers()

    # Get account ID
    account_id = get_account_id(headers)

    # Open a position
    open_position(headers, account_id)


if __name__ == "__main__":
    main()
