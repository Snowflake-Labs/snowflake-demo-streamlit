![](../shared_assets/sis-header.jpeg)

## NY Pickup Location App

An app that visualizes geo-temporal data from NY taxi pickups using H3 and time series.
It can be useful to visualize marketplace signals that are distributed spatially and temporally.

By leveraging intuitive filters in the sidebar, users can refine their analysis based on date,
time, or specific H3 cell, allowing for a granular exploration of demand patterns. Whether
seeking real-time or forecasted demand, the application generates dynamic charts that precisely
reflect the selected parameters across all H3 hexagons or a singular focus.

Additionally, the sidebar features a SMAPE metric table, providing an insightful comparison of
prediction accuracy across H3 cells. A lower SMAPE score indicates a more accurate prediction,
empowering users to identify the most reliable forecasts effortlessly.

## App layout

Below we can see two charts that show the comparision for the forecast and the actual pickup values by H3.

![Main App](./assets/app.png)

Here we can see a chart for the forecast and actual pickups as a time series.

![Comparison Chart](./assets/comparison.png)

## App data

To run this app the following objects need to be created in the Snowflake account:

```sql
create or replace database h3_timeseries_visualization_db;
create or replace schema h3_timeseries_visualization_db.h3_timeseries_visualization_s;

create or replace TABLE h3_timeseries_visualization_db.h3_timeseries_visualization_s.NY_TAXI_RIDES_METRICS (
	H3 VARCHAR(16777216),
	SMAPE VARIANT
);

create or replace TABLE h3_timeseries_visualization_db.h3_timeseries_visualization_s.NY_TAXI_RIDES_COMPARE (
	H3 VARCHAR(16777216),
	PICKUP_TIME TIMESTAMP_NTZ(9),
	PICKUPS NUMBER(18,0),
	FORECAST FLOAT
);
```

You can populate the "NY_TAXI_RIDES_METRICS" and "NY_TAXI_RIDES_COMPARE" tables running the following sql statements:

