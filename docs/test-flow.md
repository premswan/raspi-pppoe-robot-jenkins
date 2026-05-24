# PPPoE Mirror-Port Test Flow

## Correct topology

The Raspberry Pi is not the PPPoE endpoint. The Airtel router owns the PPPoE session on its WAN side. The router mirrors WAN traffic to LAN4. The Raspberry Pi is connected to LAN4 and passively captures PPPoE frames.

```text
Internet/OLT/ISP
    |
Airtel Router WAN  -- PPPoE session exists here
    |
LAN4 mirror port   -- mirrored copy of WAN packets
    |
Raspberry Pi eth0  -- tcpdump only, no ppp0 required
```

## What can be validated

Valid validations:

1. PPPoE session packets are visible on Raspberry Pi mirror interface.
2. PPPoE session ID is present, for example `0x2b58`.
3. Inner IPv4 packets are visible inside PPPoE session packets.
4. Customer WAN IP can be inferred from packets, for example `100.103.70.200`.
5. WAN IP can be classified as CGNAT or global.
6. Optional expected WAN IP can be matched exactly.

Invalid validation for this topology:

```text
ip addr show ppp0
```

There is no `ppp0` on the Raspberry Pi because Raspberry Pi is not dialing PPPoE.

## Best Jenkins topology

For clean automation, use two Raspberry Pi paths:

```text
Raspberry Pi wlan0 or management LAN = SSH from Jenkins to 192.168.1.2
Raspberry Pi eth0 = connected to Airtel LAN4 mirror port for passive tcpdump
```

If the Raspberry Pi has only eth0 connected to the mirror port, Jenkins may not be able to SSH to it because mirror ports usually do not behave like normal switched access ports.

## Manual command

```bash
sudo -n tcpdump -i eth0 -nn -e -vv -s0 -c 20 'ether proto 0x8864'
```

Expected type of output:

```text
PPPoE [ses 0x2b58] IP 100.103.70.200 > 8.8.8.8: ICMP echo request
```

## Discovery versus session traffic

PPPoE discovery uses EtherType `0x8863`.
PPPoE session traffic uses EtherType `0x8864`.

This project focuses on session traffic because the WAN IP appears inside PPPoE session IP packets, not in simple local `ppp0` output on the Raspberry Pi.
