#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

python3 /wd/py-ln-gateway/py_ln_gateway/init_db.py
honcho start -f /wd/docker/py-gateway.Procfile
