"""Settings for the bot. Secrets come from the environment (or a local .env), never from this file."""
import os

from dotenv import load_dotenv

load_dotenv()


def _env_bool(name, default):
    """Parse a boolean env var. Only explicit 'off' values turn a flag off for DRY_RUN safety."""
    raw = os.environ.get(name)
    if raw is None or raw.strip() == '':
        return default
    return raw.strip().lower() not in ('0', 'false', 'no', 'off')


# DRY_RUN is ON by default: signals are computed from public market data and
# logged, but no orders are placed and no credentials are needed.
# Set DRY_RUN=0 (and all three credentials) to trade for real.
DRY_RUN = _env_bool('DRY_RUN', True)

# API credentials: https://support.kucoin.plus/hc/en-us/articles/360015102174-How-to-Create-an-API-
# Only required when DRY_RUN=0. Put them in .env (see .env.example), never in this file.
CREDENTIALS = {
    'key': os.environ.get('KUCOIN_API_KEY', ''),
    'secret': os.environ.get('KUCOIN_API_SECRET', ''),
    'pass': os.environ.get('KUCOIN_API_PASSPHRASE', ''),
}

# Your fee percentage. (.001 = .1% fee per trade.)
FEE = float(os.environ.get('FEE', 0.001))

# Amount of USDT the bot trades with per order
FUNDS = float(os.environ.get('FUNDS', 10))

# Pairing to trade. Default = Bitcoin/USDT
SYMBOL = os.environ.get('SYMBOL', 'BTC-USDT')

# Candlestick period used for TA. Longer period = longer term strategy.
# Options: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
PERIOD = os.environ.get('PERIOD', '5min')

# Seconds to wait between market-data polls
POLL_SECONDS = float(os.environ.get('POLL_SECONDS', 1))
