#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_bitcoind
mkdir -p /wd/daemon-data/chain_2_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2

honcho start -e /wd/docker/2-chains/.env -f /wd/docker/2-chains/Procfile