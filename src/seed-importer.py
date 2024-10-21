from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins
import traceback

import util
import env

def get_zprv_from_seed(mnemonic: str) -> str:
   seed_bytes = Bip39SeedGenerator(mnemonic).Generate()
   bip84_master_key = Bip84.FromSeed(seed_bytes, Bip84Coins.BITCOIN)
   zprv = bip84_master_key.Purpose().Coin().Account(0).PrivateKey().ToExtended()
   return zprv

def import_bitcoin_seed():
   zprv = get_zprv_from_seed(env.BITCOIN_WALLET_SEED)
   util.request_electrum_rpc('restore', [zprv])

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
   util.request_electrum_rpc('load_wallet')
   util.request_electrum_rpc('changegaplimit', [1000, 'iknowhatimdoing'])
   print('Bitcoin seed has successfully been imported!')
except Exception as e:
   print(util.get_time(), 'Error importing bitcoin seed:')
   print(traceback.format_exc())

try:
   import_monero_seed()
   print('Monero seed has successfully been imported!')
except Exception as e:
   print(util.get_time(), 'Error importing monero seed:')
   print(traceback.format_exc())
