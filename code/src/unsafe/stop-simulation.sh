#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=hmi stop

docker compose --profile=plc stop