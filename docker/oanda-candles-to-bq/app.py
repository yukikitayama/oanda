import os
from datetime import datetime, timedelta

import requests
import pytz
import pandas as pd
import pandas_gbq
from dotenv import load_dotenv

load_dotenv()

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("expand_frame_repr", False)

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
INSTRUMENT = "USD_JPY"
PRICE = "M"
GRANULARITY = "D"
ALIGNMENT_TIMEZONE = "America/New_York"
TABLE = "oanda.candles"


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept-Datetime-Format": "RFC3339"
    }


def get_candles(from_str, to_str):
    headers = make_headers()
    payload = {
        "price": PRICE,
        "granularity": GRANULARITY,
        "from": from_str,
        "to": to_str,
        "smooth": False,
        "includeFirst": True,
        "dailyAlignment": 17,
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
    print(f"OANDA API response: {r.json()["candles"]}")

    candles = r.json()["candles"]
    return candles


def candles_to_df(candles):
    data = []
    for candle in candles:
        d = dict()
        d["date"] = candle["time"][:10]
        d["time"] = candle["time"]
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
    df["time"] = pd.to_datetime(df["time"])

    # print(df.shape)
    # print(df)

    return df

def main():

    # Set parameters
    # e.g. UTC 22PM (ET 6PM in Daylight, 5PM in Standard)
    # 2025-07-08 candle ends at 2025-07-09 5PM ET
    # At ET evening, I can get a candle of previous day
    # Daylight time ET 5PM = UTC 21PM
    # Standard time ET 5PM = UTC 22PM
    from_str = (datetime.now(pytz.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    to_str = datetime.now(pytz.utc).strftime("%Y-%m-%d")
    yesterday = from_str[:10]
    today = to_str[:10]

    # from_str = "2025-07-07T21:59:00Z"
    # yesterday = from_str[:10]
    # to_str = "2025-07-08T22:00:00Z"
    # today = to_str[:10]

    print(f"From: {from_str}, to: {to_str}, yesterday: {yesterday}, today: {today}")

    # Get candles
    candles = get_candles(from_str, to_str)

    # Transform for BigQuery
    df = candles_to_df(candles)

    print("Data to upload")
    print(df.loc[df["date"] == yesterday])

    # Upload to BigQuery
    if len(df.loc[df["date"] == yesterday]):
        pandas_gbq.to_gbq(
            df.loc[df["date"] == yesterday],
            destination_table=TABLE,
            if_exists="append",
        )
        print(f"Uploaded to {TABLE}")
    else:
        print("No data")


if __name__ == "__main__":
    main()
