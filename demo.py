import os
import pprint

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = "https://api-fxpractice.oanda.com"  # Demo account
# API_URL = "https://api-fxtrade.oanda.com"  # Live account

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Check account info
r = requests.get(
    url=f"{API_URL}/v3/accounts",
    headers=headers
)
account = r.json()["accounts"][0]
account_id = account["id"]
r = requests.get(
    url=f"{API_URL}/v3/accounts/{account_id}/summary",
    headers=headers
)
pprint.pprint(r.json())