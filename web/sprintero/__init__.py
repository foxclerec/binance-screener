import os
from flask import Flask
from .extensions import db, migrate, cache, limiter
from .config import Config
from .blueprints.main.routes import bp as main_bp
from .blueprints.admin.routes import bp as admin_bp

def create_app():
    app = Flask(__name__, instance_relative_config=False, static_folder=None)
    app.config.from_object(Config())

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    limiter.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app
