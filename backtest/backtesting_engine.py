import pandas as pd
from typing import Dict, List, Tuple, Any
from datetime import datetime
import sys
import os
from config import settings

# Add the database path to import
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'database'))
from database.db_engine import db_engine

def backtest_strategy(data: pd.DataFrame, 
                     strategy_name: str,
                     stock_symbol: str,
                     initial_capital: float = settings.INITIAL_CAPITAL, 
                     shares_to_buy: int = settings.SHARES_TO_BUY) -> Tuple[List[float], Dict[str, Any]]:
    """
    Backtest trading strategy based on position signals
    
    Args:
        data: DataFrame with OHLCV data and Position column (1 for buy, -1 for sell)
        strategy_name: Name of the strategy being backtested
        stock_symbol: Stock symbol being traded
        initial_capital: Starting capital amount
        shares_to_buy: Number of shares to buy on buy signal
    
    Returns:
        Tuple of (portfolio_values_list, performance_metrics_dict)
    """
    
    # Initialize variables
    portfolio_values = []
    cash = initial_capital
    shares_held = 0
    current_trade_id = None
    entry_date = None
    entry_price = None
    total_trades = 0
    winning_trades = 0
    
    # Ensure data is sorted by date
    data = data.sort_index()
    
    # Iterate through each row in the data
    for index, row in data.iterrows():
        current_price = row['Close']
        position = row.get('Position', 0)  # Get position signal
        
        # BUY SIGNAL (position == 1)
        if position == 1:
            if shares_held == 0:  # Not currently holding shares
                # Buy shares
                cost = shares_to_buy * current_price
                if cash >= cost:  # Check if we have enough cash
                    cash -= cost
                    shares_held = shares_to_buy
                    entry_price = current_price
                    entry_date = index
                    
                    # Insert trade into database
                    current_trade_id = db_engine.insert_trade(
                        strategy_name=strategy_name,
                        stock_symbol=stock_symbol,  # This will be mapped to stock_symbol in db_engine
                        trade_type="buy",
                        quantity=shares_to_buy,
                        entry_price=current_price,
                        entry_timestamp=str(index)[:19]  # Format timestamp
                    )
                    total_trades += 1
            # else: already holding shares, do nothing
        
        # SELL SIGNAL (position == -1)
        elif position == -1:
            if shares_held > 0:  # Currently holding shares
                # Sell all shares
                proceeds = shares_held * current_price
                cash += proceeds
                
                # Calculate PnL and days held
                pnl = (current_price - entry_price) * shares_held
                days_held = (pd.to_datetime(index) - pd.to_datetime(entry_date)).days
                
                # Update trade in database
                if current_trade_id:
                    db_engine.update_trade_exit(
                        trade_id=current_trade_id,
                        exit_price=current_price,
                        exit_timestamp=str(index)[:19],
                        pnl=pnl,
                        days_held=days_held
                    )
                
                # Track winning trades
                if pnl > 0:
                    winning_trades += 1
                
                # Reset position
                shares_held = 0
                current_trade_id = None
                entry_date = None
                entry_price = None
            # else: not holding any shares, do nothing
        
        # Update portfolio value
        portfolio_value = cash + (shares_held * current_price)
        portfolio_values.append(portfolio_value)
    
    # Calculate performance metrics
    final_portfolio_value = portfolio_values[-1] if portfolio_values else initial_capital
    total_return = ((final_portfolio_value - initial_capital) / initial_capital) * 100
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
    
    performance_metrics = {
        'initial_capital': initial_capital,
        'final_portfolio_value': final_portfolio_value,
        'total_return_pct': round(total_return, 2),
        'total_pnl': round(final_portfolio_value - initial_capital, 2),
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'losing_trades': total_trades - winning_trades,
        'win_rate_pct': round(win_rate, 2),
        'strategy_name': strategy_name,
        'stock_symbol': stock_symbol
    }
    
    return portfolio_values, performance_metrics