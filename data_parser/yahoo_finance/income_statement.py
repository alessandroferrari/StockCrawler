from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from data_parser.yahoo_finance.common import nan_filter, DATA_MUL, TOLERATED_DELTA
import warnings

def parse_total_revenue(data, yr):
    total_revenue = nan_filter(data["total revenue"][yr]) * DATA_MUL
    return total_revenue


def parse_cost_of_revenue(data, yr):
    cost_of_revenue = - nan_filter(data["cost of revenue"][yr]) * DATA_MUL
    return cost_of_revenue


def parse_gross_profit(data, yr):

    total_revenue = parse_total_revenue(data, yr)
    cost_of_revenue = parse_cost_of_revenue(data, yr)
    gross_profit = nan_filter(data["gross profit"][yr]) * DATA_MUL
    gross_profit_calc = total_revenue + cost_of_revenue
    if not abs(gross_profit * (1.0 - TOLERATED_DELTA)) <= abs(gross_profit_calc) <= abs(gross_profit * (1.0 + TOLERATED_DELTA)):
        warnings.warn("Gross profit scraped ({0:.4f}) differs from calculated ({1:.4f})".format(
            gross_profit, gross_profit_calc))

    return gross_profit


def parse_ebit(data, yr):

    total_revenue = nan_filter(data["total revenue"][yr]) * DATA_MUL
    total_operating_expenses = - nan_filter(data["total operating expenses"][yr]) * DATA_MUL
    
    EBIT = total_revenue + total_operating_expenses

    earnings_before_interest_and_taxes = nan_filter(data["ebitda"][yr]) * DATA_MUL
    if not abs(EBIT * (1.0 - TOLERATED_DELTA)) <= abs(earnings_before_interest_and_taxes) <= abs(EBIT * (1.0 + TOLERATED_DELTA)):
        warnings.warn("EBIT scraped ({0:.4f}) differs from calculated ({1:.4f}).".format(
            earnings_before_interest_and_taxes, EBIT))

    return EBIT


def parse_ebt(data, yr, EBIT, total_other_income_exp):

    EBT = EBIT + total_other_income_exp
    income_before_taxes = nan_filter(data["income before tax"][yr]) * DATA_MUL
    if not abs(EBT * (1.0 - TOLERATED_DELTA)) <= abs(income_before_taxes) <= abs(EBT * (1.0 + TOLERATED_DELTA)):
        warnings.warn("EBT scraped ({0:.4f}) differs from calculated ({1:.4f}).".format(
            income_before_taxes, EBT))

    return EBT


def parse_operating_net(data, yr, EBT):

    income_tax_expenses = - nan_filter(data["income tax expense"][yr]) * DATA_MUL

    operating_net = nan_filter(data["income from continuing operations"][yr]) * DATA_MUL
    operating_net_calc = EBT + income_tax_expenses
    if not abs(operating_net * (1.0 - TOLERATED_DELTA)) <= abs(operating_net_calc) <= abs(operating_net * (1.0 + TOLERATED_DELTA)):
        warnings.warn("Operating Net Income scraped ({0:.4f}) differs from calculated ({1:.4f}).".format(
            operating_net, operating_net_calc))

    return operating_net


def parse_net_income(data, yr, operating_net):

    net_income = nan_filter(data["net income"][yr]) * DATA_MUL

    return net_income


def parse_income_statement_per_yr(data, yr):

    total_revenue = parse_total_revenue(data, yr)
    gross_profit = parse_gross_profit(data, yr)

    # GROSS OPERATING INCOME
    EBIT = parse_ebit(data, yr)

    #OPERATING INCOME AFTER INTERESTS AND TAXES

    total_other_income_exp = nan_filter(data["total other income/expenses net"][yr]) * DATA_MUL
    interest_expense = nan_filter(data["interest expense"][yr]) * DATA_MUL

    EBT = parse_ebt(data, yr, EBIT, total_other_income_exp)

    operating_net = parse_operating_net(data, yr, EBT)

    #NON-RECURRING EVENTS
    net_income = parse_net_income(data, yr, operating_net)

    results = dict()
    results["Total Revenue"] = total_revenue
    results["Gross Profit"] = gross_profit
    results["EBIT"] = EBIT
    results["EBT"] = EBT
    results["Operating Net"] = operating_net
    results["Net Income"] = net_income
    results["Interest Expense"] = interest_expense

    return results
