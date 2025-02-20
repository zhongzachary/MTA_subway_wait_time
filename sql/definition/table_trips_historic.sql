CREATE TABLE IF NOT EXISTS subway.trips_historic (
  trip_uid VARCHAR,
  trip_id VARCHAR,
  route_id VARCHAR,
  direction_id BIGINT,
  start_time TIMESTAMP WITH TIME ZONE,
  vehicle_id VARCHAR,
  last_observed TIMESTAMP WITH TIME ZONE,
  marked_past TIMESTAMP WITH TIME ZONE,
  num_updates BIGINT,
  num_schedule_changes BIGINT,
  num_schedule_rewrites BIGINT
);
