# 📈 Trading Strategies Guide

This guide explains how to use the different trading strategies available in the backtesting system.

## 🎯 Available Strategies

### 1. Moving Average Crossover (`ma_crossover`)

**How it works:**
- Uses two Exponential Moving Averages (EMAs)
- **BUY** when short EMA crosses above long EMA
- **SELL** when short EMA crosses below long EMA

**Parameters:**
- `short_window`: Period for short EMA (default: 20)
- `long_window`: Period for long EMA (default: 50)

**API Example:**
```json
{
  "strategy_name": "ma_crossover",
  "stock_symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000,
  "strategy_params": {
    "short_window": 20,
    "long_window": 50
  }
}
```

### 2. Bollinger Bands (`bollinger_bands`)

**How it works:**
- Uses a Simple Moving Average with upper and lower bands
- **BUY** when price touches/goes below Lower Band (oversold)
- **SELL** when price touches/goes above Upper Band (overbought)

**Parameters:**
- `window`: Period for moving average (default: 20)
- `std_dev`: Standard deviation multiplier (default: 2.0)

**API Example:**
```json
{
  "strategy_name": "bollinger_bands",
  "stock_symbol": "MSFT", 
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 10000,
  "strategy_params": {
    "window": 20,
    "std_dev": 2.0
  }
}
```

## 🚀 How to Use

### Step 1: Start a Backtest
```bash
curl -X POST "http://127.0.0.1:8000/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_name": "bollinger_bands",
    "stock_symbol": "AAPL",
    "strategy_params": {
      "window": 14,
      "std_dev": 1.5
    }
  }'
```

**Response:**
```json
{
  "status": "success", 
  "message": "Backtest started successfully.",
  "backtest_id": "abc123..."
}
```

### Step 2: Check Status
```bash
curl "http://127.0.0.1:8000/backtest/abc123.../status"
```

### Step 3: Get Results (when completed)
```bash
curl "http://127.0.0.1:8000/backtest/abc123..."
```

## 📊 Chart Data Differences

### MA Crossover Chart Data:
```json
{
  "Date": "2023-01-04T00:00:00-0500",
  "Open": 125.13,
  "Close": 124.60,
  "EMA20": 123.45,
  "EMA50": 123.38,
  "Position": 1.0
}
```

### Bollinger Bands Chart Data:
```json
{
  "Date": "2023-01-04T00:00:00-0500", 
  "Open": 125.13,
  "Close": 124.60,
  "SMA_20": 123.50,
  "Upper_Band": 126.75,
  "Lower_Band": 120.25,
  "Percent_B": 0.65,
  "Position": -1.0
}
```

## 🛠️ Adding New Strategies

To add a new strategy:

1. Create a new file in `strategy/` folder
2. Follow the same pattern as existing strategies
3. Return DataFrame with `Position` column
4. Update `get_strategy_data()` function in `main.py`
5. Add chart data handling in results endpoint

## 💡 Tips

- **MA Crossover** works well in trending markets
- **Bollinger Bands** works well in ranging/sideways markets
- Test with different parameters to optimize performance
- Use shorter time periods for testing to get quick results