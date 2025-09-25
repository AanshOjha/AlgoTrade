import matplotlib.pyplot as plt
from strategy.ma_crossover import ma_crossover_strategy

def create_trading_chart():
    """
    Create a simple trading chart showing stock price, EMAs, and buy/sell signals
    """
    # Get data from strategy
    data = ma_crossover_strategy()
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    plt.plot(data['Close'], label='Close Price')
    plt.plot(data['EMA20'], label='20-day EMA')
    plt.plot(data['EMA50'], label='50-day EMA')
    plt.plot(
        data[data['Position'] == 1].index, 
        data['Close'][data['Position'] == 1], 
        '^', 
        markersize=10, 
        color='g', 
        label='Buy signal'
    )
    plt.plot(
        data[data['Position'] == -1].index, 
        data['Close'][data['Position'] == -1],
        'v', 
        markersize=10, 
        color='r', 
        label='Sell signal'
    )
    plt.title('ONGC.NS EMA Crossover Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()
    
    return "Chart displayed successfully"

if __name__ == "__main__":
    create_trading_chart()