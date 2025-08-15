import pandas as pd
import numpy as np
import requests
from flask import current_app

def fetch_klines(symbol: str, interval: str, limit: int = 400):
    base = current_app.config["BINANCE_BASE_URL"]
    url = f"{base}/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    df = pd.DataFrame(data, columns=[
        "open_time","open","high","low","close","volume","close_time","qav",
        "num_trades","taker_base_vol","taker_quote_vol","ignore"
    ])
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df["close_time"] = pd.to_datetime(df["close_time"], unit="ms", utc=True)
    for c in ["open","high","low","close","volume"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df.dropna().reset_index(drop=True)

def ema(series: pd.Series, span: int):
    return series.ewm(span=span, adjust=False).mean()

def rsi(series: pd.Series, period: int = 14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-9)
    return 100 - (100 / (1 + rs))

def macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

def rel_volume(vol: pd.Series, window: int = 20):
    avg = vol.rolling(window=window).mean()
    return vol / (avg + 1e-9)

def pct_change(series: pd.Series, window: int = 1):
    return series.pct_change(window) * 100.0

def correlation_to_btc(symbol_df: pd.DataFrame, btc_df: pd.DataFrame):
    left = pct_change(symbol_df["close"]).dropna()
    right = pct_change(btc_df["close"]).dropna()
    n = min(len(left), len(right))
    if n < 10:
        return None
    corr = left.tail(n).corr(right.tail(n))
    return float(corr) if pd.notna(corr) else None
