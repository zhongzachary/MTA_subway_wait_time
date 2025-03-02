# %%
import duckdb
import plotnine as pn
import pandas as pd
from src.analytics.common import (
    calculate_arrival_distribution,
    calculate_wait_time_at_prob,
    format_timedelta_hms
)



# %%
con = duckdb.connect("data/mta.duckdb")

# %%
q_train = con.query("""
select *
from subway.hourly_avg_wait_time
where route_id = 'Q'
    and stop_id = 'D35N'
    and date_part('hour', start_timestamp) = 8
    and date_part('dow',  start_timestamp) not in (0, 6)
""").df()

q_arrivals = calculate_arrival_distribution(q_train)
q_arrivals.insert(0, "train", "Q")
q_wait_time_iqr = calculate_wait_time_at_prob(q_arrivals, [0.25, 0.5, 0.75])
print(format_timedelta_hms(q_wait_time_iqr))

# %%
n_train = con.query("""
select *
from subway.hourly_avg_wait_time
where route_id = 'N'
    and stop_id = 'N08N'
    and date_part('hour', start_timestamp) = 8
    and date_part('dow',  start_timestamp) not in (0, 6)
""").df()
n_arrivals = calculate_arrival_distribution(n_train)
n_arrivals.insert(0, "train", "N")
n_wait_time_iqr = calculate_wait_time_at_prob(n_arrivals, [0.25, 0.5, 0.75])
print(format_timedelta_hms(n_wait_time_iqr))

# %%
arrivals = pd.concat([
    q_arrivals, 
    n_arrivals
])
iqr = pd.concat(
    [
        pd.DataFrame(
            {
                "train": "Q",
                "cdf": [0.25, 0.5, 0.75],
                "time": q_wait_time_iqr,
                "label": format_timedelta_hms(q_wait_time_iqr),
            }
        ),
        pd.DataFrame(
            {
                "train": "N",
                "cdf": [0.25, 0.5, 0.75],
                "time": n_wait_time_iqr,
                "label": format_timedelta_hms(n_wait_time_iqr),
            }
        ),
    ]
)

# %%
(
    pn.ggplot(arrivals.query("0.05 < cdf < 0.95"), pn.aes(x="cdf", y="time", color="train"))
    + pn.geom_line()
    + pn.geom_text(data=iqr, mapping=pn.aes(label="label"), alpha=0.75)
    + pn.theme_xkcd()
)

