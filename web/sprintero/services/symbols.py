
import time, requests
from flask import current_app

_cache = {"ts": 0, "symbols": set()}

def _load_symbols():
    base = current_app.config.get("BINANCE_BASE_URL", "https://api.binance.com")
    url = f"{base}/api/v3/exchangeInfo"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    symbols = set()
    for s in data.get("symbols", []):
        if s.get("status") == "TRADING":
            symbols.add(s.get("symbol","").upper())
    _cache["symbols"] = symbols
    _cache["ts"] = time.time()

def all_symbols(ttl=3600):
    now = time.time()
    if now - _cache["ts"] > ttl or not _cache["symbols"]:
        _load_symbols()
    return _cache["symbols"]

def is_valid_symbol(symbol: str) -> bool:
    symbol = symbol.upper()
    return symbol in all_symbols()
