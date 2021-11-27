from gemini.gemini_core import data, engine, helpers
from time import sleep
import config
import re
import ta
import datetime


def awesome_oscillator(df):
    df['ao'] = ta.momentum.awesome_oscillator(df['high'], df['low'])
    return df


def macd(df):
    df['macd'] = ta.trend.macd_diff(df['close'])
    return df


def logic(account, lookback):
    try:
        lookback = awesome_oscillator(lookback)
        lookback = macd(lookback)
        lookback = helpers.period(lookback)

        today = lookback.loc(0)
        yesterday = lookback.loc(-1)
        # Sell
        if (today['ao'] - yesterday['ao']) < 0 \
                and today['ao'] > 0.02:
            exit_price = today['close']
            for position in account.positions:
                if position.type_ == 'long':
                    account.close_position(position, 1, exit_price)

        # Buy
        if (today['ao'] - yesterday['ao']) > 0 \
                and today['ao'] < -0.01:
            risk = 1
            entry_price = today['close']
            entry_capital = account.buying_power * risk
            if entry_capital > 0:
                account.enter_position('long', entry_capital, entry_price)

    except Exception as e:
        print(e)

    pass


if __name__ == '__main__':
    # Initialize backtest engine with historical data
    symbol = config.SYMBOL.replace("-", '_')
    if (re.sub('\d+', '', config.PERIOD) == 'min'):
        period = re.sub('\D', '', config.PERIOD) + '-MIN'
    else:
        period = re.sub('\D', '', config.PERIOD) + '-HOUR'

    df = data.get_ltf_candles(symbol, period, "2021-08-01 00:00:00", "2021-11-26 00:00:00")
    backtest = engine.backtest(df)
    backtest.start(config.FUNDS, logic)
    backtest.results()
    backtest.chart()
