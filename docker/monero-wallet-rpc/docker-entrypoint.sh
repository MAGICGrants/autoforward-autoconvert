#!/bin/sh
set -e

ADDITIONAL_FLAGS=""

if [ "$TESTNET" = "1" ]; then
  ADDITIONAL_FLAGS="--testnet"
fi

set -- "monero-wallet-rpc" "--non-interactive" "--rpc-bind-ip=0.0.0.0" "--confirm-external-bind" $ADDITIONAL_FLAGS "$@"

# Start the daemon using fixuid
# to adjust permissions if needed
exec fixuid -q "$@"