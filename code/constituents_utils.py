from collections import OrderedDict

import pandas as pd
import numpy as np
import pandas_market_calendars as mcal
import matplotlib.pyplot as plt


def get_historical_constituents():
    """
    gets historical constituents from WRDS file
    """
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


def load_sp600_files():
    """
    loads data from files from investing.com
    https://www.investing.com/indices/s-p-600-components
    """
    # TODO: get latest updated files or files with latest date
    latest_date = '7-18-2018'
    folder = '../sp600_constituent_lists/investing.com/'
    dfs = []
    labels = ['price', 'performance', 'technical', 'fundamentals']
    for l in labels:
        filename = 'S&P_600_Components_{}_7-18-2018.csv'.format(l)
        dfs.append(pd.read_csv(folder + filename))

    # ensure the names and symbols are identical
    eq01 = dfs[0][['Name', 'Symbol']].equals(dfs[1][['Name', 'Symbol']])
    eq12 = dfs[1][['Name', 'Symbol']].equals(dfs[2][['Name', 'Symbol']])
    eq23 = dfs[2][['Name', 'Symbol']].equals(dfs[3][['Name', 'Symbol']])
    if eq01 and eq12 and eq23:
        print('all names/symbols are equal')
    else:
        print('WARNING: some names/symbols not equal')

    for d in dfs:
        d.set_index('Symbol', inplace=True)

    # remove 'Name' column from all but first df
    for d in dfs[1:]:
        d.drop('Name', axis=1, inplace=True)

    # add prefixes so 'Daily' is different for performance and technical dfs
    dfs[1].columns = ['perf ' + c for c in dfs[1].columns]
    dfs[2].columns = ['tech ' + c for c in dfs[2].columns]

    df = pd.concat(dfs, axis=1)
    # 'Time' column seems to be just year/month
    df.drop('Time', axis=1, inplace=True)

    # convert k to 1000, M to 1e6, and B to 1.9
    for c in ['Vol.', 'Average Vol. (3m)', 'Market Cap', 'Revenue']:
        df[c] = df[c].apply(lambda x: clean_abbreviations(x))

    # clean up % columns
    for c in ['Chg. %', 'perf Daily', 'perf 1 Week', 'perf 1 Month', 'perf YTD', 'perf 1 Year', 'perf 3 Years']:
        df[c] = df[c].apply(lambda x: clean_pcts(x))

    # maps technical indicators to numbers for sorting
    conversion_dict = {'Strong Buy': 2,
                        'Buy': 1,
                        'Neutral': 0,
                        'Sell': -1,
                        'Strong Sell': -2}

    for k, v in conversion_dict.items():
        for c in dfs[2].columns:
            df.at[df[c] == k, c] = v

    return df


def clean_pcts(x):
    """
    the 'Chg. %' column and others have entries like +1.24%
    """
    # if not enough data, will be '-'
    if x == '-':
        return np.nan

    new_x = x.replace('+', '')
    new_x = new_x.replace('%', '')
    new_x = float(new_x) / 100
    return new_x


def clean_abbreviations(x):
    """
    replaces K with 000, M with 000000, B with 000000000
    """
    # a few entries in Revenue were nan
    if pd.isnull(x):
        return np.nan
    elif 'K' in x:
        return int(float(x[:-1]) * 1e3)
    elif 'M' in x:
        return int(float(x[:-1]) * 1e6)
    elif 'B' in x:
        return int(float(x[:-1]) * 1e9)
    else:
        return int(x)


def get_current_smallest_mkt_cap(df, n=20):
    """
    using df from investing.com and the load_sp600_files function,
    gets the n number of smallest market-cap stocks
    """
    sorted_df = df.sort_values(by='Market Cap')

# TODO: scrape investing.com for files



import sys
sys.path.append('../stock_prediction/code')
import dl_quandl_EOD as dlq

all_stocks_dfs = dlq.load_stocks()


# get market cap of each stock in index for each unique date
# need to get more historical data from wrds
market_caps = OrderedDict()
unique_dates = sorted(pd.concat([sp600_df['from'], sp600_df['thru']]).unique())[:-1]
for d in unique_dates:
    mcaps = []
    for ticker in current_tickers[d]:
        mcaps.append(all_stocks_dfs[ticker][''])
    market_caps[d] =
