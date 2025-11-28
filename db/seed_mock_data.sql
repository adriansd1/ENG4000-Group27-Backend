BEGIN;

TRUNCATE TABLE
    daily_alarms,
    performance_daily_data,
    site_inventory,
    site_metadata
RESTART IDENTITY CASCADE;

-- 1) Site metadata

INSERT INTO site_metadata (
    siteid, sitename, region, province, city, site_type,
    latitude, longitude, grid_category, owner, commissioned_on
) VALUES
  ('SITE_TOR_001', 'Toronto Central Tower', 'GTA', 'ON', 'Toronto', 'macro',
   43.6510, -79.3470, 'grid-connected', 'PLC Group', '2021-03-15'),
  ('SITE_MIS_001', 'Mississauga Data Hub', 'GTA', 'ON', 'Mississauga', 'data-center',
   43.5890, -79.6441, 'grid-connected', 'PLC Group', '2022-06-01'),
  ('SITE_OTT_001', 'Ottawa Relay Site', 'Eastern', 'ON', 'Ottawa', 'macro',
   45.4215, -75.6972, 'weak-grid', 'PLC Group', '2020-11-20'),
  ('SITE_MTL_001', 'Montreal East Node', 'Quebec', 'QC', 'Montreal', 'macro',
   45.5017, -73.5673, 'grid-connected', 'PLC Group', '2019-09-05'),
  ('SITE_VAN_001', 'Vancouver Uplink Station', 'BC Coast', 'BC', 'Vancouver', 'hub',
   49.2827, -123.1207, 'grid+solar-hybrid', 'PLC Group', '2023-02-10');

-- 2) Site inventory

INSERT INTO site_inventory (
    siteid, dg_model, dg_count, battery_model, battery_capacity_kwh,
    aircon_count, aircon_model, rectifier_model, rectifier_count, solar_kwp
) VALUES
  ('SITE_TOR_001', 'Cummins C500D6', 1, 'Li-Ion Rack 200kWh', 200.0,
   3, 'Daikin 7kW', 'Eltek Flatpack2', 4, 40.0),
  ('SITE_MIS_001', 'Cummins C800D6', 2, 'Li-Ion Rack 300kWh', 300.0,
   4, 'Vertiv 10kW', 'Huawei R4850G', 6, 60.0),
  ('SITE_OTT_001', 'FG Wilson P330-3', 1, 'VRLA Bank 150kWh', 150.0,
   2, 'Carrier 5kW', 'Delta DPR 2900', 3, 20.0),
  ('SITE_MTL_001', 'CAT DE330', 1, 'Li-Ion Rack 180kWh', 180.0,
   3, 'Daikin 7kW', 'Eltek Flatpack2', 4, 30.0),
  ('SITE_VAN_001', 'Cummins C1000D6', 1, 'Li-Ion Rack 400kWh', 400.0,
   4, 'Vertiv 10kW', 'Huawei R4850G', 8, 120.0);

-- 3) Daily performance data 

-- Toronto
INSERT INTO performance_daily_data (
    siteid, date,
    gridkwh, gridkw,
    solar1kwh, solar1kw,
    batt1kwh, batt1kw,
    gridhr, solarhr, dghr
) VALUES
  ('SITE_TOR_001', '2025-01-01',
   1200.0, 55.0,
   180.0, 40.0,
   60.0, 25.0,
   19.0, 5.0, 0.0),
  ('SITE_TOR_001', '2025-01-02',
   1150.0, 53.0,
   175.0, 38.0,
   70.0, 28.0,
   19.5, 4.5, 0.0);

-- Mississauga
INSERT INTO performance_daily_data (
    siteid, date,
    gridkwh, gridkw,
    solar1kwh, solar1kw,
    batt1kwh, batt1kw,
    gridhr, solarhr, dghr
) VALUES
  ('SITE_MIS_001', '2025-01-01',
   1500.0, 70.0,
   220.0, 60.0,
   90.0, 35.0,
   16.0, 6.0, 2.5),
  ('SITE_MIS_001', '2025-01-02',
   1450.0, 68.0,
   210.0, 58.0,
   80.0, 32.0,
   17.0, 5.5, 1.0);

-- Ottawa
INSERT INTO performance_daily_data (
    siteid, date,
    gridkwh, gridkw,
    solar1kwh, solar1kw,
    batt1kwh, batt1kw,
    gridhr, solarhr, dghr
) VALUES
  ('SITE_OTT_001', '2025-01-01',
   600.0, 35.0,
   120.0, 30.0,
   110.0, 40.0,
   10.0, 5.0, 5.0);

-- Montreal
INSERT INTO performance_daily_data (
    siteid, date,
    gridkwh, gridkw,
    solar1kwh, solar1kw,
    batt1kwh, batt1kw,
    gridhr, solarhr, dghr
) VALUES
  ('SITE_MTL_001', '2025-01-01',
   1050.0, 48.0,
   160.0, 38.0,
   55.0, 22.0,
   18.5, 4.5, 0.5);

-- Vancouver
INSERT INTO performance_daily_data (
    siteid, date,
    gridkwh, gridkw,
    solar1kwh, solar1kw,
    batt1kwh, batt1kw,
    gridhr, solarhr, dghr
) VALUES
  ('SITE_VAN_001', '2025-01-01',
   900.0, 45.0,
   260.0, 90.0,
   95.0, 38.0,
   15.0, 7.0, 0.2),
  ('SITE_VAN_001', '2025-01-02',
   880.0, 43.0,
   255.0, 88.0,
   100.0, 40.0,
   15.2, 6.8, 0.0);

-- 4) Daily alarms

INSERT INTO daily_alarms (
    siteid, alarm_start, alarm_end, alarm_code,
    alarm_text, severity, acknowledged
) VALUES
  ('SITE_TOR_001', '2025-01-02 13:10', '2025-01-02 13:35',
   'INV_OT_TEMP', 'Inverter over-temperature above 70C', 'warning', FALSE),
  ('SITE_MIS_001', '2025-01-01 02:05', '2025-01-01 03:10',
   'DG_FUEL_LOW', 'Diesel generator fuel level below 25%', 'info', TRUE),
  ('SITE_OTT_001', '2025-01-01 18:20', '2025-01-01 20:45',
   'GRID_OUTAGE', 'Utility grid outage – site on DG + battery', 'critical', FALSE),
  ('SITE_VAN_001', '2025-01-02 11:00', '2025-01-02 11:20',
   'PV_STRING_MISMATCH', 'One PV string ~15% below expected', 'warning', TRUE);

COMMIT;

