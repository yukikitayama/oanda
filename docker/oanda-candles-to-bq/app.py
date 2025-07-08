import os
from datetime import datetime, timedelta

import requests
import pytz
import pandas as pd
import pandas_gbq
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
INSTRUMENT = "USD_JPY"
PRICE = "M"
GRANULARITY = "D"
ALIGNMENT_TIMEZONE = "America/New_York"
TABLE = "oanda.usdjpy_ny_day_mid_candles"


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_candles(from_str, to_str):
    headers = make_headers()
    payload = {
        "price": PRICE,
        "granularity": GRANULARITY,
        "from": from_str,
        "to": to_str,
        "alignmentTimezone": ALIGNMENT_TIMEZONE
    }
    r = requests.get(
        url=f"{API_URL}/v3/instruments/{INSTRUMENT}/candles",
        headers=headers,
        params=payload
    )

    # print("get_candles()")
    # print(f"Status code: {r.status_code}")
    # print(r.text)
    # print(r.json()["candles"])

    candles = r.json()["candles"]
    return candles


def candles_to_df(candles):
    data = []
    for candle in candles:
        d = dict()
        d["date"] = candle["time"][:10]
        d["open"] = candle["mid"]["o"]
        d["high"] = candle["mid"]["h"]
        d["low"] = candle["mid"]["l"]
        d["close"] = candle["mid"]["c"]
        d["volume"] = candle["volume"]
        data.append(d)

    df = pd.DataFrame(data)

    for c in ["open", "high", "low", "close", "volume"]:
        df[c] = pd.to_numeric(df[c])
    df["write_timestamp"] = datetime.now(pytz.utc)

    # print(df.shape)
    # print(df)

    return df

def main():

    # Get candles yesterday
    from_str = (datetime.now(pytz.timezone("America/New_York")) - timedelta(days=1)).strftime("%Y-%m-%d")
    to_str = (datetime.now(pytz.timezone("America/New_York"))).strftime("%Y-%m-%d")
    candles = get_candles(from_str, to_str)

    # Transform for BigQuery
    df = candles_to_df(candles)

    print("Data to upload")
    print(df)

    # Upload to BigQuery
    pandas_gbq.to_gbq(
        df,
        destination_table=TABLE,
        if_exists="append",
    )
    print(f"Uploaded to {TABLE}")


if __name__ == "__main__":
    main()
