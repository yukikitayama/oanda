-- Initialize table
CREATE TABLE oanda.candles (
  date DATE,
  time TIMESTAMP,
  open FLOAT64,
  high FLOAT64,
  low FLOAT64,
  close FLOAT64,
  volume INTEGER,
  write_timestamp TIMESTAMP
);

-- Check data
SELECT *
FROM `oanda.candles`
ORDER BY date DESC
LIMIT 10;