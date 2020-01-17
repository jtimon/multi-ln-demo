#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

honcho start -e /wd/docker/.env -f ${PYDEMO_PROCFILE}
