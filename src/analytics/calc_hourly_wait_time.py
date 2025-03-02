import duckdb


files = [
    "sql/macro/average_wait_time_in_period.sql",
    "sql/transformation/create_route_stop_arrivals.sql",
    "sql/transformation/create_hourly_avg_wait_time.sql",
]


def main():
    with duckdb.connect("data/mta.duckdb") as con:
        for file in files:
            with open(file) as f:
                print(f"Running {file}...")
                con.execute(f.read())


if __name__ == "__main__":
    main()
