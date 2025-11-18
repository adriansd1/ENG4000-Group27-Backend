CREATE TABLE site_inventory (
    siteid VARCHAR(64) REFERENCES site_metadata(siteid),
    dg_model TEXT,
    dg_count INTEGER,
    battery_model TEXT,
    battery_capacity_kwh DOUBLE PRECISION,
    aircon_count INTEGER,
    aircon_model TEXT,
    rectifier_model TEXT,
    rectifier_count INTEGER,
    solar_kwp DOUBLE PRECISION,
    PRIMARY KEY (siteid)
);
