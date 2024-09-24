#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=plc up --detach

docker compose --profile=hmi up --detach

timeout 5s docker compose logs hmisiemens --no-log-prefix --follow || true

timeout 5s docker compose logs hmibeckhoff --no-log-prefix --follow || true

docker compose attach hmisiemens