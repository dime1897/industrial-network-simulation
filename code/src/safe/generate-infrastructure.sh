#!/usr/bin/env bash

set -o errexit -o nounset -o pipefail -o xtrace

docker compose run --rm --entrypoint= --user=root --no-TTY ziti-ctrl chown -R "2171:2171" /home/ziggy/quickstart/
docker compose up wait-for-ziti-ctrl

docker compose exec --no-TTY ziti-ctrl bash << BASH

set -o errexit -o nounset -o pipefail -o xtrace

ziti edge login https://ziti-controller:1280 --ca=/home/ziggy/quickstart/pki/root-ca/certs/root-ca.cert -u admin -p ziggy123

ziti edge create edge-router "hmi-siemens-router" --tunneler-enabled -o /tmp/hmi-siemens-router.erott.jwt

ziti edge list edge-routers

ziti edge update identity hmi-siemens-router --role-attributes hmi-siemens-attr

ziti edge create identity "plc-siemens-tunneler" -o /tmp/plc-siemens-tunneler.ott.jwt --role-attributes plc-siemens-attr

ziti edge list identities

ziti edge create config "hmi-siemens-config" intercept.v1 '{"protocols":["tcp"],"addresses":["10.11.12.13"], "portRanges":[{"low":102, "high":102}]}'

ziti edge create config "plc-siemens-config" host.v1 '{"protocol":"tcp", "address":"plcsiemens","port":102}'

ziti edge list configs

ziti edge create service "plc-siemens-service" --configs hmi-siemens-config,plc-siemens-config --role-attributes plc-siemens-service-attr

ziti edge list services

ziti edge create service-policy "plc-siemens-service-policy" Bind --service-roles '#plc-siemens-service-attr' --identity-roles '#plc-siemens-attr'

ziti edge create service-policy "hmi-siemens-service-policy" Dial --service-roles '#plc-siemens-service-attr' --identity-roles '#hmi-siemens-attr'

ziti edge create edge-router "hmi-beckhoff-router" --tunneler-enabled -o /tmp/hmi-beckhoff-router.erott.jwt

ziti edge update identity hmi-beckhoff-router --role-attributes hmi-beckhoff-attr

ziti edge create identity "plc-beckhoff-tunneler" -o /tmp/plc-beckhoff-tunneler.ott.jwt --role-attributes plc-beckhoff-attr

ziti edge create config "hmi-beckhoff-config" intercept.v1 '{"protocols":["tcp"],"addresses":["10.21.22.23"], "portRanges":[{"low":502, "high":502}]}'

ziti edge create config "plc-beckhoff-config" host.v1 '{"protocol":"tcp", "address":"plcbeckhoff","port":502}'

ziti edge create service "plc-beckhoff-service" --configs hmi-beckhoff-config,plc-beckhoff-config --role-attributes plc-beckhoff-service-attr

ziti edge create service-policy "plc-beckhoff-service-policy" Bind --service-roles '#plc-beckhoff-service-attr' --identity-roles '#plc-beckhoff-attr'

ziti edge create service-policy "hmi-beckhoff-service-policy" Dial --service-roles '#plc-beckhoff-service-attr' --identity-roles '#hmi-beckhoff-attr'

ziti edge create edge-router "hmi-omron-router" --tunneler-enabled -o /tmp/hmi-omron-router.erott.jwt

ziti edge update identity hmi-omron-router --role-attributes hmi-omron-attr

ziti edge create identity "plc-omron-tunneler" -o /tmp/plc-omron-tunneler.ott.jwt --role-attributes plc-omron-attr

ziti edge create config "hmi-omron-config" intercept.v1 '{"protocols":["tcp", "udp"],"addresses":["10.31.32.33"], "portRanges":[{"low":9600, "high":9600}]}'

ziti edge create config "plc-omron-config" host.v1 '{"protocol":"udp", "address":"192.168.3.1","port":9600}'

ziti edge create service "plc-omron-service" --configs hmi-omron-config,plc-omron-config --role-attributes plc-omron-service-attr

ziti edge create service-policy "plc-omron-service-policy" Bind --service-roles '#plc-omron-service-attr' --identity-roles '#plc-omron-attr'

ziti edge create service-policy "hmi-omron-service-policy" Dial --service-roles '#plc-omron-service-attr' --identity-roles '#hmi-omron-attr'

ziti edge list service-policies

ziti edge list service-edge-router-policies

ziti edge list edge-router-policies

ziti edge policy-advisor services plc-siemens-service --quiet

BASH

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/plc-siemens-tunneler.ott.jwt)" \
docker compose --profile=host-siemens up --detach

docker compose exec --privileged --no-TTY plcsiemens bash << BASH

./iptables-rules.sh

BASH

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/hmi-siemens-router.erott.jwt)" \
docker compose --profile=client-siemens up --detach

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/plc-beckhoff-tunneler.ott.jwt)" \
docker compose --profile=host-beckhoff up --detach

docker compose exec --privileged --no-TTY plcbeckhoff bash << BASH

./iptables-rules.sh

BASH

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/hmi-beckhoff-router.erott.jwt)" \
docker compose --profile=client-beckhoff up --detach

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/plc-omron-tunneler.ott.jwt)" \
docker compose --profile=host-omron up --detach

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/hmi-omron-router.erott.jwt)" \
docker compose --profile=client-omron up --detach

timeout 5s docker compose logs hmisiemens --no-log-prefix --follow || true

timeout 5s docker compose logs hmibeckhoff --no-log-prefix --follow || true

timeout 5s docker compose logs hmiomron --no-log-prefix --follow || true

# read -p "Done! Press ENTER to destroy..."

# cleanup