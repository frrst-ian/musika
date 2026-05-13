CREATE TABLE IF NOT EXISTS users (
    uid          VARCHAR PRIMARY KEY,
    email        VARCHAR NOT NULL,
    username     VARCHAR NOT NULL,
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS playlist (
    id            SERIAL PRIMARY KEY,
    uid           VARCHAR NOT NULL REFERENCES users(uid) ON DELETE CASCADE,
    title         VARCHAR NOT NULL,
    artist        VARCHAR NOT NULL,
    genre         VARCHAR,
    confidence    FLOAT,
    all_scores    JSONB,
    sentiment     VARCHAR,
    emotion       VARCHAR,
    compound      FLOAT,
    scores        JSONB,
    url           VARCHAR,
    thumbnail     VARCHAR,
    youtube_url   VARCHAR,
    search_count  INTEGER DEFAULT 1,
    last_searched TIMESTAMP DEFAULT NOW(),

    UNIQUE(uid, title, artist)
);