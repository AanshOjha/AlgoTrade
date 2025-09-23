from data_feed.data_feed import fetch_stock_data
from config import settings

def ma_crossover_strategy():
    """
    Simple Moving Average Crossover Strategy
    Buy when 50-day EMA crosses above 200-day EMA
    Sell when 50-day EMA crosses below 200-day EMA
    """
    # Fetch historical stock data
    result = fetch_stock_data(
        symbol=settings.STOCK_SYMBOL, 
        start=settings.START_DATE, 
        end=settings.END_DATE, 
        data_interval=settings.INTERVAL, 
        save_to_file=True
    )
    data = result[0]  # DataFrame
    
    # Calculate EMAs for all entries
    data['EMA50'] = data['Close'].ewm(span=50, adjust=False).mean()
    #data['EMA200'] = data['Close'].ewm(span=200, adjust=False).mean()
    data['EMA200'] = data['Close'].rolling(window=200).mean()

    # Generate trading signals based on moving average crossover
    # Signal: 1 when EMA50 > EMA200 (bullish), 0 when EMA50 < EMA200 (bearish)
    data['Signal'] = (data['EMA50'] > data['EMA200']).astype(int)
    
    # Position: 1 for buy signal, -1 for sell signal, 0 for no change
    data['Position'] = data['Signal'].diff()
    
    # Mark buy and sell points
    data['Buy_Signal'] = (data['Position'] == 1)
    data['Sell_Signal'] = (data['Position'] == -1)
    
    # Remove NaN values to make JSON compliant
    data = data.dropna()
    
    print(f"Data shape: {data.shape}")
    print("Sample data:")
    print(data[['Close', 'EMA50', 'EMA200', 'Signal', 'Position']].head())
    
    return data