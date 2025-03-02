import numpy as np
import pandas as pd


def calculate_arrival_distribution(hourly_avg_wait_time_obs: pd.DataFrame):
    assert len(hourly_avg_wait_time_obs["period_length"].unique()) == 1, (
        "Function doesn't support mixing multiple period length"
    )

    period_length: np.timedelta64 = hourly_avg_wait_time_obs["period_length"][0]
    num_of_observed_periods: int = len(hourly_avg_wait_time_obs)
    wait_time_ranges: np.ndarray[np.timedelta64] = np.stack(
        np.concat(hourly_avg_wait_time_obs["wait_time_ranges"])
    )

    # critical points (crit_pts) is the time where the CDF changes slope
    crit_pts = np.sort(np.unique(wait_time_ranges.flatten()))

    # count the number of time ranegs in (crit_pts[i-1], crit_pts[i]]
    is_crit_times_within_ranges = (wait_time_ranges[:, 0, None] < crit_pts[1:]) & (
        crit_pts[1:] <= wait_time_ranges[:, 1, None]
    )
    num_ranges_in_crit_times = is_crit_times_within_ranges.sum(axis=0)

    # build the probability density and cumulative distributin
    crit_pts_as_prop_of_period = crit_pts / period_length
    dt = np.diff(crit_pts_as_prop_of_period)
    # divided by num_of_observed_periods so that cdf normalized back to 1 in the end of time
    pdf = num_ranges_in_crit_times / num_of_observed_periods
    cdf = (dt * pdf).cumsum()

    return pd.DataFrame(
        dict(
            period_length=period_length,
            time=crit_pts,
            pdf=np.insert(pdf, 0, pdf[0]),
            cdf=np.insert(cdf, 0, 0)
        )
    )


def calculate_wait_time_at_prob(
    arrival_distribution: pd.DataFrame, prob: np.typing.ArrayLike
) -> np.typing.ArrayLike:
    period_length = arrival_distribution["period_length"][0]
    return (
        np.interp(
            x=prob, xp=arrival_distribution["cdf"], fp=arrival_distribution["time"] / period_length
        )
        * period_length
    )


def format_timedelta_hms(timedeltas: np.typing.ArrayLike) -> np.typing.ArrayLike:
    seconds = timedeltas.astype("timedelta64[ms]").astype(int).round(decimals=-3) // 1000

    hh = (seconds // 3600).astype(str)
    mm = ((seconds % 3600) // 60).astype(str)
    ss = (seconds % 60).astype(str)

    if seconds.ndim == 0:
        return hh + ":" + mm.zfill(2) + ":" + ss.zfill(2)
    else:
        return hh + ":" + np.strings.zfill(mm, 2) + ":" + np.strings.zfill(ss, 2)
