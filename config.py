# Getting API credentials: https://support.kucoin.plus/hc/en-us/articles/360015102174-How-to-Create-an-API-
CREDENTIALS = {'key': 'insert-api-key',
                'secret': 'insert-api-secret',
                'pass': 'insert-api-passphrase'}


# Change this to reflect your fee percentage. (.001 = .1% fee per trade.)
FEE = 0.001 

# Change this to the amount of USDT you want the bot to trade with
FUNDS = 10

# Change this to the pairing you want to trade. Default = Bitcoin/USDT
SYMBOL = 'BTC-USDT'

# Candlestick period used for TA. Longer period = longer term strategy.
# Options: 1min, 3min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
PERIOD = '5min'