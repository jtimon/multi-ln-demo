#! /usr/bin/env bash

# Causes the shell to exit if any subcommand or pipeline returns a non-zero status
set -e

# $1=BRANCH_COMMIT $2=REPO_NAME $3=REPO_HOST $4=DAEMON_NAME

if [ "$4" = "" -o "$4" = "disabled_daemon" ]; then
    exit 0
fi

NUM_JOBS=4
if [ -f /proc/cpuinfo ]; then
    NUM_JOBS=$(cat /proc/cpuinfo | grep ^processor | wc -l)
fi

git clone $3/$2
cd $2
git checkout $1
./autogen.sh
./configure --without-gui

make "src/"$4"-tx" -j$NUM_JOBS
make "src/"$4"-cli" -j$NUM_JOBS
make "src/"$4"d" -j$NUM_JOBS
