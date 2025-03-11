from typing import Literal, cast
import traceback
import random
import time

import util
import env

# https://support.kraken.com/hc/en-us/articles/205893708-Minimum-order-size-volume-for-trading
order_min = {
    'XBT': 0.0001,
    'LTC': 0.05,
    'XMR': 0.03
}

def get_balance(asset: Literal['XBT', 'LTC', 'XMR']) -> str:
    balances = util.kraken_request('/0/private/Balance')
    balance = '0'

    if f'X{asset}' in balances:
        balance = balances[f'X{asset}']

    return balance

def get_orderbook(asset: Literal['XBT', 'LTC', 'XMR']):
    return util.kraken_request('/0/public/Depth?count=1', {'pair': f'{asset}USD'})[f'X{asset}ZUSD']

def attempt_sell(asset: Literal['XBT', 'XMR']):
    if balance < order_min[asset]:
        print(util.get_time(), f'Not enough {asset} balance to sell. (Balance: {balance}, Min order: {order_min[asset]})')
        return

    orderbook = get_orderbook(asset)
    mid_market_price = float(orderbook['bids'][0][0]) + ((float(orderbook['asks'][0][0]) - float(orderbook['bids'][0][0])) / 2) # Example 212.55+((212.72-212.55)/2) = 212.635
    limit_price = mid_market_price * (1-env.MAX_SLIPPAGE_PERCENT/100) # Example 212.365*(1-0.5/100) = 211.303175

    payload = {
        'ordertype': 'limit',
        'type': 'sell',
        'pair': f'{asset}USD',
        'volume': balance,
        'price': limit_price,
        'timeinforce': 'IOC', # Immediately fill order to extent possible, then kill
        'validate': true # Remove this after tested
    }

    util.kraken_request('/0/private/AddOrder', payload)
    print(util.get_time(), f'Selling up to {balance} at no less than {limit_price}')

while 1:
    for asset in ['XBT', 'LTC', 'XMR']:
        try:
            attempt_sell(cast(Literal['XBT', 'LTC', 'XMR'], asset))
        except Exception as e:
            print(util.get_time(), f'Error attempting to sell {asset}:')
            print(traceback.format_exc())

    delay = random.randint(30, 90)
    time.sleep(delay)
