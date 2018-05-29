# coding: utf8

# part of pybacktest package: https://github.com/ematvey/pybacktest

""" Set of data-loading helpers """

import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import os


def load_data_history(ticker='SPY', freq='15min', start='2014', end='2016'):
    """ Loads data from Yahoo. After loading it renames columns to shorter
    format, which is what Backtest expects.

    Set `adjust close` to True to correct all fields with with divident info
    provided by Yahoo via Adj Close field.

    Defaults are in place for convenience. """

    if isinstance(ticker, list):
        return pd.Panel(
            {t: load_data_history(
                ticker=t, start=start, adjust_close=adjust_close)
             for t in ticker})

    ts = TimeSeries(key='8YLDYU6Z9IAZNIS4')
    if freq == 'daily':
        data, meta_data = ts.get_daily(ticker, outputsize='full')
    elif freq == 'weekly':
        data, meta_data = ts.get_weekly(ticker, outputsize='full')
    elif freq == 'monthly':
        data, meta_data = ts.get_monthly(ticker, outputsize='full')
    else:
        data, meta_data = ts.get_intraday(ticker, interval=freq, outputsize='full') #supported 1min, 15min, 30min, 60min
    
    
    #r = data['Close']
    ohlc_cols = ['Open', 'High', 'Low', 'Close']
    #data[ohlc_cols] = data[ohlc_cols].mul(r, axis=0)
    data = data.rename(columns={'Open': 'O', 'High': 'H', 'Low': 'L',
                                'Close': 'C', 'Adj Close': 'AC',
                                'Volume': 'V'})
    return data
