#!/bin/sh
set -e
SERVER_PORT=$(grep SERVER_PORT /config.ini | cut -d= -f2 | tr -d ' ')
nc -z localhost $SERVER_PORT