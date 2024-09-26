#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=client-siemens stop

docker compose --profile=host-siemens stop

docker compose --profile=host-omron stop

docker compose --profile=client-beckhoff stop

docker compose --profile=host-beckhoff stop

docker compose stop ziti-ctrl