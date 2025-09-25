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
        
        # Run the backtest
        result = backtest_strategy(
            data=ma_crossover_strategy(
                short_window=request_data["strategy_params"].get("short_window", 20),
                long_window=request_data["strategy_params"].get("long_window", 50),
                stock_symbol=request_data["stock_symbol"],
                start_date=request_data["start_date"],
                end_date=request_data["end_date"]
            ),
            stock_symbol=request_data["stock_symbol"],
            initial_capital=request_data["initial_capital"],
            strategy_name=request_data["strategy_name"],
            shares_to_buy=settings.SHARES_TO_BUY
        )
        
        # Store results as JSON string
        results_json = json.dumps({
            "performance_metrics": result[1] if len(result) > 1 else None,
            "portfolio_values": result[0] if len(result) > 0 else None
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

@app.get("/backtest/{backtest_id}")
async def get_backtest_status(backtest_id: str):
    """
    Get the status and results of a backtest job
    """
    try:
        job = db_engine.get_backtest_job(backtest_id)
        if not job:
            return {
                "status": "error",
                "message": f"No backtest found with ID {backtest_id}"
            }
        
        response = {
            "backtest_id": job["backtest_id"],  # Changed from job[0]
            "job_status": job["status"],        # Changed from job[1]
            "request_params": json.loads(job["request_params"]) if job["request_params"] else None,  # Changed
            "results": json.loads(job["results"]) if job["results"] else None,  # Changed
            "error_message": job["error_message"],  # Changed
            "created_at": job["created_at"],        # Changed
            "updated_at": job["updated_at"]         # Changed
        }
        
        return response
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)