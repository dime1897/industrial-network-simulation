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

ziti edge list service-policies

ziti edge list service-edge-router-policies

ziti edge list edge-router-policies

ziti edge policy-advisor services plc-siemens-service --quiet

BASH

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/plc-siemens-tunneler.ott.jwt)" \
docker compose --profile=host-siemens up --detach

ZITI_ENROLL_TOKEN="$(docker compose exec --no-TTY ziti-ctrl cat /tmp/hmi-siemens-router.erott.jwt)" \
docker compose --profile=client-siemens up --detach

# timeout 10s docker compose logs hmisiemens --no-log-prefix --follow || true

# read -p "Done! Press ENTER to destroy..."

# cleanup