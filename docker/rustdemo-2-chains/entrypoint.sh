#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/bitcoind_regtest
mkdir -p /wd/daemon-data/bitcoind_chain_2

mkdir -p /wd/clightning_datadir_alice_regtest
mkdir -p /wd/clightning_datadir_bob_regtest
mkdir -p /wd/clightning_datadir_bob_chain_2
mkdir -p /wd/clightning_datadir_carol_chain_2

honcho start -e /wd/docker/rustdemo-2-chains/.env -f /wd/docker/rustdemo-2-chains/Procfile
