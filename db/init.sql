CREATE TABLE IF NOT EXISTS training_data (
    id SERIAL PRIMARY KEY,
    series_id TEXT NOT NULL,
    version TEXT NOT NULL,
    timestamp BIGINT NOT NULL,
    value DOUBLE PRECISION NOT NULL
);