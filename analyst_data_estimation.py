from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd


def compute_eps_estimate_from_analysts(earnings_estimate, uncertainty_per_year=0.75, uncertainty_bottom_cap=0.6):

    df = earnings_estimate["growth estimates"]
    current_yr = df.loc["current year"][0]
    next_yr = df.loc["next year"][0]
    next_5yrs = df.loc["next 5 years (per annum)"][0]
    third2fith_yr = (next_5yrs * 5.0 - current_yr - next_yr) / 3.0

    df = earnings_estimate["earnings estimate"]
    CURRENT_YR_EPS_FORECAST = 2
    NEXT_YR_EPS_FORECAST = 3
    eps_current_yr_low = df.loc["low estimate"][CURRENT_YR_EPS_FORECAST]
    eps_current_yr_high = df.loc["high estimate"][CURRENT_YR_EPS_FORECAST]
    eps_next_yr_low = df.loc["low estimate"][NEXT_YR_EPS_FORECAST]
    eps_next_yr_high = df.loc["high estimate"][NEXT_YR_EPS_FORECAST]
    eps_current_yr_avg = df.loc["avg. estimate"][CURRENT_YR_EPS_FORECAST]
    eps_next_yr_avg = df.loc["avg. estimate"][NEXT_YR_EPS_FORECAST]

    earnings_estimate["EPS Forecast Low"] = pd.DataFrame({1: eps_current_yr_low, 2: eps_next_yr_low,
                                                          3: eps_next_yr_low * (1 + third2fith_yr),
                                                          4: eps_next_yr_low * (1 + third2fith_yr)**2,
                                                          5: eps_next_yr_low * (1 + third2fith_yr) ** 3},
                                                         index=["EPS Low Forecast"])
    earnings_estimate["EPS Forecast High"] = pd.DataFrame({1: eps_current_yr_high, 2: eps_next_yr_high,
                                                          3: eps_next_yr_high * (1 + third2fith_yr),
                                                          4: eps_next_yr_high * (1 + third2fith_yr)**2,
                                                          5: eps_next_yr_high * (1 + third2fith_yr) ** 3},
                                                          index=["EPS High Forecast"])
    earnings_estimate["EPS Forecast Avg"] = pd.DataFrame({1: eps_current_yr_avg, 2: eps_next_yr_avg,
                                                          3: eps_next_yr_avg * (1 + third2fith_yr),
                                                          4: eps_next_yr_avg * (1 + third2fith_yr)**2,
                                                          5: eps_next_yr_avg * (1 + third2fith_yr) ** 3},
                                                          index=["EPS Avg Forecast"])
    adj_df = pd.DataFrame({1: max(uncertainty_per_year, uncertainty_bottom_cap),
                           2: max(uncertainty_per_year**2, uncertainty_bottom_cap),
                           3: max(uncertainty_per_year**3, uncertainty_bottom_cap),
                           4: max(uncertainty_per_year**4, uncertainty_bottom_cap),
                           5: max(uncertainty_per_year**2, uncertainty_bottom_cap)}, index=["Adjusting Factor"])

    df = earnings_estimate["EPS Forecast Low"]
    earnings_estimate["EPS Forecast Low Adj"] = pd.DataFrame(df.values * adj_df.values, columns=df.columns, index=df.index)
    df = earnings_estimate["EPS Forecast High"]
    earnings_estimate["EPS Forecast High Adj"] = pd.DataFrame(df.values * adj_df.values, columns=df.columns, index=df.index)
    df = earnings_estimate["EPS Forecast Avg"]
    earnings_estimate["EPS Forecast Avg Adj"] = pd.DataFrame(df.values * adj_df.values, columns=df.columns, index=df.index)
