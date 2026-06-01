"""
Module utility untuk visualisasi, formatting, dan helper functions.

Module ini menangani:
- Pembuatan grafik Plotly (price chart, volume chart)
- Formatting number dan currency
- Cache management
- UI helper functions
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from typing import Optional


def create_price_chart(
    df: pd.DataFrame,
    ticker: str = "Stock",
    height: int = 500,
    show_ma: bool = True
) -> go.Figure:
    """
    Membuat grafik harga penutupan menggunakan Plotly.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV dengan index datetime
    ticker : str, optional
        Nama ticker untuk judul grafik, default "Stock"
    height : int, optional
        Tinggi grafik dalam pixel, default 500
    show_ma : bool, optional
        Tampilkan moving average 20 hari, default True
        
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")
    >>> fig = create_price_chart(df, ticker="BBCA.JK")
    >>> fig.show()
    """
    df_plot = df.copy()
    
    # Create figure
    fig = go.Figure()
    
    # Add close price line
    fig.add_trace(go.Scatter(
        x=df_plot.index,
        y=df_plot['Close'],
        name='Close Price',
        line=dict(color='#1f77b4', width=2),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Close: Rp %{y:,.0f}<extra></extra>'
    ))
    
    # Add 20-day moving average if requested
    if show_ma and len(df_plot) >= 20:
        ma20 = df_plot['Close'].rolling(window=20).mean()
        fig.add_trace(go.Scatter(
            x=df_plot.index,
            y=ma20,
            name='MA 20',
            line=dict(color='#ff7f0e', width=1, dash='dash'),
            hovertemplate='<b>%{x|%Y-%m-%d}</b><br>MA20: Rp %{y:,.0f}<extra></extra>'
        ))
    
    # Update layout
    fig.update_layout(
        title=f'{ticker} - Stock Price Chart',
        xaxis_title='Date',
        yaxis_title='Price (Rp)',
        height=height,
        hovermode='x unified',
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(size=12),
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date'
        ),
        yaxis=dict(
            tickformat=',.0f'
        )
    )
    
    return fig


def create_volume_chart(
    df: pd.DataFrame,
    ticker: str = "Stock",
    height: int = 300
) -> go.Figure:
    """
    Membuat grafik volume transaksi menggunakan Plotly.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV dengan index datetime
    ticker : str, optional
        Nama ticker untuk judul grafik, default "Stock"
    height : int, optional
        Tinggi grafik dalam pixel, default 300
        
    Returns
    -------
    plotly.graph_objects.Figure
        Interactive Plotly figure dengan bar chart volume
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")
    >>> fig = create_volume_chart(df, ticker="BBCA.JK")
    >>> fig.show()
    """
    df_plot = df.copy()
    
    # Determine color based on price movement
    colors = []
    for i in range(len(df_plot)):
        if i == 0:
            colors.append('#1f77b4')  # Default blue
        else:
            if df_plot['Close'].iloc[i] >= df_plot['Close'].iloc[i-1]:
                colors.append('#2ca02c')  # Green for up days
            else:
                colors.append('#d62728')  # Red for down days
    
    # Create figure
    fig = go.Figure()
    
    # Add volume bars
    fig.add_trace(go.Bar(
        x=df_plot.index,
        y=df_plot['Volume'],
        name='Volume',
        marker=dict(color=colors),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Volume: %{y:,}<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=f'{ticker} - Trading Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        height=height,
        hovermode='x',
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(size=12),
        xaxis=dict(type='date'),
        yaxis=dict(
            tickformat=',d'
        ),
        showlegend=False
    )
    
    return fig


def create_returns_chart(
    df: pd.DataFrame,
    ticker: str = "Stock",
    height: int = 400
) -> go.Figure:
    """
    Membuat grafik daily returns menggunakan Plotly.
    
    Parameters
    ----------
    df : pd.DataFrame
        Data OHLCV
    ticker : str
        Nama ticker
    height : int
        Tinggi grafik
        
    Returns
    -------
    plotly.graph_objects.Figure
        Plotly figure dengan bar chart returns
    """
    from screener import calculate_returns
    
    df_plot = df.copy()
    returns = calculate_returns(df_plot)
    
    # Get last 30 days
    returns_plot = returns.tail(30)
    
    # Colors based on positive/negative
    colors = ['#2ca02c' if x > 0 else '#d62728' for x in returns_plot.values]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=returns_plot.index,
        y=returns_plot.values * 100,
        name='Daily Return',
        marker=dict(color=colors),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Return: %{y:.2f}%<extra></extra>'
    ))
    
    # Add zero line
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="#7f7f7f",
        annotation_text="Zero"
    )
    
    fig.update_layout(
        title=f'{ticker} - Daily Returns (Last 30 Days)',
        xaxis_title='Date',
        yaxis_title='Return (%)',
        height=height,
        hovermode='x',
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50),
        font=dict(size=12),
        xaxis=dict(type='date'),
        yaxis=dict(
            ticksuffix='%'
        ),
        showlegend=False
    )
    
    return fig


# Formatting Functions

def format_number(num: float, decimals: int = 2) -> str:
    """
    Format number menjadi string yang readable.
    
    Parameters
    ----------
    num : float
        Number yang akan diformat
    decimals : int
        Jumlah desimal yang ditampilkan
        
    Returns
    -------
    str
        Formatted number string
        
    Examples
    --------
    >>> format_number(1234567.89)
    '1,234,567.89'
    >>> format_number(0.125, decimals=1)
    '0.1'
    """
    return f"{num:,.{decimals}f}"


def format_currency(num: float, prefix: str = "Rp") -> str:
    """
    Format number sebagai currency Indonesia.
    
    Parameters
    ----------
    num : float
        Amount yang akan diformat
    prefix : str
        Currency prefix, default "Rp"
        
    Returns
    -------
    str
        Formatted currency string
        
    Examples
    --------
    >>> format_currency(9250.50)
    'Rp 9,250.50'
    """
    return f"{prefix} {num:,.0f}"


def format_percentage(num: float, decimals: int = 2) -> str:
    """
    Format number sebagai percentage.
    
    Parameters
    ----------
    num : float
        Number (0.05 = 5%)
    decimals : int
        Jumlah desimal
        
    Returns
    -------
    str
        Formatted percentage string
        
    Examples
    --------
    >>> format_percentage(0.0523)
    '5.23%'
    >>> format_percentage(-0.0213)
    '-2.13%'
    """
    return f"{num*100:+.{decimals}f}%"


def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format datetime menjadi string.
    
    Parameters
    ----------
    date : datetime
        Tanggal yang akan diformat
    format_str : str
        Format string
        
    Returns
    -------
    str
        Formatted date string
    """
    if isinstance(date, str):
        return date
    return date.strftime(format_str)


