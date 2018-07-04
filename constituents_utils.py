from collections import OrderedDict

import pandas as pd
import pandas_market_calendars as mcal
import matplotlib.pyplot as plt

df = pd.read_csv('historical_constituents.csv', parse_dates=['from', 'thru'], infer_datetime_format=True)

# only use s&p600 for now
sp600_df = df[df['conm'] == 'S&P Smallcap 600 Index']
# create dataframe with list of constituents for each day
start = sp600_df['from'].min()
# get todays date and reset hour, min, sec to 0s
end = pd.Timestamp.today(tz='US/Eastern').replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)

# replace NaT with tomorrow's date
# gives copy warning but can't get rid of it...
sp600_df['thru'].fillna(end + pd.DateOffset(days=1), inplace=True)


nyse = mcal.get_calendar('NYSE')
# gets all dates
# date_range = mcal.date_range(start=start, end=end)
# gets only dates valid for NYSE
date_range = nyse.valid_days(start_date=start, end_date=end)

constituent_companies = OrderedDict()
constituent_tickers = OrderedDict()
lengths = []

for d in date_range:
    # if date is within stock's from and thru, add to list
    # stocks were removed on 'thru', so if it is the 'thru' date, then shouldn't be included
    # but stocks were added on 'from' date, so include stocks on 'from' date
    # use dataframe masking
    current_stocks = sp600_df[(sp600_df['from'] <= d) & (sp600_df['thru'] > d)]
    current_companies = current_stocks['co_conm']  # company names
    current_tickers = current_stocks['co_tic']  # company tickers
    constituent_companies[d] = current_companies
    constituent_tickers[d] = current_tickers
    lengths.append(current_tickers.shape[0])

pd.value_counts(lengths)
# plt.hist(lengths)
# plt.show()

# TODO:
# need to check that no tickers are used for multiple companies



import sys
sys.path.append('../stock_prediction/code')
import dl_quandl_EOD as dlq

all_stocks_dfs = dlq.load_stocks()


# get market cap of each stock in index for each unique date

market_caps = OrderedDict()
unique_dates = sorted(pd.concat([sp600_df['from'], sp600_df['thru']]).unique())[:-1]
for d in unique_dates:
    mcaps = []
    for ticker in current_tickers[d]:
        mcaps.append(all_stocks_dfs[ticker][''])
    market_caps[d] =
