# coding: utf8

# part of pybacktest package: https://github.com/ematvey/pybacktest

""" Essential functions for translating signals into trades.
Usable both in backtesting and production.

"""

import pandas


def signals_to_positions(signals, init_pos=0,
                         mask=('Buy', 'Sell', 'Short', 'Cover')):
    """
    Translate signal dataframe into positions series (trade prices aren't
    specified.
    WARNING: In production, override default zero value in init_pos with
    extreme caution.
    """
    long_en_sv, long_ex_sv, short_en_sv, short_ex_sv, long_en_uv, long_ex_uv, short_en_uv, short_ex_uv  = mask
    pos = init_pos
    ps = pandas.Series(0., index=signals.index)
    for t, sig in signals.iterrows():
        # check svxy exit signals
        if pos != 0:  # if in position
            if pos > 0 and sig[long_ex_sv]:  # if exit long signal
                pos -= sig[long_ex_sv]
            elif pos < 0 and sig[short_ex_sv]:  # if exit short signal
                pos += sig[short_ex_sv]
        # check entry (possibly right after exit)
        if pos == 0:
            if sig[long_en_sv]:
                pos += sig[long_en_sv]
            elif sig[short_en_sv]:
                pos -= sig[short_en_sv]
        
         # check uvxy exit signals
        if pos != 0:  # if in position
            if pos > 0 and sig[long_ex_uv]:  # if exit long signal
                pos -= sig[long_ex_uv]
            elif pos < 0 and sig[short_ex_uv]:  # if exit short signal
                pos += sig[short_ex_uv]
        # check entry (possibly right after exit)
        if pos == 0:
            if sig[long_en_uv]:
                pos += sig[long_en_uv]
            elif sig[short_en_uv]:
                pos -= sig[short_en_uv]
        ps[t] = pos
    return ps[ps != ps.shift()]


def trades_to_equity(trd):
    """
    Convert trades dataframe (cols [vol, price, pos]) to equity diff series
    """

    def _cmp_fn(x):
        if x > 0:
            return 1
        elif x < 0:
            return -1
        else:
            return 0

    psig = trd.pos.apply(_cmp_fn)
    closepoint = psig != psig.shift()
    e = (trd.vol * trd.price).cumsum()[closepoint] - \
        (trd.pos * trd.price)[closepoint]
    e = e.diff()
    e = e.reindex(trd.index).fillna(value=0)
    e[e != 0] *= -1
    return e 

def extract_frame(dataobj, ext_mask, int_mask): #int = BuySV, ext = buySV
    df = {}
    for f_int, f_ext in zip(int_mask, ext_mask):
        obj1 = dataobj.get(f_ext)
        if isinstance(obj1, pandas.Series):
            df1[f_int] = obj1
        else:
            df1[f_int] = None
    
    for f_int, f_ext in zip(int_mask, ext_mask):
        obj2 = dataobj.get(f_ext)
        if isinstance(obj2, pandas.Series) and obj1 != dataobj.get(f_ext):
            df2[f_int] = obj2
        else:
            df2[f_int] = None
            
    if (any([isinstance(x, pandas.Series) for x in list(df1.values())]) and
    any([isinstance(y, pandas.Series) for y in list(df2.values())])):
        return pandas.DataFrame(df1), pandas.DataFrame(df2)
    
    return None


class Slicer(object):
    def __init__(self, target, obj):
        self.target = target
        self.__len__ = obj.__len__

    def __getitem__(self, x):
        return self.target(x)
