# OANDA

Trading hours
- Sunday 17:05 to Friday 16:59 in Eastern Time
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

- Transactions
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