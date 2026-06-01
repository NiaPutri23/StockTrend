"""
StockTrend Dashboard - Source modules
"""

from .data import get_stock_data, parse_ticker_input, validate_ticker
from .screener import (
    calculate_returns,
    is_down_n_days,
    calculate_drawdown,
    screen_stocks,
)
from .utils import (
    create_price_chart,
    create_volume_chart,
    create_returns_chart,
    format_currency,
    format_percentage,
)

__all__ = [
    "get_stock_data",
    "parse_ticker_input",
    "validate_ticker",
    "calculate_returns",
    "is_down_n_days",
    "calculate_drawdown",
    "screen_stocks",
    "create_price_chart",
    "create_volume_chart",
    "create_returns_chart",
    "format_currency",
    "format_percentage",
]
