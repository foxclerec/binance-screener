from flask import Blueprint, render_template, jsonify, request
from ...extensions import cache
from ...models import Signal, Coin
from sqlalchemy import desc

bp = Blueprint("main", __name__, template_folder="templates", static_folder="static", static_url_path='/static')

@bp.get("/")
def index():
    return render_template("main/index.html")

@bp.get("/api/coins")
@cache.cached(timeout=15)
def api_coins():
    coins = Coin.query.order_by(Coin.symbol.asc()).all()
    return jsonify([c.as_dict() for c in coins])

@bp.get("/api/signals")
@cache.cached(timeout=10, query_string=True)
def api_signals():
    n = int(request.args.get("limit", "50"))
    enabled = {c.symbol.upper() if c.symbol.upper().endswith("USDT") else c.symbol.upper()+ "USDT" for c in Coin.query.filter_by(enabled=True).all()}
    if not enabled:
        return jsonify([])
    results = []
    for sym in sorted(enabled):
        row = Signal.query.filter_by(symbol=sym).order_by(desc(Signal.created_at)).first()
        if row:
            results.append(row.as_dict())
    results = sorted(results, key=lambda x: x["symbol"])
    return jsonify(results[:n])


@bp.route('/guide')
def guide():
    return render_template('main/guide.html')

@bp.route('/donate')
def donate():
    from flask import redirect
    return redirect('https://ko-fi.com/cryptoscreeners', code=302)

