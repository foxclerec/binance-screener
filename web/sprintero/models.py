from datetime import datetime
from .extensions import db

class Coin(db.Model):
    __tablename__ = "coins"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, default=True, nullable=False)

    def as_dict(self):
        return {"id": self.id, "symbol": self.symbol, "enabled": self.enabled}

class Signal(db.Model):
    __tablename__ = "signals"
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), index=True, nullable=False)
    timeframe = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    ema200 = db.Column(db.Float, nullable=True)
    rsi_15m = db.Column(db.Float, nullable=True)
    rsi_1h = db.Column(db.Float, nullable=True)
    macd_15m = db.Column(db.Float, nullable=True)
    rel_volume = db.Column(db.Float, nullable=True)
    corr_btc = db.Column(db.Float, nullable=True)
    changed_pct = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True, nullable=False)

    def as_dict(self):
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "price": self.price,
            "ema200": self.ema200,
            "rsi_15m": self.rsi_15m,
            "rsi_1h": self.rsi_1h,
            "macd_15m": self.macd_15m,
            "rel_volume": self.rel_volume,
            "corr_btc": self.corr_btc,
            "changed_pct": self.changed_pct,
            "created_at": self.created_at.isoformat() + "Z",
        }
