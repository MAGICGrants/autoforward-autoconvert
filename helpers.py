import urllib
import hashlib
import hmac
import base64
import requests

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

def kraken_request(path: str, payload = {}) -> requests.Request:
    payload['nonce'] = str(int(1000*time.time()))
    headers = {}
    headers['API-Key'] = KRAKEN_API_KEY
    headers['API-Sign'] = get_kraken_signature(path, payload)             
    
    return requests.post(
        'https://api.kraken.com' + path,
        headers=headers,
        data=payload
    ).json()['result']