"""
Cache Manager for StockTrend Dashboard
Manages SQLite database for storing historical stock data
Enables instant loading of 700+ stocks from cache
"""

import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Database path
DB_PATH = Path(__file__).parent.parent / "data" / "stocks_cache.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class StockCacheManager:
    """Manages SQLite cache for stock data"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Main stock data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open REAL,
                    high REAL,
                    low REAL,
                    close REAL,
                    volume INTEGER,
                    UNIQUE(ticker, date)
                )
            ''')
            
            # Metadata table (track cache updates)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache_metadata (
                    ticker TEXT PRIMARY KEY,
                    last_updated TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Create indexes for faster queries
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker ON stock_data(ticker)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON stock_data(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticker_date ON stock_data(ticker, date)')
            
            conn.commit()
            logger.info(f"✅ Database initialized at {self.db_path}")
    
    def cache_stock_data(self, ticker: str, df: pd.DataFrame) -> bool:
        """
        Store stock data in cache
        
        Args:
            ticker: Stock ticker (e.g., 'BBCA')
            df: DataFrame with OHLCV data
            
        Returns:
            True if successful
        """
        try:
            # Reset index to make Date a column
            if df.index.name == 'Date':
                df = df.reset_index()
                df['Date'] = df['Date'].astype(str)
            else:
                df['Date'] = df.index.astype(str)
            
            # Prepare data
            df_prepared = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].copy()
            df_prepared.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
            df_prepared['ticker'] = ticker
            
            with sqlite3.connect(self.db_path) as conn:
                # Delete old data for this ticker
                cursor = conn.cursor()
                cursor.execute('DELETE FROM stock_data WHERE ticker = ?', (ticker,))
                
                # Insert new data
                df_prepared.to_sql('stock_data', conn, if_exists='append', index=False)
                
                # Update metadata
                cursor.execute('''
                    INSERT OR REPLACE INTO cache_metadata (ticker, last_updated, status)
                    VALUES (?, ?, ?)
                ''', (ticker, datetime.now().isoformat(), 'cached'))
                
                conn.commit()
                logger.info(f"✅ Cached {ticker}: {len(df)} records")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error caching {ticker}: {e}")
            return False
    
    def get_cached_stock(self, ticker: str, days: int = 90) -> Optional[pd.DataFrame]:
        """
        Retrieve stock data from cache
        
        Args:
            ticker: Stock ticker
            days: Number of days to retrieve (default 90)
            
        Returns:
            DataFrame if found, None otherwise
        """
        try:
            # Calculate date threshold
            threshold_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            
            query = '''
                SELECT date, open, high, low, close, volume
                FROM stock_data
                WHERE ticker = ? AND date >= ?
                ORDER BY date ASC
            '''
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql(query, conn, params=(ticker, threshold_date))
            
            if df.empty:
                logger.warning(f"⚠️ No cached data for {ticker}")
                return None
            
            # Convert to proper types
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            for col in ['open', 'high', 'low', 'close']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce', downcast='integer')
            
            logger.info(f"✅ Retrieved {ticker} from cache: {len(df)} records")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error retrieving {ticker} from cache: {e}")
            return None
    
    def is_ticker_cached(self, ticker: str) -> bool:
        """Check if ticker exists in cache"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1 FROM cache_metadata WHERE ticker = ?', (ticker,))
            return cursor.fetchone() is not None
    
    def get_cached_tickers(self) -> List[str]:
        """Get list of all cached tickers"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT ticker FROM cache_metadata ORDER BY ticker')
            return [row[0] for row in cursor.fetchall()]
    
    def get_cache_status(self) -> Dict:
        """Get cache statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total cached tickers
            cursor.execute('SELECT COUNT(DISTINCT ticker) FROM cache_metadata')
            ticker_count = cursor.fetchone()[0]
            
            # Total records
            cursor.execute('SELECT COUNT(*) FROM stock_data')
            record_count = cursor.fetchone()[0]
            
            # Last update
            cursor.execute('SELECT MAX(last_updated) FROM cache_metadata')
            last_update = cursor.fetchone()[0]
            
            # Get file size
            db_size_mb = Path(self.db_path).stat().st_size / (1024 * 1024)
            
            return {
                'tickers_cached': ticker_count,
                'total_records': record_count,
                'last_updated': last_update,
                'db_size_mb': round(db_size_mb, 2),
                'cache_status': '✅ READY' if ticker_count > 0 else '⚠️ EMPTY'
            }
    
    def clear_old_cache(self, days: int = 180):
        """Remove data older than specified days"""
        threshold_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM stock_data WHERE date < ?', (threshold_date,))
            deleted = cursor.rowcount
            conn.commit()
        
        logger.info(f"🧹 Deleted {deleted} old records (> {days} days)")
        return deleted
    
    def export_cache_to_csv(self, output_dir: str = "cache_export"):
        """Export cached data to CSV files (for backup)"""
        Path(output_dir).mkdir(exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT DISTINCT ticker FROM stock_data'
            cursor = conn.cursor()
            tickers = [row[0] for row in cursor.execute(query)]
        
        for ticker in tickers:
            df = self.get_cached_stock(ticker)
            if df is not None:
                df.to_csv(f"{output_dir}/{ticker}.csv")
        
        logger.info(f"✅ Exported {len(tickers)} stocks to {output_dir}/")
        return len(tickers)
    
    def get_db_info(self) -> str:
        """Get human-readable database info"""
        status = self.get_cache_status()
        info = f"""
        📊 CACHE STATUS:
        ├─ Tickers cached: {status['tickers_cached']}
        ├─ Total records: {status['total_records']}
        ├─ Database size: {status['db_size_mb']} MB
        ├─ Last updated: {status['last_updated']}
        └─ Status: {status['cache_status']}
        """
        return info


# Global cache manager instance
cache_manager = StockCacheManager()


def get_cache_manager() -> StockCacheManager:
    """Get or create cache manager instance"""
    return cache_manager
