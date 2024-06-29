#!/usr/bin/env bash

sudo apt update
sudo apt install -y squid
sudo sed -i "s/#http_access allow localnet/http_access allow localnet/" /etc/squid/squid.conf
sudo systemctl restart squid
curl -s https://install.zerotier.com | sudo bash
sudo sudo zerotier-cli join ffffffffffff