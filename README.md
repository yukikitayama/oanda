# OANDA

## Get candles

- https://developer.oanda.com/rest-live-v20/instrument-ep/
- `time` is start time

## Overview

Trading hours
- Sunday 17:05 to Friday 16:59 in Eastern Time
  - At 5PM ET, a trading day ends and starts a new trading day
  - e.g., 2025-07-09 9AM ET is still doing a candlestick of 2025-07-08T21?
- There will be a six minute break between 16:59 - 17:05
- During closed hours, a market order will be cancelled.
- https://www.oanda.com/us-en/trading/hours-of-operation/

## API

API base URL
- Demo account
  - https://api-fxpractice.oanda.com
- Live account
  - https://api-fxtrade.oanda.com

## Manual trading

- 逆張りしない
- Open a position when you are confident
- Open a position with stop loss
- Don't change the stop loss you initially set

## Algorithmic trading

- Open a position with stop loss and take profit
- Don't accumulate positions.
  - If you wanna make another position, close the current position and open a new position.
- Don't straddling (両建てしない)

## Database

### Candles

`usdjpy_ny_day_mid_candles`
- `date`, date
- `open`, float
- `high`, float
- `low`, float
- `close`, float
- `volumn`, integer
- `write_timestamp`, timestamp

### `activities`
- `ticket`, integer
- `datetime`, timestamp
- `type`, string
  - change trade (take profit order, stop loss order)
  - buy market (open long)
  - sell market (open short)
  - market order
  - sell market filled (close long)
  - close trade (manually close current position)
- `market`, string
- `units`, integer
- `price`, float
- `spread_cost`, float
- `profit`, float
- `amount`, float
- `commission`, float
- `balance`, float

### `transactions`
- transaction_id
- time
- type
  - STOP_LOSS_ORDER

## Metrics

- Total PL
- Average PL
- Number of positions
- Average duration of time to hold a position
- Prediction accuracy