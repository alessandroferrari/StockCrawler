from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
sys.path.insert(0, '/usr/local/lib/python3.5/dist-packages')
sys.path.insert(0, '/home/alessandro/PycharmProjects/StockScraping/')
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime
import pytz
import time
from data_parser.common import get_page_html, get_cookie_crumb
try:
    # for Python 2.x
    from StringIO import StringIO
except ImportError:
    # for Python 3.x
    from io import StringIO
import csv

DATA_MUL = 1000
TOLERATED_DELTA = 0.1

CURRENT_YR = 0
ONE_YR_AGO = 1
TWO_YR_AGO = 2
THREE_YR_AGO = 3

QUOTE_URL='https://finance.yahoo.com/quote/%s?p=%s'
INCOME_STATEMENT_URL='https://finance.yahoo.com/quote/%s/financials?p=%s'
BALANCE_SHEET_URL='https://finance.yahoo.com/quote/%s/balance-sheet?p=%s'
CASH_FLOW_URL='https://finance.yahoo.com/quote/%s/cash-flow?p=%s'
STATISTICS_URL='https://finance.yahoo.com/quote/%s/key-statistics?p=%s'
ESTIMATES_URL='https://finance.yahoo.com/quote/%s/analysis?p=%s&.tsrc=fin-srch'
STOCK_PRICES_URL='https://query1.finance.yahoo.com/v7/finance/download/%s?period1=%s&period2=%s&interval=1d&events=history&crumb=%s'

#mapping table for months
daysdf = [31,28,31,30,31,30,31,31,30,31,30,31]

def nan_filter(n):
    if math.isnan(n):
        return 0
    return n


def get_urls_financials(stock):
    income_statement=INCOME_STATEMENT_URL%(stock, stock)
    balance_sheet=BALANCE_SHEET_URL%(stock, stock)
    cash_flow=CASH_FLOW_URL%(stock, stock)
    return income_statement, balance_sheet, cash_flow


def parse_financials_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    rows = soup.select('table tbody tr')
    data = dict()
    for r in rows:
        cols_tmp = r.find_all('td')
        cols = []
        for c in cols_tmp:
            try:
                cols.append(c.find_all('span')[0])
            except:
                cols.append(c)
        rname = cols[0].get_text().lower()
        entries = []
        for c in cols[1:]:
            try:
                n = c.get_text().replace(',', '')
                n = float(n)
            except:
                n = float('NaN')
            entries.append(n)
        if len(entries)==0:
            continue
        data[rname] = entries
    return data


def get_statistics_url(stock):
    statistics_url = STATISTICS_URL%(stock, stock)
    return statistics_url


def isfloat(num):
    try:
        float(num)
    except:
        return False
    return True


def convert_date(s):
    return datetime.strptime(s.replace(",", ""), '%d %b %Y')


def isdate(s):
    try:
        convert_date(s)
    except:
        return False
    return True


def issplit(s):
    try:
        i1, i2 = s.split("/")
        i1 = int(i1)
        i2 = int(i2)
    except:
        return False
    return True


def clean_statistics_entry(value):
    value = value.replace(',', '')
    if isfloat(value):
        return float(value)
    elif isfloat(value[:-1]):
        mul = 1.0
        num = float(value[:-1])
        suffix = value[-1].upper()
        if suffix=='M':
            mul = 1000000.0
        elif suffix=='B':
            mul = 1000000000.0
        elif suffix=="%":
            mul = 0.01
        elif suffix=="K":
            mul = 1000
        else:
            raise Exception("Unsupported suffix while parsing statistics entries: %s"%value)
        num *= mul
        return num
    elif value=="N/A":
        return float('NaN')
    elif isdate(value):
        return convert_date(value)
    elif issplit(value):
        return value
    else:
        return float('NaN')


def parse_statistics_table(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table", class_="table-qsp-stats")

    statistics = dict()

    for table in tables:
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            entry = cols[0].select("span")[0].get_text().lower()
            value = cols[1].get_text()
            statistics[entry] = clean_statistics_entry(value)

    return statistics


def is_business_day(date):
    return bool(len(pd.bdate_range(date, date)))


def _get_stock_value(ticker, day, month, year):
    quote_url = QUOTE_URL%(ticker, ticker)
    cookie, crumb = get_cookie_crumb(quote_url)
    period = str(int(time.mktime(time.strptime('{0}/{1}/{2}'.format(day, month, year), "%d/%m/%Y"))))
    stock_price_url = STOCK_PRICES_URL%(ticker, period, period, crumb)
    data, _ = get_page_html(stock_price_url, cookies=cookie)
    f = StringIO(data)
    csv_parsed = csv.reader(f, delimiter=',')
    csv_parsed = list(csv_parsed)
    price = csv_parsed[-1][-2]
    return float(price)


def get_stock_price_per_month(ticker, year, month):

    now = datetime.now()

    month = int(month)
    year = int(year)
    max_day = daysdf[month-1]

    if now.year==year and now.month==month and now.day<=max_day:
        max_day=now.day

    i = 0
    dates = []
    day = max_day
    while True:
        date = datetime(year, month, day, 0, 0, 0, 0, pytz.utc)
        if is_business_day(date):
            dates.append((year, month, day))
            i += 1
        if i>=2:
            break
        day = day - 1

    price = None
    for year, month, day in dates:
        try:
            price = _get_stock_value(ticker, day, month, year)
        except Exception as e:
            continue
        else:
            break

    if price is None:
        price = float('NaN')
    return price


def get_earnings_estimate_url(ticker):
    url = ESTIMATES_URL%(ticker, ticker)
    return url


def parse_earnings_estimate(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all("table", class_="W(100%) M(0) BdB Bdc($c-fuji-grey-c) Mb(25px)")
    earnings_estimate = dict()
    for table in tables:
        table_dict = dict()

        # header
        theader = table.find_all("thead")[0]
        columns = theader.find_all("th")
        try:
            name = columns[0].select("span")[0].get_text().lower()
        except:
            name = columns[0].get_text().lower()
        cnames = []
        for cname in columns[1:]:
            try:
                cn = cname.select("span")[0].get_text()
            except:
                cn = cname.get_text()
            cnames.append(cn)

        # entries
        rows = table.find_all("tr", class_="BdT Bdc($c-fuji-grey-c)")
        for row in rows:
            cols = row.find_all("td")
            try:
                entry = cols[0].select("span")[0].get_text().lower()
            except:
                entry = cols[0].get_text().lower()
            l = []
            for c in cols[1:]:
                try:
                    value = c.select('span')[0].get_text()
                except:
                    value = c.get_text()
                value = clean_statistics_entry(value)
                l.append(value)
            table_dict[entry] = l

        earnings_estimate[name] = pd.DataFrame(table_dict, index=cnames).T

    return earnings_estimate


if __name__=="__main__":
    print(get_stock_price_per_month("WTI", 2019, 1))


