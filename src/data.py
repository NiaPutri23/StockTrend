"""
Module untuk pengambilan dan validasi data saham dari Yahoo Finance.

Fungsi-fungsi di module ini menangani:
- Pengambilan data OHLCV dari yfinance
- Validasi ticker saham
- Error handling untuk data kosong atau invalid
- Multi-level caching (SQLite database + Streamlit cache)
"""

import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime, timedelta
import logging

from .cache_manager import get_cache_manager

logger = logging.getLogger(__name__)


@st.cache_data(ttl=3600)  # Cache selama 1 jam (Streamlit cache)
def get_stock_data(ticker: str, period: str = "3mo", use_cache: bool = True) -> pd.DataFrame:
    """
    Mengambil data harga saham dari Yahoo Finance dengan multi-level caching.
    
    Strategy:
    1. Check database cache (SQLite) - instant if available!
    2. Check Streamlit cache - very fast
    3. Fetch from Yahoo Finance - fallback if no cache
    4. Auto-cache untuk penggunaan berikutnya
    
    Fungsi ini mengambil data OHLCV (Open, High, Low, Close, Volume) 
    dari Yahoo Finance dan mereturn sebagai DataFrame dengan index datetime.
    
    Parameters
    ----------
    ticker : str
        Ticker saham dalam format BEI, contoh: "BBCA.JK", "BBRI.JK"
    period : str, optional
        Periode data yang diambil, default "3mo" (3 bulan)
        Options: "1d", "5d", "1mo", "3mo", "6mo", "1y", etc.
    use_cache : bool, optional
        Apakah menggunakan cache. Default True untuk performa terbaik.
        
    Returns
    -------
    pd.DataFrame
        DataFrame dengan columns [Open, High, Low, Close, Adj Close, Volume]
        Index adalah datetime dari tanggal trading
        
    Raises
    ------
    ValueError
        Jika ticker tidak valid atau data tidak tersedia
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")  # From cache if available!
    >>> print(df.head())
                    Open        High         Low       Close  ...
    Date                                                          
    2024-03-01  9250.0  9350.0  9240.0  9300.0  ...
    2024-03-02  9310.0  9400.0  9300.0  9380.0  ...
    """
    try:
        ticker_clean = ticker.replace(".JK", "").strip()
        
        # 1️⃣ Try database cache FIRST (100x faster if available!)
        if use_cache:
            cache_manager = get_cache_manager()
            cached_data = cache_manager.get_cached_stock(ticker_clean, days=90)
            
            if cached_data is not None and not cached_data.empty:
                logger.info(f"✅ {ticker_clean}: Loaded from database cache")
                return cached_data
        
        # 2️⃣ Fetch fresh data dari Yahoo Finance
        logger.info(f"🔄 {ticker_clean}: Fetching fresh data from Yahoo Finance...")
        data = yf.download(
            ticker,
            period=period,
            progress=False,  # Suppress download progress bar
            timeout=10
        )
        
        # Validate data
        if data.empty:
            raise ValueError(f"Data tidak tersedia untuk ticker '{ticker}'")
        
        if len(data) < 5:
            raise ValueError(
                f"Data tidak cukup untuk '{ticker}' (minimum 5 hari)"
            )
        
        # Ensure datetime index
        if not isinstance(data.index, pd.DatetimeIndex):
            data.index = pd.to_datetime(data.index)
        
        # Sort by date (ascending)
        data = data.sort_index()
        
        # 3️⃣ Auto-cache untuk penggunaan berikutnya
        if use_cache:
            try:
                cache_manager = get_cache_manager()
                cache_manager.cache_stock_data(ticker_clean, data)
            except Exception as e:
                logger.warning(f"⚠️ Gagal cache {ticker_clean}: {e}")
                # Continue anyway, fallback is ok
        
        logger.info(f"✅ {ticker_clean}: Fresh data loaded and cached")
        return data
        
    except Exception as e:
        # Re-raise dengan pesan yang lebih informatif
        if "No data found" in str(e):
            raise ValueError(f"Ticker '{ticker}' tidak ditemukan atau invalid")
        elif "timeout" in str(e).lower():
            raise ValueError("Gagal connect ke Yahoo Finance (timeout)")
        else:
            raise ValueError(f"Error mengambil data untuk '{ticker}': {str(e)}")


