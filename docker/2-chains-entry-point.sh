#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/chain_1_bitcoind
mkdir -p /wd/daemon-data/chain_2_bitcoind

mkdir -p /wd/daemon-data/alice_regtest_rlbrpc

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/alice_chain_1
mkdir -p /wd/daemon-data/bob_chain_1
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2

honcho start -e daemons.env -f 2-chains-daemons.proc
