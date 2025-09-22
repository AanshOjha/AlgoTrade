from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from data_feed.data_feed import fetch_stock_data
from strategy.ma_crossover import ma_crossover_strategy
from visualisation.chart import create_trading_chart

# Create FastAPI instance
app = FastAPI(
    title="Trading App API",
    description="A basic trading application API",
    version="1.0.0"
)

# Pydantic model for stock data request
class StockDataRequest(BaseModel):
    stock_symbol: str
    start_date: str
    end_date: str
    interval: str = "1d"
    save_to_file: bool = False

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

# Run the application
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)