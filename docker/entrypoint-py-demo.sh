#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

# A python script to make the rpc calls:

# PYTHONUNBUFFERED is bad for performance https://honcho.readthedocs.io/en/latest/using_procfiles.html#buffered-output
PYTHONUNBUFFERED=true python /wd/multiln/bin/demo.py ${PYDEMO_CHAINS}
