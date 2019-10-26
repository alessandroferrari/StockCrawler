#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.morning_star.common import get_10yrs_data, FINANCIALS, PE_RATIO_ROW, EPS_ROW_TEMPLATE, GROWTH_ROW
from data_parser.yahoo_finance.common import get_stock_price_per_month
from historic_data_estimation import get_historic_PE, get_historic_growth, compute_historic_PE, compute_historic_eps,\
    compute_historic_growth, is_USD, is_EUR
from dcf_estimation import dcf_price_estimation_from_historical_data, dcf_price_estimation_from_analysts
from data_parser.yahoo_finance.price_estimation import estimate as estimate_fcf
from data_parser.common import get_page_html

import argparse
import datetime
import logging
import logging.config
import math
import os
from shutil import copyfile
import sys
import traceback
import time


def formatted_results(ticker, name, results, eps_avg, eps_avg_capped, pe_avg, pe_avg_capped, growth_avg, growth_avg_capped,
                      price_historical, price_analysts_avg, price_analysts_low, price_analysts_high, price_analysts_adj,
                      price_fcf_avg, price_fcf_last_yr, market_cap, debt_ratio_avg, debt_ratio_y1, price):

    financials_df = results[FINANCIALS]

    if is_USD(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    elif is_EUR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    else:
        raise Exception("Unknown currency while processing %s!"%ticker)
    eps_df = financials_df.loc[EPS_ROW]

    pe_df = financials_df.loc[PE_RATIO_ROW]

    growth_df = financials_df.loc[GROWTH_ROW]

    header_ticker = "Ticker,Name"
    content_ticker = "%s,%s"%(ticker, name)
    header = header_ticker
    content = content_ticker

    header = "{0},{1}".format(header, "Market Cap")
    content = "{0},{1}".format(content, market_cap)

    for date in eps_df.index.values:
        col = "EPS {0}".format(date)
        header = "{0},{1}".format(header, col)
        content = "{0},{1:.4f}".format(content, eps_df.loc[date])

    header = "{0},{1}".format(header, "Avg EPS")
    content = "{0},{1:.4f}".format(content, eps_avg)

    header = "{0},{1}".format(header, "Avg EPS Capped")
    content = "{0},{1:.4f}".format(content, eps_avg_capped)

    header = "{0},{1}".format(header, header_ticker)
    content = "{0},{1}".format(content, content_ticker)

    for date in pe_df.index.values:
        col = "PE {0}".format(date)
        header = "{0},{1}".format(header, col)
        content = "{0},{1:.4f}".format(content, pe_df.loc[date])

    header = "{0},{1}".format(header, "Avg PE")
    content = "{0},{1:.4f}".format(content, pe_avg)

    header = "{0},{1}".format(header, "Avg PE Capped")
    content = "{0},{1:.4f}".format(content, pe_avg_capped)

    header = "{0},{1}".format(header, header_ticker)
    content = "{0},{1}".format(content, content_ticker)

    for date in growth_df.index.values:
        col = "Growth {0}".format(date)
        header = "{0},{1}".format(header, col)
        content = "{0},{1:.4f}".format(content, growth_df.loc[date])

    header = "{0},{1}".format(header, "Avg Growth")
    content = "{0},{1:.4f}".format(content, growth_avg)

    header = "{0},{1}".format(header, "Avg Growth Capped")
    content = "{0},{1:.4f}".format(content, growth_avg_capped)

    header = "{0},{1}".format(header, header_ticker)
    content = "{0},{1}".format(content, content_ticker)

    header = "{0},{1}".format(header, "Current Price")
    content = "{0},{1:.4f}".format(content, price)

    header = "{0},{1}".format(header, "Price FCF")
    content = "{0},{1:.4f}".format(content, price_fcf_avg)

    header = "{0},{1}".format(header, "Price Last Yr")
    content = "{0},{1:.4f}".format(content, price_fcf_last_yr)

    header = "{0},{1}".format(header, "Price Historical")
    content = "{0},{1:.4f}".format(content, price_historical)

    header = "{0},{1}".format(header, "Price Analysts Avg")
    content = "{0},{1:.4f}".format(content, price_analysts_avg)

    header = "{0},{1}".format(header, "Price Analysts Low")
    content = "{0},{1:.4f}".format(content, price_analysts_low)

    header = "{0},{1}".format(header, "Price Analysts High")
    content = "{0},{1:.4f}".format(content, price_analysts_high)

    header = "{0},{1}".format(header, "Price Analysts Adj")
    content = "{0},{1:.4f}".format(content, price_analysts_adj)

    header = "{0},{1}".format(header, header_ticker)
    content = "{0},{1}".format(content, content_ticker)

    margin_fcf_avg = (price_fcf_avg - price) / price
    header = "{0},{1}".format(header, "Margin FCF Avg")
    content = "{0},{1:.4f}".format(content, margin_fcf_avg)

    margin_fcf_last_yr = (price_fcf_last_yr - price) / price
    header = "{0},{1}".format(header, "Margin FCF Last Yr")
    content = "{0},{1:.4f}".format(content, margin_fcf_last_yr)

    margin_historical = (price_historical - price) / price
    header = "{0},{1}".format(header, "Margin Historical")
    content = "{0},{1:.4f}".format(content, margin_historical)

    margin_analysts_avg = (price_analysts_avg - price)/price
    header = "{0},{1}".format(header, "Margin Analysts Avg")
    content = "{0},{1:.4f}".format(content, margin_analysts_avg)

    margin_analysts_low = (price_analysts_low - price)/price
    header = "{0},{1}".format(header, "Margin Analysts Low")
    content = "{0},{1:.4f}".format(content, margin_analysts_low)

    margin_analysts_high = (price_analysts_high - price)/price
    header = "{0},{1}".format(header, "Margin Analysts High")
    content = "{0},{1:.4f}".format(content, margin_analysts_high)

    header = "{0},{1}".format(header, "Margin Analysts Adj")
    content = "{0},{1:.4f}".format(content, (price - price_analysts_adj)/price)

    header = "{0},{1}".format(header, header_ticker)
    content = "{0},{1}".format(content, content_ticker)

    header = "{0},{1}".format(header, "FCF / Interests Avg")
    content = "{0},{1:.4f}".format(content, debt_ratio_avg)

    header = "{0},{1}".format(header, "FCF / Interests Last Yr")
    content = "{0},{1:.4f}".format(content, debt_ratio_y1)

    return header, content


def get_EPS_ROW(results, ticker):
    # check if recent data, other skip
    financials_df = results[FINANCIALS]
    if is_USD(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "USD"
    elif is_EUR(financials_df):
        EPS_ROW = EPS_ROW_TEMPLATE % "EUR"
    else:
        raise Exception("Unknown currency while processing %s!" % ticker)
    return EPS_ROW


def is_recent(results, ticker):
    # check if recent data, other skip
    financials_df = results[FINANCIALS]
    EPS_ROW = get_EPS_ROW(results, ticker)
    pe_df = financials_df.loc[EPS_ROW]
    date = pe_df.index.values[-2]
    year = int(date.split('-')[0])
    now = datetime.datetime.now()
    if year < now.year - 2:
        raise Exception("There are not recent data available for %s, last data: %s" % (ticker, date))


def process_stock(ticker, name, force_growth = None,
                    force_eps = None, force_pe = None):

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    try:
        logger.debug("%s|Processing %s ..." % (ticker, ticker))

        now = datetime.datetime.now()
        price = get_stock_price_per_month(ticker, now.year, now.month)
        if math.isnan(price):
            if now.month > 1:
                price = get_stock_price_per_month(ticker, now.year, now.month - 1)
            else:
                price = get_stock_price_per_month(ticker, now.year - 1, 12)

        logger.debug("{0}|Current price: {1:.4f}".format(ticker, price))

        attempts = 0
        while True:
            try:
                results = get_10yrs_data(ticker)
                get_EPS_ROW(results, ticker)
                break
            except:
                attempts += 1
                time.sleep(5)
                if attempts>5:
                    tb = traceback.format_exc()
                    logger.error("{0}|Error while scraping Morning Star: {1}".format(ticker, tb))
                    raise Exception("Invalid MorningStar data!")

        is_recent(results, ticker)

        get_historic_PE(ticker, results)
        get_historic_growth(results)

        pe_avg, pe_avg_capped = compute_historic_PE(results, pe_bottom_cap=-10.0, pe_top_cap=35.0, pe_factor=0.6,
                                                    weight_data=False)
        growth_avg, growth_avg_capped = compute_historic_growth(results, growth_bottom_cap=-0.15, growth_top_cap=0.15,
                                                                growth_factor=0.6, weight_data=False)
        eps_avg, eps_avg_capped = compute_historic_eps(results, eps_bottom_cap=0.0, weight_data=False)

        if force_growth:
            growth_avg_capped = force_growth
        
        if force_eps:
            eps_avg_capped = force_eps
        
        if force_pe:
            pe_avg_capped = force_pe

        price_forecast_from_history = \
            dcf_price_estimation_from_historical_data(ticker, eps_avg=eps_avg_capped, growth_avg=growth_avg_capped,
                                                      pe_avg=pe_avg_capped, num_yrs_forecast=5, discount_rate=0.015)

        logger.debug(
            "{4}|Price Forecast based on History: {0:.4f}. PE Avg: {1:.4f}. Growth Avg: {2:.4f}. EPS Avg: {3:.4f}.".format(
                price_forecast_from_history, pe_avg, growth_avg, eps_avg, ticker))

        try:
            price_forecast_from_analyst_avg, price_forecast_from_analyst_low, price_forecast_from_analyst_high, \
            price_forecast_from_analyst_avg_adj = dcf_price_estimation_from_analysts(ticker, expected_pe=pe_avg_capped,
                                                                                     discount_rate=0.015,
                                                                                     safety_margin_y1=0.25,
                                                                                     safety_margin_long_term=0.4)

            logger.debug("{4}|From analyst estimates, Avg: {0:.4f}, Low: {1:.4f}, High: {2:.4f}, Avg Adj: {3:.4f}".format
                  (price_forecast_from_analyst_avg, price_forecast_from_analyst_low, price_forecast_from_analyst_high,
                   price_forecast_from_analyst_avg_adj, ticker))

        except Exception:
            tb = traceback.format_exc()
            logger.error("%s|Error while processing analysts estimation %s: %s" % (ticker, ticker, tb))
            price_forecast_from_analyst_avg = float("NaN")
            price_forecast_from_analyst_low = float("NaN")
            price_forecast_from_analyst_high = float("NaN")
            price_forecast_from_analyst_avg_adj = float("NaN")

        try:
            expected_RoI = 0.1
            results_fcf = estimate_fcf(ticker, expect_RoI=expected_RoI) #10% a year
            price_fcf_avg = results_fcf["Price Avg"]
            price_fcf_last_yr = results_fcf["Price Y1"]
            market_cap = results_fcf["Market Cap"]
            debt_ratio_y1 = results_fcf["FCF / Interests Y1"]
            debt_ratio_avg = results_fcf["FCF / Interests Avg"]

            logger.debug("{3}|Last Year Estimate Price from FCF at expected RoI of {0:.2f}%: {1:.3f}$. FCF / Interest ratio: {2:.4f}.".format(
                    expected_RoI * 100, price_fcf_last_yr, debt_ratio_y1, ticker))
            logger.debug(
                "{3}|Avg Estimate Price from FCF at expected RoI of {0:.3f}%%: {1:.3f}$. FCF / Interest ratio: {2:.4f}.".format(
                    expected_RoI * 100, price_fcf_avg, debt_ratio_avg, ticker))
        except Exception:
            tb = traceback.format_exc()
            logger.error("%s|Error while processing FCF estimation %s: %s" % (ticker, ticker, tb))
            traceback.print_exc(file=sys.stdout)
            price_fcf_avg = float("NaN")
            price_fcf_last_yr = float("NaN")
            market_cap = float("NaN")
            debt_ratio_y1 = float("NaN")
            debt_ratio_avg = float("NaN")

        header, content = formatted_results(ticker, name, results, eps_avg, eps_avg_capped, pe_avg, pe_avg_capped, growth_avg,
                                            growth_avg_capped, price_historical=price_forecast_from_history,
                                            price_analysts_avg=price_forecast_from_analyst_avg,
                                            price_analysts_low=price_forecast_from_analyst_low,
                                            price_analysts_high=price_forecast_from_analyst_high,
                                            price_analysts_adj=price_forecast_from_analyst_avg_adj,
                                            price_fcf_avg=price_fcf_avg, price_fcf_last_yr=price_fcf_last_yr,
                                            market_cap=market_cap, debt_ratio_avg=debt_ratio_avg,
                                            debt_ratio_y1=debt_ratio_y1, price=price)

        save_results(header, content)

    except Exception:
        tb = traceback.format_exc()
        logger.error("%s|Error while processing %s: %s"%(ticker, ticker, tb))
        header, content = None, None

    return header, content

def save_results(header, content):

    out_fn = os.path.join(os.path.expanduser("~/Desktop"), "quantitave_%s" % os.path.basename(stocks_list_fn))
    is_first =  not os.path.exists(out_fn)
    f = open(out_fn, "a+")
    if not header is None and is_first:
        header = header.replace(",", "|")
        f.write("%s\n"%header)
    content = "%s\n" % content
    content = content.replace(",", "|")
    f.write(content)
    f.close()
    backup_fn = os.path.join(os.path.expanduser("~/Desktop"), "bckp_quantitave_%s" % os.path.basename(stocks_list_fn))
    copyfile(out_fn, backup_fn)

def get_last_ticker(resume_fn):
    if not os.path.exists(resume_fn):
        print("Specified resume path does not exists: %s" % resume_fn)
        sys.exit()
    f = open(resume_fn)
    ticker = None
    while True:
        s = f.readline()
        if s=='':
            break
        ticker = s.split("|")[0]
    if ticker=="Ticker" or ticker is None:
        print("Found invalid ticker to resume from: %s"%ticker)
        sys.exit()
    return ticker

if __name__=='__main__':

    logging.config.fileConfig("logging.conf")

    parser = argparse.ArgumentParser(description='Search for value stocks.')
    parser.add_argument('stocks_list_fn', type=str, help='File including tickers and stock names.')
    parser.add_argument('--resume', type=str, help='File from previous scrape.')
    parser.add_argument('--force_growth', type=float, help='Force growth to a certain value')
    parser.add_argument('--force_eps', type=float, help='Force EPS to a certain value')
    parser.add_argument('--force_pe', type=float, help='Force PE to a certain value')

    args = parser.parse_args()

    stocks_list_fn = args.stocks_list_fn
    if not os.path.exists(stocks_list_fn):
        print("Input stocks file list does not exists: %s" % stocks_list_fn)
        sys.exit()

    resume_fn = args.resume
    if not resume_fn is None:
        ticker_resume = get_last_ticker(resume_fn)
    else:
        ticker_resume = None

    start_adding = False

    stocks_list = []
    f = open(stocks_list_fn)
    s = f.readline() #supposedly the header
    while True:
        s = f.readline()
        if s=="":
            break
        s = s.replace("\n","")
        ticker, name = s.split("\t")
        if ticker_resume:
            if start_adding:
                stocks_list.append((ticker, name))
            if ticker == ticker_resume:
                start_adding = True
        else:
            stocks_list.append((ticker, name))
    f.close()

    results = []
    for ticker, name in stocks_list:
        res = process_stock(ticker, name, 
                            force_growth = args.force_growth,
                            force_eps = args.force_eps,
                            force_pe = args.force_pe)
        results.append(res)













