import duckdb

files = [
    "sql/definition/schema_subway_ref.sql",
    "sql/definition/schema_subway.sql",
    "sql/definition/table_trips_historic.sql",
    "sql/definition/table_stop_times_historic.sql",
    "sql/definition/index_trip_historic.sql",
    "sql/definition/index_stop_times_historic.sql",
]


def main():
    with duckdb.connect("data/mta.duckdb") as con:
        for file in files:
            with open(file) as f:
                print(f"Running {file}...")
                con.execute(f.read())


if __name__ == "__main__":
    main()
