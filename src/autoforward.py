from typing import Literal, cast
from time import sleep
import traceback
import requests
import json

from constants import MIN_BITCOIN_SEND_AMOUNT, MIN_MONERO_SEND_AMOUNT
import util
import env

def get_bitcoin_fee_rate() -> int:
    return requests.get('https://mempool.space/api/v1/fees/recommended').json()['halfHourFee']

def set_bitcoin_fee_rate(rate: int):
    util.request_electrum_rpc('setconfig', ['dynamic_fees', False])
    util.request_electrum_rpc('setconfig', ['fee_per_kb', rate * 1000])

def get_bitcoin_balance() -> float:
    return float(util.request_electrum_rpc('getbalance')['confirmed'])

def create_psbt(destination_address: str) -> str:
    params = {
        'destination': destination_address,
        'amount': '!',
        'unsigned': True # This way we can get the input amounts
    }

    return util.request_electrum_rpc('payto', params)

def get_psbt_data(psbt: str) -> dict:
    return util.request_electrum_rpc('deserialize', [psbt])

def get_total_psbt_fee(psbt_data: dict) -> float:
    inputs_sum_sats = 0
    outputs_sum_sats = 0

    for _input in psbt_data['inputs']:
        inputs_sum_sats += cast(int, _input['value_sats'])
    
    for _output in psbt_data['outputs']:
        outputs_sum_sats += cast(int, _output['value_sats'])

    total_fee_sats = inputs_sum_sats - outputs_sum_sats
    total_fee_btc = total_fee_sats / 100000000
    return total_fee_btc

def sign_psbt(psbt: str) -> str:
    return cast(str, util.request_electrum_rpc('signtransaction', [psbt]))

def broadcast_bitcoin_tx(signed_tx: str):
    util.request_electrum_rpc('broadcast', [signed_tx])

def get_monero_balance() -> float:
    params = {'account_index': 0}
    return util.request_monero_rpc('get_balance', params)['balance'] / 1000000000000

def sweep_all_monero(address: str) -> None:
    params = {
        'account_index': 0,
        'address': address,
    }

    util.request_monero_rpc('sweep_all', params)

def get_new_kraken_address(asset: Literal['XBT', 'XMR']) -> str:
    payload = {
        'asset': asset,
        'method': 'Bitcoin' if asset == 'XBT' else 'Monero'
    }

    result = util.kraken_request('/0/private/DepositAddresses', payload)

    first_new_address = next((addr for addr in result if addr.get('new', False)), None)
    if first_new_address:
        return(first_new_address['address'])
    else:
        payload = {
            'asset': asset,
            'method': 'Bitcoin' if asset == 'XBT' else 'Monero',
            'new': True
        }
        result = util.kraken_request('/0/private/DepositAddresses', payload)
        first_new_address = next((addr for addr in result if addr.get('new', False)), None)
        return(first_new_address['address'])

    raise Exception(f'Kraken did not return a new address: {json.dumps(result, indent=2)}')

def attempt_bitcoin_autoforward():
    balance = get_bitcoin_balance()

    if balance < MIN_BITCOIN_SEND_AMOUNT:
        print(util.get_time(), 'Not enough bitcoin balance to autoforward.')
        return

    fee_rate = get_bitcoin_fee_rate()
    set_bitcoin_fee_rate(fee_rate)
    address = get_new_kraken_address('XBT')

    try:
        psbt = create_psbt(address)
    except requests.exceptions.HTTPError as http_error:
        response_json = cast(dict, http_error.response.json())

        if response_json.get('error', {}).get('data', {}).get('exception', '') == 'NotEnoughFunds()':
            print(util.get_time(), f'Not autoforwarding due to high transaction fee.')
            return                 

        raise http_error

    psbt_data = get_psbt_data(psbt)
    total_fee = get_total_psbt_fee(psbt_data)
    amount = balance

    if total_fee / amount * 100 > env.MAX_BITCOIN_FEE_PERCENT:
        print(util.get_time(), f'Not autoforwarding due to high transaction fee.')
        return

    signed_tx = sign_psbt(psbt)
    broadcast_bitcoin_tx(signed_tx)

    print(util.get_time(), f'Autoforwarded {amount} BTC to {address}!')

def attempt_monero_autoforward():
    balance = get_monero_balance()

    if balance < MIN_MONERO_SEND_AMOUNT:
        print(util.get_time(), 'Not enough monero balance to autoforward.')
        return

    address = get_new_kraken_address('XMR')
    sweep_all_monero(address)
    print(util.get_time(), f'Autoforwarded {balance} XMR to {address}!')

util.wait_for_rpc()
util.wait_for_wallets()

while 1: 
    try:
        attempt_bitcoin_autoforward()
    except Exception as e:
        print(util.get_time(), 'Error autoforwarding bitcoin:')
        print(traceback.format_exc())

    try:
        attempt_monero_autoforward()
    except Exception as e:
        print(util.get_time(), 'Error autoforwarding monero:')
        print(traceback.format_exc())

    sleep(60 * 5)

