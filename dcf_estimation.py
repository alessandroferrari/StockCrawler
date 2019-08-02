from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from analyst_data_estimation import compute_eps_estimate_from_analysts
from data_parser.yahoo_finance.common import get_earnings_estimate_url, parse_earnings_estimate
from data_parser.common import get_page_html
from historic_data_estimation import EPS_forecast_based_on_history

import pandas as pd


def compute_price_DCF(eps_forecast, expected_pe, discount_rate=0.015):
    num_yrs = eps_forecast.shape[1]
    present_values = {}
    for i in range(1, num_yrs+1):
        pv = eps_forecast[i][0] / (1.0 + discount_rate)**i
        present_values[i] = pv
    present_values[num_yrs] = pv * expected_pe
    present_values_df = pd.DataFrame(present_values, index=["Future Years"])
    return present_values_df.sum(axis=1)[0]


def dcf_price_estimation_from_analysts(ticker, expected_pe, discount_rate=0.015, safety_margin_y1=0.25,
                                       safety_margin_long_term=0.4):

    safe_estimate_y1 = 1.0 - safety_margin_y1
    safe_estimate_long_term = 1.0 - safety_margin_long_term

    url = get_earnings_estimate_url(ticker)
    html, _ = get_page_html(url)
    earnings_forecast_df = parse_earnings_estimate(html)

    compute_eps_estimate_from_analysts(earnings_forecast_df, uncertainty_per_year=safe_estimate_y1,
                                       uncertainty_bottom_cap=safe_estimate_long_term)
    price_forecast_from_analyst_low = compute_price_DCF(earnings_forecast_df["EPS Forecast Low"], expected_pe,
                                                        discount_rate=discount_rate)
    price_forecast_from_analyst_high = compute_price_DCF(earnings_forecast_df["EPS Forecast High"], expected_pe,
                                                         discount_rate=discount_rate)
    price_forecast_from_analyst_avg = compute_price_DCF(earnings_forecast_df["EPS Forecast Avg"], expected_pe,
                                                        discount_rate=discount_rate)
    price_forecast_from_analyst_avg_adj = compute_price_DCF(earnings_forecast_df["EPS Forecast Avg Adj"], expected_pe,
                                                            discount_rate=0.015)

    return price_forecast_from_analyst_avg, price_forecast_from_analyst_low, price_forecast_from_analyst_high, \
        price_forecast_from_analyst_avg_adj


def dcf_price_estimation_from_historical_data(ticker, eps_avg, growth_avg, pe_avg, num_yrs_forecast=5, discount_rate=0.015):

    historic_eps_forecast = EPS_forecast_based_on_history(eps_avg, growth_avg, yrs_num=num_yrs_forecast)

    price_forecast_from_history = compute_price_DCF(historic_eps_forecast, pe_avg, discount_rate=discount_rate)

    return price_forecast_from_history

if __name__=="__main__":
    pe_avg =6.06
    eps_forecast = EPS_forecast_based_on_history(2.22, -0.04, yrs_num=5)
    print(compute_price_DCF(eps_forecast, pe_avg))
