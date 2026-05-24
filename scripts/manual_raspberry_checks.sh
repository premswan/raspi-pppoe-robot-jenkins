#!/usr/bin/env bash
set -euo pipefail

MIRROR_IFACE="${1:-eth0}"
CAPTURE_SECONDS="${2:-20}"
PACKET_COUNT="${3:-20}"

printf '\n[1] Interface check\n'
ip -o link show dev "${MIRROR_IFACE}"

printf '\n[2] tcpdump permission check\n'
sudo -n tcpdump --version

printf '\n[3] Capture PPPoE session packets from mirrored WAN traffic\n'
printf 'Generate traffic from any LAN client while this runs, for example ping 8.8.8.8 or open a website.\n\n'

timeout "${CAPTURE_SECONDS}" sudo -n tcpdump \
  -i "${MIRROR_IFACE}" \
  -nn -e -vv -s0 \
  -c "${PACKET_COUNT}" \
  'ether proto 0x8864'
