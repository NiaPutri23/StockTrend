"""
StockTrend Dashboard - Indonesian Stock Screener
Aplikasi Streamlit untuk screening saham BEI yang turun N hari berturut-turut.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import traceback

# Import custom modules
from src.data import get_stock_data, parse_ticker_input, validate_ticker
from src.screener import (
    is_mostly_down,
    screen_stocks,
    get_daily_returns_table,
    calculate_statistics,
)
from src.utils import (
    create_price_chart,
    create_volume_chart,
    create_returns_chart,
    format_currency,
    format_percentage,
    format_number,
    get_csv_filename,
    prepare_export_data
)
from src.cache_ui import (
    show_cache_status,
    show_cache_management_panel,
    show_cache_quick_stats,
    initialize_cache_system
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="StockTrend Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    
    .success {
        color: #2ca02c;
    }
    
    .danger {
        color: #d62728;
    }
    
    .neutral {
        color: #7f7f7f;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SIDEBAR SECTION
# ============================================================================

def render_sidebar() -> Tuple[List[str], int, float]:
    """
    Render sidebar untuk input parameter screening.
    
    Returns
    -------
    tuple
        (list of tickers, n_days, min_change_pct, run_button)
    """
    st.sidebar.title("📊 StockTrend Dashboard")
    st.sidebar.markdown("---")
    
    # Show cache status at the top of sidebar
    show_cache_status()
    
    st.sidebar.markdown("---")
    
    # Section 1: Input Ticker
    st.sidebar.subheader("📌 Input Saham")
    ticker_input = st.sidebar.text_area(
        "Daftar Ticker Saham",
        value="BBCA.JK\nBBRI.JK\nBMRI.JK\nTLKM.JK\nASII.JK",
        height=120,
        help="Masukkan satu ticker per baris, format: XXXX.JK"
    )
    
    # Parse dan validate tickers
    raw_tickers = [t.strip().upper() for t in ticker_input.split('\n') if t.strip()]
    valid_tickers = []
    invalid_tickers = []
    
    for ticker in raw_tickers:
        if validate_ticker(ticker):
            valid_tickers.append(ticker)
        else:
            invalid_tickers.append(ticker)
    
    # Show warnings untuk invalid tickers
    if invalid_tickers:
        st.sidebar.warning(
            f"⚠️ {len(invalid_tickers)} ticker invalid: {', '.join(invalid_tickers[:3])}"
            + (f" ..." if len(invalid_tickers) > 3 else "")
        )
    
    if valid_tickers:
        st.sidebar.success(f"✓ {len(valid_tickers)} ticker valid")
    else:
        st.sidebar.error("❌ Tidak ada ticker valid!")
    
    st.sidebar.markdown("---")
    
    # Section 2: Screening Parameters
    st.sidebar.subheader("⚙️ Parameter Screening")
    
    n_days = st.sidebar.slider(
        "📅 Jumlah Hari Turun",
        min_value=2,
        max_value=30,
        value=5,
        step=1,
        help="Jumlah hari berturut-turut yang dicari untuk penurunan"
    )
    
    min_change_pct = st.sidebar.slider(
        "📉 Minimal Penurunan (%)",
        min_value=0.0,
        max_value=50.0,
        value=5.0,
        step=0.5,
        help="Minimal penurunan harga dibanding N hari lalu"
    )
    
    st.sidebar.markdown("---")
    
    # Section 3: Action Buttons
    st.sidebar.subheader("🎯 Aksi")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        run_button = st.button(
            "🔍 Run Screening",
            use_container_width=True,
            key="run_screening"
        )
    
    with col2:
        clear_cache = st.button(
            "🔄 Clear Cache",
            use_container_width=True,
            key="clear_cache"
        )
    
    if clear_cache:
        st.cache_data.clear()
        st.success("✓ Cache cleared!")
    
    st.sidebar.markdown("---")
    
    # Section 4: Info & Help
    st.sidebar.subheader("ℹ️ Informasi")
    with st.sidebar.expander("Bantuan & Tips"):
        st.markdown("""
        **Format Ticker:**
        - Format: XXXX.JK (contoh: BBCA.JK)
        - Pisahkan dengan line break (Enter)
        
        **Parameter Screening:**
        - Hari Turun: Cari saham turun N hari berturut-turut
        - Minimal Penurunan: Filter berdasarkan persentase penurunan
        
        **Data Source:**
        - Yahoo Finance (real-time dengan lag ~15-20 menit)
        - Period: 3 bulan data historis
        
        **Waktu Proses:**
        - ±2-5 detik per 10 ticker
        - Tergantung kecepatan internet
        """)
    
    with st.sidebar.expander("Tentang App"):
        st.markdown("""
        **StockTrend Dashboard v1.0**
        
        Aplikasi screening saham BEI yang mengalami downtrend.
        
        - Framework: Streamlit
        - Data: yfinance (Yahoo Finance)
        - Visualization: Plotly
        
        Build with ❤️ for Indonesian Investors
        """)
    
    return valid_tickers, n_days, min_change_pct, run_button


# ============================================================================
# MAIN DASHBOARD
# ============================================================================

def render_dashboard():
    """
    Render halaman utama dashboard.
    """
    
    # Header
    st.title("📈 StockTrend Dashboard")
    st.markdown("Screening saham BEI yang mengalami penurunan harga berturut-turut")
    st.markdown("---")
    
    # Get sidebar inputs
    valid_tickers, n_days, min_change_pct, run_button = render_sidebar()
    
    # Initialize session state
    if 'screening_results' not in st.session_state:
        st.session_state.screening_results = None
    if 'screening_time' not in st.session_state:
        st.session_state.screening_time = None
    if 'last_tickers' not in st.session_state:
        st.session_state.last_tickers = None
    
    # Main content area
    main_content = st.container()
    
    with main_content:
        # Run screening jika button diklik
        if run_button:
            if not valid_tickers:
                st.error("❌ Silakan input minimal 1 ticker yang valid!")
                return
            
            # Run screening
            with st.spinner(f"🔍 Screening {len(valid_tickers)} saham..."):
                try:
                    # Fetch data
                    stock_data_dict = {}
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    for idx, ticker in enumerate(valid_tickers):
                        status_text.text(f"Loading data: {ticker}...")
                        try:
                            data = get_stock_data(ticker, period="3mo")
                            stock_data_dict[ticker] = data
                        except Exception as e:
                            st.warning(f"⚠️ Error loading {ticker}: {str(e)}")
                        
                        progress = (idx + 1) / len(valid_tickers)
                        progress_bar.progress(progress)
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    progress_bar.empty()
                    status_text.empty()
                    
                    # ==================================================
                    # 🛠️ MULAI KODE DEBUGGING YFINANCE
                    # ==================================================
                    st.markdown("---")
                    st.subheader("🛠️ Debugging: Status Data YFinance")
                    with st.expander("Buka untuk melihat raw data dari YFinance"):
                        if not stock_data_dict:
                            st.error("Gagal total: stock_data_dict kosong. YFinance tidak memberikan data sama sekali.")
                        else:
                            debug_info = []
                            success_tickers = []
                            for t, df in stock_data_dict.items():
                                if df is not None and not df.empty:
                                    success_tickers.append(t)
                                    last_date = df.index[-1].strftime('%Y-%m-%d') if not df.index.empty else "No Date"
                                    debug_info.append({"Ticker": t, "Status": "✅ Sukses", "Jumlah Baris": len(df), "Tgl Terakhir": last_date})
                                else:
                                    debug_info.append({"Ticker": t, "Status": "❌ Kosong/Gagal", "Jumlah Baris": 0, "Tgl Terakhir": "-"})
                            
                            st.write(f"**Berhasil diunduh:** {len(success_tickers)} dari {len(stock_data_dict)} saham.")
                            st.dataframe(pd.DataFrame(debug_info), use_container_width=True)
                            
                            if success_tickers:
                                sample_ticker = success_tickers[0]
                                st.write(f"**Contoh Raw Data untuk {sample_ticker} (5 Hari Terakhir):**")
                                sample_df = stock_data_dict[sample_ticker].tail()
                                st.dataframe(sample_df, use_container_width=True)
                                st.write("**Daftar Kolom yang Diterima:**")
                                st.write(list(sample_df.columns))
                    # ==================================================
                    # 🛑 AKHIR KODE DEBUGGING
                    # ==================================================

                    # Screen stocks - FIX: Menghapus argumen -min_change_pct ganda dan menambahkan koma yang kurang
                    results_df = screen_stocks(
                        stock_data_dict,
                        n_days=n_days,
                        min_change_pct=min_change_pct,
                        threshold=0.8
                    )
                    
                    # Screen stocks - FIX: Menghapus argumen -min_change_pct ganda dan menambahkan koma yang kurang
                    results_df = screen_stocks(
                        stock_data_dict,
                        n_days=n_days,
                        min_change_pct=min_change_pct,
                        threshold=0.8
                    )
                    
                    # Store in session
                    st.session_state.screening_results = results_df
                    st.session_state.screening_time = datetime.now()
                    st.session_state.last_tickers = valid_tickers
                    st.session_state.stock_data_dict = stock_data_dict
                    
                    st.success(f"✓ Screening selesai! Found {len(results_df)} saham")
                    
                except Exception as e:
                    st.error(f"❌ Error during screening: {str(e)}")
                    st.write(traceback.format_exc())
                    return
        
        # Display metrics
        if st.session_state.screening_results is not None:
            display_metrics(st.session_state)
            st.markdown("---")
            
            # Display results
            display_screening_results(st.session_state)
        else:
            st.info(
                "📌 Klik tombol 'Run Screening' di sidebar untuk memulai screening"
            )


def display_metrics(session_state):
    """Display metric cards dengan hasil screening."""
    results_df = session_state.screening_results
    last_tickers = session_state.last_tickers
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📊 Total Dianalisis",
            value=len(last_tickers),
            delta=None
        )
    
    with col2:
        passed_count = len(results_df)
        st.metric(
            label="✅ Lolos Screening",
            value=passed_count,
            delta=None
        )
    
    with col3:
        if len(last_tickers) > 0:
            success_rate = (passed_count / len(last_tickers)) * 100
            st.metric(
                label="📈 Success Rate",
                value=f"{success_rate:.1f}%",
                delta=None
            )
        else:
            st.metric(label="📈 Success Rate", value="0%", delta=None)
    
    with col4:
        if session_state.screening_time:
            update_time = session_state.screening_time.strftime("%H:%M:%S")
            st.metric(
                label="🕐 Update Terakhir",
                value=update_time,
                delta=None
            )


def display_screening_results(session_state):
    """Display tabel hasil screening dan interaksi detail saham."""
    results_df = session_state.screening_results
    
    if len(results_df) == 0:
        st.warning("⚠️ Tidak ada saham yang lolos screening dengan kriteria ini")
        return
    
    # Format results untuk display
    display_df = results_df.copy()
    display_df.columns = [
        'Ticker',
        'Harga Sekarang',
        'Harga N Hari Lalu',
        'Perubahan %',
        'Jumlah Hari Turun',
        'Num Days Checked'
    ]
    
    # Format numeric columns
    display_df['Harga Sekarang'] = display_df['Harga Sekarang'].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    display_df['Harga N Hari Lalu'] = display_df['Harga N Hari Lalu'].apply(
        lambda x: f"Rp {x:,.0f}"
    )
    display_df['Perubahan %'] = display_df['Perubahan %'].apply(
        lambda x: f"{x:.2f}%"
    )
    
    # Hide unnecessary columns
    display_cols = ['Ticker', 'Harga Sekarang', 'Harga N Hari Lalu', 
                     'Perubahan %', 'Jumlah Hari Turun']
    
    # Display table
    st.subheader("📊 Hasil Screening")
    st.dataframe(
        display_df[display_cols],
        use_container_width=True,
        height=400,
        hide_index=True
    )
    
    # Export button
    col1, col2 = st.columns([1, 3])
    with col1:
        csv_data = results_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=get_csv_filename("screening"),
            mime="text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Detail saham section
    st.subheader("🔍 Detail Saham")
    
    selected_ticker = st.selectbox(
        "Pilih ticker untuk melihat detail:",
        options=[''] + list(results_df['Ticker']),  # Pastikan kolom yang dirujuk benar sesuai format baris 373
        index=0,
        format_func=lambda x: "Pilih saham..." if x == '' else x
    )
    
    if selected_ticker:
        display_stock_details(selected_ticker, session_state)


def display_stock_details(ticker: str, session_state):
    """Display detail saham terpilih."""
    try:
        # Get data from session
        df = session_state.stock_data_dict[ticker]
        
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📈 Grafik Harga", "📊 Grafik Volume", "📋 Data Harian"])
        
        with tab1:
            # Price chart
            fig = create_price_chart(df, ticker=ticker)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Volume chart
            fig = create_volume_chart(df, ticker=ticker)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Daily returns table
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Daily Returns (Last 10 Days)")
                returns_table = get_daily_returns_table(df, n_rows=10)
                st.dataframe(returns_table, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("Statistik Harga")
                stats = calculate_statistics(df)
                
                stats_display = {
                    'Harga Sekarang': f"Rp {stats['current']:,.0f}",
                    'Harga Terendah': f"Rp {stats['min']:,.0f}",
                    'Harga Tertinggi': f"Rp {stats['max']:,.0f}",
                    'Harga Rata-rata': f"Rp {stats['mean']:,.0f}",
                    'Harga Median': f"Rp {stats['median']:,.0f}",
                    'Std Dev': f"Rp {stats['std']:,.0f}",
                }
                
                for key, value in stats_display.items():
                    st.metric(key, value)
                    
    except Exception as e:
        st.error(f"❌ Error loading detail: {str(e)}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Initialize cache system on startup
    cache_manager, scheduler = initialize_cache_system()
    
    # Page navigation
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "📑 Navigation",
        options=["Dashboard", "Cache Management"],
        index=0
    )
    
    if page == "Dashboard":
        render_dashboard()
    elif page == "Cache Management":
        show_cache_management_panel()