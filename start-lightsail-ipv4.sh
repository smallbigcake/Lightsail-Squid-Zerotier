#!/usr/bin/env bash

aws lightsail create-instances --instance-names Debian-Squid-IPv4 \
    --availability-zone us-west-2a \
    --blueprint-id debian_12 \
    --bundle-id nano_3_0 \
    --key-pair-name debian-squid \
    --user-data file:///home/cake/lightsail-user-data.sh
python auth-new-zero-member.py
