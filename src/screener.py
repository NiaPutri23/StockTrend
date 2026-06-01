"""
Module untuk logic screening saham yang mengalami downtrend.

Module ini menangani:
- Kalkulasi daily returns
- Deteksi downtrend N hari
- Kalkulasi drawdown percentage
- Main screening logic
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict


def calculate_returns(df: pd.DataFrame, column: str = "close") -> pd.Series:
    """
    Menghitung daily percentage returns dari data harga.
    
    Returns dihitung sebagai: (price_today - price_yesterday) / price_yesterday
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame dengan data OHLCV
    column : str, optional
        Kolom yang digunakan untuk kalkulasi, default "close"
        
    Returns
    -------
    pd.Series
        Daily returns dalam format decimal (0.05 = 5% gain)
        Index sama dengan input dataframe
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")
    >>> returns = calculate_returns(df)
    >>> print(returns.tail())
    2024-03-28    0.0234
    2024-03-29   -0.0156
    ...
    """
    # Get price column (handle different cases)
    price_col = None
    for col in df.columns:
        if col.lower() == column.lower():
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Column '{column}' not found in dataframe")
    
    # Calculate percentage change
    returns = df[price_col].pct_change()
    
    return returns


def is_down_n_days(returns: pd.Series, n: int) -> bool:
    """
    Cek apakah saham turun N hari berturut-turut.
    
    Mengecek apakah N return terakhir semua negatif.
    
    Parameters
    ----------
    returns : pd.Series
        Daily returns series
    n : int
        Jumlah hari yang dicek
        
    Returns
    -------
    bool
        True jika semua N return terakhir negatif, False sebaliknya
        
    Examples
    --------
    >>> returns = pd.Series([-0.02, -0.01, -0.03, -0.015, -0.005])
    >>> is_down_n_days(returns, 5)
    True
    
    >>> returns = pd.Series([-0.02, -0.01, 0.01, -0.015, -0.005])
    >>> is_down_n_days(returns, 5)
    False
    """
    if len(returns) < n:
        return False
    
    # Get last N returns (exclude NaN at the beginning)
    last_n_returns = returns.dropna().tail(n)
    
    # Check if all are negative
    is_downtrend = (last_n_returns < 0).all()
    
    return bool(is_downtrend)


def calculate_drawdown(df: pd.DataFrame, n: int, column: str = "close") -> float:
    """
    Menghitung drawdown percentage dalam N hari terakhir.
    
    Drawdown adalah percentage decline dari highest point ke current price.
    Formula: ((lowest_price - current_price) / current_price) * 100
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame dengan data OHLCV
    n : int
        Jumlah hari yang dihitung
    column : str, optional
        Kolom yang digunakan, default "close"
        
    Returns
    -------
    float
        Drawdown dalam persen (e.g., -5.23 untuk -5.23%)
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")
    >>> dd = calculate_drawdown(df, 5)
    >>> print(f"Drawdown: {dd:.2f}%")
    Drawdown: -3.45%
    """
    # Get price column
    price_col = None
    for col in df.columns:
        if col.lower() == column.lower():
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Column '{column}' not found in dataframe")
    
    # Get last N prices
    last_n_prices = df[price_col].tail(n)
    
    if len(last_n_prices) < n:
        raise ValueError(f"Data tidak cukup untuk menghitung drawdown ({len(last_n_prices)} < {n})")
    
    # Find lowest price in the period
    lowest_price = last_n_prices.min()
    current_price = last_n_prices.iloc[-1]
    
    # Calculate drawdown
    drawdown = ((lowest_price - current_price) / current_price) * 100
    
    return float(drawdown)


def calculate_statistics(df: pd.DataFrame, column: str = "close") -> dict:
    """
    Hitung statistik dasar dari data harga.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame dengan data OHLCV
    column : str, optional
        Kolom yang digunakan, default "close"
        
    Returns
    -------
    dict
        Dictionary berisi min, max, mean, std
    """
    price_col = None
    for col in df.columns:
        if col.lower() == column.lower():
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Column '{column}' not found")
    
    prices = df[price_col]
    
    return {
        'min': float(prices.min()),
        'max': float(prices.max()),
        'mean': float(prices.mean()),
        'median': float(prices.median()),
        'std': float(prices.std()),
        'current': float(prices.iloc[-1]),
    }


def get_price_n_days_ago(df: pd.DataFrame, n: int, column: str = "close") -> float:
    """
    Ambil harga N hari yang lalu.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV
    n : int
        Jumlah hari
    column : str
        Kolom harga
        
    Returns
    -------
    float
        Harga N hari yang lalu
    """
    price_col = None
    for col in df.columns:
        if col.lower() == column.lower():
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Column '{column}' not found")
    
    if len(df) < n + 1:
        raise ValueError(f"Data tidak cukup untuk ambil harga {n} hari lalu")
    
    return float(df[price_col].iloc[-n-1])


def get_current_price(df: pd.DataFrame, column: str = "close") -> float:
    """
    Ambil harga terkini (terakhir).
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV
    column : str
        Kolom harga
        
    Returns
    -------
    float
        Harga terkini
    """
    price_col = None
    for col in df.columns:
        if col.lower() == column.lower():
            price_col = col
            break
    
    if price_col is None:
        raise ValueError(f"Column '{column}' not found")
    
    return float(df[price_col].iloc[-1])


def screen_stocks(
    stock_data_dict: Dict[str, pd.DataFrame],
    n_days: int,
    min_drawdown: float = 0.0
) -> pd.DataFrame:
    """
    Screen saham yang memenuhi kriteria downtrend.
    
    Screening criteria:
    1. Harus turun N hari berturut-turut
    2. Drawdown harus >= min_drawdown
    
    Parameters
    ----------
    stock_data_dict : dict
        Dictionary dengan ticker sebagai key dan data DataFrame sebagai value
    n_days : int
        Jumlah hari penurunan yang dicari
    min_drawdown : float, optional
        Minimal drawdown percentage, default 0.0
        
    Returns
    -------
    pd.DataFrame
        DataFrame hasil screening dengan columns:
        - ticker
        - current_price
        - price_n_days_ago
        - drawdown_pct
        - days_down
        - num_days_checked
        
    Examples
    --------
    >>> data = {
    ...     'BBCA.JK': df1,
    ...     'BBRI.JK': df2,
    ... }
    >>> results = screen_stocks(data, n_days=5, min_drawdown=1.0)
    >>> print(results)
    """
    results = []
    
    for ticker, df in stock_data_dict.items():
        try:
            # Validate data
            if df is None or len(df) < n_days + 1:
                continue
            
            # Calculate returns
            returns = calculate_returns(df)
            
            # Check if down N days
            if not is_down_n_days(returns, n_days):
                continue
            
            # Calculate drawdown
            drawdown = calculate_drawdown(df, n_days)
            
            # Check minimum drawdown
            if drawdown > min_drawdown:  # Remember drawdown is negative
                continue
            
            # Get prices
            current_price = get_current_price(df)
            price_n_days_ago = get_price_n_days_ago(df, n_days)
            
            # Add to results
            results.append({
                'ticker': ticker,
                'current_price': current_price,
                'price_n_days_ago': price_n_days_ago,
                'drawdown_pct': drawdown,
                'days_down': n_days,
                'num_days_checked': len(df),
            })
        
        except Exception as e:
            # Skip jika ada error untuk ticker ini
            print(f"Error processing {ticker}: {str(e)}")
            continue
    
    # Create DataFrame
    if results:
        results_df = pd.DataFrame(results)
        # Sort by drawdown (most negative first)
        results_df = results_df.sort_values('drawdown_pct')
        results_df = results_df.reset_index(drop=True)
        return results_df
    else:
        # Return empty dataframe with correct columns
        return pd.DataFrame(columns=[
            'ticker', 'current_price', 'price_n_days_ago',
            'drawdown_pct', 'days_down', 'num_days_checked'
        ])


def get_daily_returns_table(df: pd.DataFrame, n_rows: int = 10) -> pd.DataFrame:
    """
    Buat tabel daily returns untuk display.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV
    n_rows : int
        Jumlah baris yang ditampilkan, default 10
        
    Returns
    -------
    pd.DataFrame
        Tabel dengan columns: Date, Close, Return %
    """
    returns = calculate_returns(df)
    
    # Get last N rows
    last_n = n_rows
    result_df = pd.DataFrame({
        'Date': df.index[-last_n:],
        'Close': df['Close'].tail(last_n).values,
        'Return %': (returns.tail(last_n).values * 100),
    })
    
    result_df = result_df.reset_index(drop=True)
    
    return result_df


# Testing function
if __name__ == "__main__":
    from data import get_stock_data
    
    print("Testing screener functions...\n")
    
    # Test data
    try:
        df = get_stock_data("BBCA.JK", period="1mo")
        print(f"✓ Loaded data for BBCA.JK (shape: {df.shape})\n")
        
        # Test calculate_returns
        print("Testing calculate_returns...")
        returns = calculate_returns(df)
        print(f"✓ Returns calculated")
        print(f"  Last 3 returns: {returns.tail(3).values}\n")
        
        # Test is_down_n_days
        print("Testing is_down_n_days...")
        is_down_5 = is_down_n_days(returns, 5)
        print(f"✓ Is down 5 days: {is_down_5}\n")
        
        # Test calculate_drawdown
        print("Testing calculate_drawdown...")
        dd = calculate_drawdown(df, 5)
        print(f"✓ Drawdown (5 days): {dd:.2f}%\n")
        
        # Test statistics
        print("Testing calculate_statistics...")
        stats = calculate_statistics(df)
        print(f"✓ Statistics: {stats}\n")
        
    except Exception as e:
        print(f"✗ Error: {e}")
