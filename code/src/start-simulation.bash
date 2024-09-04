#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=ziti up --detach

docker compose --profile=host up --detach

docker compose --profile=client up --detach