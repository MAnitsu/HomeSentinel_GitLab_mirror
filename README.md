# Pi-hole Network Ad Blocking

A self-hosted network-wide DNS filtering solution using **Raspberry Pi, Pi-hole, and Quad9 DNS**.

The project provides centralized DNS-level ad and tracker blocking for devices connected to the home network, while also serving as a practical exercise in Linux administration, networking, DNS, Bash scripting, and infrastructure maintenance.

## Architecture

```text
                    Internet
                       │
                       ▼
                ┌──────────────┐
                │ TP-Link      │
                │ Router       │
                │ DHCP / DNS   │
                └──────┬───────┘
                       │
              DNS queries sent
                 to Pi-hole
                       │
                       ▼
              ┌─────────────────┐
              │ Raspberry Pi    │
              │ Raspberry Pi OS │
              │                 │
              │    Pi-hole      │
              │   DNS Filter    │
              └────────┬────────┘
                       │
                 Allowed DNS
                       │
                       ▼
                  Quad9 DNS
                       │
                       ▼
                   Internet
```

### How it works

1. Devices connect to the router as usual.
2. The router advertises the Raspberry Pi as the network's DNS server through DHCP.
3. DNS requests are received by Pi-hole.
4. Pi-hole checks requested domains against configured blocklists.
5. Blocked domains are rejected.
6. Allowed requests are forwarded to the configured upstream DNS provider.
7. Pi-hole provides statistics and query visibility through its web dashboard.

## Hardware

* Raspberry Pi 3B+
* 64 GB MicroSD card
* Power supply
* Ethernet connection recommended
* Router with DHCP configuration access

Other Raspberry Pi models and storage devices can also be used.

## Software

* Raspberry Pi OS Lite 64-bit
* Pi-hole
* Quad9 DNS
* Bash
* SSH
* Git

## Setup

### 1. Install Raspberry Pi OS

Download and install **Raspberry Pi Imager**.

Configure the image with:

* Raspberry Pi OS Lite 64-bit
* Hostname: `pi-hole`
* A local username and password
* SSH enabled
* Network connectivity

Flash the operating system to the MicroSD card and insert it into the Raspberry Pi.

### 2. Connect to the Raspberry Pi

After powering on the Raspberry Pi, connect through SSH:

```bash
ssh <username>@pi-hole.local
```

Update the operating system:

```bash
sudo apt update
sudo apt full-upgrade
sudo reboot
```

### 3. Configure a Reserved IP

The Raspberry Pi acts as a network service, so its IP address should remain consistent.

Create a DHCP address reservation for the Raspberry Pi in the router configuration.

For a TP-Link router:

```text
Advanced
└── Network
    └── DHCP Server
        └── Address Reservation
```

Reserve the Raspberry Pi's address based on its connected device/MAC address.

> Do not use the example IP address from this documentation. Use the address assigned to your own Raspberry Pi.

### 4. Install Pi-hole

Connect to the Raspberry Pi through SSH and run the official Pi-hole installer.

During installation:

* Select the network interface being used.

  * `eth0` for Ethernet
  * `wlan0` for Wi-Fi
* Select an upstream DNS provider.
* Enable the default blocklists.
* Enable the web administration interface.

After installation, open the Pi-hole dashboard:

```text
http://<PI-HOLE-IP>/admin
```

### 5. Configure the Network DNS

The router needs to distribute the Raspberry Pi's IP address as the DNS server to connected devices.

For a TP-Link router:

```text
Advanced
└── Network
    └── DHCP Server
        └── Primary DNS
```

Set the Primary DNS to:

```text
<PI-HOLE-IP>
```

Reconnect devices or renew their DHCP leases so they receive the updated DNS configuration.

### 6. Update Pi-hole Blocklists

After configuring additional lists, refresh Pi-hole's Gravity database:

```bash
sudo pihole updateGravity
```

Pi-hole will then use the updated blocklists when processing DNS queries.

## Additional Blocklists

The project uses the **Hagezi DNS Blocklists** as an optional additional source.

The recommended approach is to select an appropriate list based on the desired balance between blocking and compatibility.

For example:

```text
Hagezi Multi Pro
```

