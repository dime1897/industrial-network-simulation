#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail #-o xtrace

docker compose --profile=ziti up --detach

docker compose --profile=host-omron up --detach

docker compose --profile=host-beckhoff up --detach

docker compose exec --privileged --no-TTY plcbeckhoff bash << BASH

./iptables-rules.sh

BASH

docker compose --profile=client-beckhoff up --detach

docker compose --profile=host-siemens up --detach

docker compose exec --privileged --no-TTY plcsiemens bash << BASH

./iptables-rules.sh

BASH

docker compose --profile=client-siemens up --detach