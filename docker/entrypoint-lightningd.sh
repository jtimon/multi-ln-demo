#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

mkdir -p /wd/daemon-data/alice_regtest
mkdir -p /wd/daemon-data/bob_regtest
mkdir -p /wd/daemon-data/bob_chain_2
mkdir -p /wd/daemon-data/carol_chain_2
mkdir -p /wd/daemon-data/carol_chain_3
mkdir -p /wd/daemon-data/david_chain_3

honcho start -f ${LIGHTNINGD_PROCFILE}
