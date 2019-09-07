#!/usr/bin/python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import argparse
import pandas as pd
import os
import sys

if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Filter for value stocks.')
    parser.add_argument('stocks_valuations', type=str, help='File including stocks valuations.')
    parser.add_argument('--fcf_margin_threshold', type=float,
                        help='This should be a margin on the average FCF of the last 4 years.', default=-0.10)
    parser.add_argument('--fcf_margin_threshold_last_yr', type=float,
                        help='This should be a margin on the average FCF of the last 4 years.', default=-0.10)
    parser.add_argument('--historical_margin_threshold', type=float,
                        help='This should be a margin on the average historical price of the last 10 years.', default=0.1)
    parser.add_argument('--fcf_interest_avg_threshold', type=float,
                        help='Ratio between free cash flow and debt interests in the last 4 years.', default=3.0)
    parser.add_argument('--fcf_interest_last_yr_threshold', type=float,
                        help='Ratio between free cash flow and debt interests last year.', default=4.0)
    parser.add_argument('--margin_analyst_low_threshold', type=float,
                        help='Margin between lowest analyst projection and current prices.', default=0.0)


    args = parser.parse_args()

    stocks_valuations_fn = os.path.expanduser(args.stocks_valuations)
    if not os.path.exists(stocks_valuations_fn):
        print("Invalid stocks_valuations path %s: file does not exist!")
        sys.exit()

    data = pd.read_csv(stocks_valuations_fn, sep="|")

    fcf = data["Margin FCF Avg"].astype(float)>args.fcf_margin_threshold
    fcf_last_yr = data["Margin FCF Last Yr"].astype(float) > args.fcf_margin_threshold_last_yr
    historical = data["Margin Historical"].astype(float)>args.historical_margin_threshold
    fcf_interest_avg = data["FCF / Interests Avg"].astype(float)>args.fcf_interest_avg_threshold
    fcf_interest_last_yr = data["FCF / Interests Last Yr"].astype(float) > args.fcf_interest_last_yr_threshold
    margin_analyst_low = data["Margin Analysts Low"].astype(float) > args.margin_analyst_low_threshold

    filtered_data = data[fcf & historical & fcf_last_yr & fcf_interest_avg & fcf_interest_last_yr &
                        margin_analyst_low]

    basepath = os.path.dirname(stocks_valuations_fn)
    fname = "filtered_%s"%os.path.basename(stocks_valuations_fn)
    out_fn = os.path.join(basepath, fname)
    filtered_data.to_csv(out_fn, sep="|")


