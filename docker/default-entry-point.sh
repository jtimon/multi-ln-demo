#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_alice_bitcoind
mkdir -p /wd/daemon-data/regtest_bob_bitcoind
mkdir -p /wd/daemon-data/chain_1_alice_bitcoind
mkdir -p /wd/daemon-data/chain_1_bob_bitcoind
mkdir -p /wd/daemon-data/chain_2_bob_bitcoind
mkdir -p /wd/daemon-data/chain_2_carol_bitcoind
mkdir -p /wd/daemon-data/chain_3_carol_bitcoind
mkdir -p /wd/daemon-data/chain_3_david_bitcoind
mkdir -p /wd/daemon-data/chain_4_david_bitcoind
mkdir -p /wd/daemon-data/chain_4_ezra_bitcoind
mkdir -p /wd/daemon-data/chain_5_ezra_bitcoind
mkdir -p /wd/daemon-data/chain_5_fiona_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/alice_chain_1
mkdir -p /wd/daemon-data/bob_chain_1
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2
mkdir -p /wd/daemon-data/carol_chain_3
mkdir -p /wd/daemon-data/david_chain_3
mkdir -p /wd/daemon-data/david_chain_4
mkdir -p /wd/daemon-data/ezra_chain_4
mkdir -p /wd/daemon-data/ezra_chain_5
mkdir -p /wd/daemon-data/fiona_chain_5

honcho start -e daemons.env -f default-daemons.proc
