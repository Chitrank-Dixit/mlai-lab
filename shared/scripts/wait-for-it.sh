#!/usr/bin/env bash
# File: shared/scripts/wait-for-it.sh
# Simple shell script to wait for a service port to become available

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Waiting for $host:$port..."

# Check if curl is available, otherwise use bash tcp sockets
if command -v curl >/dev/null 2>&1; then
  until curl -s "http://$host:$port" > /dev/null; do
    echo "Waiting for http://$host:$port to respond..."
    sleep 2
  done
else
  until bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null; do
    echo "Waiting for port $port on $host to be open..."
    sleep 2
  done
fi

echo "$host:$port is up - executing command: $cmd"
exec $cmd
