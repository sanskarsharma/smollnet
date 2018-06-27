#!/bin/bash
# This script downloads and runs redis-server.
# If redis has been already downloaded, it just runs it
if [ ! -d redis-4.0.8/src ]; then
    wget http://download.redis.io/releases/redis-4.0.8.tar.gz
    tar xzf redis-4.0.8.tar.gz
    rm redis-4.0.8.tar.gz
    cd redis-4.0.8
    make
else
    cd redis-4.0.8
fi
src/redis-server
