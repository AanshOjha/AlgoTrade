# 📈 AlgoTrade - Advanced Algorithmic Trading Platform

A comprehensive full-stack trading application featuring a **FastAPI backend** with advanced backtesting capabilities and a **Vue.js frontend** with interactive charts and real-time analysis. Built for testing and analyzing multiple trading strategies with historical market data.

![Trading Platform](https://img.shields.io/badge/Trading-Platform-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi) ![Vue.js](https://img.shields.io/badge/Vue.js-4FC08D?logo=vue.js&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-003B57?logo=sqlite&logoColor=white)

## ✨ Features

### 🎯 **Trading Strategies**
- **Moving Average Crossover**: EMA-based trend following strategy
- **Bollinger Bands**: Mean reversion strategy with volatility bands
- **Extensible Architecture**: Easy to add custom strategies

### 📊 **Backtesting Engine**
- Historical data backtesting with real market data
- Performance metrics calculation (P&L, win rate, drawdown)
- Trade execution simulation with realistic constraints
- Portfolio value tracking over time

### 🖥️ **Interactive Frontend**
- Modern Vue.js interface with gradient animations
- Real-time chart visualization with Chart.js
- Strategy parameter configuration
- Visual trade analysis and performance reports

### 🔄 **Async Processing**
- Background task processing for long-running backtests
- Real-time status monitoring
- Non-blocking API endpoints

### 💾 **Data Management**
- SQLite database for trade storage
- Historical data caching
- CSV export capabilities

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   Database      │
│   Vue.js        │◄──►│   FastAPI       │◄──►│   SQLite        │
│   - Chart.js    │    │   - Strategies  │    │   - Trades      │
│   - Vite        │    │   - Backtesting │    │   - Backtests   │
│   - Pinia       │    │   - Data Feed   │    │   - Jobs        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Available Trading Strategies

### 1. Moving Average Crossover (`ma_crossover`)

**Strategy Logic:**
- Uses two Exponential Moving Averages (EMAs)
- **BUY SIGNAL**: When short EMA crosses above long EMA (bullish crossover)
- **SELL SIGNAL**: When short EMA crosses below long EMA (bearish crossover)

**Parameters:**
- `short_window` (default: 20): Period for short-term EMA
- `long_window` (default: 50): Period for long-term EMA

**Best For:** Trending markets, momentum trading

### 2. Bollinger Bands (`bollinger_bands`)

**Strategy Logic:**
- Uses Simple Moving Average with standard deviation bands
- **BUY SIGNAL**: When price touches or goes below Lower Band (oversold condition)
- **SELL SIGNAL**: When price touches or goes above Upper Band (overbought condition)

**Parameters:**
- `window` (default: 20): Period for moving average calculation
- `std_dev` (default: 2.0): Standard deviation multiplier for bands

**Indicators Provided:**
- Middle Band (SMA)
- Upper Band (SMA + 2×STD)
- Lower Band (SMA - 2×STD)
- %B (Price position within bands)
- Bandwidth (volatility measure)

**Best For:** Range-bound markets, mean reversion trading

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:8000
```

### Authentication
No authentication required for this demo application.

---

### 📈 **GET** `/trades`
Retrieve trade history with optional filtering.

**Query Parameters:**
- `strategy_name` (optional): Filter by strategy (`ma_crossover`, `bollinger_bands`)
- `ticker` (optional): Filter by stock symbol (`AAPL`, `MSFT`, etc.)
- `backtest_id` (optional): Filter by specific backtest session
- `limit` (optional): Limit number of results returned

**Response Format:**
```json
[
  {
    "trade_id": 1,
    "strategy_name": "ma_crossover",
    "ticker": "AAPL",
    "quantity": 50,
    "entry_datetime": "2024-01-15T00:00:00",
    "entry_price": 185.50,
    "exit_datetime": "2024-01-25T00:00:00",
    "exit_price": 192.30,
    "pnl": 340.00,
    "trade_duration_days": 10
  }
]
```

**Example Requests:**
```bash
# Get all trades
curl "http://127.0.0.1:8000/trades"

# Get trades for specific strategy
curl "http://127.0.0.1:8000/trades?strategy_name=ma_crossover"

# Get trades for specific stock with limit
curl "http://127.0.0.1:8000/trades?ticker=AAPL&limit=10"
```

---

### 🚀 **POST** `/backtest`
Start a new backtest job in background.

**Request Body:**
```json
{
  "stock_symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 100000,
  "strategy_name": "ma_crossover",
  "strategy_params": {
    "short_window": 20,
    "long_window": 50
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Backtest started successfully.",
  "backtest_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Strategy Examples:**

**Moving Average Crossover:**
```json
{
  "strategy_name": "ma_crossover",
  "stock_symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 50000,
  "strategy_params": {
    "short_window": 12,
    "long_window": 26
  }
}
```

**Bollinger Bands:**
```json
{
  "strategy_name": "bollinger_bands",
  "stock_symbol": "MSFT",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "initial_capital": 75000,
  "strategy_params": {
    "window": 20,
    "std_dev": 2.5
  }
}
```

---

### ⏱️ **GET** `/backtest/{backtest_id}/status`
Check the current status of a backtest job.

**Response:**
```json
{
  "backtest_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "job_status": "RUNNING",
  "error_message": null,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:31:00"
}
```

**Status Values:**
- `PENDING`: Job queued but not started
- `RUNNING`: Currently executing backtest
- `COMPLETED`: Successfully finished
- `FAILED`: Error occurred during execution

---

### 📊 **GET** `/backtest/{backtest_id}`
Retrieve complete backtest results with performance metrics and chart data.

**Response Structure:**
```json
{
  "backtest_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "performance_report": {
    "final_portfolio_value": 110500.00,
    "total_profit_loss_pct": 10.50,
    "total_trades": 15,
    "win_rate_pct": 66.67,
    "initial_capital": 100000.00,
    "total_pnl": 10500.00,
    "strategy_name": "ma_crossover",
    "stock_symbol": "AAPL"
  },
  "equity_curve": [
    {
      "date": "2023-01-01",
      "value": 100000.00
    },
    {
      "date": "2023-01-02", 
      "value": 100250.00
    }
  ],
  "chart_data": [
    {
      "Date": "2023-01-01T00:00:00",
      "Open": 130.28,
      "High": 131.89,
      "Low": 130.11,
      "Close": 131.44,
      "Volume": 70790800,
      "Position": 0,
      "EMA20": 130.50,
      "EMA50": 129.80
    }
  ]
}
```

---

### 🗑️ **DELETE** `/trades`
Delete all trade records from database.

**Response:**
```json
{
  "status": "success",
  "message": "Successfully deleted 25 trades",
  "deleted_count": 25
}
```

---

### 🗑️ **DELETE** `/backtests`
Delete all backtest job records from database.

**Response:**
```json
{
  "status": "success", 
  "message": "Successfully deleted 5 backtest jobs",
  "deleted_count": 5
}
```

## 🖥️ Frontend Features

### 🏠 **Home Page**
- **Modern Design**: Gradient backgrounds with floating animations
- **Strategy Overview**: Cards explaining each trading strategy
- **Quick Navigation**: Direct access to backtesting interface
- **Responsive Layout**: Mobile-friendly design

### 📈 **Backtest Dashboard**
- **Strategy Configuration**: 
  - Stock symbol selection
  - Date range picker
  - Strategy parameter adjustment
  - Initial capital setting

- **Real-time Monitoring**:
  - Live status updates during backtest execution
  - Progress indicators
  - Error handling with user-friendly messages

- **Performance Analysis**:
  - Key metrics dashboard (P&L, win rate, total trades)
  - Visual performance indicators with color coding
  - Backtest details and configuration summary

### 📊 **Interactive Charts** (Chart.js Integration)
- **Price Chart with Signals**:
  - OHLC candlestick data visualization
  - Strategy-specific indicators overlay
  - Buy/sell signal markers
  - Customizable time ranges

- **Portfolio Equity Curve**:
  - Portfolio value progression over time
  - Initial vs final capital comparison
  - Performance percentage tracking

- **Trade History Analysis**:
  - Individual trade details
  - Profit/loss visualization
  - Trade duration analysis
  - Win/loss statistics

### 🎨 **UI/UX Features**
- **Animated Backgrounds**: Floating geometric shapes
- **Responsive Design**: Mobile and desktop optimized
- **Loading States**: Smooth transitions and spinners
- **Error Handling**: User-friendly error messages
- **Color-coded Results**: Green for profits, red for losses

## 🚀 Quick Start Guide

### Prerequisites
- **Python 3.8+**
- **Node.js 20.19.0+**
- **npm or yarn**

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure settings (optional):**
Edit `config.py` or create `.env` file:
```python
STOCK_SYMBOL=AAPL
START_DATE=2024-01-01
END_DATE=2024-12-31
INITIAL_CAPITAL=100000.0
```

4. **Start the FastAPI server:**
```bash
python main.py
```
Server will start at `http://127.0.0.1:8000`

5. **View API documentation:**
- Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install Node.js dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```
Frontend will start at `http://localhost:5173`

### Production Build

**Backend:**
```bash
# Install gunicorn for production
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

**Frontend:**
```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## 📁 Project Structure

```
AlgoTrade/
├── 📂 backend/                          # FastAPI Backend
│   ├── 📄 main.py                       # FastAPI application & API routes
│   ├── 📄 config.py                     # Configuration settings
│   ├── 📄 requirements.txt              # Python dependencies
│   ├── 📄 STRATEGIES.md                 # Strategy documentation
│   ├── 📄 trade_data.db                 # SQLite database
│   │
│   ├── 📂 backtest/                     # Backtesting Engine
│   │   ├── 📄 __init__.py
│   │   └── 📄 backtesting_engine.py     # Core backtesting logic
│   │
│   ├── 📂 data_feed/                    # Market Data Management
│   │   ├── 📄 __init__.py
│   │   ├── 📄 data_feed.py              # Yahoo Finance integration
│   │   └── 📄 *.csv                     # Historical data cache
│   │
│   ├── 📂 database/                     # Database Layer
│   │   ├── 📄 __init__.py
│   │   └── 📄 db_engine.py              # SQLite operations
│   │
│   ├── 📂 strategy/                     # Trading Strategies
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ma_crossover.py           # MA Crossover strategy
│   │   └── 📄 bollinger_bands.py        # Bollinger Bands strategy
│   │
│   └── 📂 testing/                      # Testing & Development
│       ├── 📄 test_backtest.py          # Backtest tests
│       ├── 📄 test_strategies.py        # Strategy tests
│       └── 📄 chart.py                  # Chart generation utilities
│
├── 📂 frontend/                         # Vue.js Frontend
│   ├── 📄 package.json                  # Node.js dependencies
│   ├── 📄 vite.config.js                # Vite configuration
│   ├── 📄 index.html                    # HTML entry point
│   │
│   ├── 📂 src/                          # Source code
│   │   ├── 📄 main.js                   # Vue app entry
│   │   ├── 📄 App.vue                   # Root component
│   │   │
│   │   ├── � views/                    # Page components
│   │   │   ├── 📄 HomeView.vue          # Landing page
│   │   │   └── 📄 BacktestView.vue      # Backtest dashboard
│   │   │
│   │   ├── 📂 router/                   # Vue Router
│   │   │   └── 📄 index.js              # Route definitions
│   │   │
│   │   └── 📂 stores/                   # Pinia state management
│   │       └── 📄 counter.js            # Store example
│   │
│   └── 📂 public/                       # Static assets
│       ├── 📄 favicon.ico
│       └── 📄 logo.png
│
└── 📄 README.md                         # This file
```

## 📊 Performance Metrics

The system calculates comprehensive performance metrics:

- **Total Return %**: Overall portfolio performance 
- **Profit/Loss**: Absolute dollar gains/losses
- **Win Rate**: Percentage of profitable trades
- **Total Trades**: Number of completed trades 
- **Portfolio Value Progression**: Daily portfolio values

### 📈 **Chart Visualizations**
- **Price Chart with Signals**: Candlestick charts showing buy/sell entry and exit points
- **Equity Curve**: Portfolio value progression over the backtesting period
- **Trade History**: Individual trade performance and duration analysis