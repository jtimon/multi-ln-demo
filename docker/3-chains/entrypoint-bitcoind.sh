#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_bitcoind
mkdir -p /wd/daemon-data/chain_2_bitcoind
mkdir -p /wd/daemon-data/chain_3_bitcoind

honcho start -f /wd/docker/3-chains/bitcoind.Procfile
