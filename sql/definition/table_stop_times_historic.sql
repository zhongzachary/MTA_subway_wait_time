CREATE TABLE IF NOT EXISTS subway.stop_times_historic (
  trip_uid VARCHAR,
  stop_id VARCHAR,
  track VARCHAR,
  arrival_time TIMESTAMP WITH TIME ZONE,
  departure_time TIMESTAMP WITH TIME ZONE,
  last_observed TIMESTAMP WITH TIME ZONE,
  marked_past TIMESTAMP WITH TIME ZONE
);
