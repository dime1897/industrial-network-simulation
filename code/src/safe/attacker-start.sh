#!/usr/bin/env bash

docker compose up omron-attacker -d

docker compose exec --privileged --no-TTY omron-attacker bash << BASH

./iptables-rules.sh

python3 OmronAttacker.py

BASH