def format_large_number(num: int) -> str:
    """
    Format large number dengan shorthand (K, M, B).
    
    Parameters
    ----------
    num : int
        Number
        
    Returns
    -------
    str
        Formatted string
        
    Examples
    --------
    >>> format_large_number(1234567)
    '1.2M'
    >>> format_large_number(1234567890)
    '1.2B'
    """
    if abs(num) >= 1e9:
        return f"{num/1e9:.1f}B"
    elif abs(num) >= 1e6:
        return f"{num/1e6:.1f}M"
    elif abs(num) >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return str(int(num))


# Data Processing Functions

def get_ticker_display_name(ticker: str) -> str:
    """
    Get display name untuk ticker (remove .JK suffix).
    
    Parameters
    ----------
    ticker : str
        Ticker dengan format XXXX.JK
        
    Returns
    -------
    str
        Display name
    """
    if ticker.endswith(".JK"):
        return ticker[:-3]
    return ticker


def prepare_export_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare data untuk export ke CSV.
    
    Parameters
    ----------
    df : pd.DataFrame
        Results dataframe
        
    Returns
    -------
    pd.DataFrame
        Formatted dataframe untuk export
    """
    export_df = df.copy()
    
    # Format columns
    if 'current_price' in export_df.columns:
        export_df['current_price'] = export_df['current_price'].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
        )
    
    if 'price_n_days_ago' in export_df.columns:
        export_df['price_n_days_ago'] = export_df['price_n_days_ago'].apply(
            lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A"
        )
    
    if 'drawdown_pct' in export_df.columns:
        export_df['drawdown_pct'] = export_df['drawdown_pct'].apply(
            lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A"
        )
    
    return export_df


def get_csv_filename(prefix: str = "screening") -> str:
    """
    Generate filename untuk CSV export dengan timestamp.
    
    Parameters
    ----------
    prefix : str
        Prefix untuk filename, default "screening"
        
    Returns
    -------
    str
        Filename dengan timestamp
        
    Examples
    --------
    >>> get_csv_filename()
    'screening_2024_03_28_143025.csv'
    """
    timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    return f"{prefix}_{timestamp}.csv"


# Testing function
if __name__ == "__main__":
    from data import get_stock_data
    
    print("Testing utils functions...\n")
    
    # Test formatting functions
    print("Testing formatting functions...")
    print(f"✓ format_number(1234567.89) = {format_number(1234567.89)}")
    print(f"✓ format_currency(9250.50) = {format_currency(9250.50)}")
    print(f"✓ format_percentage(0.0523) = {format_percentage(0.0523)}")
    print(f"✓ format_large_number(1234567) = {format_large_number(1234567)}\n")
    
    # Test chart creation
    print("Testing chart creation...")
    try:
        df = get_stock_data("BBCA.JK", period="1mo")
        
        price_fig = create_price_chart(df, ticker="BBCA.JK")
        print(f"✓ Price chart created")
        
        volume_fig = create_volume_chart(df, ticker="BBCA.JK")
        print(f"✓ Volume chart created")
        
        returns_fig = create_returns_chart(df, ticker="BBCA.JK")
        print(f"✓ Returns chart created\n")
        
    except Exception as e:
        print(f"✗ Error: {e}\n")
    
    # Test other utilities
    print("Testing other utilities...")
    print(f"✓ get_ticker_display_name('BBCA.JK') = {get_ticker_display_name('BBCA.JK')}")
    print(f"✓ get_csv_filename() = {get_csv_filename()}")
