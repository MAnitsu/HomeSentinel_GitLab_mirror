# Setup

HomeSentinel runs on a Raspberry Pi with Raspberry Pi OS Lite.

The repository contains reusable code and configuration templates. Private values such as IP addresses, credentials and API keys remain on the Raspberry Pi.

## Requirements

* Raspberry Pi 3B+ or newer
* Raspberry Pi OS Lite 64-bit
* Ethernet connection
* Router with DHCP configuration access

Additional components require:

* Git — for cloning the repository
* Python 3 — for HomeSentinel API
* Docker — for Homepage
* Nmap — for network discovery
* Tailscale — for remote access

## 1. Raspberry Pi

Install Raspberry Pi OS Lite and enable SSH.

Connect:

```bash
ssh <user>@<hostname>
```

Update the system:

```bash
sudo apt update
sudo apt full-upgrade
```

Configure a DHCP reservation for the Raspberry Pi on the router.

## 2. Pi-hole

Install Pi-hole using its official installation method.

Configure the router's DHCP DNS server to use the Raspberry Pi.

Verify:

```bash
pihole status
dig example.com
```

Configure additional blocklists if required and update Gravity:

```bash
sudo pihole updateGravity
```

## 3. HomeSentinel API

Clone/copy the API files to the Raspberry Pi and create the Python environment:

```bash
cd /opt/homesentinel-api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the local `.env` file with environment-specific configuration.

Never commit `.env`.

Run the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Test:

```bash
curl http://127.0.0.1:8000/health
```

The API is normally started through systemd.

## 4. Monitoring & Automation

Install the systemd templates from:

```text
systemd/
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now homesentinel-api.service
sudo systemctl enable --now pi-hole-network-health.timer
sudo systemctl enable --now pi-hole-network-update.timer
```

Check:

```bash
systemctl list-timers
```

## 5. Homepage

Create the local Homepage configuration using the templates in:

```text
homepage/
```

Start Docker:

```bash
docker compose up -d
```

Homepage is available at:

```text
http://<PI-IP>:3000
```

## 6. Network Discovery

Install Nmap:

```bash
sudo apt install nmap
```

Configure the private LAN in `.env`.

Test:

```bash
python api/network_scan.py
```

The latest scan is stored locally and exposed through:

```text
GET /network/scan
```

## 7. Remote Access

Install Tailscale on the Raspberry Pi using the official installation method.

Start Tailscale:

```bash
sudo tailscale up
```

Authenticate the Raspberry Pi with the Tailscale account.

Verify:

```bash
tailscale status
tailscale ip
```

Install Tailscale on a phone and connect it to the same Tailscale network.

Verify remote access to the Raspberry Pi:

```text
http://<TAILSCALE-IP>:3000
http://<TAILSCALE-IP>:8000/control
http://<TAILSCALE-IP>/admin
```

The current HomeSentinel setup uses direct access to the Raspberry Pi through Tailscale.

Subnet routing and exit-node functionality are not required.

## Verification

Check the main components:

```bash
pihole status
systemctl status homesentinel-api.service
systemctl list-timers
docker compose ps
curl http://127.0.0.1:8000/health
tailscale status
```

The system is ready when the components selected during installation are running normally.
