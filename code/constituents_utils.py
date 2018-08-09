import os
import glob
import datetime

from collections import OrderedDict

import pandas as pd
import numpy as np
import pandas_market_calendars as mcal
import matplotlib.pyplot as plt

def get_home_dir(repo_name='beat_market_analysis'):
    cwd = os.getcwd()
    cwd_list = cwd.split('/')
    repo_position = [i for i, s in enumerate(cwd_list) if s == repo_name]
    if len(repo_position) > 1:
        print("error!  more than one intance of repo name in path")
        return None

    home_dir = '/'.join(cwd_list[:repo_position[0] + 1]) + '/'
    return home_dir


def get_historical_constituents_wrds():
    """
    gets historical constituents from WRDS file
    """
    df = pd.read_csv(get_home_dir() + 'data/wrds/historical_constituents_2018-06-26.csv', parse_dates=['from', 'thru'], infer_datetime_format=True)

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

    # TODO: multiprocessing to speed up
    for d in date_range:
        # if date is within stock's from and thru, add to list
        # stocks were removed on 'thru', so if it is the 'thru' date, then shouldn't be included
        # but stocks were added on 'from' date, so include stocks on 'from' date
        # use dataframe masking
        date_string = d.strftime('%Y-%m-%d')
        current_stocks = sp600_df[(sp600_df['from'] <= d) & (sp600_df['thru'] > d)]
        current_companies = current_stocks['co_conm']  # company names
        current_tickers = current_stocks['co_tic']  # company tickers
        constituent_companies[date_string] = current_companies
        constituent_tickers[date_string] = current_tickers
        lengths.append(current_tickers.shape[0])

    # look at number of constituents as a histogram; mostly 600 but a few above and below
    # pd.value_counts(lengths)
    # plt.hist(lengths)
    # plt.show()

    # TODO:
    # need to check that no tickers are used for multiple companies

    # get unique dates where changes were made
    unique_dates = set(sp600_df['from'].unique()) | set(sp600_df['thru'].unique())

    return constituent_companies, constituent_tickers, unique_dates


def get_latest_daily_date(source='barchart.com'):
    # get latest date from daily scrapes
    daily_files = glob.glob(get_home_dir() + 'data/{}/*.csv'.format(source))
    if len(daily_files) == 0:
        return None

    daily_dates = [pd.to_datetime(f.split('/')[-1].split('_')[-1].split('.')[0]) for f in daily_files]
    last_daily = max(daily_dates)
    return last_daily


def get_latest_index_date(ticker='IJR'):
    # get latest date from daily scrapes
    extension = 'csv'
    if ticker == 'SLY':
        extension = 'xls'
    daily_files = glob.glob(get_home_dir() + 'data/index_funds/{}/*.{}'.format(ticker, extension))
    if len(daily_files) == 0:
        return None

    daily_dates = [pd.to_datetime(f.split('/')[-1].split('_')[-1].split('.')[0]) for f in daily_files]
    last_daily = max(daily_dates)
    return last_daily


