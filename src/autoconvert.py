import time
import random
from typing import Literal, cast

from util import *

MAX_SLIPPAGE_PERCENT = 1

order_min = {
    'XBT': 0.0001,
    'XMR': 0.03
}

def get_balance(asset: Literal['XBT', 'XMR']) -> str:
    balances = kraken_request('/0/private/Balance')
    balance = '0'

    if f'X{asset}' in balances:
        balance = balances[f'X{asset}']

    return balance

def get_bids(asset: Literal['XBT', 'XMR']):
    return kraken_request('/0/public/Depth', {'pair': f'{asset}USD'})[f'X{asset}ZUSD']['bids']
    
def attempt_sell(asset: Literal['XBT', 'XMR']):
    balance = float(get_balance(asset))
    to_sell_amount = 0

    if balance < order_min[asset]:
        print(get_time(), f'No enough {asset} balance to sell.')
        return

    bids = get_bids(asset)
    market_price = float(bids[0][0])

    for bid in bids:
        bid_price = float(bid[0]) # Example 161.05
        bid_volume = float(bid[1])
        slippage_percent = ((market_price - bid_price) / market_price) * 100 # Example ((161.06-161.05)/161.06)*100 = 0.0062088662610207

        # Break loop if slippage is too high
        if slippage_percent > MAX_SLIPPAGE_PERCENT:
            break

        # Otherwise, add the bid_volume to the to_sell_amount
        to_sell_amount += bid_volume

    if to_sell_amount > balance:
        to_sell_amount = balance

    # Sell asset if amount is greater than the minimum order amount
    # Otherwise, it means that we could not get to the minimum amount under the max slippage
    if to_sell_amount > order_min[asset]:
        payload = {
            'ordertype': 'market',
            'type': 'sell',
            'pair': f'{asset}USD',
            'volume': to_sell_amount,
        }

        kraken_request('/0/private/AddOrder', payload)
        print(get_time(), f'Sold {to_sell_amount} {asset}!')
    else:
        print(get_time(), f'Not selling {asset} due to high slippage.')

while 1:
    for asset in ['XBT', 'XMR']:
        try:
            attempt_sell(cast(Literal['XBT', 'XMR'], asset))
        except Exception as e:
            print(get_time(), f'Error attempting to sell {asset}:', e)

    delay = random.randint(30, 90)
    time.sleep(delay)