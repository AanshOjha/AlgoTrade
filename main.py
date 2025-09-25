from fastapi import FastAPI, BackgroundTasks, Query
from pydantic import BaseModel
import uvicorn
from data_feed.data_feed import fetch_stock_data
from strategy.ma_crossover import ma_crossover_strategy
from visualisation.chart import create_trading_chart
from config import settings
from backtest.backtesting_engine import backtest_strategy
from database.db_engine import db_engine
from typing import List, Dict, Any, Tuple, Optional
import uuid
import json

# Create FastAPI instance
app = FastAPI(
    title="Basic Algo Trading App",
    description="A basic trading application API",
    version="3.0.0"
)

# Pydantic model for stock data request
class StockDataRequest(BaseModel):
    stock_symbol: str = settings.STOCK_SYMBOL
    start_date: str = settings.START_DATE
    end_date: str = settings.END_DATE
    interval: str = settings
    save_to_file: bool = True

class BacktestRequest(BaseModel):
    stock_symbol: str = settings.STOCK_SYMBOL
    start_date: str = settings.START_DATE
    end_date: str = settings.END_DATE   
    initial_capital: float = settings.INITIAL_CAPITAL
    strategy_name: str = settings.STRATEGY_NAME
    strategy_params: Dict[str, Any] = {
        "short_window": 20,
        "long_window": 50
    }


# Basic routes
@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to Trading App API"
    }

@app.post("/fetch-stock-data")
async def get_stock_data(request: StockDataRequest):
    """
    Fetch stock data and return the head of the dataframe
    Optional: save data to CSV file
    """
    try:
        # Fetch the stock data
        result_data = fetch_stock_data(
            symbol=request.stock_symbol,
            start=request.start_date,
            end=request.end_date,
            data_interval=request.interval,
            save_to_file=request.save_to_file
        )
        
        # Handle return based on save_to_file option
        if request.save_to_file:
            df, filepath = result_data
            df_head = df.head()
            
            response = {
                "status": "success",
                "stock_symbol": request.stock_symbol,
                "data_shape": df.shape,
                "saved_to_file": True,
                "file_path": filepath,
                "head_data": df_head.to_dict(orient="index")
            }
        else:
            df = result_data
            df_head = df.head()
            
            response = {
                "status": "success",
                "stock_symbol": request.stock_symbol,
                "data_shape": df.shape,
                "saved_to_file": False,
                "head_data": df_head.to_dict(orient="index")
            }
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
    
