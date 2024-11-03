import functions_framework
import os
import json
import collections
import time
from datetime import timedelta

import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import root_mean_squared_error, mean_absolute_percentage_error
import xgboost as xgb

# from dotenv import load_dotenv
# load_dotenv()

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("expand_frame_repr", False)

API_KEY = os.environ["API_KEY"]
API_URL = os.environ["API_URL"]
ACCOUNT_ID = os.environ["ACCOUNT_ID"]
INSTRUMENT = "USD_JPY"
UNITS = 10000
GRANULARITY = "D"
COUNT = "5000"
SMAS = [15, 25, 50, 100, 200]
N_SLOPE = 25
N_CANDLE = 3
N_PREDICT = 5
N_TEST = 5
VALI_SIZE = 0.2
RANDOM_STATE = 0
CV = 5
HOME = "/tmp"
# HOME = "."
SAVEFIG_01 = f"{HOME}/evaluation.png"
SAVEFIG_02 = f"{HOME}/prediction.png"
ORDER = {
    "type": "MARKET",
    "instrument": "USD_JPY",
    # Unit is dynamically set
    # "units": "100000",  # Positive is long, negative is short
    "timeInForce": "FOK",
    "positionFill": "DEFAULT",
    "stopLossOnFill": {
        "distance": "1.5"  # In USD/JPY, if position is 150, 149.5 is stop loss
    },
    "takeProfitOnFill": {
        # distance doesn't exist in API documentation (https://developer.oanda.com/rest-live-v20/transaction-df/#TakeProfitDetails),
        # but worked
        "distance": "3.0"  # In USD/JPY, if position is 150, 150.5 is take profit
    }
}


def make_headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


def get_positions():
    headers = make_headers()
    r = requests.get(
        url=f"{API_URL}/v3/accounts/{ACCOUNT_ID}/openPositions",
        headers=headers
    )
    print("get_positions()")
    print(f"Status code: {r.status_code}")
    return r.json()["positions"]


def get_candles():
    headers = make_headers()
    payload = {
        "price": "M",
        "granularity": GRANULARITY,
        "count": COUNT,
        "alignmentTimezone": "UTC"
    }
    r = requests.get(
        url=f"{API_URL}/v3/instruments/{INSTRUMENT}/candles",
        headers=headers,
        params=payload
    )
    # print("get_candles()")
    # print(f"Status code: {r.status_code}")
    # pprint.pprint(r.json()["candles"])
    candles = r.json()["candles"]
    return candles


def clean_df(df):
    df_c = df.copy()
    df_c["time"] = pd.to_datetime(df_c["time"])
    for c in ["open", "high", "low", "close"]:
        df_c[c] = pd.to_numeric(df_c[c])
    return df_c


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


def engineer_features(df):
    df_c = df.copy()
    df_c["date"] = df_c["time"].dt.date
    df_c.set_index("date", inplace=True)

    for n in SMAS:
        # Compute simple moving average
        df_c[f"sma_{n}"] = df_c["close"].rolling(window=n).mean()
        # Compute slope of simple moving average
        df_c[f"slope_{N_SLOPE}_sma_{n}"] = compute_sma_slope(df_c[f"sma_{n}"].to_list(), N_SLOPE)
        # Compute position of current price relative to simple moving average
        df_c[f"price_position_to_sma_{n}"] = compute_price_position_to_sma(df_c[f"sma_{n}"].to_list(),
                                                                           df_c["close"].to_list())

    # Compute candle information
    upper_shadows = []
    bodys = []
    lower_shadows = []
    for i, row in df.iterrows():
        res = compute_candle_information(row["open"], row["high"], row["low"], row["close"])
        upper_shadows.append(res[0])
        bodys.append(res[1])
        lower_shadows.append(res[2])
    df_c["upper_shadow_0"] = upper_shadows
    df_c["body_0"] = bodys
    df_c["lower_shadow_0"] = lower_shadows

    for m in range(1, N_CANDLE):
        df_c[f"upper_shadow_{m}"] = df_c["upper_shadow_0"].shift(m)
        df_c[f"body_{m}"] = df_c["body_0"].shift(m)
        df_c[f"lower_shadow_{m}"] = df_c["lower_shadow_0"].shift(m)

    # CLean
    df_c.dropna(inplace=True)
    df_c.drop(
        columns=["time", "open", "high", "low"],
        inplace=True
    )

    # Create Y
    y = df_c["close"].shift(-N_PREDICT)
    df_c.insert(0, "y", y)

    print("engineer_features()")
    print(df_c.shape)
    print(df_c.dtypes)
    print(df_c.head())
    print(df_c.tail())
    print()

    return df_c


def compute_sma_slope(sma, n):
    queue = collections.deque(maxlen=n)
    res = []

    for price in sma:

        queue.append(price)

        if len(queue) == n:
            x = [i for i in range(len(queue))]
            slope, intercept = np.polyfit(x, queue, 1)
            res.append(slope)
        else:
            res.append(None)

    return res


def compute_price_position_to_sma(smas, closes):
    res = []
    for i in range(len(smas)):

        if smas[i] is None:
            continue

        position = closes[i] / smas[i]
        res.append(position)

    return res


