# Raspberry Pi PPPoE Mirror Capture - Jenkins + Robot Framework

This project has one Robot Framework testcase. Jenkins connects to Raspberry Pi using an **SSH Username with private key** credential named `raspi-ssh-key`, captures PPPoE session packets from the mirrored WAN port, and prints only normalized public/CGNAT IPv4 flows with source and destination ports.

Example tcpdump input:

```text
21:54:13.386596 PPPoE [ses 0x2b58] IP 100.103.70.200.13227 > 117.96.122.77.domain: 59384+ PTR? ...
21:54:13.386603 PPPoE [ses 0x2b58] IP 100.103.70.200.50077 > 87.70.96.34.bc.googleusercontent.com.https: Flags [.], ...
```

Console output:

```text
PPPoE public/CGNAT IP flows with ports: ['100.103.70.200.13227 > 117.96.122.77.domain:', '100.103.70.200.50077 > 87.70.96.34.https:']
```

`100.103.70.200` is CGNAT, not a true public Internet address, but it is included because many Airtel PPPoE/ISP captures show CGNAT WAN addresses.

## Jenkins credential

Create this credential:

```text
Kind      : SSH Username with private key
ID        : raspi-ssh-key
Username  : pi
Private key: private key that can SSH to Raspberry Pi
```

The public key must be present on Raspberry Pi:

```text
/home/pi/.ssh/authorized_keys
```

## Jenkins parameters

```text
RPI_HOST          192.168.1.2
MIRROR_IFACE      eth0
CAPTURE_SECONDS   20
PACKET_COUNT      20
GENERATE_TRAFFIC  False
PING_TARGET       8.8.8.8
PING_COUNT         4
```

Keep `GENERATE_TRAFFIC=False` when Raspberry Pi is only a passive sniffer on the mirror port. Generate traffic from another LAN device while Jenkins is running.

## Manual tcpdump equivalent

The Robot keyword uses `-n` so IP addresses remain numeric while ports can still appear as names such as `domain` or `https`:

```bash
sudo -n tcpdump -i eth0 -n -e -vv -s0 -c 20 'ether proto 0x8864'
```

Full tcpdump output is stored in `results/log.html`, not printed to Jenkins console.
