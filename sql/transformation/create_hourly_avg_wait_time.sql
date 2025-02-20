CREATE OR REPLACE TABLE subway.hourly_avg_wait_time AS (
WITH
  calculate_wait_time AS (
    SELECT
      route_id,
      stop_id,
      any_value(stop_name) AS stop_name,
      any_value(stop_name_full) AS stop_name_full,
      arrival_time::DATE AS arrival_date,
      time_bucket('1 hour', arrival_time) as start_timestamp,
      INTERVAL '1 hour' AS period_length,
      
      list(arrival_time ORDER BY arrival_time) AS arrivals_in_period,
      first(next_arrival_time ORDER BY arrival_time DESC) AS next_arrival_after_period,
    FROM (
      SELECT * REPLACE (
        IF(next_arrival_time - arrival_time > INTERVAL '2 hour', NULL, next_arrival_time) AS next_arrival_time,
        IF(arrival_time - prev_arrival_time > INTERVAL '2 hour', NULL, prev_arrival_time) AS prev_arrival_time
      )
      FROM subway.route_stop_arrivals
    )
    GROUP BY ALL
  )
SELECT
  *,
  len(arrivals_in_period) AS num_arrivals,
  subway.average_wait_time_in_period(
    start_timestamp,
    start_timestamp + period_length,
    arrivals_in_period,
    next_arrival_after_period
  ) as avg_wait_time
FROM calculate_wait_time
);
