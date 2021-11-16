# Press Shift+F10 to execute.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from kucoin.client import Client
from kucoin.exceptions import KucoinAPIException
from time import sleep
import pandas as pd
import ta
import math
import config


client = Client(config.CREDENTIALS['key'], config.CREDENTIALS['secret'], config.CREDENTIALS['pass'])
# Available USDT balance in Kucoin trading account
balance = math.floor(float(client.get_accounts('USDT')[0]['available']) * 100) / 100.0


# Pulls trade data from the start of the day (UTC) to present
def getminutedata(symbol):
    global balance

    while True:
        try:
            df = pd.DataFrame(client.get_kline_data(symbol, '5min'))
            break
        except KucoinAPIException as e:
            print(e)
            sleep(5)
    df.columns = ['Time', 'Open', 'Close', 'High', 'Low', 'Amount', 'Volume']
    df = df.set_index('Time')
    df.index = pd.to_datetime(df.index, unit='s')
    df = df.astype(float)
    df = df.iloc[::-1]
    print(df.iloc[-1])
    balance = math.floor(float(client.get_accounts('USDT')[0]['available']) * 100) / 100.0
    print('Balance: $' + str(balance))
    return df


# Sell when MACD histogram is negative, buy when it's positive
# qty = string, a number equal to the USDT value of the position
def tradingstrat(symbol, qty, buyprice, buymacd, open_position=True):
    fee = str(int(qty) * config.FEE)

    # Sells if MACD Histogram (MACD - MACD Signal) is negative
	#
    # WIP (Strategy and implementation): 
    # Sells if MACD is .01 more than MACD at purchase.
    # Sells if trade profit is at least .6% before fees
    # This ensures that insignificant fluctuations don't create orders.
    if open_position:
        while True:
            sleep(1)
            df = getminutedata(symbol)
            print('Open position. MACDH: ')
            print(ta.trend.macd_diff(df.Close).iloc[-1])
            if ta.trend.macd_diff(df.Close).iloc[-1] < 0 \
                    and ta.trend.macd_diff(df.Close).iloc[-2] > 0 \
                    and (buyprice == 0 or float(df.iloc[-1].Close) - buyprice > (buyprice * 0.004)):
                # and (buymacd == 0 or float(ta.trend.macd(df.Close).iloc[-1]) - buymacd > 0.01) \
                order = client.create_market_order(symbol=symbol, side='sell', funds=qty)
                sellmacd = float(ta.trend.macd(df.Close).iloc[-1])
                sellprice = float(df.iloc[-1].Close)
		sleep(4)
                print('Sold $' + qty + ' worth of ' + symbol + ' at $' + str(sellprice))
                open_position = False
                break

    # Buys if MACD Histogram (MACD - MACD Signal) is positive 
	# Also buys if price has dropped 2% since last sale
	#
    # WIP (Strategy and implementation): 
	# Buys if MACD is .01 less than MACD at purchase.
    # Buys if cost is at least .6% less than revenue from last trade
    # This ensures that insignificant fluctuations don't create orders.
    while True:
        sleep(1)
        df = getminutedata(symbol)
        print('Closed position. MACDH:')
        print(ta.trend.macd_diff(df.Close).iloc[-1])
        if not open_position:
            if (
                    ta.trend.macd_diff(df.Close).iloc[-1] > 0 \
                    and ta.trend.macd_diff(df.Close).iloc[-2] < 0 \
                    # and (sellprice - float(df.iloc[-1].Close)) > (sellprice * 0.003) \
                    # and sellmacd - float(ta.trend.macd(df.Close).iloc[-1]) > 0.01 \
            ) or sellprice - float(df.iloc[-1].Close) > (sellprice * 0.02):
                order = client.create_market_order(symbol=symbol, side='buy', funds=qty)
                buymacd = float(ta.trend.macd(df.Close).iloc[-1])
                buyprice = float(df.iloc[-1].Close)
		sleep(4)
                print('Bought $' + qty + ' worth of ' + symbol + ' at $' + str(buyprice))
                open_position = True
                break
    return buyprice


if __name__ == '__main__':
    buyprice = 0
    buymacd = 0
    sellprice = 0
    sellmacd = 0
    funds = config.FUNDS
    symbol = config.SYMBOL
    while True:
        buyprice = tradingstrat(symbol, funds, buyprice, buymacd)
