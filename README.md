# StockCrawler

## How it works

StockCrawler scan all the stocks provided in a csv file as inputs, that includes names and tickers.
The repository already includes csv that includes NASDAQ and NYSE stocks index.
The scripts uses BeautifulSoup and Selenium python libraries for downloading financial datas from Yahoo Finance and MorningStar.
The financial data extend to the past ten years. It provides quantitative financial price estimates, and their margin of safety compared to the current prices.
Many stocks listed in indeces may not have data filled in Yahoo Finance or MorningStar portals, so the software just skip those.

### Literature
Many of the methods explained here are proposed in books such as:
* *The Intelligent Investor* by Benjamin Graham
* *Manuale dell'Investitore Consapevole* (Italian edition) by Gabriele Bellelli, Andrew Lawford, Maurizio Mazziero
* *Strategie di investimento per il lungo termine* (Italian edition, *Strategies for long term investors*) W.J. Bernstein
* *Seeking Wisdom - From Darwin to Munger* by Peter Bevelin.
* *GET RICH SLOW - Step by step value investing with Python* Udemy Course by Russell Birkholtz.

### Price estimation based on Free Cash Flow
Free Cash Flow is positive cash produced by the company, after all the bad things. Typically, it should be reinvested for dividends or shares buybacks, that lowers outstanding shares, thus increases EPS.
Many school of thoughts for evaluating stocks, assert that future is too uncertain to be estimated, so price should be a result of the capability of the company to produce cash.
#### Estimate Free Cash Flow based price
StockCrawler estimates price based on the average of the last four years Free Cash Flow, assuming the company would pay a 10% dividend. Then, it does the same only for the Free Cash Flow of the previous year.
#### Estimated Free Cash Flow over Interests
Financial obligations can drown a company, especially on tough times. A value investor should never consider companies that has a FCF / Interests ratio below 3.0, and I would recommend 5.0 to be safe.  
### Price estimation based on historical data
This method is inspired to the concepts explained in "The Intelligent Investor" of Benjamin Graham. Benjamin Graham gives also a lot of emphasis of *book value* and ratio such as *Market Cap / Book Value* or *Market Cap / Working Capital*.
The provided methods here are only based on earnings.
#### EPS - Earnings per Share
StockCrawler retrieves the EPS of the last ten years (if available), and it provides an average as expected EPS, to take into account fluctuations of market cycle in cyclical industries.
#### Price per Earnings
StockCrawler retrieves the prices of the last ten years (if available), and together with the EPS, computes the PE (Price per Earnings). Then, it averages the PE to the last 10 years, caps it to 35, and it applies a 40% **margin of safety**, (multiply final value by 0.6). 
#### Historical growth
StockCrawler estimates the growth of the EPS of the last ten years (year over year), averages it, cap it 15%, and applies a *margin of safety* of the 40%, (multiply final value by 0.6).
#### Discounted cash flow based on historical data
Estimates value based on 5 years DCF using as a discount value of 1.5%, using as final capital value estimated PE with margin of safety and as a growth rate, the historic growth rate, with margin of safety.

### Price estimation based on analysts previsions
Future is indeed uncertain, though Wall Street analysts get paid a substantial amount of bucks for attempting to predict it.
StockCrawler provides price estimates of the stocks, based on EPS projections of the analysts, including:
* average of analysts consensus
* lowest analyst projection
* highest analyst projection
* *adjusted* projection, providing a catastrophic 25% drop in EPS versus analysts consensus, and 40% for the 4 years after the next one. This is a really conservative projection.

For each of these EPS projection, performs evaluation using Discounted Cash Flow formula at 5 years, using a discount rate of 1.5% and a final capital value the average PE computed in the historical series.

### Additional things to consider

Please, keep in mind that the analysis only takes into account quantitative parameters, and it does not do any qualitative analysis of the underlying goodness of the company, in term of future competitiveness and integrity.
Also, companies sometimes are undervaluated for a good reason, thus check additional parameters, such as:
* *Current ratio*: capability of the company to pay its short term financial obligations with its liquid and semi-liquid asset. It should be around 1.5 or greater to be good.
* *Operating margin* and *Profit margin*: they tell you how much the companies are financially profitable in their operation, and this becomes really important, especially in tough time. I recommend company with high margins, such as greater than 10%.
* *Asset / Debt* ratio: an healthy company should have this in the range of 2:1.
* Company had always positive EPS in the last ten year, so it is robust to the economic cycle (especial emphasis should be put in years such as 2009).

