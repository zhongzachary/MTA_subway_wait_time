# this script load ready to use data from https://subwaydata.nyc/programmatic-access
# when running the script, it will load from the last loaded date to the latest available date
# if data has not been loaded before, it will be loaded from 2024-01-01 (or customized it in the __main__ block)

import os
import duckdb
import shutil
import tarfile
import requests

from typing import Optional
from datetime import date, timedelta
from tqdm import tqdm

# %%
DuckDBPyConnection = duckdb.duckdb.DuckDBPyConnection


def _check_table_exists(con: DuckDBPyConnection, table_name: str, table_schema: str = "main"):
    result = con.query(
        "SELECT 1 FROM information_schema.tables WHERE table_name = $1 AND table_schema = $2",
        params=[table_name, table_schema],
    )
    return len(result) > 0


def _get_last_loaded_date(con: DuckDBPyConnection) -> Optional[date]:
    if not _check_table_exists(con, "trips_historic", "subway"):
        return None

    # file of a given date may have trip data until the next day's 5AM
    # hence subtracting 1 day
    sql = """SELECT
      max(start_time - INTERVAL '1 day')::DATE
    FROM subway.trips_historic
    """

    if row := con.query(sql).fetchone():
        return row[0]
    else:
        return None


# Define the date for the file
def _download_data(date: str) -> str:
    dir_name = f"data/subwaydatanyc_{date}_csv"
    file_name = f"{dir_name}.tar.xz"
    url = f"https://subwaydata.nyc/{file_name}"
    response = requests.get(url)
    response.raise_for_status()
    with open(file_name, "wb") as f:
        f.write(response.content)

    os.makedirs(dir_name, exist_ok=True)
    with tarfile.open(file_name, "r:xz") as tar:
        tar.extractall(path=dir_name)
    os.remove(file_name)

    return dir_name


def _insert_data_to_duck(con: DuckDBPyConnection, date: str) -> str:
    for data_name in ["trips", "stop_times"]:
        with open(f"sql/ingestion/insert_{data_name}.sql") as f:
            query = f.read()
        con.query(
            query,
            params=dict(file_name=f"data/subwaydatanyc_{date}_csv/subwaydatanyc_{date}_{data_name}.csv"),
        )


# %%
if __name__ == "__main__":
    with duckdb.connect("data/mta.duckdb") as con:
        start_date = (_get_last_loaded_date(con) or date(2023, 12, 31)) + timedelta(days=1)
        date_range = [
            (start_date + timedelta(days=days)).isoformat()
            for days in range((date.today() - start_date).days)
        ]

        status_bar = tqdm(date_range)
        for date in status_bar:
            status_bar.set_postfix_str(date)
            dir_name = _download_data(date)
            _insert_data_to_duck(con, date)
            shutil.rmtree(dir_name)

        con.close()
