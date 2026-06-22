#!/bin/sh
set -e

WORKERS="${WORKERS:-4}"
PORT="${PORT:-8000}"
FORWARDED_ALLOW_IPS="${FORWARDED_ALLOW_IPS:-*}"

GRANIAN_ARGS="--interface asgi --host 0.0.0.0 --port $PORT --workers $WORKERS --forwarded-allow-ips $FORWARDED_ALLOW_IPS"

if [ -n "$ROOT_PATH" ]; then
    GRANIAN_ARGS="$GRANIAN_ARGS --root-path $ROOT_PATH"
fi

exec granian $GRANIAN_ARGS api.main:app
