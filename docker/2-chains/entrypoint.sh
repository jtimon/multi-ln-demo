#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

honcho start -e /wd/docker/2-chains/.env -f /wd/docker/2-chains/Procfile
