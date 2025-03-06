#!/usr/bin/env sh
set -ex

trap 'pkill -TERM -P1; electrum stop; exit 0' SIGTERM

rm -f .electrum/daemon
electrum --offline setconfig rpcuser ${BITCOIN_ELECTRUM_USER}
electrum --offline setconfig rpcpassword ${BITCOIN_ELECTRUM_PASSWORD}
electrum --offline setconfig rpchost 0.0.0.0
electrum --offline setconfig rpcport 7000

if [ -n "${BITCOIN_ELECTRUM_SERVER_ADDRESS}" ]; then
    electrum daemon -1 -s "${BITCOIN_ELECTRUM_SERVER_ADDRESS}" "$@"
else
    electrum daemon "$@"
fi

