import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_conn = None

def _new_conn():
    c = psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)
    c.autocommit = False
    return c

def get_conn():
    global _conn
    if _conn is None or _conn.closed:
        _conn = _new_conn()
    else:
        try:
            with _conn.cursor() as cur:
                cur.execute("SELECT 1")
        except Exception:
            _conn = _new_conn()
    return _conn

def init_db():
    global _conn
    _conn = _new_conn()
    schema = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
    with open(schema) as f:
        sql = f.read()
    try:
        with _conn.cursor() as cur:
            cur.execute(sql)
        _conn.commit()
    except Exception:
        _conn.rollback()
        raise
