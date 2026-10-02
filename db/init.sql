-- init.sql
-- Creates the tasks table if it doesn't already exist.
-- Mounted into the Postgres container's docker-entrypoint-initdb.d/ directory.

CREATE TABLE IF NOT EXISTS tasks (
    id    SERIAL PRIMARY KEY,
    title TEXT    NOT NULL CHECK (char_length(trim(title)) > 0),
    done  BOOLEAN NOT NULL DEFAULT FALSE
);

-- Seed a few starter rows so the API isn't empty on first boot
INSERT INTO tasks (title, done) VALUES
    ('Start The DB server',   FALSE),
    ('Check The DB server',   FALSE),
    ('Stopped the DB server', TRUE)
ON CONFLICT DO NOTHING;
