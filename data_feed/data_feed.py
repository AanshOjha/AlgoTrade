import yfinance as yf
import os
from config import settings

# Configuration variables
stock_symbol = settings.STOCK_SYMBOL
start_date = settings.START_DATE
end_date = settings.END_DATE
interval = settings.INTERVAL

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

