#!/bin/bash

set -e

trap 'pkill -TERM -P1; electrum-ltc.appimage stop; exit 0' SIGTERM

rm -f $HOME/.electrum-ltc/daemon
./squashfs-root/AppRun --offline setconfig rpcuser ${ELECTRUM_RPC_USER}
./squashfs-root/AppRun --offline setconfig rpcpassword ${ELECTRUM_RPC_PASSWORD}
./squashfs-root/AppRun --offline setconfig rpchost 0.0.0.0
./squashfs-root/AppRun --offline setconfig rpcport 7000

if [ -n "${ELECTRUM_SERVER_ADDRESS}" ]; then
    ./squashfs-root/AppRun daemon -1 -s "${ELECTRUM_SERVER_ADDRESS}" "$@"
else
    ./squashfs-root/AppRun daemon "$@"
fi

