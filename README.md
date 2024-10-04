# autoforward-autoconvert

Programs to auto-forward BTC and XMR wallets to Kraken, and then auto-convert to USD.

## Requirements

- Docker
- Docker Compose

## Configuration

Create a `.env` file as a copy of `.env.example` and set the values for the empty variables.

### Environment variables

| Variable name | Required | Default | Description |
| - | - | - | - |
| `BITCOIN_WALLET_SEED` | Yes | - | Your BIP39 Bitcoin mnemonic seed. |
| `MONERO_WALLET_SEED` | Yes | - | Your 25 word Monero mnemonic seed. |
| `MONERO_WALLET_HEIGHT` | Yes | - | The restore height of your Monero wallet. |
| `ELECTRUM_RPC_PASSWORD` | Yes | - | A new strong password for your Electrum RPC. |
| `MONERO_RPC_PASSWORD` | Yes | - | A new strong password for your Monero RPC. |
| `MONERO_WALLET_PASSWORD` | Yes | - | A new strong password for your Monero Wallet. |
| `KRAKEN_API_KEY` | Yes | - | Your API key from Kraken. |
| `KRAKEN_API_SECRET` | Yes | - | Your API secret from Kraken. |
| `MONERO_DAEMON_ADDRESS` | Yes | - | The address of a Monero daemon you own or trust. |
| `ELECTRUM_SERVER_ADDRESS` | **No** | - | The address of an Electrum server you own or trust. E.g.: `localhost:50001:t` (no SSL) or `my.electrum.server:50001:s` (SSL). By leaving this blank you're letting Electrum select a random server for you, which may be a privacy concern. |
| `MAX_BITCOIN_FEE_PERCENT` | **No** | `10` | The maximum accepted bitcoin miner's fee percent when auto-forwarding. |
| `MAX_SLIPPAGE_PERCENT` | **No** | `1` | The maximum accepted slippage percent when auto-converting. |


## Running

After setting the required environment variable values, you can run the containers:

```bash
$ docker-compose --env-file .env up -d
```

## Changing seeds

If you wish to change any of the wallet seeds in the future, first you have to take down all Docker Compose services and delete the volumes:

```bash
$ docker-compose down -v
```

Change the seeds in the `.env` file and start all services again:

```bash
$ docker-compose --env-file .env up -d
```

# Contributing

Pull requests welcome!
Thanks for supporting MAGIC Grants.

# License

[MIT](LICENSE)
