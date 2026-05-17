CREATE TABLE IF NOT EXISTS users (
    uid          VARCHAR PRIMARY KEY,
    email        VARCHAR NOT NULL,
    username     VARCHAR NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS songs (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR NOT NULL,
    artist      VARCHAR NOT NULL,
    url         VARCHAR,
    thumbnail   VARCHAR,
    youtube_url VARCHAR,
    UNIQUE(title, artist)
);

CREATE TABLE IF NOT EXISTS song_analysis (
    id          SERIAL PRIMARY KEY,
    song_id     INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    genre       VARCHAR,
    confidence  FLOAT,
    all_scores  JSONB,
    sentiment   VARCHAR,
    emotion     VARCHAR,
    compound    FLOAT,
    scores      JSONB,
    UNIQUE(song_id)
);

CREATE TABLE IF NOT EXISTS playlist (
    id            SERIAL PRIMARY KEY,
    uid           VARCHAR NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    song_id       INTEGER NOT NULL REFERENCES songs(id) ON DELETE CASCADE,
    search_count  INTEGER DEFAULT 1,
    last_searched TIMESTAMP DEFAULT NOW(),
    UNIQUE(uid, song_id)
);