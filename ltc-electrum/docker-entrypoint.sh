#!/usr/bin/env sh
set -ex

trap 'pkill -TERM -P1; electrum stop; exit 0' SIGTERM

rm -f .electrum/daemon
electrum --offline setconfig rpcuser ${LITECOIN_ELECTRUM_USER}
electrum --offline setconfig rpcpassword ${LITECOIN_ELECTRUM_PASSWORD}
electrum --offline setconfig rpchost 0.0.0.0
electrum --offline setconfig rpcport 7001

if [ -n "${LITECOIN_ELECTRUM_SERVER_ADDRESS}" ]; then
    electrum daemon -1 -s "${LITECOIN_ELECTRUM_SERVER_ADDRESS}" "$@"
else
    electrum daemon "$@"
fi

