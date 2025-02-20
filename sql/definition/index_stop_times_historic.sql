CREATE UNIQUE INDEX IF NOT EXISTS stop_times_historic_trip_uid_stop_id
ON subway.stop_times_historic (trip_uid, stop_id);
