import os
import pprint

import requests
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv

load_dotenv()
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("expand_frame_repr", False)

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
INSTRUMENT = "USD_JPY"
SAVEFIG_01 = "./image1.png"


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_candles(instrument, headers):
    payload = {
        "price": "M",
        "granularity": "D",
        "count": "260",
        "alignmentTimezone": "UTC"
    }
    r = requests.get(
        url=f"{API_URL}/v3/instruments/{instrument}/candles",
        headers=headers,
        params=payload
    )
    # print("get_candles()")
    # print(f"Status code: {r.status_code}")
    # pprint.pprint(r.json()["candles"])

    candles = r.json()["candles"]


    return candles


def convert_candle_to_df(candles):
    data = []
    for candle in candles:
        d = dict()
        d["time"] = candle["time"]
        d["open"] = candle["mid"]["o"]
        d["high"] = candle["mid"]["h"]
        d["low"] = candle["mid"]["l"]
        d["close"] = candle["mid"]["c"]
        data.append(d)

    # pprint.pprint(data)

    df = pd.DataFrame(data)
    df = clean_df(df)

    print("convert_candle_to_df()")
    print(df.shape)
    print(df.dtypes)
    print(df.head())
    print(df.tail())
    print()

    return df


def clean_df(df):
    df_c = df.copy()
    df_c["time"] = pd.to_datetime(df_c["time"])
    for c in ["open", "high", "low", "close"]:
        df_c[c] = pd.to_numeric(df_c[c])
    return df_c


def engineer_features(df):
    df_c = df.copy()
    df_c["date"] = df_c["time"].dt.date
    df_c.set_index("date", inplace=True)

    for n in [200, 100, 50, 25, 15]:
        df_c[f"sma_{n}"] = df_c["close"].rolling(window=n).mean()

    df_c.dropna(inplace=True)

    print("engineer_features()")
    print(df_c.shape)
    print(df_c.dtypes)
    print(df_c.head())
    print(df_c.tail())
    print()

    return df_c


def visualize_data(df):
    plt.plot(df["close"], label="Close")
    for n in [200, 100, 50, 25, 15]:
        plt.plot(df[f"sma_{n}"], label=f"SMA_{n}")
    plt.legend()
    plt.title("Data")
    plt.ylabel(INSTRUMENT)
    plt.xlabel("Date")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(SAVEFIG_01)
    plt.clf()


def main():

    # Make headers
    headers = make_headers()

    # Get candles
    candles = get_candles(INSTRUMENT, headers)

    # Convert to dataframe
    df = convert_candle_to_df(candles)

    # Feature engineering
    df = engineer_features(df)

    # Visualize data
    visualize_data(df)


if __name__ == "__main__":
    main()
