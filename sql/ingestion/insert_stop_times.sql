INSERT INTO subway.stop_times_historic BY NAME
(
  SELECT 
    * REPLACE(
      to_timestamp(arrival_time) AS arrival_time,
      to_timestamp(departure_time) AS departure_time,
      to_timestamp(last_observed) AS last_observed,
      to_timestamp(marked_past) AS marked_past,
    )
  FROM read_csv($file_name)
  QUALIFY 1 = row_number() OVER (
    PARTITION BY trip_uid, stop_id
    ORDER BY arrival_time DESC
  )
)
ON CONFLICT DO UPDATE
SET
  arrival_time = greatest(stop_times_historic.arrival_time, EXCLUDED.arrival_time),
  departure_time = greatest(stop_times_historic.departure_time, EXCLUDED.departure_time),
  last_observed = greatest(stop_times_historic.last_observed, EXCLUDED.last_observed),
  marked_past = greatest(stop_times_historic.marked_past, EXCLUDED.marked_past)
;

