import os
class Config:
    def __call__(self):
        return self
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 30
    RATELIMIT_DEFAULT = "60 per minute"
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "adminpass")
    BINANCE_BASE_URL = os.getenv("BINANCE_BASE_URL", "https://api.binance.com")
    REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "60"))
