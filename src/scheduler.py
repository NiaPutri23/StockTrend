"""
Cache Scheduler for StockTrend Dashboard
Schedules daily cache updates of all 700 BEI stocks
Runs in background to keep cache fresh
"""

import schedule
import time
import yfinance as yf
from datetime import datetime
import logging
from typing import List, Dict, Callable
import threading

from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)

# Indonesian Stock Exchange stocks (BEI)
# This is a curated list of most active stocks
BEI_STOCKS = {
    'Finance': ['BBCA', 'BBRI', 'BMRI', 'BNIS', 'INDF', 'PBANK', 'BDMN', 'BSIM'],
    'Technology': ['TLKM', 'GOTO', 'MSIN', 'DLIN', 'MRTI'],
    'Energy': ['UNTR', 'ADRO', 'SSMS', 'PGAS', 'EXCL'],
    'Retail': ['AMRT', 'MIDI', 'MTRA', 'AKRA', 'SUWW'],
    'Healthcare': ['KAEF', 'UNVR', 'JSMR', 'SIDO', 'DVLA'],
    'Manufacturing': ['INAI', 'PRAS', 'ISSP', 'IRON', 'TINS'],
    'Property': ['JRPT', 'PJPP', 'ELTY', 'MDKA', 'ADHI'],
    'Transportation': ['PTBA', 'RIGS', 'ITMG', 'MBSS', 'NELY'],
    'Chemicals': ['ASII', 'WIKA', 'SMGR', 'IPOL', 'TKDN'],
    'Mining': ['ANTM', 'CPIN', 'HRUM', 'SOHO', 'INCO'],
}

# Flatten all stocks
ALL_BEI_TICKERS = [ticker for tickers in BEI_STOCKS.values() for ticker in tickers]


