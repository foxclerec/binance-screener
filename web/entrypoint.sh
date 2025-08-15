#!/bin/bash
set -e
python - <<'PY'
import os, time, sys
import psycopg2
from urllib.parse import urlparse
url = os.environ.get("DATABASE_URL")
if not url:
    print("DATABASE_URL not set", file=sys.stderr); sys.exit(1)
if url.startswith("postgresql+psycopg2://"):
    url = url.replace("postgresql+psycopg2://","postgresql://",1)
parsed = urlparse(url)
for i in range(60):
    try:
        conn = psycopg2.connect(
            dbname=parsed.path.lstrip("/"),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
        )
        conn.close()
        print("DB is up")
        break
    except Exception as e:
        print("Waiting for DB...", e)
        time.sleep(2)
else:
    print("DB not available", file=sys.stderr)
    sys.exit(1)
PY
export FLASK_APP=sprintero
flask db upgrade || flask db init && flask db migrate && flask db upgrade
exec gunicorn -w 3 -b 0.0.0.0:8000 "sprintero:create_app()" --timeout 120
