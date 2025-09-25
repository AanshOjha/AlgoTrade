import sqlite3
from typing import Optional, List, Dict, Any
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseEngine:
    """
    SQLite Database Engine for Trading System
    Manages trades table with all required columns and operations
    """
    
    def __init__(self, db_path = "trade_data.db"):
        """Initialize database connection and create tables"""
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            return conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
    
    def init_database(self):
        """Initialize database and create tables"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create trades table with all required columns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    trade_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_name TEXT NOT NULL,
                    stock_symbol TEXT NOT NULL,
                    trade_type TEXT NOT NULL CHECK (trade_type IN ('buy', 'sell')),
                    quantity INTEGER NOT NULL,
                    entry_price REAL,
                    exit_price REAL,
                    entry_timestamp TEXT NOT NULL,
                    exit_timestamp TEXT,
                    pnl REAL DEFAULT 0.0,
                    days_held INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for better query performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trades_symbol_strategy 
                ON trades(stock_symbol, strategy_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_trades_timestamp 
                ON trades(entry_timestamp)
            ''')
            
            # Create backtest_jobs table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS backtest_jobs (
                    backtest_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL CHECK (status IN ('PENDING', 'RUNNING', 'COMPLETED', 'FAILED')),
                    request_params TEXT NOT NULL,
                    results TEXT,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for backtest jobs
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_backtest_status 
                ON backtest_jobs(status)
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
            
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()
    
    def insert_trade(self, 
                    strategy_name: str,
                    stock_symbol: str,
                    trade_type: str,
                    quantity: int,
                    entry_price: float,
                    entry_timestamp: str,
                    exit_price: Optional[float] = None,
                    exit_timestamp: Optional[str] = None,
                    pnl: Optional[float] = None,
                    days_held: Optional[int] = None) -> int:
        """
        Insert a new trade into the database
        Returns the trade_id of the inserted trade
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO trades (
                    strategy_name, stock_symbol, trade_type, quantity,
                    entry_price, exit_price, entry_timestamp, exit_timestamp,
                    pnl, days_held
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (strategy_name, stock_symbol, trade_type, quantity,
                  entry_price, exit_price, entry_timestamp, exit_timestamp,
                  pnl or 0.0, days_held or 0))
            
            trade_id = cursor.lastrowid
            conn.commit()
            logger.info(f"Trade inserted successfully with ID: {trade_id}")
            return trade_id
            
        except sqlite3.Error as e:
            logger.error(f"Error inserting trade: {e}")
            raise
        finally:
            conn.close()
    
    def update_trade_exit(self, 
                         trade_id: int,
                         exit_price: float,
                         exit_timestamp: str,
                         pnl: float,
                         days_held: int) -> bool:
        """
        Update trade with exit information
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE trades 
                SET exit_price = ?, exit_timestamp = ?, pnl = ?, days_held = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE trade_id = ?
            ''', (exit_price, exit_timestamp, pnl, days_held, trade_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Trade {trade_id} updated successfully")
                return True
            else:
                logger.warning(f"No trade found with ID: {trade_id}")
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error updating trade: {e}")
            raise
        finally:
            conn.close()
    
    def get_trades(self, 
                  stock_symbol: Optional[str] = None,
                  strategy_name: Optional[str] = None,
                  limit: Optional[int] = None) -> List[Dict[Any, Any]]:
        """
        Retrieve trades with optional filtering
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM trades WHERE 1=1"
            params = []
            
            if stock_symbol:
                query += " AND stock_symbol = ?"
                params.append(stock_symbol)
            
            if strategy_name:
                query += " AND strategy_name = ?"
                params.append(strategy_name)
            
            query += " ORDER BY entry_timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            trades = [dict(row) for row in rows]
            return trades
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving trades: {e}")
            raise
        finally:
            conn.close()
    
    def create_backtest_job(self, backtest_id: str, request_params: str) -> bool:
        """
        Create a new backtest job with PENDING status
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO backtest_jobs (backtest_id, status, request_params)
                VALUES (?, 'PENDING', ?)
            ''', (backtest_id, request_params))
            
            conn.commit()
            logger.info(f"Backtest job {backtest_id} created successfully")
            return True
            
        except sqlite3.Error as e:
            logger.error(f"Error creating backtest job: {e}")
            raise
        finally:
            conn.close()
    
    def update_backtest_status(self, backtest_id: str, status: str, 
                              results: Optional[str] = None, 
                              error_message: Optional[str] = None) -> bool:
        """
        Update backtest job status and optionally results or error message
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE backtest_jobs 
                SET status = ?, results = ?, error_message = ?, updated_at = CURRENT_TIMESTAMP
                WHERE backtest_id = ?
            ''', (status, results, error_message, backtest_id))
            
            if cursor.rowcount > 0:
                conn.commit()
                logger.info(f"Backtest job {backtest_id} status updated to {status}")
                return True
            else:
                logger.warning(f"No backtest job found with ID: {backtest_id}")
                return False
                
        except sqlite3.Error as e:
            logger.error(f"Error updating backtest job: {e}")
            raise
        finally:
            conn.close()
    
    def get_backtest_job(self, backtest_id: str) -> Optional[Dict[Any, Any]]:
        """
        Get a specific backtest job by ID
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM backtest_jobs WHERE backtest_id = ?
            ''', (backtest_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving backtest job: {e}")
            raise
        finally:
            conn.close()
    
    def get_all_backtest_jobs(self, status: Optional[str] = None) -> List[Dict[Any, Any]]:
        """
        Get all backtest jobs, optionally filtered by status
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if status:
                cursor.execute('''
                    SELECT * FROM backtest_jobs WHERE status = ?
                    ORDER BY created_at DESC
                ''', (status,))
            else:
                cursor.execute('''
                    SELECT * FROM backtest_jobs ORDER BY created_at DESC
                ''')
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            logger.error(f"Error retrieving backtest jobs: {e}")
            raise
        finally:
            conn.close()

# Create a global database instance
db_engine = DatabaseEngine()