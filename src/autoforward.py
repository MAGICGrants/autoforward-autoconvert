from typing import Literal, cast
from time import sleep
import traceback
import requests
import json

from constants import MIN_BITCOIN_SEND_AMOUNT, MIN_LITECOIN_SEND_AMOUNT, MIN_MONERO_SEND_AMOUNT
import util
import env

ElectrumCoin = Literal['btc', 'ltc', 'ltc-mweb']

def get_fee_rate(coin: ElectrumCoin) -> int:
    coin_to_source: dict[ElectrumCoin, str] = {
        'btc': env.BITCOIN_FEE_SOURCE,
        'ltc': env.LITECOIN_FEE_SOURCE,
        'ltc-mweb': env.LITECOIN_FEE_SOURCE
    }

    coin_to_rate: dict[ElectrumCoin, str] = {
        'btc': env.BITCOIN_FEE_RATE,
        'ltc': env.LITECOIN_FEE_RATE,
        'ltc-mweb': env.LITECOIN_FEE_RATE
    }

    source = coin_to_source[coin]
    rate = coin_to_rate[coin]

    return requests.get(source).json()[rate]

def set_electrum_fee_rate(coin: ElectrumCoin, rate: int, dynamic: bool):
    if dynamic:  # Fall back to the Electrum rate if there is an issue
        util.request_electrum_rpc(coin, 'setconfig', ['dynamic_fees', True])
    else:
        util.request_electrum_rpc(coin, 'setconfig', ['dynamic_fees', False])
        util.request_electrum_rpc(coin, 'setconfig', ['fee_per_kb', rate * 1000])

def get_electrum_balance(coin: ElectrumCoin) -> float:
    return float(util.request_electrum_rpc(coin, 'getbalance')['confirmed'])

def create_psbt(coin: ElectrumCoin, destination_address: str, unsigned = True) -> str:
    params = {
        'destination': destination_address,
        'amount': '!',
        'unsigned': unsigned # This way we can get the input amounts
    }

    return util.request_electrum_rpc(coin, 'payto', params)

def get_psbt_data(coin: ElectrumCoin, psbt: str) -> dict:
    return util.request_electrum_rpc(coin, 'deserialize', [psbt])

def get_total_psbt_fee(psbt_data: dict) -> float:
    inputs_sum_sats = 0
    outputs_sum_sats = 0

    for _input in psbt_data['inputs']:
        inputs_sum_sats += cast(int, _input['value_sats'])
    
    for _output in psbt_data['outputs']:
        outputs_sum_sats += cast(int, _output['value_sats'])

    total_fee_sats = inputs_sum_sats - outputs_sum_sats
    total_fee = total_fee_sats / 100000000
    return total_fee

def sign_psbt(coin: ElectrumCoin, psbt: str) -> str:
    return cast(str, util.request_electrum_rpc(coin, 'signtransaction', [psbt]))

def broadcast_electrum_tx(coin: ElectrumCoin, signed_tx: str):
    util.request_electrum_rpc(coin, 'broadcast', [signed_tx])

def get_monero_balance() -> float:
    params = {'account_index': 0}
    return util.request_monero_rpc('get_balance', params)['balance'] / 1000000000000

def sweep_all_monero(address: str) -> None:
    params = {
        'account_index': 0,
        'address': address,
    }

    util.request_monero_rpc('sweep_all', params)

def get_new_kraken_address(asset: Literal['btc', 'ltc', 'xmr']) -> str:
    sym_to_name = {
        "btc": "Bitcoin",
        "ltc": "Litecoin",
        "xmr": "Monero"
    }

    payload: dict[str, str | bool] = {
        'asset': asset,
        'method': sym_to_name[asset]
    }

    result = util.kraken_request('/0/private/DepositAddresses', payload)

    first_new_address = next((addr for addr in result if addr.get('new', False)), None)
    if first_new_address:
        return first_new_address['address']
    else:
        payload['new'] = True
        result = util.kraken_request('/0/private/DepositAddresses', payload)
        first_new_address = next((addr for addr in result if addr.get('new', False)), None)
        if first_new_address:
            return first_new_address['address']

    raise Exception(f'Kraken did not return a new address: {json.dumps(result, indent=2)}')

def attempt_electrum_autoforward(coin: ElectrumCoin):
    coin_upper = coin.upper()
    balance = get_electrum_balance(coin)

    coin_to_min_send: dict[ElectrumCoin, float] = {
        'btc': MIN_BITCOIN_SEND_AMOUNT,
        'ltc': MIN_LITECOIN_SEND_AMOUNT,
        'ltc-mweb': MIN_LITECOIN_SEND_AMOUNT
    }

    min_send = coin_to_min_send[coin]

    if balance < MIN_BITCOIN_SEND_AMOUNT:
        print(util.get_time(), f'Not enough {coin_upper} balance to autoforward. (Balance: {balance}, Min. send: {min_send})')
        return

    try:
        fee_rate = get_fee_rate(coin)
        set_electrum_fee_rate(coin, fee_rate, dynamic=False)
    except:
        set_electrum_fee_rate(coin, rate=0, dynamic=True)
    address = get_new_kraken_address(coin if coin != 'ltc-mweb' else 'ltc')

    # Electrum-ltc doesn't support deserializing mweb transactions, so we can't check total fee
    if coin != 'ltc-mweb':
        try:
            psbt = create_psbt(coin, address)
        except requests.exceptions.HTTPError as http_error:
            response_json = cast(dict, http_error.response.json())

            if response_json.get('error', {}).get('data', {}).get('exception', '') == 'NotEnoughFunds()':
                print(util.get_time(), f'Not autoforwarding due to high transaction fee.')
                return                 

            raise http_error

        psbt_data = get_psbt_data(coin, psbt)
        total_fee = get_total_psbt_fee(psbt_data)
        amount = balance

        if total_fee / amount * 100 > env.MAX_NETWORK_FEE_PERCENT:
            print(util.get_time(), f'Not autoforwarding due to high transaction fee ({total_fee} {coin_upper}).')
            return

        signed_tx = sign_psbt(coin, psbt)
    else:
        signed_tx = create_psbt(coin, address, unsigned=False)

    broadcast_electrum_tx(coin, signed_tx)
    print(util.get_time(), f'Autoforwarded {amount} {coin_upper} to {address}!')

def attempt_monero_autoforward():
    balance = get_monero_balance()

    if balance < MIN_MONERO_SEND_AMOUNT:
        print(util.get_time(), f'Not enough XMR balance to autoforward. (Balance: {balance}, Min Send: {MIN_MONERO_SEND_AMOUNT})')
        return

    address = get_new_kraken_address('xmr')
    sweep_all_monero(address)
    print(util.get_time(), f'Autoforwarded {balance} XMR to {address}!')

util.wait_for_rpc()
util.wait_for_wallets()

while 1: 
    try:
        attempt_electrum_autoforward('btc')
    except Exception as e:
        print(util.get_time(), 'Error autoforwarding Bitcoin:')
        print(traceback.format_exc())

    try:
        attempt_electrum_autoforward('ltc')
    except Exception as e:
        print(util.get_time(), 'Error autoforwarding litecoin:')
        print(traceback.format_exc())
    
    # try:
    #     attempt_electrum_autoforward('ltc-mweb')
    # except Exception as e:
    #     print(util.get_time(), 'Error autoforwarding Litecoin MWEB:')
    #     print(traceback.format_exc())

    try:
        attempt_monero_autoforward()
    except Exception as e:
        print(util.get_time(), 'Error autoforwarding Monero:')
        print(traceback.format_exc())

    sleep(60 * 5)