def compute_candle_information(open_, high, low, close):
    upper_shadow = high - max(open_, close)
    lower_shadow = min(open_, close) - low
    # body is positive if go up, and negative if go down
    body = close - open_
    return upper_shadow, body, lower_shadow


def split_data(df):
    df_data = df.loc[~df["y"].isna()]
    df_no_data = df.loc[df["y"].isna()]

    print("Data after feature engineering: ", df.shape)
    print("Data for model: ", df_data.shape)
    print("Data not for model", df_no_data.shape)

    df_test = df_data.iloc[-N_TEST:]
    df_model = df_data.iloc[:-N_TEST]

    print(f"Model: {df_model.shape}")
    print(f"Test: {df_test.shape}")

    return df_data, df_no_data, df_model, df_test


def develop_model(df_model):
    param_grid = {
        'max_depth': [3, 5, 7],
        'learning_rate': [0.1, 0.01, 0.001],
        'subsample': [0.5, 0.7, 1]
    }

    # Create the XGBoost model object
    xgb_model = xgb.XGBRegressor()

    # Create the GridSearchCV object
    grid_search = GridSearchCV(xgb_model, param_grid, cv=CV, scoring='neg_mean_squared_error')

    # Fit the GridSearchCV object to the training data
    y_train = df_model.pop("y")
    close_train = df_model.pop("close")
    X_train = df_model
    start_time = time.time()
    print("Started training...")
    grid_search.fit(X_train, y_train)
    print(f"Finished training, spent {time.time() - start_time:.1f} seconds")

    # Print the best set of hyperparameters and the corresponding score
    print("Best set of hyperparameters: ", grid_search.best_params_)
    print("Best score: ", grid_search.best_score_)

    return grid_search.best_estimator_


def evaluate_model(model, df_test):
    df_c = df_test.copy()
    y_test = df_c.pop("y")
    close_test = df_c.pop("close")
    X_test = df_c

    y_test_pred = model.predict(X_test)
    df_eval = df_test.copy()
    df_eval.insert(0, "y_pred", y_test_pred)
    rmse = root_mean_squared_error(df_eval["y"], df_eval["y_pred"])
    mape = mean_absolute_percentage_error(df_eval["y"], df_eval["y_pred"])
    print(f"RMSE: {rmse:.3f}, MAPE: {mape:.2%}")
    print(f"Actual: {df_eval['y'].to_list()}")
    print(f"Predict: {[round(p, 3) for p in df_eval['y_pred'].to_list()]}")
    plt.plot(df_eval["y"], label="Actual")
    plt.plot(df_eval["y_pred"], label="Predict")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(SAVEFIG_01)
    plt.clf()


def predict_prices(model, df_no_data):
    df_c = df_no_data.copy()

    df_c.pop("y")
    close_no_data = df_c.pop("close")
    X_no_data = df_c

    # Create prediction data
    y_test_pred = model.predict(X_no_data)
    indices = []
    for i in range(N_PREDICT):
        t = close_no_data.index[-1] + timedelta(days=i + 1)
        indices.append(t)
    predicts = pd.Series(data=y_test_pred, index=indices)

    plt.plot(close_no_data, marker=".", label="Actual")
    plt.plot(predicts, marker=".", linestyle="--", label="Predict")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(SAVEFIG_02)
    plt.clf()

    return predicts.iloc[-1]

def get_future_price():

    # Get historical candles
    candles = get_candles()

    # Convert candles to dataframe
    df = convert_candle_to_df(candles)

    # Feature engineering
    df = engineer_features(df)

    # Data split
    df_data, df_no_data, df_model, df_test = split_data(df)

    # Develop model
    model = develop_model(df_model)

    # Evaluation
    evaluate_model(model, df_test)

    # Prediction
    future_price = predict_prices(model, df_no_data)

    return future_price


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


def open_position():

    # Get future price
    future_price = get_future_price()

    # Get the most recent price
    recent_price = get_recent_price()

    # Create an order
    order = ORDER
    # Long
    if future_price > recent_price:
        order["units"] = str(UNITS)
    # Short
    else:
        order["units"] = str(-UNITS)

    # Check order
    print(f"Future price: {future_price:.3f}, recent price: {recent_price}")
    print(f"Order: {order}")

    payload = json.dumps({
        "order": order
    })
    headers = make_headers()
    r = requests.post(
        url=f"{API_URL}/v3/accounts/{ACCOUNT_ID}/orders",
        headers=headers,
        data=payload
    )
    print(f"open_position()")
    print(f"Status code: {r.status_code}")
    return r.json()


@functions_framework.http
def main(request):

    start_time = time.time()

    # Check position
    positions = get_positions()

    # Test
    # positions = []

    # If there is no position
    if not positions:
        # Open position
        new_position = open_position()
        print(new_position)
        print(f"Spent {time.time() - start_time:.1f} seconds")
        return 'Opened a new position'

    # If there is a position
    else:
        print("Don't open a new position, because there is an existing following position")
        print(positions)
        print(f"Spent {time.time() - start_time:.1f} seconds")
        return 'No new position'


if __name__ == "__main__":
    main(None)
