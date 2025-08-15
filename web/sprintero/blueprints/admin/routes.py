from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from ...models import Coin, Signal
from ...extensions import db
from functools import wraps

bp = Blueprint("admin", __name__, template_folder="templates")

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper

@bp.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username","")
        pw = request.form.get("password","")
        if user == current_app.config["ADMIN_USERNAME"] and pw == current_app.config["ADMIN_PASSWORD"]:
            session["is_admin"] = True
            return redirect(url_for("admin.index"))
        return render_template("admin/login.html", error="Invalid credentials")
    return render_template("admin/login.html")

@bp.get("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin.login"))

@bp.get("/")
@login_required
def index():
    coins = Coin.query.order_by(Coin.symbol.asc()).all()
    # health: is there a recent signal?
    import datetime as _dt
    refresh = int(current_app.config.get("REFRESH_SECONDS", 60))
    last = Signal.query.order_by(Signal.created_at.desc()).first()
    status = {"ok": False, "text": "Waiting for data…"}
    if last:
        age = (_dt.datetime.utcnow() - last.created_at).total_seconds()
        status["ok"] = age <= refresh * 2.5
        status["text"] = "OK" if status["ok"] else f"Stale (age {int(age)}s)"
    return render_template("admin/index.html", coins=coins, status=status)

@bp.post("/coins")
@login_required
def add_coin():
    from ...services.symbols import is_valid_symbol
    symbol = request.form.get("symbol","").upper().strip()
    # empty -> back
    if not symbol:
        flash("Symbol is empty", "err")
        return redirect(url_for("admin.index"))
    # normalize to USDT only
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"
    # cheap sanity regex before hitting Binance
    import re as _re
    if not _re.match(r"^[A-Z0-9]{3,15}USDT$", symbol):
        flash(f"Invalid format: {symbol}", "err")
        return redirect(url_for("admin.index"))
    # validate against Binance exchangeInfo (TRADING only)
    try:
        if not is_valid_symbol(symbol):
            flash(f"Symbol not found on Binance: {symbol}", "err")
            return redirect(url_for("admin.index"))
    except Exception as e:
        # network hiccup -> do not add silently
        flash("Could not verify symbol with Binance right now. Try again.", "err")
        return redirect(url_for("admin.index"))
    # dedupe
    if not Coin.query.filter_by(symbol=symbol).first():
        db.session.add(Coin(symbol=symbol, enabled=True))
        db.session.commit()
    else:
        flash(f"{symbol} already exists", "ok")
    return redirect(url_for("admin.index"))
    if not symbol.endswith("USDT"):
        symbol = symbol + "USDT"
    if not Coin.query.filter_by(symbol=symbol).first():
        db.session.add(Coin(symbol=symbol, enabled=True))
        db.session.commit()
    return redirect(url_for("admin.index"))

@bp.post("/coins/<int:coin_id>/toggle")
@login_required
def toggle_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    coin.enabled = not coin.enabled
    db.session.commit()
    return redirect(url_for("admin.index"))

@bp.post("/coins/<int:coin_id>/delete")
@login_required
def delete_coin(coin_id):
    coin = Coin.query.get_or_404(coin_id)
    db.session.delete(coin)
    db.session.commit()
    return redirect(url_for("admin.index"))
