import os

ELECTRUM_RPC_URL = os.getenv('ELECTRUM_RPC_URL', 'http://electrs:7000')
ELECTRUM_RPC_USERNAME = os.getenv('ELECTRUM_RPC_USERNAME', '')
ELECTRUM_RPC_PASSWORD = os.getenv('ELECTRUM_RPC_PASSWORD', '')
BITCOIN_WALLET_SEED = os.getenv('BITCOIN_WALLET_SEED', '')

MONERO_RPC_URL = os.getenv('MONERO_RPC_URL', 'http://monero-wallet-rpc:18082/json_rpc')
MONERO_RPC_USERNAME = os.getenv('MONERO_RPC_USERNAME', '')
MONERO_RPC_PASSWORD = os.getenv('MONERO_RPC_PASSWORD', '')
MONERO_WALLET_SEED = os.getenv('MONERO_WALLET_SEED', '')
MONERO_WALLET_PASSWORD = os.getenv('MONERO_WALLET_PASSWORD', '')
MONERO_WALLET_HEIGHT = os.getenv('MONERO_WALLET_HEIGHT', '')

KRAKEN_API_KEY = os.getenv('KRAKEN_API_KEY', '')
KRAKEN_API_SECRET = os.getenv('KRAKEN_API_SECRET', '')