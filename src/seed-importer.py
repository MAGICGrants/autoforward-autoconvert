from bip_utils import Bip39SeedGenerator, Bip84, Bip84Coins

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
   monero_params = {
      'filename': 'wallet',
      'seed': env.MONERO_WALLET_SEED,
      'password': env.MONERO_RPC_PASSWORD,
      'restore_height': env.MONERO_WALLET_HEIGHT,
      'language': 'english',
      'autosave_current': True
   }

   util.request_monero_rpc('restore_deterministic_wallet', monero_params)

try:
   import_bitcoin_seed()
except Exception as e:
   print(util.get_time(), 'Error importing bitcoin seed:', e)

try:
   import_monero_seed()
except Exception as e:
   print(util.get_time(), 'Error importing monero seed:', e)