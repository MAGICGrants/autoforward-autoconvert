import ast
from requests.auth import HTTPDigestAuth
from datetime import datetime
import urllib.parse
import requests
import hashlib
import base64
import hmac
import json
import time

import env

def get_time() -> str:
    return f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]'

def request_electrum_rpc(rpc_url: str, method: str, params: list | dict = []):
    headers = {'content-type': 'application/json'}

    data = {
        'jsonrpc': '2.0',
        'id': 'curltext',
        'method': method,
        'params': params,
    }

    response =  requests.post(
        rpc_url,
        headers=headers,
        data=json.dumps(data),
        auth=(env.ELECTRUM_RPC_USERNAME, env.ELECTRUM_RPC_PASSWORD)
    )

    response_json = response.json()

    if 'error' in response_json:
        raise Exception(response_json)

    response.raise_for_status()

    return response_json['result']

def request_monero_rpc(method: str, params: dict = {}):
    headers = {'content-type': 'application/json'}

    data = {
        'jsonrpc': '2.0',
        'id': '0',
        'method': method,
        'params': params
    }

    response = requests.post(
        env.MONERO_RPC_URL,
        headers=headers,
        json=data,
        auth=HTTPDigestAuth(env.MONERO_RPC_USERNAME, env.MONERO_RPC_PASSWORD)
    )

    response_json = response.json()

    if 'error' in response_json:
        raise Exception(response_json)

    response.raise_for_status()

    return response_json['result']

def open_bitcoin_wallet():
    request_electrum_rpc(env.BTC_ELECTRUM_RPC_URL, 'load_wallet')

def open_litecoin_wallet():
    request_electrum_rpc(env.LTC_ELECTRUM_RPC_URL, 'load_wallet')

def open_monero_wallet() -> None:
    params = {'filename': 'foo', 'password': env.MONERO_WALLET_PASSWORD}
    request_monero_rpc('open_wallet', params)

def wait_for_rpc():
    print('Waiting for BTC Electrum RPC...')

    while 1:
        try:
            request_electrum_rpc(env.BTC_ELECTRUM_RPC_URL, 'getinfo')
            break
        except:
            time.sleep(10)
    
    print('Waiting for LTC Electrum RPC...')

    while 1:
        try:
            request_electrum_rpc(env.LTC_ELECTRUM_RPC_URL, 'getinfo')
            break
        except:
            time.sleep(10)
    
    print('Waiting for Monero RPC...')

    while 1:
        try:
            request_monero_rpc('getinfo')
            break
        except:
            time.sleep(10)

def wait_for_wallets():
    print('Waiting for Bitcoin wallet...')

    while 1:
        try:
            open_bitcoin_wallet()
            break
        except:
            time.sleep(10)
        
    print('Waiting for Litecoin wallet...')

    while 1:
        try:
            open_litecoin_wallet()
            break
        except:
            time.sleep(10)

    print('Waiting for Monero wallet...')

    while 1:                  
        try:
            request_monero_rpc('get_balance', {'account_index': 0})
            break
        except Exception as e:
            print('Failed to check Monero balance:', e)
            print('Attempting to open Monero wallet...')
        
        try:
            open_monero_wallet()
            break
        except Exception as e:
            print('Failed to open Monero wallet:', e)

        time.sleep(10)

def get_kraken_signature(url: str, payload: dict):
    postdata = urllib.parse.urlencode(payload)
    encoded = (str(payload['nonce']) + postdata).encode()
    message = url.encode() + hashlib.sha256(encoded).digest()
    mac = hmac.new(base64.b64decode(env.KRAKEN_API_SECRET), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()

def kraken_request(path: str, payload = {}) -> dict:
    payload['nonce'] = str(int(1000*time.time()))
    headers = {}
    headers['API-Key'] = env.KRAKEN_API_KEY
    headers['API-Sign'] = get_kraken_signature(path, payload)

    response = requests.post(
        'https://api.kraken.com' + path,
        headers=headers,
        data=payload
    )

    response_json = response.json()

    if response_json['error']:
        raise Exception(response_json)
    
    return response_json['result']
