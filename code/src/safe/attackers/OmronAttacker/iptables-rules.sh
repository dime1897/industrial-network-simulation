#!/usr/bin/env bash

iptables -t filter -A OUTPUT -p udp -d 192.168.3.1 --dport 9600 -m state --state NEW,ESTABLISHED -j DROP