CREATE TABLE IF NOT EXISTS clients (
    client_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    address TEXT
);

CREATE TABLE IF NOT EXISTS properties (
    id SERIAL PRIMARY KEY,
    internal_id TEXT NOT NULL,
    provider TEXT NOT NULL,
    url TEXT NOT NULL,
    captured_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_id INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS search_queries (
    query_id SERIAL PRIMARY KEY,
    search_text TEXT NOT NULL,
    provider_name TEXT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_id INTEGER,
    enabled BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (client_id) REFERENCES clients (client_id) ON DELETE SET NULL
);