```sql
-- Generate 100 random rows for the NY_TAXI_RIDES_METRICS table
INSERT INTO h3_timeseries_visualization_db.h3_timeseries_visualization_s.NY_TAXI_RIDES_METRICS (
    H3,
    SMAPE
)
SELECT
    '882a10' ||
    CASE MOD(uniform(0, 44, random()), 44)
        WHEN 0 THEN '0d65fffff'
        WHEN 1 THEN '725bfffff'
        WHEN 2 THEN '0d29fffff'
        WHEN 3 THEN '0d23fffff'
        WHEN 4 THEN '0d2bfffff'
        WHEN 5 THEN '0d25fffff'
        WHEN 6 THEN '0d27fffff'
        WHEN 7 THEN '72c9fffff'
        WHEN 8 THEN '0d2dfffff'
        WHEN 9 THEN '0d21fffff'
        WHEN 10 THEN '72cdfffff'
        WHEN 11 THEN '72c1fffff'
        WHEN 12 THEN '72c3fffff'
        WHEN 13 THEN '089bfffff'
        WHEN 14 THEN '0d6dfffff'
        WHEN 15 THEN '08b9fffff'
        WHEN 16 THEN '7289fffff'
        WHEN 17 THEN '08bbfffff'
        WHEN 18 THEN '7259fffff'
        WHEN 19 THEN '08b3fffff'
        WHEN 20 THEN '72cbfffff'
        WHEN 21 THEN '7219fffff'
        WHEN 22 THEN '3b1dfffff'
        WHEN 23 THEN '728dfffff'
        WHEN 24 THEN '0889fffff'
        WHEN 25 THEN '3b03fffff'
        WHEN 26 THEN '0d61fffff'
        WHEN 27 THEN '0d6bfffff'
        WHEN 28 THEN '721bfffff'
        WHEN 29 THEN '0d63fffff'
        WHEN 30 THEN '0899fffff'
        WHEN 31 THEN '0d45fffff'
        WHEN 32 THEN '0d67fffff'
        WHEN 33 THEN '0883fffff'
        WHEN 34 THEN '0d35fffff'
        WHEN 35 THEN '7253fffff'
        WHEN 36 THEN '0891fffff'
        WHEN 37 THEN '0e25fffff'
        WHEN 38 THEN '0d69fffff'
        WHEN 39 THEN '72c7fffff'
        WHEN 40 THEN '0f53fffff'
        WHEN 41 THEN '0897fffff'
        WHEN 42 THEN '0f57fffff'
        WHEN 43 THEN '0893fffff'
    END AS H3,
    uniform(0.164, 0.632, random()) AS SMAPE
FROM
    TABLE(GENERATOR(ROWCOUNT => 100));

-- Generate 100 random rows for the NY_TAXI_RIDES_COMPARE table
INSERT INTO h3_timeseries_visualization_db.h3_timeseries_visualization_s.NY_TAXI_RIDES_COMPARE (
    H3,
    PICKUP_TIME,
    PICKUPS,
    FORECAST
)
SELECT
    '882a10' ||
    CASE MOD(uniform(0, 44, random()), 44)
        WHEN 0 THEN '0d65fffff'
        WHEN 1 THEN '725bfffff'
        WHEN 2 THEN '0d29fffff'
        WHEN 3 THEN '0d23fffff'
        WHEN 4 THEN '0d2bfffff'
        WHEN 5 THEN '0d25fffff'
        WHEN 6 THEN '0d27fffff'
        WHEN 7 THEN '72c9fffff'
        WHEN 8 THEN '0d2dfffff'
        WHEN 9 THEN '0d21fffff'
        WHEN 10 THEN '72cdfffff'
        WHEN 11 THEN '72c1fffff'
        WHEN 12 THEN '72c3fffff'
        WHEN 13 THEN '089bfffff'
        WHEN 14 THEN '0d6dfffff'
        WHEN 15 THEN '08b9fffff'
        WHEN 16 THEN '7289fffff'
        WHEN 17 THEN '08bbfffff'
        WHEN 18 THEN '7259fffff'
        WHEN 19 THEN '08b3fffff'
        WHEN 20 THEN '72cbfffff'
        WHEN 21 THEN '7219fffff'
        WHEN 22 THEN '3b1dfffff'
        WHEN 23 THEN '728dfffff'
        WHEN 24 THEN '0889fffff'
        WHEN 25 THEN '3b03fffff'
        WHEN 26 THEN '0d61fffff'
        WHEN 27 THEN '0d6bfffff'
        WHEN 28 THEN '721bfffff'
        WHEN 29 THEN '0d63fffff'
        WHEN 30 THEN '0899fffff'
        WHEN 31 THEN '0d45fffff'
        WHEN 32 THEN '0d67fffff'
        WHEN 33 THEN '0883fffff'
        WHEN 34 THEN '0d35fffff'
        WHEN 35 THEN '7253fffff'
        WHEN 36 THEN '0891fffff'
        WHEN 37 THEN '0e25fffff'
        WHEN 38 THEN '0d69fffff'
        WHEN 39 THEN '72c7fffff'
        WHEN 40 THEN '0f53fffff'
        WHEN 41 THEN '0897fffff'
        WHEN 42 THEN '0f57fffff'
        WHEN 43 THEN '0893fffff'
    END AS H3,
    DATEADD(
           hour,
           FLOOR(uniform(1, 100, random()) * (DATEDIFF(hour, '2015-06-05 00:00:00.000', '2015-06-05 00:00:00.000') + 1)),
           '2015-06-05 00:00:00.000'
       ) AS PICKUP_TIME,
    uniform(1, 1859, random()) AS PICKUPS,
    ABS(PICKUPS - uniform(-300, 300, random())) AS FORECAST
FROM
    TABLE(GENERATOR(ROWCOUNT => 100));
```
