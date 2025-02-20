-- since trips from the following day will update unfinished trips from previous day
-- an index is helpful for ingesting data (even after considering its performance impact)
CREATE UNIQUE INDEX IF NOT EXISTS trips_historic_trip_uid
ON subway.trips_historic (trip_uid);
