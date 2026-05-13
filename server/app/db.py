import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

_conn = None

def get_conn():
    global _conn
    # reconnect if connection dropped
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(os.environ["DATABASE_URL"], cursor_factory=RealDictCursor)
    return _conn


def init_db():
    schema = os.path.join(os.path.dirname(__file__), "..", "schema.sql")
    with open(schema, "r") as f:
        sql = f.read()
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()