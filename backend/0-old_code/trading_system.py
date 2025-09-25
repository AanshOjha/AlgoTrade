import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
import mplfinance as mpf
import os

# ==============================================================================
# 1. DATABASE MANAGER
# ==============================================================================
class DatabaseManager:
    """Handles all interactions with the SQLite database."""

    def __init__(self, db_name="trading_data.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self._create_table()
        print(f"DatabaseManager initialized. Connected to '{self.db_name}'.")

    def _create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                symbol TEXT NOT NULL, timestamp DATETIME NOT NULL,
                open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL,
                close REAL NOT NULL, volume INTEGER NOT NULL,
                PRIMARY KEY (symbol, timestamp)
            )
        ''')
        self.conn.commit()

    def save_data(self, symbol, data_df):
        if data_df is None or data_df.empty: return
        df = data_df.copy()
        df['symbol'] = symbol
        df.reset_index(inplace=True)
        
        # Debug: Print the actual column names to understand the structure
        print(f"DEBUG: Columns in downloaded data: {list(df.columns)}")
        
        # Handle different possible index names from yfinance
        timestamp_col = None
        if 'Date' in df.columns:
            timestamp_col = 'Date'
        elif 'Datetime' in df.columns:
            timestamp_col = 'Datetime'
        elif df.index.name == 'Date':
            # If index is still named Date after reset_index, it should be available as a column
            timestamp_col = 'Date'
        else:
            # If none of the above, assume the first column after reset_index is the timestamp
            timestamp_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
        
        # Create rename mapping based on actual columns
        rename_mapping = {
            timestamp_col: 'timestamp',
            'Open': 'open', 
            'High': 'high', 
            'Low': 'low', 
            'Close': 'close', 
            'Volume': 'volume'
        }
        
        # Only rename columns that actually exist
        actual_rename_mapping = {k: v for k, v in rename_mapping.items() if k in df.columns}
        df.rename(columns=actual_rename_mapping, inplace=True)
        
        # Ensure we have the required columns
        required_cols = ['symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in required_cols if col in df.columns]
        
        if 'timestamp' not in available_cols:
            print(f"ERROR: Could not find timestamp column. Available columns: {list(df.columns)}")
            return
            
        df = df[available_cols]
        
        print(f"Saving {len(df)} records for {symbol} to the database...")
        try:
            df.to_sql('historical_prices', self.conn, if_exists='append', index=False)
        except sqlite3.IntegrityError:
            print(f"Some records for {symbol} already exist. Skipping duplicates.")

    def get_data(self, symbol, start_date, end_date):
        print(f"Attempting to load data for {symbol} from local database...")
        query = f"SELECT * FROM historical_prices WHERE symbol = ? AND timestamp BETWEEN ? AND ?"
        df = pd.read_sql_query(query, self.conn, params=(symbol, start_date, end_date),
                               index_col='timestamp', parse_dates=['timestamp'])
        df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 
                           'close': 'Close', 'volume': 'Volume'}, inplace=True)
        return df

    def close(self):
        if self.conn: self.conn.close()

# ==============================================================================
# 2. DATA FEED HANDLER
# ==============================================================================
class DataFeedHandler:
    """Handles fetching historical data, using the database as a cache."""
    def __init__(self, db_manager):
        self.db_manager = db_manager
        print("DataFeedHandler initialized.")

    def fetch_historical_data(self, symbol, start_date, end_date, interval='15m'):
        data = self.db_manager.get_data(symbol, start_date, end_date)
        days_requested = (pd.to_datetime(end_date) - pd.to_datetime(start_date)).days
        if not data.empty and len(data) >= days_requested * 0.7:
            print(f"Successfully loaded {len(data)} records for {symbol} from the database.")
            return data
        
        print(f"Downloading data for {symbol} from yfinance...")
        try:
            ticker = yf.Ticker(symbol)
            data_downloaded = ticker.history(start=start_date, end=end_date, interval=interval)
            if data_downloaded.empty: return None
            self.db_manager.save_data(symbol, data_downloaded)
            return data_downloaded
        except Exception as e:
            print(f"An error occurred while fetching data for {symbol}: {e}")
            return None

# ==============================================================================
# 3. STRATEGY AND BACKTESTING
# ==============================================================================
class StrategyBacktester:
    """Handles strategy implementation, backtesting, and visualization."""

    def __init__(self, initial_capital=100000.0):
        self.initial_capital = initial_capital
        print(f"StrategyBacktester initialized with initial capital of ${initial_capital:,.2f}")

    def _calculate_indicators(self, data, short_window, long_window, use_ema_for_long=True):
        if use_ema_for_long:
            print(f"Calculating {short_window}-day EMA and {long_window}-day EMA...")
            data['Short_EMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
            data['Long_MA'] = data['Close'].ewm(span=long_window, adjust=False).mean()
            data['Long_MA_Type'] = 'EMA'
        else:
            print(f"Calculating {short_window}-day EMA and {long_window}-day SMA...")
            data['Short_EMA'] = data['Close'].ewm(span=short_window, adjust=False).mean()
            data['Long_MA'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
            data['Long_MA_Type'] = 'SMA'
        return data

    def _generate_signals(self, data):
        print("Generating trading signals...")
        data['Signal'] = np.where(data['Short_EMA'] > data['Long_MA'], 1.0, 0.0)
        data['Position'] = data['Signal'].diff()
        return data

    def run_backtest(self, data, short_window=50, long_window=200, use_ema_for_long=True):
        if data is None or data.empty: return None, {}
        data_with_indicators = self._calculate_indicators(data, short_window, long_window, use_ema_for_long)
        signals = self._generate_signals(data_with_indicators)
        
        print("Simulating trades...")
        portfolio = pd.DataFrame(index=signals.index).fillna(0.0)
        portfolio['Holdings'] = 0.0
        portfolio['Cash'] = self.initial_capital
        position = 0

        for i in range(len(signals)):
            price = signals.loc[signals.index[i], 'Close']
            if i > 0:
                portfolio.loc[signals.index[i], 'Cash'] = portfolio.loc[signals.index[i-1], 'Cash']
                portfolio.loc[signals.index[i], 'Holdings'] = portfolio.loc[signals.index[i-1], 'Holdings']

            if signals.loc[signals.index[i], 'Position'] == 1.0 and position == 0:
                position = 1
                shares_to_buy = portfolio.loc[signals.index[i], 'Cash'] / price
                portfolio.loc[signals.index[i], 'Holdings'] = shares_to_buy * price
                portfolio.loc[signals.index[i], 'Cash'] = 0.0
                print(f"{signals.index[i].date()}: BUY signal at ${price:.2f}")

            elif signals.loc[signals.index[i], 'Position'] == -1.0 and position == 1:
                position = 0
                portfolio.loc[signals.index[i], 'Cash'] = portfolio.loc[signals.index[i], 'Holdings']
                portfolio.loc[signals.index[i], 'Holdings'] = 0.0
                print(f"{signals.index[i].date()}: SELL signal at ${price:.2f}")

            if position == 1:
                # Find the last buy signal up to current date
                signals_up_to_now = signals.loc[:signals.index[i]]
                buy_signals_mask = signals_up_to_now['Position'] == 1.0
                buy_dates = signals_up_to_now.index[buy_signals_mask]
                if len(buy_dates) > 0:
                    last_buy_date = buy_dates.max()
                    buy_price = signals.loc[last_buy_date, 'Close']
                    shares_held = (portfolio.loc[last_buy_date, 'Holdings'] + portfolio.loc[last_buy_date, 'Cash']) / buy_price
                    portfolio.loc[signals.index[i], 'Holdings'] = shares_held * price
        
        portfolio['Total'] = portfolio['Cash'] + portfolio['Holdings']
        final_value = portfolio['Total'].iloc[-1]
        returns = (final_value - self.initial_capital) / self.initial_capital * 100
        
        results = {"final_value": final_value, "total_return_pct": returns}
        full_report = pd.concat([signals, portfolio], axis=1)
        return full_report, results

    def plot_results(self, report, symbol, start_date, end_date, short_window=50, long_window=200):
        if report is None:
            print("No report to plot.")
            return

        print("Generating enhanced chart with legends and buy/sell signals...")
        
        # Calculate time period in years
        start_year = pd.to_datetime(start_date).year
        end_year = pd.to_datetime(end_date).year
        time_period = end_year - start_year
        
        # Get MA type
        ma_type = report['Long_MA_Type'].iloc[0] if 'Long_MA_Type' in report.columns else 'EMA'
        
        # Create Results directory if it doesn't exist
        results_dir = "Results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"Created '{results_dir}' directory")
        
        # Create plot with moving averages and custom labels
        ap0 = [
            mpf.make_addplot(report['Short_EMA'], color='blue', width=1.2, label=f'{short_window}-day EMA'),
            mpf.make_addplot(report['Long_MA'], color='orange', width=1.2, label=f'{long_window}-day {ma_type}'),
        ]
        
        # Create markers for buy/sell signals
        buy_signal_prices = pd.Series(index=report.index, dtype=float)
        sell_signal_prices = pd.Series(index=report.index, dtype=float)
        
        buy_mask = report['Position'] == 1.0
        sell_mask = report['Position'] == -1.0
        
        buy_signal_prices[buy_mask] = report.loc[buy_mask, 'Close']
        sell_signal_prices[sell_mask] = report.loc[sell_mask, 'Close']
        
        if buy_signal_prices.notna().any():
            ap0.append(mpf.make_addplot(buy_signal_prices, type='scatter', marker='^', 
                                      color='green', markersize=120, label='Buy Signal'))
        if sell_signal_prices.notna().any():
            ap0.append(mpf.make_addplot(sell_signal_prices, type='scatter', marker='v', 
                                      color='red', markersize=120, label='Sell Signal'))

        # Generate the chart with enhanced styling
        strategy_name = f"50EMA-{long_window}{ma_type}"
        chart_title = f'{symbol} | {strategy_name} Crossover Strategy | {time_period}Y ({start_year}-{end_year})'
        
        fig, axes = mpf.plot(report, type='candle', style='charles',
                             title=chart_title,
                             ylabel='Price ($)',
                             addplot=ap0,
                             figsize=(16, 9),
                             returnfig=True,
                             volume=False)
        
        # Add custom legend manually since mplfinance doesn't support legends directly
        import matplotlib.patches as mpatches
        
        # Create legend elements
        legend_elements = [
            mpatches.Patch(color='blue', label=f'{short_window}-day EMA'),
            mpatches.Patch(color='orange', label=f'{long_window}-day {ma_type}'),
        ]
        
        if buy_signal_prices.notna().any():
            legend_elements.append(mpatches.Patch(color='green', label='Buy Signal ▲'))
        if sell_signal_prices.notna().any():
            legend_elements.append(mpatches.Patch(color='red', label='Sell Signal ▼'))
        
        # Add candlestick legend
        legend_elements.append(mpatches.Patch(color='black', label='Price Candlesticks'))
        
        # Add legend to the plot
        axes[0].legend(handles=legend_elements, loc='upper left', frameon=True, 
                      fancybox=True, shadow=True, fontsize=10)
        
        # Create descriptive filename
        chart_filename = f"{symbol}_{strategy_name}_{time_period}Y_{start_year}-{end_year}_backtest.png"
        chart_path = os.path.join(results_dir, chart_filename)
        
        # Save with high DPI for better quality
        fig.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"✅ Chart saved to: '{os.path.abspath(chart_path)}'")
        print(f"📊 Strategy: {strategy_name} | Period: {time_period} years | Symbol: {symbol}")
        
        return chart_path


# ==============================================================================
# 4. USER INPUT FUNCTIONS
# ==============================================================================
def get_user_preferences():
    """Get user preferences for trading strategy configuration."""
    print("\n=== Trading Strategy Configuration ===")
    
    while True:
        choice = input("\nChoose the long-term moving average type:\n1. EMA (Exponential Moving Average) - More responsive\n2. SMA (Simple Moving Average) - Smoother\nEnter your choice (1 or 2): ").strip()
        
        if choice == '1':
            use_ema = True
            print("✓ Selected: 200-day EMA (more responsive to recent price changes)")
            break
        elif choice == '2':
            use_ema = False
            print("✓ Selected: 200-day SMA (smoother, less sensitive to noise)")
            break
        else:
            print("❌ Invalid choice. Please enter 1 or 2.")
    
    return use_ema

# ==============================================================================
# 5. MAIN APPLICATION EXECUTION
# ==============================================================================
def main():
    """Main function to run the entire trading system process."""
    print("\n--- Trading System Initializing ---")
    
    # Get user preferences
    use_ema_for_long = get_user_preferences()
    
    # Configuration
    SYMBOL = 'AAPL'
    START_DATE = '2020-01-01'
    END_DATE = '2024-12-31'
    SHORT_WINDOW = 50
    LONG_WINDOW = 200

    # Initialization
    db_manager = DatabaseManager()
    data_handler = DataFeedHandler(db_manager)
    backtester = StrategyBacktester(initial_capital=100000.0)

    # --- Step 1: Fetch Data ---
    print("\n--- 1. Fetching Historical Data ---")
    historical_data = data_handler.fetch_historical_data(SYMBOL, START_DATE, END_DATE)

    if historical_data is not None:
        # --- Step 2: Run Backtest ---
        print("\n--- 2. Running Backtest ---")
        report, metrics = backtester.run_backtest(
            data=historical_data, 
            short_window=SHORT_WINDOW,
            long_window=LONG_WINDOW,
            use_ema_for_long=use_ema_for_long
        )

        if report is not None:
            print("\n--- 3. Backtest Results ---")
            print(f"Final Portfolio Value: ${metrics.get('final_value', 0):,.2f}")
            print(f"Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            
            # --- Step 4: Generate Chart ---
            print("\n--- 4. Visualizing Results ---")
            backtester.plot_results(report, SYMBOL, START_DATE, END_DATE, SHORT_WINDOW, LONG_WINDOW)
            
    # Cleanup
    db_manager.close()
    print("\n--- Trading System Finished ---")


if __name__ == '__main__':
    main()