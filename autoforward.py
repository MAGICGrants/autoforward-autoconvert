import requests
import json
from time import sleep
from datetime import datetime
from requests.auth import HTTPDigestAuth

BITCOIN_RPC_URL = os.getenv('BITCOIN_RPC_URL')
BITCOIN_RPC_USERNAME = os.getenv('BITCOIN_RPC_USERNAME')
BITCOIN_RPC_PASSWORD = os.getenv('BITCOIN_RPC_PASSWORD')
MONERO_RPC_URL = os.getenv('MONERO_RPC_URL')
MONERO_RPC_USERNAME = os.getenv('MONERO_RPC_USERNAME')
MONERO_RPC_PASSWORD = os.getenv('MONERO_RPC_PASSWORD')
KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY')
KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET')

def get_time() -> str:
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'

def get_kraken_signature(url: str, payload: dict):
    postdata = urllib.parse.urlencode(payload)
    encoded = (str(payload['nonce']) + postdata).encode()
    message = url.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(KRAKEN_API_SECRET), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(path: str, payload: dict) -> requests.Request:
    headers = {}
    headers['API-Key'] = KRAKEN_API_KEY
    headers['API-Sign'] = get_kraken_signature(path, payload)             
    
    return requests.post(
        'https://api.kraken.com/0' + path,
        headers=headers,
        data=payload
    ).json()['result']

def request_bitcoin_rpc(method: str, params: list[str] = []) -> any:
    headers = {'content-type': 'application/json'}

    data = {
        'jsonrpc': '1.0',
        'id': 'python-bitcoin',
        'method': 'getbalance',
        'params': params,
    }

    return requests.post(
        BITCOIN_RPC_URL,
        headers=headers,
        data=json.dumps(data),
        auth=(BITCOIN_RPC_USERNAME, BITCOIN_RPC_PASSWORD)
    ).json()['result']

def request_monero_rpc(method: str, params: dict[str, any] = {}) -> any:
    headers = {'content-type': 'application/json'}

    data = {
        'jsonrpc': '2.0',
        'id': '0',
        'method': method,
        'params': params
    }

    return requests.post(
        MONERO_RPC_URL,
        headers=headers,
        json=data,
        auth=HTTPDigestAuth(MONERO_RPC_USERNAME, MONERO_RPC_PASSWORD)
    ).json()['result']

def get_bitcoin_fee_rate() -> int:
    return requests.get('https://mempool.space/api/v1/fees/recommended').json()['halfHourFee']

def get_bitcoin_balance() -> float:
    return request_bitcoin_rpc('getbalance')

def send_bitcoin(address: str, amount: float, fee_rate: int) -> None:
    # https://bitcoincore.org/en/doc/24.0.0/rpc/wallet/sendtoaddress/
    params = [address, amount, null, null, true, true, null, null, null, fee_rate]
    request_bitcoin_rpc('sendtoaddress', params)

def get_monero_balance() -> float:
    params = {'account_index': 0}

    return request_monero_rpc('get_balance', params)['balance']

def sweep_all_monero(address: str) -> None:
    params = {
        'account_index': 0,
        'address': address,
    }

    request_monero_rpc('sweep_all', params)

def get_new_kraken_address(asset: 'XBT' | 'XMR') -> str:
    payload = {
        'asset': asset,
        'method': 'Bitcoin' if asset == 'XBT' else 'Monero'
    }

    result = kraken_request('/private/DepositAddresses', payload)
    adddress = next((address['address'] for address in result['result'] if address['new']), None)

    return address

while 1:
    try:
        balance = get_bitcoin_balance()

        if balance > 0:
            fee_rate = get_bitcoin_fee_rate()
            address = get_new_kraken_address('XBT')
            amount = balance
            send_bitcoin(address, amount, fee_rate)
            print(get_time(), f'Sent {amount} BTC to {address}!')
        else:
            print(get_time(), 'No bitcoin balance to sweep.')
    except Exception as e:
        print(get_time(), 'Error autoforwarding Bitcoin:', e)

    try:
        balance = get_monero_balance()

        if balance > 0:
            address = get_new_kraken_address('XMR')
            sweep_all_monero(address)
        else:
            print(get_time(), 'No bitcoin balance to sweep.')
    except Exception as e:
        print(get_time(), 'Error autoforwarding Monero:', e)

    sleep(60 * 5)
