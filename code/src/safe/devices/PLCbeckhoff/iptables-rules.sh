#!/usr/bin/env bash

iptables -t filter -P INPUT DROP
iptables -t filter -P FORWARD DROP
iptables -t filter -P OUTPUT DROP

iptables -t filter -A INPUT -p tcp -s $ZITI_PLCBECKHOFF_TUNNELER_ADDRESS -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -p tcp -d $ZITI_PLCBECKHOFF_TUNNELER_ADDRESS -m state --state ESTABLISHED -j ACCEPT

iptables -L