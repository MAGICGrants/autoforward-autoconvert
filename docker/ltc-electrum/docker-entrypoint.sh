#!/bin/sh
set -e

# trap 'pkill -TERM -P1; electrum-ltc.appimage stop; exit 0' SIGTERM

rm -f .electrum-ltc/daemon .electrum-ltc/testnet/daemon

ADDITIONAL_SETCONFIG_FLAGS=""
ADDITIONAL_DAEMON_FLAGS=""

if [ "$TESTNET" = "1" ]; then
    ADDITIONAL_SETCONFIG_FLAGS="--testnet"
    ADDITIONAL_DAEMON_FLAGS="--testnet"
fi

if [ -n "$ELECTRUM_SERVER_ADDRESS" ]; then
    ADDITIONAL_DAEMON_FLAGS="$ADDITIONAL_DAEMON_FLAGS -1 -s $ELECTRUM_SERVER_ADDRESS"
fi

./squashfs-root/AppRun $ADDITIONAL_SETCONFIG_FLAGS --offline setconfig rpcuser $ELECTRUM_RPC_USER
./squashfs-root/AppRun $ADDITIONAL_SETCONFIG_FLAGS --offline setconfig rpcpassword $ELECTRUM_RPC_PASSWORD
./squashfs-root/AppRun $ADDITIONAL_SETCONFIG_FLAGS --offline setconfig rpchost 0.0.0.0
./squashfs-root/AppRun $ADDITIONAL_SETCONFIG_FLAGS --offline setconfig rpcport 7000
./squashfs-root/AppRun daemon $ADDITIONAL_DAEMON_FLAGS "$@"

