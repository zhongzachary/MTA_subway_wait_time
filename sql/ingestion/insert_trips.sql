INSERT INTO subway.trips_historic BY NAME
(
  SELECT 
    * REPLACE(
      -- the provided time stamps in local time (ET)
      -- since `to_timestamp` also return a timestamp with time zone, some resetting is needed
      to_timestamp(start_time)
        AT TIME ZONE 'GMT'
        AT TIME ZONE 'America/New_York' AS start_time,
      to_timestamp(last_observed) AS last_observed,
      to_timestamp(marked_past) AS marked_past,
    )
  FROM read_csv($file_name)
  QUALIFY 1 = row_number() OVER (
    PARTITION BY trip_uid
    ORDER BY last_observed DESC
  )
)
ON CONFLICT DO UPDATE
SET
  last_observed = greatest(trips_historic.last_observed, EXCLUDED.last_observed),
  marked_past = greatest(trips_historic.marked_past, EXCLUDED.marked_past)
;
