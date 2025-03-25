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

def get_balance(settlement_kraken_ticker) -> str:
    balances = util.kraken_request('/0/private/Balance')
    balance = '0'

    if f'{settlement_kraken_ticker}' in balances:
        balance = balances[f'{settlement_kraken_ticker}']

    return balance

def get_orderbook(asset: Literal['XBT', 'LTC', 'XMR'], settlement_currency='USD', settlement_kraken_ticker='ZUSD'):
    return util.kraken_request('/0/public/Depth?count=1', {'pair': f'{asset}{settlement_currency}'})[f'X{asset}{settlement_kraken_ticker}'] #TODO check

def make_trade(orderbook, payload):
    mid_market_price = float(orderbook['bids'][0][0]) + ((float(orderbook['asks'][0][0]) - float(orderbook['bids'][0][0])) / 2) # Example 212.55+((212.72-212.55)/2) = 212.635
    limit_price = mid_market_price * (1-env.MAX_SLIPPAGE_PERCENT/100) # Example 212.365*(1-0.5/100) = 211.303175
    payload['price'] = limit_price
    util.kraken_request('/0/private/AddOrder', payload)
    print(util.get_time(), f'Selling up to {balance} for pair {payload['pair']} at no less than {limit_price}')

def attempt_sell(asset: Literal['XBT', 'LTC', 'XMR']):
    balance = get_balance(f'X{asset}')
    if balance < order_min[asset]:
        print(util.get_time(), f'Not enough {asset} balance to sell. (Balance: {balance}, Min order: {order_min[asset]})')
        return
    
    settlement_currency = env.SETTLEMENT_CURRENCY
    # https://support.kraken.com/hc/en-us/articles/360001206766-Bitcoin-currency-code-XBT-vs-BTC
    if settlement_currency in ['AUD', 'CAD', 'EUR', 'GBP', 'JPY', 'USD']:
        settlement_kraken_ticker = 'Z' + settlement_currency
    elif settlement_currency in ['ETC', 'ETH', 'LTC', 'MLN', 'REP', 'XBT', 'XDG', 'XLM', 'XMR', 'XRP', 'ZEC']:
        settlement_kraken_ticker = 'X' + settlement_currency
    else:
        settlement_kraken_ticker = settlement_currency

    payload = {
        'ordertype': 'limit',
        'type': 'sell',
        'pair': f'{asset}{settlement_currency}',
        'volume': balance,
        'timeinforce': 'IOC', # Immediately fill order to extent possible, then cancel
        'validate': true # Remove this after tested
    }

    if settlement_currency != asset:
        try:
            orderbook = get_orderbook(asset, settlement_currency, settlement_kraken_ticker)
            if orderbook.status_code == 200:
                make_trade(orderbook, payload)
            else:
                raise Exception
        except:
            print(f'No direct trading pair for {payload['pair']}, trying USD')
            payload['pair'] = f'{asset}USD'
            orderbook = get_orderbook(asset)
            make_trade(orderbook, payload)
            payload['pair'] = f'{settlement_currency}USD'
            payload['balance'] = get_balance('ZUSD')
            orderbook = get_orderbook(settlement_currency)
            make_trade(orderbook, payload)

    else:
        print(f'Not converting {asset} since it is already in the settlement currency')

while 1:
    for asset in ['XBT', 'LTC', 'XMR']:
        try:
            attempt_sell(cast(Literal['XBT', 'LTC', 'XMR'], asset))
        except Exception as e:
            print(util.get_time(), f'Error attempting to sell {asset}:')
            print(traceback.format_exc())

    delay = random.randint(30, 90)
    time.sleep(delay)
