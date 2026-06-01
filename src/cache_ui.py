"""
Streamlit UI components for cache management
Provides dashboard and controls for cache status and operations
"""

import streamlit as st
from datetime import datetime
import time

from .cache_manager import get_cache_manager
from .scheduler import get_scheduler, init_scheduler


def show_cache_status():
    """Display cache status in sidebar"""
    with st.sidebar:
        st.divider()
        
        cache_manager = get_cache_manager()
        status = cache_manager.get_cache_status()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📦 Cached", status['tickers_cached'])
        with col2:
            st.metric("📊 Records", f"{status['total_records']:,}")
        
        with st.expander("📈 Cache Info"):
            st.write(f"**Database Size:** {status['db_size_mb']} MB")
            st.write(f"**Last Updated:** {status['last_updated']}")
            st.write(f"**Status:** {status['cache_status']}")


def show_cache_management_panel():
    """Display cache management dashboard"""
    st.header("📦 Cache Management Dashboard")
    
    cache_manager = get_cache_manager()
    scheduler = get_scheduler()
    
    # Tab 1: Cache Status
    tab1, tab2, tab3, tab4 = st.tabs(["Status", "Manage", "Scheduler", "Settings"])
    
    with tab1:
        st.subheader("📊 Cache Status")
        status = cache_manager.get_cache_status()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📦 Tickers Cached", status['tickers_cached'])
        with col2:
            st.metric("📊 Total Records", f"{status['total_records']:,}")
        with col3:
            st.metric("💾 Size", f"{status['db_size_mb']} MB")
        with col4:
            st.metric("⏱️ Status", status['cache_status'])
        
        st.write("**Last Updated:**", status['last_updated'] or "Never")
        
        # Show cached tickers
        if status['tickers_cached'] > 0:
            with st.expander(f"📋 Cached Tickers ({status['tickers_cached']})"):
                cached_tickers = cache_manager.get_cached_tickers()
                
                # Display in columns for better readability
                cols = st.columns(5)
                for i, ticker in enumerate(cached_tickers):
                    with cols[i % 5]:
                        st.write(f"✅ {ticker}")
    
    with tab2:
        st.subheader("🛠️ Cache Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Manual Cache Update**")
            
            # Update all stocks
            if st.button("🔄 Update All 700+ Stocks", help="Cache semua saham BEI (takes ~30 min)", key="update_all"):
                st.info("⏳ Starting cache update... This will take about 30 minutes. Please wait.")
                
                from .scheduler import CacheScheduler
                from threading import Thread
                
                # Run in background thread so UI doesn't freeze
                def run_update():
                    scheduler_instance = CacheScheduler()
                    stats = scheduler_instance.cache_all_stocks()
                    st.session_state.last_cache_stats = stats
                
                thread = Thread(target=run_update, daemon=True)
                thread.start()
                st.success("✅ Cache update started in background!")
                st.info("You can close this and come back later. Cache will be ready when complete.")
        
        with col2:
            st.write("**Quick Updates**")
            
            # Update by sector
            from .scheduler import BEI_STOCKS
            sector = st.selectbox("Select Sector", list(BEI_STOCKS.keys()))
            
            if st.button(f"Update {sector} Sector"):
                st.info(f"⏳ Caching {sector} stocks...")
                
                from .scheduler import CacheScheduler
                scheduler_instance = CacheScheduler()
                tickers = BEI_STOCKS[sector]
                stats = scheduler_instance.cache_all_stocks(tickers=tickers)
                
                st.success(f"✅ Cached {stats['successful']}/{stats['total']} {sector} stocks")
                st.write(f"Time: {stats['elapsed_seconds']:.0f} seconds")
        
        st.divider()
        
        # Cache cleanup
        st.write("**Cache Maintenance**")
        col1, col2 = st.columns(2)
        
        with col1:
            days_to_keep = st.slider("Keep data older than (days)", 30, 365, 180)
            if st.button("🧹 Delete Old Data"):
                deleted = cache_manager.clear_old_cache(days=days_to_keep)
                st.success(f"✅ Deleted {deleted} old records")
        
        with col2:
            if st.button("🗑️ Clear All Cache"):
                if st.checkbox("⚠️ Confirm: I want to delete ALL cache"):
                    import os
                    from pathlib import Path
                    db_path = cache_manager.db_path
                    if os.path.exists(db_path):
                        os.remove(db_path)
                        cache_manager.init_database()
                        st.success("✅ Cache cleared successfully")
                        st.rerun()
    
    with tab3:
        st.subheader("🌙 Scheduler Status")
        
        scheduler = get_scheduler()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Scheduler Control**")
            
            if scheduler.is_running:
                st.success("🟢 Scheduler is RUNNING")
                if st.button("⏹️ Stop Scheduler"):
                    scheduler.stop_scheduler()
                    st.rerun()
            else:
                st.warning("🔴 Scheduler is STOPPED")
                if st.button("▶️ Start Scheduler"):
                    init_scheduler(start_now=False)
                    st.rerun()
        
        with col2:
            st.write("**Scheduled Update Time**")
            update_time = st.time_input("Set daily update time", value=None)
            if st.button("📅 Configure Schedule"):
                if update_time:
                    time_str = f"{update_time.hour:02d}:{update_time.minute:02d}"
                    scheduler.schedule_daily_update(time_str=time_str)
                    st.success(f"✅ Daily update scheduled for {time_str}")
        
        st.divider()
        st.write("**Job Statistics**")
        stats = scheduler.get_stats()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Jobs", stats['total_jobs_run'])
        with col2:
            st.metric("✅ Successful", stats['successful_updates'])
        with col3:
            st.metric("❌ Failed", stats['failed_updates'])
        
        st.write(f"Last run: {stats['last_run'] or 'Never'}")
    
    with tab4:
        st.subheader("⚙️ Cache Settings")
        
        st.write("**Cache Configuration**")
        
        use_db_cache = st.checkbox(
            "Use SQLite Database Cache",
            value=True,
            help="Cache stock data to local SQLite database for instant access"
        )
        st.session_state.use_db_cache = use_db_cache
        
        cache_retention = st.slider(
            "Cache Retention (days)",
            min_value=30,
            max_value=365,
            value=180,
            help="How long to keep cached data"
        )
        st.session_state.cache_retention = cache_retention
        
        st.divider()
        
        st.write("**Database Export**")
        if st.button("📥 Export Cache to CSV"):
            cache_manager = get_cache_manager()
            count = cache_manager.export_cache_to_csv()
            st.success(f"✅ Exported {count} stocks to 'cache_export/' folder")
        
        st.divider()
        
        st.write("**Info**")
        st.info("""
        **Smart Caching System:**
        - First load: Fetch from Yahoo Finance (~30 min for 700 stocks)
        - Subsequent loads: Instant from database (<1 second)
        - Background scheduler: Updates nightly at 2 AM
        - Fallback: If cache fails, fetches fresh data
        """)


def show_cache_quick_stats():
    """Show quick cache stats in main app"""
    cache_manager = get_cache_manager()
    status = cache_manager.get_cache_status()
    
    return status


def initialize_cache_system():
    """Initialize cache system on app startup"""
    # Initialize cache manager
    cache_manager = get_cache_manager()
    
    # Initialize scheduler (but don't start immediately unless user requests)
    # In production, you would start this automatically
    scheduler = get_scheduler()
    
    return cache_manager, scheduler
