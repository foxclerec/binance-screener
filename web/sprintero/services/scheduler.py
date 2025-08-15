import time, traceback
from flask import Flask
from ..config import Config
from ..extensions import db
from ..models import Coin, Signal
from .data import fetch_klines, ema, rsi, macd, rel_volume, correlation_to_btc
import pandas as pd

def create_worker_app():
    app = Flask(__name__)
    app.config.from_object(Config())
    db.init_app(app)
    return app

def compute_for_symbol(symbol: str):
    sym_df = fetch_klines(symbol, "15m", limit=400)
    btc_df = fetch_klines("BTCUSDT", "15m", limit=400)
    if len(sym_df) < 50:
        return None
    sym_df["ema200"] = ema(sym_df["close"], 200)
    sym_df["rsi_15m"] = rsi(sym_df["close"], 14)
    macd_line, signal_line, hist = macd(sym_df["close"], 12,26,9)
    sym_df["macd_15m"] = hist
    sym_df["rel_volume"] = rel_volume(sym_df["volume"], 20)
    sym_df["changed_pct"] = (sym_df["close"].pct_change() * 100).fillna(0)
    corr = correlation_to_btc(sym_df, btc_df)
    last = sym_df.iloc[-1]
    return {
        "price": float(last["close"]),
        "ema200": float(last["ema200"]) if pd.notna(last["ema200"]) else None,
        "rsi_15m": float(last["rsi_15m"]) if pd.notna(last["rsi_15m"]) else None,
        "macd_15m": float(last["macd_15m"]) if pd.notna(last["macd_15m"]) else None,
        "rel_volume": float(last["rel_volume"]) if pd.notna(last["rel_volume"]) else None,
        "changed_pct": float(last["changed_pct"]) if pd.notna(last["changed_pct"]) else None,
        "corr_btc": corr,
    }

def main_loop(app: Flask):
    refresh = int(app.config.get("REFRESH_SECONDS", 60))
    print(f"[worker] starting refresh loop with {refresh}s interval")
    with app.app_context():
        while True:
            try:
                coins = Coin.query.filter_by(enabled=True).all()
                if not coins:
                    time.sleep(refresh)
                    continue
                for coin in coins:
                    symbol = coin.symbol.upper()
                    if not symbol.endswith("USDT"):
                        symbol = symbol + "USDT"
                    try:
                        payload = compute_for_symbol(symbol)
                        if not payload:
                            continue
                        sig = Signal(
                            symbol=symbol,
                            timeframe="15m",
                            price=payload["price"],
                            ema200=payload["ema200"],
                            rsi_15m=payload["rsi_15m"],
                            macd_15m=payload["macd_15m"],
                            rel_volume=payload["rel_volume"],
                            corr_btc=payload["corr_btc"],
                            changed_pct=payload["changed_pct"],
                        )
                        db.session.add(sig)
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        print("[worker] error for", symbol, e)
                time.sleep(refresh)
            except KeyboardInterrupt:
                print("[worker] exit"); break
            except Exception as e:
                print("[worker] loop error:", e); traceback.print_exc(); time.sleep(refresh)

if __name__ == "__main__":
    app = create_worker_app()
    main_loop(app)
