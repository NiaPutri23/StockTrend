# StockTrend Dashboard - Developer Guide

Panduan lengkap untuk developer yang ingin mengembangkan dan extend aplikasi StockTrend Dashboard.

## 📋 Daftar Isi

- [Project Structure](#project-structure)
- [Code Style Guide](#code-style-guide)
- [Module Documentation](#module-documentation)
- [Adding New Features](#adding-new-features)
- [Testing](#testing)
- [Debugging](#debugging)
- [Performance Optimization](#performance-optimization)

---

## 📁 Project Structure

Struktur folder yang rapi dan mudah dipahami:

```
stockTrend-dashboard/
├── app.py                    # Main Streamlit application
├── data.py                   # Data fetching & validation
├── screener.py               # Core screening logic
├── utils.py                  # Utility & visualization functions
├── requirements.txt          # Python dependencies
│
├── README.md                 # User documentation
├── SETUP.md                  # Installation guide
├── PLANNING.md               # Project planning document
├── DEVELOPMENT.md            # This file
├── .gitignore                # Git ignore rules
│
└── (venv/)                   # Virtual environment (ignored by git)
```

### File Organization Philosophy

- **app.py**: UI layer - Streamlit components dan layout
- **data.py**: Data layer - Yahoo Finance API interactions
- **screener.py**: Business logic - Calculation dan algorithm
- **utils.py**: Utility layer - Formatting, visualization, helpers
- **requirements.txt**: Dependency management

---

## 🎨 Code Style Guide

### PEP 8 Compliance

Ikuti Python Enhancement Proposal 8 (PEP 8) untuk code style.

```python
# ✅ GOOD
def calculate_returns(df: pd.DataFrame, column: str = "close") -> pd.Series:
    """Detailed docstring here."""
    prices = df[column]
    returns = prices.pct_change()
    return returns

# ❌ BAD
def calc_ret(df,col="close"):
    return df[col].pct_change()
```

### Naming Conventions

```python
# Functions & variables: snake_case
def calculate_returns():
    daily_returns = df.pct_change()

# Classes: PascalCase
class StockScreener:
    pass

# Constants: UPPER_CASE
MAX_TICKERS = 100
DEFAULT_PERIOD = "3mo"

# Private functions: _snake_case
def _validate_internal_data():
    pass
```

### Line Length

Maximum 100 characters per line:

```python
# ✅ GOOD - break long lines
error_message = (
    f"Error processing {ticker}: "
    f"Data insufficient for analysis"
)

# ❌ BAD - too long
error_message = f"Error processing {ticker}: Data insufficient for analysis"
```

### Docstrings

Gunakan NumPy style docstrings:

```python
def calculate_drawdown(df: pd.DataFrame, n: int) -> float:
    """
    Calculate drawdown percentage in N recent days.
    
    Drawdown adalah decline dari highest point ke current price.
    
    Parameters
    ----------
    df : pd.DataFrame
        OHLCV data with 'Close' column
    n : int
        Number of days to check
        
    Returns
    -------
    float
        Drawdown percentage (e.g., -5.23 for -5.23%)
        
    Raises
    ------
    ValueError
        If data insufficient for calculation
        
    Examples
    --------
    >>> df = get_stock_data("BBCA.JK")
    >>> dd = calculate_drawdown(df, 5)
    >>> print(f"Drawdown: {dd:.2f}%")
    """
    # Implementation
    pass
```

### Import Organization

```python
# 1. Standard library
import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple

# 2. Third-party libraries
import streamlit as st
import numpy as np
import plotly.graph_objects as go

# 3. Local imports
from data import get_stock_data
from screener import calculate_returns
from utils import format_currency
```

### Type Hints

Selalu gunakan type hints:

```python
# ✅ GOOD
def process_data(
    data: pd.DataFrame,
    n_days: int,
    threshold: float = 0.0
) -> Dict[str, any]:
    """Process stock data with parameters."""
    pass

# ❌ BAD
def process_data(data, n_days, threshold=0.0):
    """Process stock data."""
    pass
```

---

## 📚 Module Documentation

### data.py - Data Layer

**Responsibilities:**
- Fetch data dari Yahoo Finance
- Validate ticker format
- Handle network errors
- Cache data

**Key Functions:**

```python
get_stock_data(ticker: str, period: str = "3mo") -> pd.DataFrame
```
- **Input**: Ticker saham (e.g., "BBCA.JK")
- **Output**: DataFrame dengan OHLCV data
- **Cache**: 1 jam TTL

```python
validate_ticker(ticker: str) -> bool
```
- **Input**: Ticker string
- **Output**: Boolean validity

```python
parse_ticker_input(ticker_string: str) -> List[str]
```
- **Input**: Comma/line separated tickers
- **Output**: List of valid tickers

**Extension Points:**
- Add support untuk ticker non-.JK
- Implement database caching
- Add proxy support untuk restricted networks

---

### screener.py - Business Logic Layer

**Responsibilities:**
- Calculate technical indicators
- Detect downtrend patterns
- Apply filtering logic
- Generate results

**Key Functions:**

```python
calculate_returns(df: pd.DataFrame, column: str = "close") -> pd.Series
```
- Compute daily percentage returns
- Handle NaN values

```python
is_down_n_days(returns: pd.Series, n: int) -> bool
```
- Check if last N returns all negative
- Tolerance untuk rounding errors

```python
calculate_drawdown(df: pd.DataFrame, n: int) -> float
```
- Compute max decline percentage
- Based pada N-day window

```python
screen_stocks(
    stock_data_dict: Dict[str, pd.DataFrame],
    n_days: int,
    min_drawdown: float = 0.0
) -> pd.DataFrame
```
- Main screening logic
- Apply filters dan sorting
- Handle errors per ticker

**Extension Points:**
- Add more technical indicators (RSI, MACD, BB)
- Implement ML-based screening
- Add volume analysis
- Portfolio-level analysis

---

### utils.py - Utility Layer

**Responsibilities:**
- Create visualizations
- Format data untuk display
- Export functionality
- Helper functions

**Key Functions:**

```python
create_price_chart(df: pd.DataFrame, ticker: str) -> go.Figure
create_volume_chart(df: pd.DataFrame, ticker: str) -> go.Figure
create_returns_chart(df: pd.DataFrame, ticker: str) -> go.Figure
```
- Generate interactive Plotly charts
- Customizable styling

```python
format_currency(num: float) -> str
format_percentage(num: float) -> str
format_number(num: float) -> str
```
- Format numeric values untuk display
- Locale-aware formatting

**Extension Points:**
- Add more chart types (candlestick, heatmap)
- Dark mode support
- Custom color schemes
- Export ke HTML/PDF

---

### app.py - Presentation Layer

**Responsibilities:**
- Render Streamlit UI
- Handle user interactions
- Manage state
- Coordinate modules

**Key Components:**

```python
render_sidebar() -> Tuple[List[str], int, float, bool]
```
- Sidebar input controls
- Returns validated parameters

```python
render_dashboard()
```
- Main dashboard layout
- Orchestrate components

```python
display_metrics(session_state)
```
- Metric cards display

```python
display_screening_results(session_state)
```
- Results table dan actions

```python
display_stock_details(ticker: str, session_state)
```
- Detail view untuk selected stock

**Extension Points:**
- Add more sidebar sections
- Custom metrics
- Advanced filters
- Comparison view

---

## 🆕 Adding New Features

### Feature 1: Add New Technical Indicator

**Goal**: Tambahkan RSI (Relative Strength Index) indicator

**Steps:**

1. **Add calculation function di screener.py:**

```python
def calculate_rsi(df: pd.DataFrame, period: int = 14, column: str = "close") -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    Parameters
    ----------
    df : pd.DataFrame
        OHLCV data
    period : int
        RSI period (default 14)
    column : str
        Price column to use
        
    Returns
    -------
    pd.Series
        RSI values
    """
    prices = df[column.lower()]
    
    # Calculate changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)
    
    # Calculate average gains/losses
    avg_gains = gains.rolling(window=period).mean()
    avg_losses = losses.rolling(window=period).mean()
    
    # Calculate RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
```

2. **Add to screening logic:**

```python
def is_oversold(df: pd.DataFrame, rsi_threshold: int = 30) -> bool:
    """Check if stock is oversold (RSI < threshold)."""
    rsi = calculate_rsi(df)
    current_rsi = rsi.iloc[-1]
    return current_rsi < rsi_threshold
```

3. **Add to app.py UI:**

```python
# Di sidebar
rsi_threshold = st.sidebar.slider(
    "RSI Threshold (Oversold)",
    min_value=10,
    max_value=50,
    value=30
)

# Di screening logic
if is_oversold(df, rsi_threshold):
    include_stock = True
```

4. **Add visualization di utils.py:**

```python
def create_rsi_chart(df: pd.DataFrame, ticker: str = "Stock") -> go.Figure:
    """Create RSI indicator chart."""
    rsi = calculate_rsi(df)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=rsi,
        name='RSI(14)',
        line=dict(color='#1f77b4')
    ))
    
    # Add threshold lines
    fig.add_hline(y=70, line_dash="dash", annotation_text="Overbought")
    fig.add_hline(y=30, line_dash="dash", annotation_text="Oversold")
    
    return fig
```

---

### Feature 2: Add Export Format (JSON)

**Goal**: Tambahkan export ke JSON format

**Steps:**

1. **Update utils.py:**

```python
def export_to_json(df: pd.DataFrame, filename: str = None) -> str:
    """Export results to JSON format."""
    json_str = df.to_json(orient='records', indent=2)
    return json_str
```

2. **Update app.py - Display button:**

```python
# Di bagian export
col1, col2, col3 = st.columns([1, 1, 2])

with col1:
    csv_data = results_df.to_csv(index=False)
    st.download_button(
        label="📥 CSV",
        data=csv_data,
        file_name=get_csv_filename("screening"),
        mime="text/csv"
    )

with col2:
    json_data = export_to_json(results_df)
    st.download_button(
        label="📥 JSON",
        data=json_data,
        file_name=get_csv_filename("screening").replace(".csv", ".json"),
        mime="application/json"
    )
```

---

### Feature 3: Add Watchlist Persistence

**Goal**: Save favorite stocks ke local storage

**Steps:**

1. **Add persistence functions di utils.py:**

```python
import json
from pathlib import Path

WATCHLIST_FILE = Path(".streamlit/watchlist.json")

def load_watchlist() -> List[str]:
    """Load watchlist dari file."""
    if WATCHLIST_FILE.exists():
        with open(WATCHLIST_FILE, 'r') as f:
            return json.load(f)
    return []

def save_watchlist(tickers: List[str]) -> None:
    """Save watchlist ke file."""
    WATCHLIST_FILE.parent.mkdir(exist_ok=True)
    with open(WATCHLIST_FILE, 'w') as f:
        json.dump(tickers, f)

def add_to_watchlist(ticker: str) -> None:
    """Add ticker ke watchlist."""
    watchlist = load_watchlist()
    if ticker not in watchlist:
        watchlist.append(ticker)
        save_watchlist(watchlist)
```

2. **Update app.py:**

```python
# Di sidebar
with st.sidebar.expander("⭐ Watchlist"):
    watchlist = load_watchlist()
    
    # Display current watchlist
    st.write("Current watchlist:")
    for ticker in watchlist:
        st.write(f"- {ticker}")
    
    # Add ticker ke watchlist
    new_ticker = st.text_input("Add ticker to watchlist:")
    if new_ticker:
        add_to_watchlist(new_ticker)
        st.success(f"✓ Added {new_ticker} to watchlist")
```

---

## 🧪 Testing

### Unit Testing

Create `tests/test_screener.py`:

```python
import unittest
import pandas as pd
from screener import calculate_returns, is_down_n_days

class TestScreener(unittest.TestCase):
    
    def setUp(self):
        """Setup test data."""
        self.prices = pd.Series([100, 98, 96, 95, 93, 92])
        self.df = pd.DataFrame({'Close': self.prices})
    
    def test_calculate_returns(self):
        """Test return calculation."""
        returns = calculate_returns(self.df)
        self.assertEqual(len(returns), len(self.df))
        self.assertTrue(returns.iloc[1] < 0)  # Second day negative
    
    def test_is_down_n_days(self):
        """Test downtrend detection."""
        returns = calculate_returns(self.df)
        self.assertTrue(is_down_n_days(returns, 5))
        self.assertFalse(is_down_n_days(returns, 6))

if __name__ == '__main__':
    unittest.main()
```

### Running Tests

```bash
# Run all tests
python -m unittest discover

# Run specific test
python -m unittest tests.test_screener.TestScreener.test_calculate_returns

# Run dengan coverage
pip install coverage
coverage run -m unittest discover
coverage report
```

### Integration Testing

Test end-to-end screening flow:

```python
def test_full_screening_flow():
    """Test complete screening workflow."""
    tickers = ["BBCA.JK", "BBRI.JK"]
    
    # Fetch data
    stock_data = {}
    for ticker in tickers:
        stock_data[ticker] = get_stock_data(ticker)
    
    # Screen
    results = screen_stocks(stock_data, n_days=5, min_drawdown=-2.0)
    
    # Verify
    assert isinstance(results, pd.DataFrame)
    assert all(col in results.columns for col in [
        'ticker', 'current_price', 'drawdown_pct'
    ])
```

---

## 🐛 Debugging

### Enable Debug Mode

```python
# Di app.py, tambahkan di atas render_dashboard()
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Tickers: {valid_tickers}")
logger.debug(f"Parameters: n_days={n_days}, min_drawdown={min_drawdown}")
```

### Print Debugging

```python
# Check data shape
print(f"Data shape: {df.shape}")

# Check calculations
returns = calculate_returns(df)
print(f"Last 3 returns: {returns.tail(3).values}")

# Check results
print(f"Results found: {len(results_df)}")
```

### Streamlit Debug Info

```python
# Display debug info di sidebar
with st.sidebar.expander("🔧 Debug Info"):
    st.write(f"Tickers: {valid_tickers}")
    st.write(f"N days: {n_days}")
    st.write(f"Min drawdown: {min_drawdown}")
    if 'stock_data_dict' in st.session_state:
        st.write(f"Cached stocks: {len(st.session_state.stock_data_dict)}")
```

---

## ⚡ Performance Optimization

### 1. Caching Strategy

```python
# Cache expensive operations
@st.cache_data(ttl=3600)
def get_stock_data(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """Data di-cache selama 1 jam."""
    pass

# Cache calculation results
@st.cache_data(ttl=1800)
def screen_stocks_cached(tickers: List[str], n_days: int) -> pd.DataFrame:
    """Screening results di-cache selama 30 menit."""
    pass
```

### 2. Vectorized Operations

```python
# ✅ FAST - vectorized
returns = df['Close'].pct_change()

# ❌ SLOW - loop
returns = []
for i in range(1, len(df)):
    ret = (df['Close'].iloc[i] - df['Close'].iloc[i-1]) / df['Close'].iloc[i-1]
    returns.append(ret)
```

### 3. Lazy Loading

```python
# Load data hanya ketika dibutuhkan
if selected_ticker:  # Only if user selected
    df = get_stock_data(selected_ticker)
    # Render charts
```

### 4. Batch Operations

```python
# Fetch semua data sekaligus
stock_data_dict = {}
for ticker in tickers:
    stock_data_dict[ticker] = get_stock_data(ticker)

# Process semua sekaligus
results_df = screen_stocks(stock_data_dict, n_days, min_drawdown)
```

### 5. Database Instead of API (Future)

```python
# Current: Direct API calls
data = yf.download(ticker, period="3mo")

# Future: From database
data = db.query(f"SELECT * FROM stock_data WHERE ticker = {ticker}")
```

---

## 📈 Code Review Checklist

Sebelum commit/push, pastikan:

- [ ] Code follows PEP 8 style guide
- [ ] All functions have docstrings
- [ ] Type hints implemented
- [ ] No hardcoded values (use constants)
- [ ] Error handling implemented
- [ ] No debug print statements left
- [ ] Tested locally
- [ ] No credentials in code
- [ ] Requirements.txt updated if added packages
- [ ] Documentation updated

---

## 📝 Commit Message Guidelines

```bash
# Format: <type>(<scope>): <subject>

# Examples:
git commit -m "feat(screener): add RSI indicator"
git commit -m "fix(data): handle missing ticker data"
git commit -m "docs(readme): update installation steps"
git commit -m "refactor(utils): optimize chart creation"

# Types:
# feat: New feature
# fix: Bug fix
# docs: Documentation
# refactor: Code refactoring
# test: Test additions
# perf: Performance improvement
```

---

## 🚀 Future Development Roadmap

### Version 1.1 (Q3 2026)
- [ ] Historical screening results
- [ ] Watchlist functionality
- [ ] Email alerts
- [ ] Performance statistics

### Version 2.0 (Q4 2026)
- [ ] Database backend (PostgreSQL)
- [ ] User authentication
- [ ] Save screening profiles
- [ ] REST API endpoints

### Version 3.0 (2027)
- [ ] Machine learning predictions
- [ ] Sentiment analysis
- [ ] Portfolio optimization
- [ ] Mobile app

---

## 📞 Getting Help

- Check existing issues: https://github.com/NiaPutri23/StockTrend/issues
- Streamlit docs: https://docs.streamlit.io/
- Stack Overflow: Tag `streamlit`, `python`
- Ask in discussions: GitHub Discussions

---

**Happy Coding! 🚀**

Last Updated: June 2026
