
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
import os
sys.path.insert(0, '/usr/lib/python3/dist-packages')
sys.path.insert(0, os.path.expanduser("/usr/local/lib/python3.5/dist-packages"))
sys.path.insert(0, os.path.expanduser("~/PycharmProjects/StockScraping/"))

import csv
import re

try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import datetime
import pandas as pd
from selenium import webdriver

KEYRATIO_URL = "http://financials.morningstar.com/ratios/r.html?t=%s"

FINANCIALS = "Financials"
MARGIN_OF_SALES = "Margins % of Sales"
PROFITABILITY = "Profitability"
REVENUE = "Revenue %"
OPERATING_INCOME = "Operating Income %"
NET_INCOME = "Net Income %"
EPS = "EPS %"
CASH_FLOW_RATIO = "Cash Flow Ratios"
FINANCIAL_HEALTH = "Balance Sheet Items (in %)"
LIQUIDITY = "Liquidity/Financial Health"
EFFICIENCY = "Efficiency"

EPS_ROW_TEMPLATE = "Earnings Per Share %s"
PRICES_ROW_TEMPLATE = "Prices %s"
PE_RATIO_ROW = "PE Ratio"
GROWTH_ROW = "Growth"

DATE_PATTERN = re.compile("([0-9]){4}-([0-9]){2}")

def initialize_webdriver():
    profile = webdriver.FirefoxProfile()
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", '/tmp/')
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/html")


    global driver
    driver = webdriver.Firefox(firefox_profile=profile)

initialize_webdriver()

def check_if_date(s):
    if DATE_PATTERN.match(s):
        return True
    else:
        return False


def to_date(s):
    if s=='TTM' or s=='Latest Qtr':
        now = datetime.datetime.now()
        return now.strftime("%Y-%m")
    return s


def get_table():
    return {"columns": [], "indeces": [], "data": []}


def to_float(s):
    s = s.replace("\n", "").replace(" ", "").replace(",","")
    try:
        n = float(s)
    except:
        n = float('NaN')
    return n


def get_10yrs_data_from_csv(ticker):

    idx_dot = ticker.find('.')
    if idx_dot!=-1:
        ticker = ticker[:idx_dot]

    driver.get(KEYRATIO_URL % ticker)
    driver.find_element_by_id("financials").find_element_by_class_name("large_button").click()

    f = open("/tmp/%s Key Ratios.csv" % ticker, "r")
    csv_parsed = csv.reader(f, delimiter=',')

    gt = get_table
    datas = {FINANCIALS: gt(), MARGIN_OF_SALES: gt(), PROFITABILITY: gt(), REVENUE: gt(), OPERATING_INCOME: gt(),
             NET_INCOME: gt(), EPS: gt(), CASH_FLOW_RATIO: gt(), FINANCIAL_HEALTH: gt(), LIQUIDITY: gt(),
             EFFICIENCY: gt()}
    d = None
    last_columns = None
    for r in csv_parsed:
        if len(r)==0:
            d = None
            continue
        first_col = r[0]
        if first_col in datas:
            d = datas[first_col]
        if len(r) == 1:
            continue
        second_col = r[1]
        if not (d is None):
            if check_if_date(second_col):
                last_columns = []
                for c in r[1:]:
                    last_columns.append(to_date(c))
                continue
            if not d["columns"] and last_columns:
                d["columns"] = last_columns
            d["indeces"].append(r[0])
            entries = []
            for c in r[1:]:
                entries.append(to_float(c))
            d["data"].append(entries)

    for k in datas:
        v = datas[k]
        datas[k] = pd.DataFrame(v["data"], index=v["indeces"], columns=v["columns"])

    f.close()

    os.remove("/tmp/%s Key Ratios.csv" % ticker)

    return datas


get_10yrs_data = get_10yrs_data_from_csv


if __name__=="__main__":
    results = get_10yrs_data('NVDA')
    print(results[FINANCIALS].loc["Earnings Per Share USD"])






