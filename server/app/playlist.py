import json
from app.db import get_conn


def upsert(uid: str, song: dict):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO songs (title, artist, url, thumbnail, youtube_url)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, artist) DO UPDATE SET
                url         = EXCLUDED.url,
                thumbnail   = EXCLUDED.thumbnail,
                youtube_url = EXCLUDED.youtube_url
            RETURNING id
            """,
            (song["title"], song["artist"], song.get("url"), song.get("thumbnail"), song.get("youtube_url")),
        )
        song_id = cur.fetchone()["id"]

        cur.execute(
            """
            INSERT INTO song_analysis (song_id, genre, confidence, all_scores, sentiment, emotion, compound, scores)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (song_id) DO UPDATE SET
                genre      = EXCLUDED.genre,
                confidence = EXCLUDED.confidence,
                all_scores = EXCLUDED.all_scores,
                sentiment  = EXCLUDED.sentiment,
                emotion    = EXCLUDED.emotion,
                compound   = EXCLUDED.compound,
                scores     = EXCLUDED.scores
            """,
            (
                song_id,
                song.get("genre"),
                song.get("confidence"),
                json.dumps(song.get("all_scores")),
                song.get("sentiment"),
                song.get("emotion"),
                song.get("compound"),
                json.dumps(song.get("scores")),
            ),
        )

        cur.execute(
            """
            INSERT INTO playlist (uid, song_id)
            VALUES (%s, %s)
            ON CONFLICT (uid, song_id) DO UPDATE SET
                search_count  = playlist.search_count + 1,
                last_searched = NOW()
            """,
            (uid, song_id),
        )
    conn.commit()


def get_all(uid: str) -> list:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.title, s.artist, s.url, s.thumbnail, s.youtube_url,
                   a.genre, a.confidence, a.all_scores, a.sentiment, a.emotion, a.compound, a.scores,
                   p.search_count, p.last_searched
            FROM playlist p
            JOIN songs s ON s.id = p.song_id
            JOIN song_analysis a ON a.song_id = s.id
            WHERE p.uid = %s
            ORDER BY p.last_searched DESC
            """,
            (uid,),
        )
        return _serialize(cur.fetchall())


def get_top(uid: str, limit: int = 10) -> list:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT s.title, s.artist, s.url, s.thumbnail, s.youtube_url,
                   a.genre, a.confidence, a.all_scores, a.sentiment, a.emotion, a.compound, a.scores,
                   p.search_count, p.last_searched
            FROM playlist p
            JOIN songs s ON s.id = p.song_id
            JOIN song_analysis a ON a.song_id = s.id
            WHERE p.uid = %s
            ORDER BY p.search_count DESC
            LIMIT %s
            """,
            (uid, limit),
        )
        return _serialize(cur.fetchall())


def remove(uid: str, title: str, artist: str):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM playlist
            WHERE uid = %s AND song_id = (
                SELECT id FROM songs WHERE title = %s AND artist = %s
            )
            """,
            (uid, title, artist),
        )
    conn.commit()


def get_stats(uid: str) -> dict:
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT a.genre, COUNT(*) as count
            FROM playlist p
            JOIN songs s ON s.id = p.song_id
            JOIN song_analysis a ON a.song_id = s.id
            WHERE p.uid = %s AND a.genre IS NOT NULL
            GROUP BY a.genre
            ORDER BY count DESC
            """,
            (uid,),
        )
        genre_rows = cur.fetchall()

        cur.execute(
            """
            SELECT a.sentiment, a.emotion, COUNT(*) as count
            FROM playlist p
            JOIN songs s ON s.id = p.song_id
            JOIN song_analysis a ON a.song_id = s.id
            WHERE p.uid = %s AND a.sentiment IS NOT NULL
            GROUP BY a.sentiment, a.emotion
            ORDER BY count DESC
            """,
            (uid,),
        )
        sentiment_rows = cur.fetchall()

        cur.execute(
            """
            SELECT s.title, s.artist, s.youtube_url, a.genre, p.search_count
            FROM playlist p
            JOIN songs s ON s.id = p.song_id
            JOIN song_analysis a ON a.song_id = s.id
            WHERE p.uid = %s
            ORDER BY p.search_count DESC
            LIMIT 10
            """,
            (uid,),
        )
        top_songs = cur.fetchall()

    return {
        "genre_distribution": [dict(r) for r in genre_rows],
        "sentiment_breakdown": [dict(r) for r in sentiment_rows],
        "top_songs": [dict(r) for r in top_songs],
    }


def _serialize(rows: list) -> list:
    result = []
    for row in rows:
        r = dict(row)
        if isinstance(r.get("all_scores"), str):
            r["all_scores"] = json.loads(r["all_scores"])
        if isinstance(r.get("scores"), str):
            r["scores"] = json.loads(r["scores"])
        result.append(r)
    return result