Add the selected list through:

```text
Pi-hole Dashboard
└── Domains on Lists
    └── Manage lists
```

After adding a list:

```bash
sudo pihole updateGravity
```

## Maintenance

Pi-hole and the underlying operating system should be updated periodically.

Manual maintenance:

```bash
sudo apt update
sudo apt full-upgrade
sudo pihole updatePihole
sudo pihole updateGravity
sudo reboot
```

## Automated Maintenance

The project includes a Bash script to automate the maintenance process.

`script/update.sh`:

```bash
#!/bin/bash

set -e

echo "Updating operating system..."
sudo apt update
sudo apt full-upgrade -y

echo "Updating Pi-hole..."
sudo pihole updatePihole

echo "Updating Pi-hole blocklists..."
sudo pihole updateGravity

echo "Maintenance completed successfully."
echo "Rebooting..."
sudo reboot
```

Make the script executable:

```bash
chmod +x scripts/update.sh
```

Run it with:

```bash
./scripts/update.sh
```

> Rebooting automatically is optional. For a more robust implementation, the script can later be extended with logging, error handling, and a reboot flag.

## Verification

After configuring the network DNS, verify that clients are actually using Pi-hole.

### Check the DNS configuration

Linux:

```bash
resolvectl status
```

or:

```bash
cat /etc/resolv.conf
```

Windows:

```powershell
ipconfig /all
```

The configured DNS server should point to the Raspberry Pi.

### Check Pi-hole

Open the Pi-hole dashboard and verify that DNS queries are appearing.

The dashboard provides visibility into:

* Total DNS queries
* Blocked queries
* Block percentage
* Frequently requested domains
* Frequently blocked domains
* Client activity

### Test DNS resolution

```bash
nslookup example.com
```

The DNS server shown in the response should be the Raspberry Pi/Pi-hole address.

## Troubleshooting

### Devices are not using Pi-hole

Check:

1. The router's DHCP DNS configuration.
2. The client's current DHCP lease.
3. The client's configured DNS server.
4. Whether the client has manually configured DNS.
5. Whether IPv6 DNS configuration is bypassing the Pi-hole.

### Pi-hole dashboard is unavailable

Check that the Raspberry Pi is reachable:

```bash
ping <PI-HOLE-IP>
```

Check Pi-hole status:

```bash
pihole status
```

Check listening services:

```bash
sudo ss -lntup
```

### DNS stops working

Check Pi-hole logs and DNS resolution:

```bash
pihole status
```

```bash
nslookup example.com <PI-HOLE-IP>
```

If Pi-hole is unavailable, clients configured exclusively to use it as DNS may lose DNS resolution. This is an important availability consideration for a network-wide DNS service.

## Security Considerations

This project is intended for a private home network.

Recommended practices:

* Keep Raspberry Pi OS updated.
* Keep Pi-hole updated.
* Use SSH keys instead of password authentication where practical.
* Do not expose the Pi-hole administration interface to the public internet.
* Restrict router administration to the local network.
* Use a strong Pi-hole administrator password.
* Monitor DNS activity for unexpected behavior.
* Keep backups of important configuration.

## Future Improvements

Planned improvements:

* [x] Add automated update script
* [ ] Run the maintenance script automatically using `systemd` or cron
* [ ] Add structured logging
* [ ] Add update failure handling
* [ ] Add health-check script
* [ ] Monitor Pi-hole availability
* [ ] Export Pi-hole metrics to a monitoring dashboard
* [ ] Send alerts using ntfy when DNS service becomes unavailable, system is updated using the automated script, a device connects on the network, something suspicios happens in the logs
* [ ] Add GitLab CI validation for Bash scripts
* [ ] Document disaster recovery / SD-card replacement
* [ ] Move the system to SSD storage for improved reliability

## Disclaimer

This project is designed for educational and personal home-network use. DNS filtering can occasionally block domains required by websites or applications. Blocklists should therefore be selected and maintained according to the network's requirements.

## Author
Mihai A. Nițu

GitLab: https://gitlab.com/MAnitsu
LinkedIn: https://www.linkedin.com/in/mihai-alexandru-nitu-b8035a16a/
