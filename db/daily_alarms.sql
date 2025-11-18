CREATE TABLE daily_alarms (
    alarm_id BIGSERIAL PRIMARY KEY,
    siteid VARCHAR(64) REFERENCES site_metadata(siteid),
    alarm_start TIMESTAMP,
    alarm_end TIMESTAMP,
    alarm_code TEXT,
    alarm_text TEXT,
    severity TEXT,
    acknowledged BOOLEAN DEFAULT FALSE
);
