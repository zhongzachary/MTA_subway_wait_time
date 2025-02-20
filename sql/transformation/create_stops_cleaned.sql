CREATE OR REPLACE TABLE subway_ref.stops_cleaned AS
SELECT
  stop_id,
  stop_name,
  any_value(stop_name)
    || ' [' 
    || string_agg(DISTINCT route_name_short, ',' ORDER BY route_name_short)
    || ']' AS stop_name_full,
  array_agg(DISTINCT route_id ORDER BY route_id) route_ids,
  any_value(direction_id) AS direction_id,
  array_agg(DISTINCT {
      'route_id': route_id,
      'services': services
    }
  ) AS route_details
FROM (
  SELECT DISTINCT
    route_id,
    regexp_replace(route_id, 'X$', '') AS route_name_short,
    direction_id,
    stop_id,
    array_agg(DISTINCT {
      'service_id': service_id,
      'trip_headsign': trip_headsign
    }) AS services
  FROM subway_ref.trips
  JOIN subway_ref.stop_times
    USING (trip_id)
  GROUP BY ALL
)
JOIN subway_ref.stops
  USING (stop_id)
GROUP BY ALL
ORDER BY 1;
