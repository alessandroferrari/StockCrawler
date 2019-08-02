
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.yahoo_finance.income_statement import parse_income_statement_per_yr
from data_parser.yahoo_finance.cash_flow import parse_cash_flow_statement_per_yr
from data_parser.yahoo_finance.common import get_statistics_url, parse_statistics_table
from data_parser.yahoo_finance.common import parse_financials_tables, get_urls_financials
from data_parser.common import get_page_html
from data_parser.yahoo_finance.common import CURRENT_YR, ONE_YR_AGO, TWO_YR_AGO, THREE_YR_AGO
from datetime import datetime
import numpy as np


def value_investing_on_fcf(expected_rate, fcf, outstanding_shares):
    estimated_price = fcf / (outstanding_shares * expected_rate)
    return estimated_price


def estimate_per_yr(data_income, data_cash, yr):

    results_income = parse_income_statement_per_yr(data_income, yr)
    results_cash = parse_cash_flow_statement_per_yr(data_cash, yr)
    fcf = results_cash["FCF"]

    interest_expense = results_income["Interest Expense"]
    interest_expense = max(abs(interest_expense), 0.0)
    if interest_expense>0.0:
        ratio = fcf / interest_expense
    else:
        ratio = 10000.0

    return fcf, ratio


def estimate(stock_name, expect_RoI=0.1):

    income_statement, balance_sheet, cash_flow = get_urls_financials(stock_name)

    html, _ = get_page_html(income_statement)
    data_income = parse_financials_tables(html)

    html, _ = get_page_html(cash_flow)
    data_cash = parse_financials_tables(html)

    fcfs = []
    ratios = []

    fcf_y1, ratio_y1 = estimate_per_yr(data_income, data_cash, CURRENT_YR)
    fcfs.append(fcf_y1)
    ratios.append(ratio_y1)

    try: #it may be a recent company
        fcf_y2, ratio_y2 = estimate_per_yr(data_income, data_cash, ONE_YR_AGO)
        fcfs.append(fcf_y2)
        ratios.append(ratio_y2)
    except:
        fcf_y2 = float('NaN')
        ratio_y2 = float('NaN')

    try:
        fcf_y3, ratio_y3 = estimate_per_yr(data_income, data_cash, TWO_YR_AGO)
        fcfs.append(fcf_y3)
        ratios.append(ratio_y3)
    except:
        fcf_y3 = float('NaN')
        ratio_y3 = float('NaN')

    try:
        fcf_y4, ratio_y4 = estimate_per_yr(data_income, data_cash, THREE_YR_AGO)
        fcfs.append(fcf_y4)
        ratios.append(ratio_y4)
    except:
        fcf_y4 = float('NaN')
        ratio_y4 = float('NaN')

    fcfs = np.array(fcfs)
    ratios = np.array(ratios)

    statistics_url = get_statistics_url(stock_name)
    html, _ = get_page_html(statistics_url)
    statistics = parse_statistics_table(html)

    outstanding_shares = statistics["shares outstanding"]

    pr_y1 = fcf_y1 / (expect_RoI * outstanding_shares)

    try:
        pr_y2 = fcf_y2 / (expect_RoI * outstanding_shares)
    except:
        pr_y2 = float('NaN')

    try:
        pr_y3 = fcf_y3 / (expect_RoI * outstanding_shares)
    except:
        pr_y3 = float('NaN')

    try:
        pr_y4 = fcf_y4 / (expect_RoI * outstanding_shares)
    except:
        pr_y4 = float('NaN')

    pr_avg = np.sum(fcfs) / (len(fcfs) * expect_RoI * outstanding_shares)

    results = {}
    results["Price Y1"] = pr_y1
    results["Price Y2"] = pr_y2
    results["Price Y3"] = pr_y3
    results["Price Y4"] = pr_y4
    results["Price Avg"] = pr_avg
    results["FCF / Interests Y1"] = ratio_y1
    results["FCF / Interests Y2"] = ratio_y2
    results["FCF / Interests Y3"] = ratio_y3
    results["FCF / Interests Y4"] = ratio_y4
    results["FCF / Interests Avg"] = np.sum(ratios) / len(ratios)

    results["Expected RoI"] = expect_RoI
    results["Market Cap"] = "{:.4f}B".format(statistics["market cap (intraday)"]/10**9)

    return results


def print_fcf_based_price_estimation(results):
    pr_avg = results["Price Avg"]
    pr_y1 = results["Price Y1"]
    ratio_y1 = results["FCF / Interests Y1"]
    pr_y2 = results["Price Y2"]
    ratio_y2 = results["FCF / Interests Y2"]
    pr_y3 = results["Price Y3"]
    ratio_y3 = results["FCF / Interests Y3"]
    pr_y4 = results["Price Y4"]
    ratio_y4 = results["FCF / Interests Y4"]
    expected_RoI = results["Expected RoI"]

    now = datetime.now()
    last_yr = now.year - 1

    print(
        "Yr {0}. Estimate Price from FCF at expected RoI of {1:.2f}%: {2:.3f}$. FCF / Interest ratio: {3:.4f}.".format(
          last_yr, expected_RoI * 100, pr_y1, ratio_y1))
    print(
        "Yr {0}. Estimate Price from FCF at expected RoI of {1:.2f}%: {2:.3f}$. FCF / Interest ratio: {3:.4f}.".format(
            last_yr-1, expected_RoI * 100, pr_y2, ratio_y2))
    print(
        "Yr {0}. Estimate Price from FCF at expected RoI of {1:.2f}%: {2:.3f}$. FCF / Interest ratio: {3:.4f}.".format(
            last_yr - 2, expected_RoI * 100, pr_y3, ratio_y3))
    print(
        "Yr {0}. Estimate Price from FCF at expected RoI of {1:.2f}%: {2:.3f}$. FCF / Interest ratio: {3:.4f}.".format(
            last_yr - 4, expected_RoI * 100, pr_y4, ratio_y4))
    print(
        "Avg from {2} to {3}. Estimate Price from FCF at expected RoI of {0:.3f}%%: {1:.3f}$. FCF / Interest ratio: {2:.4f}.".format(
            expected_RoI * 100, pr_avg, (ratio_y1 + ratio_y2 + ratio_y3 + ratio_y4) / 4.0, last_yr - 4, last_yr))


if __name__=="__main__":
    ticker = 'BRQS'
    RoI=0.065
    results = estimate(ticker, RoI)
    print_fcf_based_price_estimation(results)