As additional parameters, for picking the best stocks, some important parameters are:

* Company pays dividend, and it does since last ten year, possibly with an increasing series.
* *Market Cap / Book Value* and *Market Cap / Working Capital* ratios: those were metric highly stressed by Graham in his historic book on value investing, though today they have a bit loose of relevance. Graham recommends to do not buy stocks of company with those ratio greater than 3.0, however in today market intangible asset and technology have made this less and less important.

*Quantitative analysis* is only a small part of stock picking, that needs to be follow by *qualitative analysis*.
Always ensure to read and understand the company business when you are investing in it, and also read also the company SEC fillings.
Value investing only works when there is good diversification of bought stocks, so ensure to a have a diversified portfolio. The less you want to do due-diligence of the stock, the more you should diversify.
Also, Value investing only works long term, you may need to old positions for years.

## Install

If you need to install *pip* package manager for *python3*:

    sudo apt-get install python3-pip

Once *pip* is installed, ensure *virtualenv* is installed:

    sudo pip3 install virtualenv 

Then, create a new virtualenv environment:

    virtualenv stocks_venv

Activates it:

    source stocks_venv/bin/activate
    
Or, if you do not use *bash*:

    source stocks_venv/bin/activate.(shell of your choice)

Install dependencies:

    pip3 install -r requirements.txt

Selenium with Mozilla Firefox is required. Additionally, you will need to add the *geckodriver*.

You can download [here](https://github.com/mozilla/geckodriver/releases) the *geckodriver*.

    cd ~/Downloads
    sudo chmod 0777 geckodriver
    cp geckodriver /usr/bin

After finishing the stocks crawling, you can deactivate your virtualenv:

    deactivate    

## Estimate value for stocks listing

For estimating qualitative margins on prices on the NASDAQ index:

    python3 price_estimation.py NASDAQ.csv

A file called *quantitative_NASDAQ.csv* will be saved in your desktop.

On the NYSE index:

    python3 price_estimation.py NYSE.csv

A file called *quantitative_NYSE.csv* will be save in your desktop.

For stopping, simply press Ctrl+C in the terminal.

For resuming:

    python3 price_estimation.py NYSE.csv --resume /home/user/Desktop/quantitative_NYSE.csv

Once, estimated financials for all the index (it may even take a couple of days), you can run *filter_bargains.py* script for filtering stocks that standout from a value perspective.

    python3 filter_bargains.py /home/user/Desktop/quantitative_NYSE.csv

This will generate an additional *filtered_quantitative_NYSE.csv*, that will filter only the stocks that are included in the filtering criteria.
It is possible to adjust the thresholds of the criteria via command line:

    python3 filter_bargains.py -h
        usage: filter_bargains.py [-h] [--fcf_margin_threshold FCF_MARGIN_THRESHOLD]
                                  [--fcf_margin_threshold_last_yr FCF_MARGIN_THRESHOLD_LAST_YR]
                                  [--historical_margin_threshold HISTORICAL_MARGIN_THRESHOLD]
                                  [--fcf_interest_avg_threshold FCF_INTEREST_AVG_THRESHOLD]
                                  [--fcf_interest_last_yr_threshold FCF_INTEREST_LAST_YR_THRESHOLD]
                                  [--margin_analyst_low_threshold MARGIN_ANALYST_LOW_THRESHOLD]
                                  stocks_valuations
        
        Filter for value stocks.
        
        positional arguments:
          stocks_valuations     File including stocks valuations.
        
        optional arguments:
          -h, --help            show this help message and exit
          --fcf_margin_threshold FCF_MARGIN_THRESHOLD
                                This should be a margin on the average FCF of the last
                                4 years.
          --fcf_margin_threshold_last_yr FCF_MARGIN_THRESHOLD_LAST_YR
                                This should be a margin on the average FCF of the last
                                4 years.
          --historical_margin_threshold HISTORICAL_MARGIN_THRESHOLD
                                This should be a margin on the average historical
                                price of the last 10 years.
          --fcf_interest_avg_threshold FCF_INTEREST_AVG_THRESHOLD
                                Ratio between free cash flow and debt interests in the
                                last 4 years.
          --fcf_interest_last_yr_threshold FCF_INTEREST_LAST_YR_THRESHOLD
                                Ratio between free cash flow and debt interests last
                                year.
          --margin_analyst_low_threshold MARGIN_ANALYST_LOW_THRESHOLD
                                Margin between lowest analyst projection and current
                                prices
    
All the criteria are then enforced with a logical AND operation on all the Pandas frame.
 