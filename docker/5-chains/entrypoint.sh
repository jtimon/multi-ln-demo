#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_bitcoind
mkdir -p /wd/daemon-data/chain_2_bitcoind
mkdir -p /wd/daemon-data/chain_3_bitcoind
mkdir -p /wd/daemon-data/chain_4_bitcoind
mkdir -p /wd/daemon-data/chain_5_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2
mkdir -p /wd/daemon-data/carol_chain_3
mkdir -p /wd/daemon-data/david_chain_3
mkdir -p /wd/daemon-data/david_chain_4
mkdir -p /wd/daemon-data/ezra_chain_4
mkdir -p /wd/daemon-data/ezra_chain_5
mkdir -p /wd/daemon-data/fiona_chain_5

honcho start -e /wd/docker/5-chains/.env -f /wd/docker/5-chains/Procfile
