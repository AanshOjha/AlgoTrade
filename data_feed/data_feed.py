import yfinance as yf
import pandas as pd
import os

# Configuration variables
stock_symbol = "AAPL"
start_date = "2017-01-01"
end_date = "2024-12-31"
interval = "1d"  # 1d, 1wk, 1mo, etc.

def fetch_stock_data(symbol=stock_symbol, start=start_date, end=end_date, data_interval=interval, save_to_file=False):
    """
    Fetch stock data using yfinance and return as pandas DataFrame
    Optional: save data to CSV file in data_feed folder
    """
    
    # Create ticker object
    ticker = yf.Ticker(symbol)
    
    # Download historical data
    data = ticker.history(
        start=start,
        end=end,
        interval=data_interval
    )
    
    # Save to file if requested
    if save_to_file and not data.empty:
        # Create filename with symbol and date range
        filename = f"{symbol.replace('.', '_')}_{start}_{end}_{data_interval}.csv"
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Save to CSV
        data.to_csv(filepath)
        return data, filepath
    
    return data

