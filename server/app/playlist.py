import json
from app.db import get_conn


def upsert(uid: str, song: dict):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO playlist (
                uid, title, artist, genre, confidence, all_scores,
                sentiment, emotion, compound, scores,
                url, thumbnail, youtube_url, search_count, last_searched
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, 1, NOW()
            )
            ON CONFLICT (uid, title, artist) DO UPDATE SET
                search_count  = playlist.search_count + 1,
                last_searched = NOW()
            """,
            (
                uid,
                song["title"],
                song["artist"],
                song.get("genre"),
                song.get("confidence"),
                json.dumps(song.get("all_scores")),
                song.get("sentiment"),
                song.get("emotion"),
                song.get("compound"),
                json.dumps(song.get("scores")),
                song.get("url"),
                song.get("thumbnail"),
                song.get("youtube_url"),
            ),
        )
    conn.commit()


def get_all(uid: str) -> list:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM playlist WHERE uid = %s ORDER BY last_searched DESC",
            (uid,),
        )
        return _serialize(cur.fetchall())


def get_top(uid: str, limit: int = 10) -> list:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "SELECT * FROM playlist WHERE uid = %s ORDER BY search_count DESC LIMIT %s",
            (uid, limit),
        )
        return _serialize(cur.fetchall())


def remove(uid: str, title: str, artist: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM playlist WHERE uid = %s AND title = %s AND artist = %s",
            (uid, title, artist),
        )
    conn.commit()


def _serialize(rows: list) -> list:
    result = []
    for row in rows:
        r = dict(row)
        # psycopg2 returns JSONB as dict already but guard anyway
        if isinstance(r.get("all_scores"), str):
            r["all_scores"] = json.loads(r["all_scores"])
        if isinstance(r.get("scores"), str):
            r["scores"] = json.loads(r["scores"])
        result.append(r)
    return result