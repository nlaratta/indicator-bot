"""Pure MACD swing strategy. No network, no clock, no I/O, so it is easy to test."""
import pandas as pd
import ta

SELL_GAIN = 0.004   # sell only if price is >0.4% above the buy price
BUY_DROP = 0.02     # also buy if price is >2% below the last sale price


def decide(prices, open_position, buy_price=0.0, sell_price=0.0):
    """Return 'buy', 'sell' or None.

    prices: DataFrame with a 'Close' column (oldest first, newest last) or a Series of closes.
    open_position: True if the bot currently holds the asset.
    buy_price: price of the last buy (0 = unknown, e.g. a pre-existing position; gain check skipped).
    sell_price: price of the last sale, used for the 2% drop re-entry rule.
    """
    close = prices['Close'] if isinstance(prices, pd.DataFrame) else prices
    if len(close) < 2:
        return None
    hist = ta.trend.macd_diff(close)
    now, prev = hist.iloc[-1], hist.iloc[-2]
    last = float(close.iloc[-1])

    if open_position:
        # MACD histogram crosses below zero and the trade is up at least 0.4%
        if now < 0 and prev > 0 and (buy_price == 0 or last - buy_price > buy_price * SELL_GAIN):
            return 'sell'
        return None

    # MACD histogram crosses above zero, or price fell more than 2% since the last sale
    if (now > 0 and prev < 0) or (sell_price and sell_price - last > sell_price * BUY_DROP):
        return 'buy'
    return None
