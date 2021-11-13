# Crypto Indicator Swing Bot (Kucoin) #
Swing trading bot that attempts to capitalize on short term reversal events using the MACD indicator. 

Currently requires that you already have an open position in your desired trading pair.

## Strategy ##

- Sells if MACD crosses below the MACD signal line and price has risen by .4% since purchase.
- Buys if MACD crosses above the MACD signal line.
	- Also buys if price drops by 2% since last sale.

## Setup ##

1. Follow [https://support.kucoin.plus/hc/en-us/articles/360015102174-How-to-Create-an-API-](https://support.kucoin.plus/hc/en-us/articles/360015102174-How-to-Create-an-API- "Kucoin API guide") to create a Kucoin API.
2. Open config.py in a text editor.
	1. Replace fields in credentials with your api-key, api-secret, and api-passphrase.
	1. Modify fee percentage, change trading pair, and specify the amount of funds in USDT allowed by the bot to trade with.

## Running the bot ##

**On Windows:**

1. Execute the 'run.bat' file.

**On Linux:**

1. Install virtualenv, create and activate a Python3 virtual environment    :

    `pip install virtualenv`  
	`python3 -m venv env`  
	`source env/bin/activate`  

2. Install requirements:

    `pip install -r requirements.txt`

3. Run the program:

    `python main.py`

# DISCLAIMER #

I am not responsible for any losses incurred through the use of this bot.

In it's current state, the bot is little more than a foundation to build off of. New trading strategies will be implemented with updates, along with a more dynamic interface.
