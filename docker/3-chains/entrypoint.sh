#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_bitcoind
mkdir -p /wd/daemon-data/chain_2_bitcoind
mkdir -p /wd/daemon-data/chain_3_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2
mkdir -p /wd/daemon-data/carol_chain_3
mkdir -p /wd/daemon-data/david_chain_3

python3 /wd/py-ln-gateway/py_ln_gateway/init_db.py
honcho start -e /wd/docker/3-chains/.env -f /wd/docker/3-chains/Procfile
