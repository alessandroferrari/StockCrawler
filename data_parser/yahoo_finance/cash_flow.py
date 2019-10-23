
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.yahoo_finance.common import nan_filter, DATA_MUL


def parse_cash_flow_statement_per_yr(data, yr):

    cash_flow_from_operating = nan_filter(data["net cash provided by operating activites"][yr]) * DATA_MUL

    capex = nan_filter(data["capital expenditure"][yr]) * DATA_MUL
    cash_from_investing = nan_filter(data["net cash used for investing activites"][yr]) * DATA_MUL

    dividends_paid = nan_filter(data["dividends paid"][yr]) * DATA_MUL
    cash_from_financing = nan_filter(data["net cash used privided by (used for) financing activities"][yr]) * DATA_MUL

    change_in_cash = nan_filter(data["net change in cash"][yr]) * DATA_MUL

    fcf = cash_flow_from_operating + capex

    results = dict()
    results["CAPEX"] = capex
    results["FCF"] = fcf
    results["Cash from Financing"] = cash_from_financing
    results["Cash from Investing"] = cash_from_investing
    results["Change in Cash"] = change_in_cash
    results["Dividends Paid"] = dividends_paid

    return results
