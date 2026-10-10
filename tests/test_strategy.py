import pandas as pd
import pytest
import ta

from strategy import decide


def series(values):
    return pd.Series(values, dtype=float)


def hist(close):
    return ta.trend.macd_diff(close)


def find_cross(make, direction):
    """Find the shortest series from make(n) whose last bar is a fresh histogram cross."""
    for n in range(40, 200):
        close = make(n)
        h = hist(close)
        if direction == 'up' and h.iloc[-1] > 0 > h.iloc[-2]:
            return close
        if direction == 'down' and h.iloc[-1] < 0 < h.iloc[-2]:
            return close
    raise AssertionError('no cross found')


def decline_then_rise(n):
    return series([200 - i for i in range(60)] + [141 + 3 * i for i in range(n - 60)])


def rise_then_fall(n):
    return series([100 + i for i in range(60)] + [159 - 3 * i for i in range(n - 60)])


def test_macd_cross_up_buys():
    close = find_cross(decline_then_rise, 'up')
    assert decide(close, open_position=False, sell_price=0) == 'buy'


def test_no_buy_without_cross_while_open_or_flat():
    close = series([100.0] * 80)
    assert decide(close, open_position=False, sell_price=100) is None


def test_cross_down_with_gain_sells():
    close = find_cross(rise_then_fall, 'down')
    last = close.iloc[-1]
    assert decide(close, True, buy_price=last * 0.99) == 'sell'   # up >0.4%


def test_cross_down_without_enough_gain_holds():
    close = find_cross(rise_then_fall, 'down')
    last = close.iloc[-1]
    assert decide(close, True, buy_price=last * 0.999) is None    # up only 0.1%
    assert decide(close, True, buy_price=last * 1.05) is None     # underwater


def test_unknown_buy_price_skips_gain_check():
    close = find_cross(rise_then_fall, 'down')
    assert decide(close, True, buy_price=0) == 'sell'


def test_two_percent_drop_since_sale_buys():
    # Flat series: no MACD cross, but price is >2% under the last sale price
    close = series([100.0] * 80)
    assert decide(close, False, sell_price=103.0) == 'buy'
    assert decide(close, False, sell_price=101.0) is None


def test_no_sell_signal_without_cross_even_with_gain():
    close = series([100.0] * 80)
    assert decide(close, True, buy_price=50.0) is None


def test_accepts_dataframe_and_short_input():
    close = find_cross(decline_then_rise, 'up')
    df = pd.DataFrame({'Close': close, 'Open': close})
    assert decide(df, False) == 'buy'
    assert decide(series([1.0]), True) is None
    assert decide(series([1.0, 2.0, 3.0]), False, sell_price=10.0) == 'buy'
