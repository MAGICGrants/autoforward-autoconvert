#!/bin/bash

set -e

trap 'pkill -TERM -P1; electrum-ltc.appimage stop; exit 0' SIGTERM

rm -f $HOME/.electrum-ltc/daemon
./electrum-ltc.appimage --offline setconfig rpcuser ${ELECTRUM_RPC_USER}
./electrum-ltc.appimage --offline setconfig rpcpassword ${ELECTRUM_RPC_PASSWORD}
./electrum-ltc.appimage --offline setconfig rpchost 0.0.0.0
./electrum-ltc.appimage --offline setconfig rpcport 7000

if [ -n "${ELECTRUM_SERVER_ADDRESS}" ]; then
    ./electrum-ltc.appimage daemon -1 -s "${ELECTRUM_SERVER_ADDRESS}" "$@"
else
    ./electrum-ltc.appimage daemon "$@"
fi

