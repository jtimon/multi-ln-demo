#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

# $1=BRANCH_COMMIT $2=REPO_NAME $3=REPO_HOST

NUM_JOBS=4
if [ -f /proc/cpuinfo ]; then
    NUM_JOBS=$(cat /proc/cpuinfo | grep ^processor | wc -l)
fi

git clone $3/$2
cd $2
git checkout $1
./configure
make -j$NUM_JOBS
