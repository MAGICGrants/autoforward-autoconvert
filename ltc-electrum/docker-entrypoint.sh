#!/usr/bin/env sh
set -ex

trap 'pkill -TERM -P1; electrum-ltc stop; exit 0' SIGTERM

rm -f .electrum/daemon
electrum-ltc --offline setconfig rpcuser ${ELECTRUM_RPC_USER}
electrum-ltc --offline setconfig rpcpassword ${ELECTRUM_RPC_PASSWORD}
electrum-ltc --offline setconfig rpchost 0.0.0.0
electrum-ltc --offline setconfig rpcport 7000

if [ -n "${LITECOIN_ELECTRUM_SERVER_ADDRESS}" ]; then
    electrum-ltc daemon -1 -s "${LITECOIN_ELECTRUM_SERVER_ADDRESS}" "$@"
else
    electrum-ltc daemon "$@"
fi

