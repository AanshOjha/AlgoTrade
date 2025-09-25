from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STOCK_SYMBOL: str = "AAPL"
    INTERVAL: str = "1d"
    START_DATE: str = "2024-01-01"
    END_DATE: str = "2024-12-31"
    INITIAL_CAPITAL: float = 100000.0
    SHARES_TO_BUY: int = 50
    STRATEGY_NAME: str = "MA_Crossover"
    
    class Config:
        env_file = ".env"

settings = Settings()