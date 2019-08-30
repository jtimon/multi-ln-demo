#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data
chown -R $user:$user /wd/daemon-data

mkdir -p /wd/daemon-data/regtest_bitcoind

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest

honcho start -e /wd/docker/regtest/.env -f /wd/docker/regtest/Procfile