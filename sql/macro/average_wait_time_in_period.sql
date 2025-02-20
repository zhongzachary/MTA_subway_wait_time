CREATE OR REPLACE MACRO subway.average_wait_time_in_period
  -- Calculate the average wait time during a period with the given arrivals and next arrival after the period
  -- Parameters:
  --   start_timestamp TIMESTAMP[TZ]:           start time of the period
  --   end_timestamp TIMESTAMP[TZ]:             end time of the period, must be greater than start_timestamp
  --   arrivals_in_period LIST<TIMESTAMP[TZ]>:  arrival times during the period, must be sorted in ascending order
  --   next_after_after_period TIMESTAMP[TZ]:   the next arrival after the period, NULL if there is no more arrival
  -- Returns: INTERVAL
  (start_timestamp, end_timestamp, arrivals_in_period, next_after_after_period) AS (
  to_seconds(
    (
      (
        SELECT sum(epoch(unnest[2] - unnest[1]) ** 2 / 2)
        FROM unnest(list_zip(
          list_prepend(start_timestamp, arrivals_in_period),
          list_append(arrivals_in_period, next_arrival_after_period)
        ))
      )
      - if(next_arrival_after_period IS NULL,
        0, 
        epoch(next_arrival_after_period - end_timestamp) ** 2 / 2
      )
    )
    / if(next_arrival_after_period IS NULL,
      nullif(epoch(list_max(arrivals_in_period) - start_timestamp), 0),
      epoch(end_timestamp - start_timestamp)
    )
  )
);
