#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=client stop

docker compose --profile=host stop

docker compose stop ziti-ctrl