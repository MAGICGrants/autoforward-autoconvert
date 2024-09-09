#!/usr/bin/env sh
set -ex

trap 'pkill -TERM -P1; electrum stop; exit 0' SIGTERM

rm -f .electrum/daemon
electrum --offline setconfig rpcuser ${ELECTRUM_USER}
electrum --offline setconfig rpcpassword ${ELECTRUM_PASSWORD}
electrum --offline setconfig rpchost 0.0.0.0
electrum --offline setconfig rpcport 7000
electrum daemon "$@"