import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.db import get_conn

_bearer = HTTPBearer()


def _init():
    if firebase_admin._apps:
        return
    raw = os.environ["FIREBASE_SERVICE_ACCOUNT_JSON"]
    cert = credentials.Certificate(json.loads(raw))
    firebase_admin.initialize_app(cert)

_init()


def verify_token(creds: HTTPAuthorizationCredentials = Security(_bearer)) -> str:
    try:
        decoded = auth.verify_id_token(creds.credentials)
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def create_user_doc(uid: str, email: str, username: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO users (uid, email, username)
            VALUES (%s, %s, %s)
            ON CONFLICT (uid) DO NOTHING
            """,
            (uid, email, username),
        )
    conn.commit()   