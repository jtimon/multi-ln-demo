#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_alice_bitcoind
mkdir -p /wd/daemon-data/regtest_bob_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest

honcho start -e daemons.env -f regtest-daemons.proc
