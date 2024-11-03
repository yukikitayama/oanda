import os
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


def check_position():
    headers = make_headers()
    r = requests.get(
        url=f"{API_URL}/v3/accounts/{ACCOUNT_ID}/openPositions",
        headers=headers
    )
    print(f"Status code: {r.status_code}")
    positions = r.json()["positions"]

    # If no position, {'lastTransactionID': '41', 'positions': []}
    if not positions:
        print("No position")
    else:
        pprint.pprint(positions)


def main():

    # Check position
    check_position()


if __name__ == "__main__":
    main()
