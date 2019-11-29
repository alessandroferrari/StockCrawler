from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.morning_star.common import get_10yrs_data, FINANCIALS, EPS_ROW_TEMPLATE, PRICES_ROW_TEMPLATE, \
    PE_RATIO_ROW, GROWTH_ROW
from data_parser.yahoo_finance.common import get_stock_price_per_month
import pandas as pd
import numpy as np


def is_USD(financials_df):
    EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    return EPS_ROW in financials_df.index


def is_EUR(financials_df):
    EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    return EPS_ROW in financials_df.index

def is_INR(financials_df):
    EPS_ROW = EPS_ROW_TEMPLATE % "INR"
    return EPS_ROW in financials_df.index

def clean_outliers(df, confidence_interval=1.96):

    median = df.median()
    std = df.std()
    low = median - confidence_interval * std
    high = median + confidence_interval * std
    df_cleaned = df.copy()
    df_cleaned[df<low] = float('NaN')
    df_cleaned[df>high] = float('NaN')
    df_cleaned = df_cleaned.dropna()
    return df_cleaned


def get_historic_PE(ticker, data):

    financials_df = data[FINANCIALS]

    if is_USD(financials_df):
        PRICES_ROW = PRICES_ROW_TEMPLATE % "USD"
        EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    elif is_EUR(financials_df):
        PRICES_ROW = PRICES_ROW_TEMPLATE % "EUR"
        EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    elif is_INR(financials_df):
        PRICES_ROW = PRICES_ROW_TEMPLATE % "INR"
        EPS_ROW = EPS_ROW_TEMPLATE % "INR"
    else:
        raise Exception("Unknown currency while processing %s!"%ticker)

    prices = dict()
    for date in financials_df:
        year, month = date.split('-')
        price = get_stock_price_per_month(ticker, year, month)
        if not price:
            price = float("NaN")
        else:
            price = float(price)
        prices[date] = price
    prices_df = pd.DataFrame(prices, index=[PRICES_ROW])
    eps_df = financials_df.loc[EPS_ROW, :]
    pe_df = pd.DataFrame(prices_df / eps_df)
    pe_df = pe_df.rename(index={PRICES_ROW: PE_RATIO_ROW})
    data[FINANCIALS] = pd.concat([financials_df, prices_df, pe_df])


def get_historic_growth(data):
    financials_df = data[FINANCIALS]

    if is_USD(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    elif is_EUR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    elif is_INR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "INR"
    else:
        raise Exception("Unknown currency while processing %s!"%ticker)

    eps_df = financials_df.loc[EPS_ROW, :]
    growth = dict()
    is_first = True
    for date in financials_df:
        if is_first:
            growth[date] = float("NaN")
            eps0 = eps_df.loc[date]
            is_first = False
        else:
            eps1 = eps_df.loc[date]
            g = (eps1-eps0)/abs(eps0)
            growth[date] = g
            eps0 = eps1
    growth_df = pd.DataFrame(growth, index=[GROWTH_ROW])
    data[FINANCIALS] = pd.concat([financials_df, growth_df])


def compute_historic_PE(data, pe_bottom_cap=0.0, pe_top_cap=35.0, pe_factor=0.6, weight_data=True):

    financials_df = data[FINANCIALS]

    pe_df = financials_df.loc[PE_RATIO_ROW]
    # do not modify original values with capping and drop NaN, exclude them from AVG
    pe_df_capped = pe_df.copy().dropna()
    #pe_df_capped = clean_outliers(pe_df_capped)
    num_yrs = pe_df_capped.shape[0]
    if weight_data:
        weights = np.exp(-np.arange(num_yrs)[::-1]/(2*float(num_yrs)))
        weights /= np.sum(weights)
    else:
        weights = np.ones(num_yrs)/num_yrs
    pe_avg = (pe_df_capped * weights).sum()
    pe_avg_capped = pe_avg
    if not pe_bottom_cap is None:
        if pe_avg < pe_bottom_cap:
            pe_avg_capped = pe_bottom_cap
    if not pe_top_cap is None:
        if pe_avg > pe_top_cap:
            pe_avg_capped = pe_top_cap
    if not pe_factor is None:
        pe_avg_capped *= pe_factor

    return pe_avg, pe_avg_capped


def compute_historic_growth(data, growth_bottom_cap=0.0, growth_top_cap=0.15, growth_factor=0.6, weight_data=True):

    financials_df = data[FINANCIALS]

    growth_df = financials_df.loc[GROWTH_ROW]

    growth_df = growth_df.dropna()
    num_y = growth_df.shape[0]
    if weight_data:
        weights = np.exp(-np.arange(num_y)[::-1]/(2*float(num_y)))
        weights /= np.sum(weights)
    else:
        weights = np.ones(num_y) / num_y
    growth_avg = (growth_df * weights).sum()
    growth_avg_capped = growth_avg
    if not growth_bottom_cap is None:
        if growth_avg < growth_bottom_cap:
            growth_avg_capped = growth_bottom_cap
    if not growth_top_cap is None:
        if growth_avg > growth_top_cap:
            growth_avg_capped = growth_top_cap
    if not growth_factor is None:
        growth_avg_capped *= growth_factor

    return growth_avg, growth_avg_capped


def compute_historic_eps(data, eps_bottom_cap=0.0, weight_data=True):

    financials_df = data[FINANCIALS]

    if is_USD(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    elif is_EUR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    elif is_INR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "INR"
    else:
        raise Exception("Unknown currency while processing!")

    eps_df = financials_df.loc[EPS_ROW]
    eps_df_capped = eps_df.copy().dropna()
    #eps_df_capped = clean_outliers(eps_df_capped)
    num_y = eps_df_capped.shape[0]
    if weight_data:
        weights = np.exp(-np.arange(num_y)[::-1]/(2*float(num_y)))
        weights /= np.sum(weights)
    else:
        weights = np.ones(num_y)/num_y
    eps_avg = (eps_df_capped * weights).sum()
    eps_avg_capped = eps_avg
    if not eps_bottom_cap is None:
        if eps_avg < eps_bottom_cap:
            eps_avg_capped = eps_bottom_cap

    return eps_avg, eps_avg_capped


def EPS_forecast_based_on_history(eps_avg, growth_avg, yrs_num=5):

    pv = eps_avg
    future_values = {}
    for i in range(1, yrs_num+1):
        fv = pv * (1.0 + growth_avg)
        future_values[i] = fv
        pv = fv

    return pd.DataFrame(future_values, index=["EPS Forecast based on History"])