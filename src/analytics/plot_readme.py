# %%
import numpy as np
import pandas as pd
import plotnine as pn
from src.analytics.common import (
    calculate_arrival_distribution,
    format_timedelta_hms
)

# %%
def plot_wait_times(period_length: np.timedelta64, arrivals: np.typing.ArrayLike):
    wait_times = create_wait_times(period_length, arrivals)
    avg_wait_time = calculate_avg_wait_times(period_length, arrivals)
    return (
        pn.ggplot(wait_times, pn.aes(x="time", y="wait_time"))
        + pn.geom_area(data=wait_times.query("in_period"), fill="#dddddd", color="#000000")
        + pn.geom_line(data=wait_times.query("~in_period"), linetype="dashed")
        + pn.geom_vline(xintercept=period_length, linetype="dashed")
        + pn.geom_hline(yintercept=avg_wait_time, linetype="dotted")
        + pn.geom_text(
            x=period_length,
            y=avg_wait_time + np.timedelta64(2, "m"),
            label="avg. wait time\n" + format_timedelta_hms(avg_wait_time)[-5:],
        )
        + pn.coord_equal()
        + pn.theme_xkcd()
    )


def create_wait_times(period_length: np.timedelta64, arrivals: np.typing.ArrayLike) -> pd.DataFrame:
    wait_time_range_starts = pd.DataFrame(
        dict(time=np.insert(arrivals[:-1], 0, 0), wait_time=np.diff(arrivals, prepend=0))
    )
    wait_time_range_ends = pd.DataFrame(dict(time=arrivals, wait_time=np.timedelta64(0, "m")))

    wait_times = pd.concat([wait_time_range_starts, wait_time_range_ends])
    wait_times["in_period"] = wait_times["time"] <= period_length

    if arrivals[-1] > period_length:
        wait_time_at_boundery = pd.DataFrame(
            dict(
                time=period_length, wait_time=arrivals[-1] - period_length, in_period=[True, False]
            )
        )
        wait_times = pd.concat([wait_times, wait_time_at_boundery])

    return wait_times.sort_values(["time", "wait_time", "in_period"], ascending=[True, True, False])


def create_wait_time_ranges(
    period_length: np.timedelta64, arrivals: np.typing.ArrayLike
) -> pd.DataFrame:
    range_df = pd.DataFrame(
        {
            "period_length": [period_length],
            "wait_time_ranges": [
                np.stack([arrivals - np.minimum(60, arrivals), np.diff(arrivals, prepend=0)]).T
            ],
        }
    )
    return range_df


def calculate_avg_wait_times(
    period_length: np.timedelta64, arrivals: np.typing.ArrayLike
) -> np.timedelta64:
    total_wait_time = sum((np.diff(arrivals, prepend=0) / period_length) ** 2 / 2)

    if arrivals[-1] > period_length:
        after_period_adj = ((arrivals[-1] - period_length) / period_length) ** 2 / 2
        total_wait_time -= after_period_adj

    avg_wait_time = total_wait_time * period_length.astype("timedelta64[ms]")

    return avg_wait_time




# %%
if __name__ == "__main__":
    period_length = np.timedelta64(1, "h")
    even_arrivals = np.array([5, 20, 35, 50, 65], "timedelta64[m]")
    even_plot = plot_wait_times(period_length, even_arrivals)
    even_plot.show()


    uneven_arrivals = np.array([5, 20, 46, 50, 65], "timedelta64[m]")
    uneven_plot = plot_wait_times(period_length, uneven_arrivals)
    uneven_plot.show()


    even_distribution = calculate_arrival_distribution(create_wait_time_ranges(period_length, even_arrivals))
    even_distribution['train'] = 'even'

    uneven_distribution = calculate_arrival_distribution(create_wait_time_ranges(period_length, uneven_arrivals))
    uneven_distribution['train'] = 'uneven'

    combined_distributions = pd.concat([even_distribution, uneven_distribution])

    cdf = (
        pn.ggplot(combined_distributions, pn.aes(x="cdf", y="time", color="train"))
        + pn.geom_line()
        + pn.theme_xkcd()
    )
    cdf.show()


# %%
