#!/bin/sh
set -e

exec granian \
    --interface asgi \
    --host 0.0.0.0 \
    --port "${GRANIAN_PORT:-8000}" \
    --workers "${GRANIAN_WORKERS:-4}" \
    --respawn-failed-workers \
    ${GRANIAN_URL_PATH_PREFIX:+--url-path-prefix "$GRANIAN_URL_PATH_PREFIX"} \
    api.main:app
