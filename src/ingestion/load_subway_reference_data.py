# this script read the static GTFS data feeds from https://www.mta.info/developers
# here we mostly concern with the stops and routes tables

import os
import shutil
import requests
import duckdb


def load_subway_reference_data(con: duckdb.DuckDBPyConnection):
    print("Downloading reference files from MTA...")
    url = "https://rrgtfsfeeds.s3.amazonaws.com/gtfs_subway.zip"
    resp = requests.get(url)
    resp.raise_for_status()

    zip_file = "data/gtfs_subway.zip"
    with open(zip_file, "wb") as f:
        f.write(resp.content)

    print("Extracting reference files...")
    dir_name = "data/gtfs_subway"
    shutil.unpack_archive(zip_file, dir_name)
    os.remove(zip_file)

    print("Loading data into duckdb...")
    schema = "subway_ref"
    for data in ["routes", "stops", "shapes", "trips", "stop_times"]:
        create_sql = f"""CREATE OR REPLACE TABLE {schema}.{data} AS
        FROM read_csv('{dir_name}/{data}.txt')
        """
        con.execute(create_sql)

    print("Cleaning up downloaded files...")
    shutil.rmtree(dir_name)


def create_stops_cleaned_table(con: duckdb.DuckDBPyConnection):
    print("Creating table stops_cleaned...")
    with open("sql/transformation/create_stops_cleaned.sql") as f:
        query = f.read()

    con.execute(query)


if __name__ == "__main__":
    with duckdb.connect("data/mta.duckdb") as con:
        load_subway_reference_data(con)
        create_stops_cleaned_table(con)