@app.get("/ma-crossover")
async def ma_crossover():
    try:
        data = ma_crossover_strategy()
        return {
            "status": "success",
            "data_shape": data.shape,
            "head_data": data.head().to_dict(orient="index")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/show-chart")
async def show_chart():
    """
    Display trading chart with EMAs and buy/sell signals
    """
    try:
        result = create_trading_chart()
        return {
            "status": "success",
            "message": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/trades")
async def get_all_trades(
    strategy_name: Optional[str] = Query(None, description="Filter trades by strategy name"),
    ticker: Optional[str] = Query(None, description="Filter trades by stock ticker/symbol"),
    limit: Optional[int] = Query(None, description="Limit the number of trades returned")
):
    """
    Get all trades from the database.
    
    This endpoint retrieves the history of all completed trades from the database.
    Can be filtered by strategy_name or ticker using query parameters.
    
    Example Usage: /trades?strategy_name=ma_crossover&ticker=AAPL
    """
    try:
        # Get trades from database using the existing method
        trades = db_engine.get_trades(
            stock_symbol=ticker,
            strategy_name=strategy_name,
            limit=limit
        )
        
        # Transform the data to match the expected response format
        formatted_trades = []
        for trade in trades:
            formatted_trade = {
                "trade_id": trade["trade_id"],
                "strategy_name": trade["strategy_name"],
                "ticker": trade["stock_symbol"],
                "quantity": trade["quantity"],
                "entry_datetime": trade["entry_timestamp"],
                "entry_price": trade["entry_price"],
                "exit_datetime": trade["exit_timestamp"],
                "exit_price": trade["exit_price"],
                "pnl": trade["pnl"],
                "trade_duration_days": trade["days_held"]
            }
            formatted_trades.append(formatted_trade)
        
        return formatted_trades
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve trades: {str(e)}"
        }
    
def run_backtest_task(backtest_id: str, request_data: dict):
    """
    Background task function to run backtest
    """
    try:
        # Update status to RUNNING
        db_engine.update_backtest_status(backtest_id, "RUNNING")
        
        # Generate strategy data first
        strategy_data = ma_crossover_strategy(
            short_window=request_data["strategy_params"].get("short_window", 20),
            long_window=request_data["strategy_params"].get("long_window", 50),
            stock_symbol=request_data["stock_symbol"],
            start_date=request_data["start_date"],
            end_date=request_data["end_date"]
        )
        
        # Run the backtest
        result = backtest_strategy(
            data=strategy_data,
            stock_symbol=request_data["stock_symbol"],
            initial_capital=request_data["initial_capital"],
            strategy_name=request_data["strategy_name"],
            shares_to_buy=settings.SHARES_TO_BUY
        )
        
        # Store comprehensive results as JSON string
        results_json = json.dumps({
            "performance_metrics": result[1] if len(result) > 1 else None,
            "portfolio_values": result[0] if len(result) > 0 else None,
            "strategy_data_shape": strategy_data.shape if strategy_data is not None else None,
            "timeframe": {
                "start": str(strategy_data.index[0])[:10] if strategy_data is not None and len(strategy_data) > 0 else None,
                "end": str(strategy_data.index[-1])[:10] if strategy_data is not None and len(strategy_data) > 0 else None
            }
        })
        
        # Update status to COMPLETED with results
        db_engine.update_backtest_status(backtest_id, "COMPLETED", results_json)
        
    except Exception as e:
        # Update status to FAILED with error message
        print(f"Error in backtest task: {str(e)}")
        db_engine.update_backtest_status(backtest_id, "FAILED", error_message=str(e))

@app.post("/backtest")
async def backtest(background_tasks: BackgroundTasks, request: BacktestRequest):
    """
    Start a new backtest job in the background
    """
    # Generate new backtest ID
    backtest_id = str(uuid.uuid4())
    
    # Convert request to dictionary for JSON storage
    request_data = {
        "stock_symbol": request.stock_symbol,
        "start_date": request.start_date,
        "end_date": request.end_date,
        "initial_capital": request.initial_capital,
        "strategy_name": request.strategy_name,
        "strategy_params": request.strategy_params
    }
    
    # Store request parameters as JSON string
    request_params_json = json.dumps(request_data)
    
    # Create backtest job in database with PENDING status
    db_engine.create_backtest_job(backtest_id, request_params_json)
    
    # Add background task
    background_tasks.add_task(run_backtest_task, backtest_id, request_data)
    
    return {
        "status": "success",
        "message": "Backtest started successfully.",
        "backtest_id": backtest_id
    }

@app.get("/backtest/{backtest_id}/status")
async def get_backtest_status(backtest_id: str):
    """
    Get the current status of a backtest job (without full results)
    
    Use this endpoint to check if a backtest is still running.
    For completed backtests, use GET /backtest/{backtest_id} to get full results.
    """
    try:
        job = db_engine.get_backtest_job(backtest_id)
        if not job:
            return {
                "status": "error",
                "message": f"No backtest found with ID {backtest_id}"
            }
        
        response = {
            "backtest_id": job["backtest_id"],
            "job_status": job["status"],
            "error_message": job["error_message"],
            "created_at": job["created_at"], 
            "updated_at": job["updated_at"]
        }
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/backtest/{backtest_id}")
async def get_backtest_results(backtest_id: str):
    """
    Get the full results of a completed backtest
    
    Retrieves comprehensive backtest data including:
    - Performance metrics (final portfolio value, P&L, win rate, etc.)
    - Equity curve data for plotting portfolio growth over time
    - Complete chart data with OHLCV, indicators, and trading signals
    """
    try:
        job = db_engine.get_backtest_job(backtest_id)
        if not job:
            return {
                "status": "error",
                "message": f"No backtest found with ID {backtest_id}"
            }
        
        # If backtest is not completed, return status info
        if job["status"] != "COMPLETED":
            return {
                "backtest_id": job["backtest_id"],
                "job_status": job["status"],
                "error_message": job["error_message"],
                "created_at": job["created_at"],
                "updated_at": job["updated_at"]
            }
        
        # Parse the stored results
        stored_results = json.loads(job["results"]) if job["results"] else {}
        request_params = json.loads(job["request_params"]) if job["request_params"] else {}
        
        # Get performance metrics from stored results
        performance_metrics = stored_results.get("performance_metrics", {})
        portfolio_values = stored_results.get("portfolio_values", [])
        
        # Regenerate strategy data to get chart data with indicators
        strategy_data = ma_crossover_strategy(
            short_window=request_params.get("strategy_params", {}).get("short_window", 20),
            long_window=request_params.get("strategy_params", {}).get("long_window", 50),
            stock_symbol=request_params.get("stock_symbol", "AAPL"),
            start_date=request_params.get("start_date", "2020-01-01"),
            end_date=request_params.get("end_date", "2024-12-31")
        )
        
        # Create equity curve data
        equity_curve = []
        if portfolio_values and len(portfolio_values) > 0:
            # Get date range from strategy data
            dates = strategy_data.index.tolist()
            for i, value in enumerate(portfolio_values):
                if i < len(dates):
                    equity_curve.append({
                        "date": dates[i].strftime("%Y-%m-%d"),
                        "value": round(value, 2)
                    })
        
        # Create chart data with OHLCV, indicators, and signals
        chart_data = []
        short_window = request_params.get("strategy_params", {}).get("short_window", 20)
        long_window = request_params.get("strategy_params", {}).get("long_window", 50)
        
        for index, row in strategy_data.iterrows():
            chart_point = {
                "Date": index.strftime("%Y-%m-%dT%H:%M:%S%z") if hasattr(index, 'strftime') else str(index),
                "Open": round(float(row['Open']), 2),
                "High": round(float(row['High']), 2),
                "Low": round(float(row['Low']), 2), 
                "Close": round(float(row['Close']), 2),
                "Volume": int(row['Volume']),
                f"EMA{short_window}": round(float(row[f'EMA{short_window}']), 2) if f'EMA{short_window}' in row else None,
                f"EMA{long_window}": round(float(row[f'EMA{long_window}']), 2) if f'EMA{long_window}' in row else None,
                "Position": float(row.get('Position', 0))  # Signal for frontend markers
            }
            chart_data.append(chart_point)
        
        # Build the comprehensive response
        response = {
            "backtest_id": backtest_id,
            "performance_report": {
                "final_portfolio_value": performance_metrics.get("final_portfolio_value", 0),
                "total_profit_loss_pct": performance_metrics.get("total_return_pct", 0),
                "total_trades": performance_metrics.get("total_trades", 0),
                "win_rate_pct": performance_metrics.get("win_rate_pct", 0),
                "initial_capital": performance_metrics.get("initial_capital", 0),
                "total_pnl": performance_metrics.get("total_pnl", 0),
                "strategy_name": performance_metrics.get("strategy_name", ""),
                "stock_symbol": performance_metrics.get("stock_symbol", "")
            },
            "equity_curve": equity_curve,
            "chart_data": chart_data
        }
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to retrieve backtest results: {str(e)}"
        }

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)