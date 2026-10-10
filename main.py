"""KuCoin MACD swing bot. Runs in DRY_RUN mode (log only) unless DRY_RUN=0 with credentials set."""
import argparse
import math
import sys
from time import sleep

import pandas as pd
import requests
from kucoin.client import Client
from kucoin.exceptions import KucoinAPIException

import config
from strategy import decide

KLINE_COLUMNS = ['Time', 'Open', 'Close', 'High', 'Low', 'Amount', 'Volume']


def require_live_credentials():
    """Fail fast with a clear message if live trading is requested without credentials."""
    names = {'key': 'KUCOIN_API_KEY', 'secret': 'KUCOIN_API_SECRET', 'pass': 'KUCOIN_API_PASSPHRASE'}
    missing = [env for k, env in names.items() if not config.CREDENTIALS.get(k)]
    if missing:
        sys.exit('Live trading (DRY_RUN=0) needs all three credentials. Missing: '
                 + ', '.join(missing) + '. Set them in .env (see .env.example), or use DRY_RUN=1.')


def make_client():
    # Public market data needs no credentials, so dry run uses an unauthenticated client.
    if config.DRY_RUN:
        return Client()
    require_live_credentials()
    return Client(config.CREDENTIALS['key'], config.CREDENTIALS['secret'], config.CREDENTIALS['pass'])


def get_usdt_balance(client):
    return math.floor(float(client.get_accounts('USDT')[0]['available']) * 100) / 100.0


def get_minute_data(client, symbol, period):
    """Candles from the start of the day (UTC) to now, oldest first, indexed by time."""
    df = pd.DataFrame(client.get_kline_data(symbol, period), columns=KLINE_COLUMNS)
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index.astype(float), unit='s')
    df = df.astype(float)
    return df.iloc[::-1]


def run(client, once=False):
    symbol, qty = config.SYMBOL, str(config.FUNDS)
    mode = 'DRY RUN (no orders will be placed)' if config.DRY_RUN else 'LIVE'
    print(f'Starting {mode}: {symbol} {config.PERIOD}, ${qty} per order')
    # Like the original bot, assume an open position exists with unknown buy price.
    open_position, buy_price, sell_price = True, 0.0, 0.0
    while True:
        try:
            df = get_minute_data(client, symbol, config.PERIOD)
        except (KucoinAPIException, requests.RequestException) as e:
            if once:
                raise
            print(e)
            sleep(5)
            continue
        if df.empty:
            print('No candles returned.')
            if once:
                return None
            sleep(config.POLL_SECONDS)
            continue
        last = float(df.iloc[-1].Close)
        print(df.iloc[-1])
        if not config.DRY_RUN:
            print('Balance: $' + str(get_usdt_balance(client)))
        signal = decide(df, open_position, buy_price, sell_price)
        print(f'{"Open" if open_position else "Closed"} position, last close {last}, signal: {signal}')

        if signal:
            side = signal
            if config.DRY_RUN:
                print(f'[DRY RUN] WOULD {side.upper()} ${qty} of {symbol} at ${last}')
            else:
                client.create_market_order(symbol=symbol, side=side, funds=qty)
                sleep(4)
                print(f'{side.capitalize()} ${qty} worth of {symbol} at ${last}')
            if side == 'sell':
                open_position, sell_price = False, last
            else:
                open_position, buy_price = True, last
        if once:
            return signal
        sleep(config.POLL_SECONDS)


def main(argv=None):
    parser = argparse.ArgumentParser(description='KuCoin MACD swing bot (DRY_RUN by default)')
    parser.add_argument('--once', action='store_true', help='fetch data, evaluate one signal, then exit')
    args = parser.parse_args(argv)
    client = make_client()
    try:
        run(client, once=args.once)
    except KeyboardInterrupt:
        print('\nStopped.')


if __name__ == '__main__':
    main()
