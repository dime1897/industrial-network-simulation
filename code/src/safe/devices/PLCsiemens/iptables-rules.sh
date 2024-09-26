#!/usr/bin/env bash

iptables -t filter -P INPUT DROP
iptables -t filter -P FORWARD DROP
iptables -t filter -P OUTPUT DROP

iptables -t filter -A INPUT -p tcp -s $ZITI_CTRL_ADDRESS -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A INPUT -p tcp -s 127.0.0.1 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A INPUT -p udp -s $PLCOMRON_ADDRESS -m state --state NEW,ESTABLISHED -j ACCEPT

iptables -t filter -A OUTPUT -p tcp -d $ZITI_CTRL_ADDRESS -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -p tcp -s 127.0.0.1 -m state --state NEW,ESTABLISHED -j ACCEPT
iptables -t filter -A OUTPUT -p udp -d $PLCOMRON_ADDRESS -m state --state NEW,ESTABLISHED -j ACCEPT

iptables -L