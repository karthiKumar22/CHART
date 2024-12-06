from typing import Dict, Tuple

INTERVAL_CONFIG: Dict[str, Tuple[str, str]] = {
    '1m': ('1m', '5d'),     # 1 minute data for 7 days
    '2m': ('2m', '5d'),     # 2 minute data for 7 days
    '5m': ('5m', '5d'),     # 5 minute data for 7 days
    '15m': ('15m', '5d'),   # 15 minute data for 7 days
    '30m': ('30m', '5d'),   # 30 minute data for 7 days
    '60m': ('1h', '5d'),    # 1 hour data for 7 days
    '1h': ('1h', '5d'),     # 1 hour data for 7 days
    '1d': ('1d', '1mo'),    # Daily data for 1 month
    '5d': ('5d', '3mo'),    # 5-day data for 3 months
    '1wk': ('1wk', '3mo'),  # Weekly data for 3 months
    '1mo': ('1mo', '1y')    # Monthly data for 1 year
}

def get_interval_config(interval: str) -> Tuple[str, str]:
    """Get the proper interval and period configuration."""
    interval = clean_interval_string(interval)
    return INTERVAL_CONFIG.get(interval, ('1d', '1mo'))

def clean_interval_string(interval: str) -> str:
    """Clean and standardize interval string."""
    return interval.lower().replace(' ', '').replace('minute', 'm').replace('hour', 'h').replace('day', 'd').replace('week', 'wk').replace('month', 'mo')

