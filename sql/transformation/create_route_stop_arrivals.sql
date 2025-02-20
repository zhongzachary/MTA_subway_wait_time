-- creating a table containing the previous and next arrivals of a route at a stop
CREATE OR REPLACE TABLE subway.route_stop_arrivals AS
SELECT
  trips_historic.route_id,
  stop_times_historic.stop_id,
  trip_uid,
  trips_historic.trip_id,
  trips_historic.direction_id,
  trips_historic.start_time,
  stop_times_historic.track,
  stop_times_historic.arrival_time,
  stop_times_historic.departure_time,
  stop_times_historic.last_observed,
  stop_times_historic.marked_past,
  stops_cleaned.stop_name,
  stops_cleaned.stop_name_full,
  lag(stop_times_historic.arrival_time, 1) OVER route_stop_arrival AS prev_arrival_time,
  lead(stop_times_historic.arrival_time, 1) OVER route_stop_arrival AS next_arrival_time
FROM subway.stop_times_historic
JOIN subway.trips_historic
  USING (trip_uid)
JOIN subway_ref.stops_cleaned
  USING (stop_id)
WINDOW 
  route_stop_arrival AS (
    PARTITION BY route_id, stop_id
    ORDER BY arrival_time
    -- limit to ±2 hours. 
    -- any train arrives outside of the frame will not be considered as 
    RANGE BETWEEN INTERVAL 2 HOURS PRECEDING AND INTERVAL 2 HOURS FOLLOWING
  );