def load_sp600_files(date='latest', source='barchart.com'):
    """
    loads data from files from investing.com
    https://www.investing.com/indices/s-p-600-components

    date should be a string, either 'latest' to use the latest available date, or
    a specific date like YYYY-mm-dd
    """
    folder = get_home_dir() + 'data/{}/'.format(source)
    dfs = []
    labels = ['price', 'performance', 'technical', 'fundamental']
    if date == 'latest':
        file_date = get_latest_daily_date(source=source).strftime('%Y-%m-%d')
        if file_date is None:
            print('no files to load!')
            return None
    else:
        file_date = date

    for l in labels:
        filename = 'sp600_{}_{}.csv'.format(l, file_date)
        print(filename)
        if source == 'barchart.com':
            dfs.append(pd.read_csv(folder + filename, skipfooter=1))
        elif source == 'investing.com':
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
        if source == 'barchart.com':
            d = d[:-2]  # the last row has some info about barchart.com

    # remove 'Name' column from all but first df
    for d in dfs[1:]:
        d.drop('Name', axis=1, inplace=True)
        if source == 'barchart.com':
            if 'Last' in d.columns:
                d.drop('Last', axis=1, inplace=True)

    if source == 'investing.com':
        # add prefixes so 'Daily' is different for performance and technical dfs
        dfs[1].columns = ['perf ' + c for c in dfs[1].columns]
        dfs[2].columns = ['tech ' + c for c in dfs[2].columns]

    df = pd.concat(dfs, axis=1)
    # 'Time' column seems to be just year/month
    df.drop('Time', axis=1, inplace=True)

    # convert k to 1000, M to 1e6, and B to 1.9
    if source == 'barchart.com':
        # just need to rename the column, the data is not $K, just $
        df['Market Cap'] = df['Market Cap, $K']
        df.drop('Market Cap, $K', axis=1, inplace=True)
    elif source == 'investing.com':
        for c in ['Vol.', 'Average Vol. (3m)', 'Market Cap', 'Revenue']:
            df[c] = df[c].apply(lambda x: clean_abbreviations(x))

    # clean up % columns
    if source == 'barchart.com':
        cols = ['%Chg', 'Wtd Alpha', 'YTD %Chg', '1M %Chg', '3M %Chg', '52W %Chg', '20D Rel Str', '20D His Vol', 'Div Yield(a)']
    elif source == 'investing.com':
        cols = ['Chg. %', 'perf Daily', 'perf 1 Week', 'perf 1 Month', 'perf YTD', 'perf 1 Year', 'perf 3 Years']
    for c in cols:
        df[c] = df[c].apply(lambda x: clean_pcts(x))

    if source == 'investing.com':
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
    # if not enough data, will be '-' with investing.com
    if x == '-' or pd.isnull(x):
        return np.nan
    elif x == 'unch':
        return float(0)
    elif type(x) == float:
        return x

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

    should use barchart.com or wrds as source of constituents
    """
    sorted_df = df.sort_values(by='Market Cap')
    return sorted_df.iloc[:n].index


def load_ijr_holdings():
    latest_date = get_latest_index_date(ticker='IJR')
    if latest_date is None:
        print('no files')
        return

    filename = get_home_dir() + 'data/index_funds/IJR/IJR_holdings_' + latest_date.strftime('%Y-%m-%d') + '.csv'
    df = pd.read_csv(filename, skiprows=10)
    df = df[df['Asset Class'] == 'Equity']
    for c in ['Shares', 'Market Value', 'Notional Value']:
        df[c] = df[c].apply(lambda x: x.replace(',', '')).astype(float)

    df['Price'] = df['Price'].astype(float)

    df.set_index('Ticker', inplace=True)

    return df


def load_sly_holdings():
    latest_date = get_latest_index_date(ticker='SLY')
    if latest_date is None:
        print('no files')
        return

    filename = get_home_dir() + 'data/index_funds/SLY/SLY_holdings_' + latest_date.strftime('%Y-%m-%d') + '.xls'
    df = pd.read_excel(filename, skiprows=3, skipfooter=11)

    # remove non-equities
    df = df[df['Identifier'] != 'Unassigned']

    df.set_index('Identifier', inplace=True)

    return df


def load_vioo_holdings():
    latest_date = get_latest_index_date(ticker='VIOO')
    if latest_date is None:
        print('no files')
        return

    filename = get_home_dir() + 'data/index_funds/VIOO/VIOO_holdings_' + latest_date.strftime('%Y-%m-%d') + '.csv'
    df = pd.read_csv(filename, skiprows=4)
    df.drop(['Unnamed: 0', 'Unnamed: 10'], axis=1, inplace=True)
    missing_row_idx = np.where(df.isna().sum(axis=1) == df.shape[1])[0][0]
    df = df.iloc[:missing_row_idx]
    df.drop('Security depository receipt type', axis=1, inplace=True)
    df['Shares'] = df['Shares'].apply(lambda x: x.replace(',', '')).astype(float)
    df['Market value'] = df['Market value'].apply(lambda x: x.replace('$', '').replace(',', '')).astype(float)
    df['% of fund*'] = df['% of fund*'].astype(float)
    df['SEDOL'] = df['SEDOL'].apply(lambda x: x.replace('=', '').replace('"', ''))
    df['Ticker'] = df['Ticker'].apply(lambda x: x.strip())

    df.set_index('Ticker', inplace=True)

    return df


# import sys
# sys.path.append('../stock_prediction/code')
# import dl_quandl_EOD as dlq
#
# all_stocks_dfs = dlq.load_stocks()
#
#
# # get market cap of each stock in index for each unique date
# # need to get more historical data from wrds
# market_caps = OrderedDict()
# unique_dates = sorted(pd.concat([sp600_df['from'], sp600_df['thru']]).unique())[:-1]
# for d in unique_dates:
#     mcaps = []
#     for ticker in current_tickers[d]:
#         mcaps.append(all_stocks_dfs[ticker][''])
#     market_caps[d] =


if __name__ == '__main__':
    constituent_companies, constituent_tickers, unique_dates = get_historical_constituents_wrds()
    # # get list of tickers from latest WRDS data
    # 6-26-2018 was last time it was downloaded
    wrds_tickers = constituent_tickers['2018-06-26']
    wrds_set = set(wrds_tickers)
    ijr = load_ijr_holdings()
    sly = load_sly_holdings()
    vioo = load_vioo_holdings()
    ijr_set = set(ijr.index)
    sly_set = set(sly.index)
    vioo_set = set(vioo.index)
    # all currently have at least 3 differences -- ijr seems to differ the most
    ijr_set.difference(wrds_set)
    sly_set.difference(wrds_set)
    vioo_set.difference(wrds_set)

    df = load_sp600_files()
    current_set = set(df.index)
    current_set.difference(wrds_set)
    wrds_set.difference(current_set)

    print('latest constituents:')
    print(get_current_smallest_mkt_cap(df))

    # TODO:
    # see how often the bottom 20 companies have changed
    # need to get historical market caps first
    # for d in unique_dates:
    #     get_current_smallest_mkt_cap(df)

    # VIOO seems to be slower to remove companies that are not in the index;
    # companies that are not in the current set from barchart.com are only in vioo

    # overall, barchart seems to be a pretty good source

    # sorted_df = df.sort_values(by='Market Cap')
    # smallest = get_current_smallest_mkt_cap(df)
    # print(smallest)
