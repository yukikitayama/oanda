import os
import json
import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_transactions():
    headers = make_headers()
    r = requests.get(
        url=f"{API_URL}/v3/accounts/{ACCOUNT_ID}/transactions/sinceid?id=1",
        headers=headers
    )
    print("get_trades()")
    print(f"Status code: {r.status_code}")
    pprint.pprint(r.json())
    # return r.json()["positions"]


def main():

    # Get trade
    transactions = get_transactions()


if __name__ == "__main__":
    main()
