from typing import Literal
from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins
import traceback
import util
import env

def get_zprv_from_seed(coin: Literal['btc', 'ltc'], mnemonic: str ) -> str:
   coin_type = Bip84Coins.BITCOIN if coin == 'btc' else Bip84Coins.LITECOIN
   seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
   bip84_master_key = Bip84.FromSeed(seed_bytes, coin_type)
   zprv = bip84_master_key.Purpose().Coin().Account(0).PrivateKey().ToExtended()
   return zprv

def import_bitcoin_seed():
   zprv = get_zprv_from_seed('btc', env.BITCOIN_WALLET_SEED)
   util.request_electrum_rpc('btc', 'restore', [zprv])

def import_litecoin_seed():
   zprv = get_zprv_from_seed('ltc', env.LITECOIN_WALLET_SEED)
   util.request_electrum_rpc('ltc', 'restore', [zprv])

def import_monero_seed():
   params = {
      'filename': 'foo',
      'seed': env.MONERO_WALLET_SEED,
      'password': env.MONERO_WALLET_PASSWORD,
      'restore_height': env.MONERO_WALLET_HEIGHT,
      'language': 'english',
      'autosave_current': True
   }

   util.request_monero_rpc('restore_deterministic_wallet', params)

util.wait_for_rpc()

try:
   import_bitcoin_seed()
   util.request_electrum_rpc('btc', 'load_wallet')
   util.request_electrum_rpc('btc', 'changegaplimit', [1000, 'iknowhatimdoing'])
   print('Bitcoin seed has successfully been imported!')
except Exception as e:
   print(util.get_time(), 'Error importing bitcoin seed:')
   print(traceback.format_exc())

try:
   import_litecoin_seed()
   util.request_electrum_rpc('ltc', 'load_wallet')
   util.request_electrum_rpc('ltc', 'changegaplimit', [1000, 'iknowhatimdoing'])
   print('Litecoin seed has successfully been imported!')
except Exception as e:
   print(util.get_time(), 'Error importing litecoin seed:')
   print(traceback.format_exc())

try:
   import_monero_seed()
   print('Monero seed has successfully been imported!')
except Exception as e:
   print(util.get_time(), 'Error importing monero seed:')
   print(traceback.format_exc())