class CacheScheduler:
    """Manages scheduled cache updates"""
    
    def __init__(self):
        self.cache_manager = get_cache_manager()
        self.is_running = False
        self.scheduler_thread = None
        self.job_stats = {
            'total_jobs': 0,
            'successful': 0,
            'failed': 0,
            'last_run': None,
            'next_run': None
        }
    
    def fetch_and_cache_stock(self, ticker: str, period: str = '1y') -> bool:
        """
        Fetch single stock and cache it
        
        Args:
            ticker: Stock ticker (without .JK suffix)
            period: Period to fetch (default 1 year)
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"⏳ Fetching {ticker}...")
            
            # Fetch from Yahoo Finance
            data = yf.download(
                f"{ticker}.JK",
                period=period,
                progress=False,
                interval='1d'
            )
            
            if data.empty:
                logger.warning(f"⚠️ No data for {ticker}")
                return False
            
            # Cache the data
            success = self.cache_manager.cache_stock_data(ticker, data)
            
            if success:
                self.job_stats['successful'] += 1
                logger.info(f"✅ {ticker} cached successfully")
            else:
                self.job_stats['failed'] += 1
                logger.error(f"❌ Failed to cache {ticker}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Error fetching {ticker}: {e}")
            self.job_stats['failed'] += 1
            return False
    
    def cache_all_stocks(self, tickers: List[str] = None, period: str = '1y') -> Dict:
        """
        Cache all BEI stocks
        
        Args:
            tickers: List of tickers to cache (default: all BEI)
            period: Period to fetch
            
        Returns:
            Statistics dictionary
        """
        if tickers is None:
            tickers = ALL_BEI_TICKERS
        
        logger.info(f"🚀 Starting cache update for {len(tickers)} stocks...")
        start_time = datetime.now()
        
        successful = 0
        failed = 0
        
        for i, ticker in enumerate(tickers):
            progress = f"[{i+1}/{len(tickers)}]"
            
            if self.fetch_and_cache_stock(ticker, period):
                successful += 1
            else:
                failed += 1
            
            # Log progress every 10 stocks
            if (i + 1) % 10 == 0:
                elapsed = (datetime.now() - start_time).total_seconds()
                rate = (i + 1) / elapsed
                remaining = len(tickers) - (i + 1)
                eta = remaining / rate if rate > 0 else 0
                
                logger.info(f"{progress} ✅ {successful} ❌ {failed} (ETA: {eta:.0f}s)")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        stats = {
            'total': len(tickers),
            'successful': successful,
            'failed': failed,
            'elapsed_seconds': elapsed,
            'rate_per_minute': (len(tickers) / elapsed) * 60 if elapsed > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"""
        ✅ CACHE UPDATE COMPLETE:
        ├─ Total: {stats['total']}
        ├─ ✅ Successful: {stats['successful']}
        ├─ ❌ Failed: {stats['failed']}
        ├─ ⏱️ Time: {stats['elapsed_seconds']:.0f}s
        └─ 📊 Rate: {stats['rate_per_minute']:.1f} stocks/min
        """)
        
        self.job_stats['total_jobs'] += 1
        self.job_stats['last_run'] = datetime.now().isoformat()
        
        return stats
    
    def schedule_daily_update(self, time_str: str = "02:00", period: str = '1y'):
        """
        Schedule daily cache update
        
        Args:
            time_str: Time to run update (24h format, e.g., "02:00")
            period: Period to fetch
        """
        def job():
            logger.info(f"🌙 Running scheduled cache update at {datetime.now()}")
            self.cache_all_stocks(period=period)
        
        schedule.every().day.at(time_str).do(job)
        logger.info(f"📅 Scheduled daily cache update at {time_str}")
    
    def schedule_sector_update(self, sector: str, time_str: str = "02:00"):
        """
        Schedule sector-specific cache update
        
        Args:
            sector: Sector name
            time_str: Time to run
        """
        def job():
            tickers = BEI_STOCKS.get(sector, [])
            logger.info(f"🌙 Running scheduled {sector} update at {datetime.now()}")
            self.cache_all_stocks(tickers=tickers)
        
        schedule.every().day.at(time_str).do(job)
        logger.info(f"📅 Scheduled {sector} cache update at {time_str}")
    
    def start_scheduler(self):
        """Start scheduler in background thread"""
        if self.is_running:
            logger.warning("⚠️ Scheduler already running")
            return
        
        self.is_running = True
        
        def run_scheduler():
            logger.info("🎯 Cache scheduler started")
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            logger.info("🛑 Cache scheduler stopped")
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("✅ Scheduler thread started (daemon mode)")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("🛑 Scheduler stopped")
    
    def get_stats(self) -> Dict:
        """Get scheduler statistics"""
        cache_status = self.cache_manager.get_cache_status()
        return {
            'scheduler_running': self.is_running,
            'total_jobs_run': self.job_stats['total_jobs'],
            'successful_updates': self.job_stats['successful'],
            'failed_updates': self.job_stats['failed'],
            'last_run': self.job_stats['last_run'],
            'cache_status': cache_status
        }
    
    def get_stats_text(self) -> str:
        """Get human-readable statistics"""
        stats = self.get_stats()
        cache = stats['cache_status']
        
        text = f"""
        📊 SCHEDULER STATS:
        ├─ Status: {'🟢 RUNNING' if stats['scheduler_running'] else '🔴 STOPPED'}
        ├─ Total jobs: {stats['total_jobs_run']}
        ├─ ✅ Successful: {stats['successful_updates']}
        ├─ ❌ Failed: {stats['failed_updates']}
        ├─ Last run: {stats['last_run']}
        │
        └─ 📦 CACHE INFO:
           ├─ Tickers: {cache['tickers_cached']}
           ├─ Records: {cache['total_records']}
           ├─ Size: {cache['db_size_mb']} MB
           └─ Status: {cache['cache_status']}
        """
        return text


# Global scheduler instance
_scheduler = None


def get_scheduler() -> CacheScheduler:
    """Get or create scheduler instance"""
    global _scheduler
    if _scheduler is None:
        _scheduler = CacheScheduler()
    return _scheduler


def init_scheduler(start_now: bool = False):
    """
    Initialize scheduler with daily updates
    
    Args:
        start_now: Whether to run first update immediately
    """
    scheduler = get_scheduler()
    
    # Schedule daily update at 2 AM
    scheduler.schedule_daily_update(time_str="02:00", period="1y")
    
    # Start scheduler background thread
    scheduler.start_scheduler()
    
    # Optional: run first update immediately
    if start_now:
        logger.info("🚀 Running initial cache update...")
        scheduler.cache_all_stocks(period="3mo")  # Smaller period for first run
    
    return scheduler
