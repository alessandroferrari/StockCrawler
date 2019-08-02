
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.yahoo_finance.common import nan_filter, DATA_MUL


def parse_cash_flow_statement_per_yr(data, yr):

    net_income = nan_filter(data["net income"][yr]) * DATA_MUL

    # The math here does not match 100%, not sure if something is missing
    depreciation = nan_filter(data["depreciation"][yr]) * DATA_MUL
    adjustments_to_net_income = nan_filter(data["adjustments to net income"][yr]) * DATA_MUL
    changes_in_accounts_receivables = nan_filter(data["changes in accounts receivables"][yr]) * DATA_MUL
    changes_in_liabilities = nan_filter(data["changes in liabilities"][yr]) * DATA_MUL
    changes_in_inventories = nan_filter(data["changes in inventories"][yr]) * DATA_MUL
    changes_in_other_operating_activities = nan_filter(data["changes in other operating activities"][yr]) * DATA_MUL

    cash_flow_from_operating = nan_filter(data["total cash flow from operating activities"][yr]) * DATA_MUL

    capex = nan_filter(data["capital expenditure"][yr]) * DATA_MUL
    investments = nan_filter(data["investments"][yr]) * DATA_MUL
    other_cash_from_investing = nan_filter(data["other cash flows from investing activities"][yr]) * DATA_MUL
    cash_from_investing = nan_filter(data["total cash flows from investing activities"][yr]) * DATA_MUL

    dividends_paid = nan_filter(data["dividends paid"][yr]) * DATA_MUL
    sale_purchase_of_stock = nan_filter(data["sale purchase of stock"][yr]) * DATA_MUL
    net_borrowings = nan_filter(data["net borrowings"][yr]) * DATA_MUL
    other_cash_from_financing = nan_filter(data["other cash flows from financing activities"][yr]) * DATA_MUL
    cash_from_financing = nan_filter(data["total cash flows from financing activities"][yr]) * DATA_MUL

    effect_of_exchange_rate_changes = nan_filter(data["effect of exchange rate changes"][yr]) * DATA_MUL
    change_in_cash = nan_filter(data["change in cash and cash equivalents"][yr]) * DATA_MUL

    fcf = cash_flow_from_operating + capex

    results = dict()
    results["CAPEX"] = capex
    results["FCF"] = fcf
    results["Cash from Financing"] = cash_from_financing
    results["Cash from Investing"] = cash_from_investing
    results["Change in Cash"] = change_in_cash
    results["Dividends Paid"] = dividends_paid

    return results
