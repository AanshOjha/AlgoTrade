from data_feed.data_feed import fetch_stock_data
from config import settings

def bollinger_bands_strategy(
        window: int = 20,
        std_dev: float = 2.0,
        stock_symbol: str = settings.STOCK_SYMBOL,
        start_date: str = settings.START_DATE,
        end_date: str = settings.END_DATE
    ):
    """Bollinger Bands strategy: Buy at lower band, sell at upper band"""
    
    # Fetch historical stock data
    print(f"Fetching data for {stock_symbol} from {start_date} to {end_date}")
    result = fetch_stock_data(
        symbol=stock_symbol,
        start=start_date,
        end=end_date,
        data_interval=settings.INTERVAL,
        save_to_file=True
    )
    data = result[0]  # DataFrame
    
    # Calculate Bollinger Bands components
    
    # 1. Calculate Simple Moving Average (Middle Band)
    data[f'SMA_{window}'] = data['Close'].rolling(window=window).mean()
    
    # 2. Calculate Standard Deviation
    data[f'STD_{window}'] = data['Close'].rolling(window=window).std()
    
    # 3. Calculate Upper and Lower Bands
    data['Upper_Band'] = data[f'SMA_{window}'] + (data[f'STD_{window}'] * std_dev)
    data['Lower_Band'] = data[f'SMA_{window}'] - (data[f'STD_{window}'] * std_dev)
    
    # 4. Calculate Band Width (useful for volatility analysis)
    data['Band_Width'] = data['Upper_Band'] - data['Lower_Band']
    
    # 5. Calculate %B (Price position within bands)
    # %B = (Price - Lower Band) / (Upper Band - Lower Band)
    # %B > 1: Price above upper band
    # %B < 0: Price below lower band
    # %B = 0.5: Price at middle band
    data['Percent_B'] = (data['Close'] - data['Lower_Band']) / (data['Upper_Band'] - data['Lower_Band'])
    
    # Generate Trading Signals
    data['Buy_Signal'] = data['Close'] <= data['Lower_Band']
    data['Sell_Signal'] = data['Close'] >= data['Upper_Band']
    
    # Create position signals for backtesting
    data['Signal'] = 0
    data.loc[data['Buy_Signal'], 'Signal'] = 1
    data.loc[data['Sell_Signal'], 'Signal'] = -1
    data['Position'] = data['Signal'].diff()
    
    # Clean up data - remove NaN values
    data = data.dropna()
    
    # Display summary information
    print(f"Bollinger Bands Strategy: {data.shape} rows, {data['Buy_Signal'].sum()} buy signals, {data['Sell_Signal'].sum()} sell signals")
    
    return data