import yfinance as yf

class DataFeedHandler:
    """
    Handles fetching historical data.
    - Uses yfinance for historical OHLCV data.
    """

    def __init__(self):
        """Initializes the DataFeedHandler."""
        print("DataFeedHandler initialized.")

    def fetch_historical_data(self, symbol, start_date, end_date, interval='1d'):
        """
        Fetches historical OHLCV data for a given symbol.

        Args:
            symbol (str): The stock/crypto symbol (e.g., 'AAPL', 'BTC-USD').
            start_date (str): The start date in 'YYYY-MM-DD' format.
            end_date (str): The end date in 'YYYY-MM-DD' format.
            interval (str): The data interval (e.g., 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 4h, 1d, 5d, 1wk, 1mo, 3mo).

        Returns:
            pandas.DataFrame: A DataFrame containing the historical data,
                              or None if an error occurs.
        """ 
        print(f"Fetching historical data for {symbol} from {start_date} to {end_date}...")
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start_date, end=end_date, interval=interval)
            if data.empty:
                print(f"No historical data found for symbol {symbol} in the given date range.")
                return None
            print(f"Successfully fetched {len(data)} records for {symbol}.")
            return data
        except Exception as e:
            print(f"An error occurred while fetching historical data for {symbol}: {e}")
            return None


# --- Main Application Logic Example ---
def main():
    """Main function to demonstrate the DataFeedHandler."""
    print("\n--- Trading App Data Feed Demonstration ---")
    handler = DataFeedHandler()

    # 1. Fetch historical data
    print("\n--- 1. Testing Historical Data ---")
    historical_data = handler.fetch_historical_data('AAPL', '2017-01-01', '2024-12-31', '1d')
    if historical_data is not None:
        print("Historical Data Head:")
        print(historical_data)    # print(historical_data.head()) == prints first 5 rows
    
    print("\nDemonstration finished.")


if __name__ == '__main__':
    main()