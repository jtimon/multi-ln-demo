#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

python3 /wd/py-ln-gateway/py_ln_gateway/init_db.py
# No point in running it as a process while prices are constant
python3 /wd/py-ln-gateway/py_ln_gateway/cron/update_price.py
honcho start -f /wd/docker/py-gateway.Procfile
