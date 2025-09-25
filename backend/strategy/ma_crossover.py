from data_feed.data_feed import fetch_stock_data
from config import settings

def ma_crossover_strategy(
        short_window: int = 20, 
        long_window: int = 50,
        stock_symbol: str = settings.STOCK_SYMBOL,
        start_date: str = settings.START_DATE,
        end_date: str = settings.END_DATE
    ):
    f"""
    Simple Moving Average Crossover Strategy
    Buy when {short_window}-day EMA crosses above {long_window}-day EMA
    Sell when {short_window}-day EMA crosses below {long_window}-day EMA
    """
    # Fetch historical stock data
    result = fetch_stock_data(
        symbol=stock_symbol,
        start=start_date,
        end=end_date,
        data_interval=settings.INTERVAL,
        save_to_file=True
    )
    data = result[0]  # DataFrame
    
    # Calculate EMAs for all entries
    data[f'EMA{short_window}'] = data['Close'].ewm(span=short_window, adjust=False).mean()
    data[f'EMA{long_window}'] = data['Close'].ewm(span=long_window, adjust=False).mean()

    # Generate trading signals based on moving average crossover
    # Signal: 1 when EMA20 > EMA50 (bullish), 0 when EMA20 < EMA50 (bearish)
    data['Signal'] = (data[f'EMA{short_window}'] > data[f'EMA{long_window}']).astype(int)
    
    # Position: 1 for buy signal, -1 for sell signal, 0 for no change
    data['Position'] = data['Signal'].diff()
    
    # Mark buy and sell points
    data['Buy_Signal'] = (data['Position'] == 1)
    data['Sell_Signal'] = (data['Position'] == -1)
    
    # Remove NaN values to make JSON compliant
    data = data.dropna()
    
    print(f"MA Crossover Strategy: {data.shape} rows, EMA{short_window}/EMA{long_window}")
    
    return data