def validate_ticker(ticker: str) -> bool:
    """
    Validasi format ticker saham Indonesia.
    
    Parameters
    ----------
    ticker : str
        Ticker yang akan divalidasi
        
    Returns
    -------
    bool
        True jika format ticker valid, False sebaliknya
        
    Examples
    --------
    >>> validate_ticker("BBCA.JK")
    True
    >>> validate_ticker("INVALID")
    False
    """
    ticker = ticker.strip().upper()
    
    # Check format: XXXX.JK atau XXXXX.JK
    if not ticker.endswith(".JK"):
        return False
    
    code = ticker[:-3]  # Remove ".JK"
    
    # Check code length (2-5 characters for Indonesian stocks)
    if len(code) < 1 or len(code) > 5:
        return False
    
    # Check if code contains only alphanumeric
    if not code.isalnum():
        return False
    
    return True


def parse_ticker_input(ticker_string: str) -> list:
    """
    Parse input string ticker menjadi list of tickers.
    
    Memisahkan ticker dengan koma dan strip whitespace.
    
    Parameters
    ----------
    ticker_string : str
        Ticker input dari user, contoh: "BBCA.JK, BBRI.JK, BMRI.JK"
        
    Returns
    -------
    list
        List of uppercase tickers
        
    Examples
    --------
    >>> parse_ticker_input("BBCA.JK, BBRI.JK")
    ['BBCA.JK', 'BBRI.JK']
    """
    if not ticker_string or ticker_string.strip() == "":
        return []
    
    # Split by comma dan strip
    tickers = [t.strip().upper() for t in ticker_string.split(",")]
    
    # Remove empty strings
    tickers = [t for t in tickers if t]
    
    return tickers


def get_stock_info(ticker: str) -> dict:
    """
    Ambil informasi dasar saham dari Yahoo Finance.
    
    Parameters
    ----------
    ticker : str
        Ticker saham
        
    Returns
    -------
    dict
        Dictionary dengan info saham (name, sector, market cap, dll)
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        return {
            'name': info.get('longName', ticker),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
        }
    except Exception as e:
        return {
            'name': ticker,
            'sector': 'N/A',
            'industry': 'N/A',
            'market_cap': 'N/A',
            'pe_ratio': 'N/A',
            'dividend_yield': 'N/A',
        }


def format_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format data untuk penggunaan di aplikasi.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw data dari yfinance
        
    Returns
    -------
    pd.DataFrame
        Formatted data
    """
    # Create copy to avoid modification
    df = df.copy()
    
    # Rename columns untuk consistency
    df.columns = [col.lower() for col in df.columns]
    
    # Round numeric values
    numeric_cols = df.select_dtypes(include=['float64']).columns
    df[numeric_cols] = df[numeric_cols].round(2)
    
    return df


# Testing function
if __name__ == "__main__":
    # Test get_stock_data
    print("Testing get_stock_data...")
    try:
        df = get_stock_data("BBCA.JK", period="1mo")
        print(f"✓ Successfully fetched data for BBCA.JK")
        print(f"  Shape: {df.shape}")
        print(df.head())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test validate_ticker
    print("\nTesting validate_ticker...")
    test_tickers = ["BBCA.JK", "INVALID", "BBRI.JK", "XYZ"]
    for ticker in test_tickers:
        result = validate_ticker(ticker)
        print(f"  {ticker}: {result}")
    
    # Test parse_ticker_input
    print("\nTesting parse_ticker_input...")
    input_str = "BBCA.JK, BBRI.JK, BMRI.JK"
    tickers = parse_ticker_input(input_str)
    print(f"  Input: {input_str}")
    print(f"  Output: {tickers}")
