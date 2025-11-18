CREATE TABLE site_metadata (
    siteid VARCHAR(64) PRIMARY KEY,
    sitename TEXT,
    region TEXT,
    province TEXT,
    city TEXT,
    site_type TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    grid_category TEXT,
    owner TEXT,
    commissioned_on DATE
);
