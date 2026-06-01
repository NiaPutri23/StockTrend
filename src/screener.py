"""
Module untuk logic screening saham yang mengalami downtrend.
"""

import pandas as pd
import numpy as np
from typing import Tuple, List, Dict

def _get_price_col(df: pd.DataFrame, column: str) -> any:
    """Helper untuk mengambil nama kolom dengan aman (support MultiIndex YFinance)"""
    for col in df.columns:
        # Handle jika format YFinance berupa tuple, contoh: ('Close', 'BBCA.JK')
        col_name = col[0] if isinstance(col, tuple) else col
        if str(col_name).lower() == column.lower():
            return col
    raise ValueError(f"Kolom '{column}' tidak ditemukan di dataframe")

def calculate_returns(df: pd.DataFrame, column: str = "close") -> pd.Series:
    price_col = _get_price_col(df, column)
    return df[price_col].pct_change()

def is_mostly_down(returns, n, threshold=0.8):
    last_n = returns.dropna().tail(n)
    down_days = (last_n < 0).sum()
    return down_days >= (n * threshold)

def calculate_statistics(df: pd.DataFrame, column: str = "close") -> dict:
    price_col = _get_price_col(df, column)
    prices = df[price_col].dropna()
    
    return {
        'min': float(prices.min()),
        'max': float(prices.max()),
        'mean': float(prices.mean()),
        'median': float(prices.median()),
        'std': float(prices.std()),
        'current': float(prices.iloc[-1]),
    }

def get_price_n_days_ago(df: pd.DataFrame, n: int, column: str = "close") -> float:
    price_col = _get_price_col(df, column)
    if len(df) < n + 1:
        raise ValueError(f"Data tidak cukup untuk ambil harga {n} hari lalu")
    return float(df[price_col].iloc[-n-1])

def get_current_price(df: pd.DataFrame, column: str = "close") -> float:
    price_col = _get_price_col(df, column)
    return float(df[price_col].iloc[-1])

def screen_stocks(
    stock_data_dict: Dict[str, pd.DataFrame],
    n_days: int,
    min_change_pct: float = 0.0,
    threshold: float = 0.8
) -> pd.DataFrame:
    
    results = []

    for ticker, df in stock_data_dict.items():
        try:
            if df is None or len(df) < n_days + 1:
                continue

            returns = calculate_returns(df)

            # Cek mayoritas merah
            if not is_mostly_down(returns, n_days, threshold=threshold):
                continue

            current_price = get_current_price(df)
            price_n_days_ago = get_price_n_days_ago(df, n_days)

            # Hitung persentase. Jika harga turun, change_pct bernilai negatif.
            change_pct = ((current_price - price_n_days_ago) / price_n_days_ago) * 100

            # Jika penurunannya TIDAK lebih dalam dari batas minimal, maka lewati.
            if change_pct > -min_change_pct:
                continue

            down_days = int((returns.dropna().tail(n_days) < 0).sum())

            results.append({
                "Ticker": ticker,  # Format huruf kapital agar seragam dengan app.py
                "Harga Sekarang": current_price,
                "Harga N Hari Lalu": price_n_days_ago,
                "Perubahan %": change_pct,
                "Jumlah Hari Turun": down_days,
                "Num Days Checked": len(df),
            })

        except Exception as e:
            # Tetap tangkap error agar looping tidak berhenti, tapi pastikan kamu bisa melihatnya di terminal IDE-mu
            print(f"⚠️ Error processing {ticker}: {str(e)}")
            continue

    if not results:
        return pd.DataFrame(columns=[
            "Ticker", "Harga Sekarang", "Harga N Hari Lalu",
            "Perubahan %", "Jumlah Hari Turun", "Num Days Checked"
        ])

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values("Perubahan %", ascending=True).reset_index(drop=True)
    
    return results_df

def get_daily_returns_table(df: pd.DataFrame, n_rows: int = 10) -> pd.DataFrame:
    returns = calculate_returns(df)
    price_col = _get_price_col(df, "close")
    
    last_n = n_rows
    result_df = pd.DataFrame({
        'Date': df.index[-last_n:],
        'Close': df[price_col].tail(last_n).values,
        'Return %': (returns.tail(last_n).values * 100),
    })
    
    result_df = result_df.reset_index(drop=True)
    return result_df