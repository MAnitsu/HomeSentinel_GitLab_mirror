# HomeSentinel Setup Guide

This document describes how to deploy the HomeSentinel infrastructure on a Raspberry Pi.

The guide uses placeholders for environment-specific values. Replace them with values appropriate for the target environment.

Private IP addresses, usernames, passwords, API credentials, tokens, and other environment-specific information should not be committed to the GitLab repository.

---

# 1. Hardware

The reference deployment uses:

* Raspberry Pi 3B+
* 64 GB MicroSD card
* Appropriate Raspberry Pi power supply
* Ethernet connection
* Home router with DHCP configuration access

The architecture can also be adapted to other Raspberry Pi models and storage devices.

---

# 2. Operating System

Install **Raspberry Pi OS Lite 64-bit** using Raspberry Pi Imager.

Configure the image before writing it to the storage device.

Recommended configuration:

* Hostname
* Local Linux username
* Strong password
* SSH enabled
* Network connectivity

After writing the image, insert the storage device into the Raspberry Pi and power it on.

---

# 3. Initial SSH Connection

Connect to the Raspberry Pi:

```bash
ssh <USERNAME>@<HOSTNAME>.local
```

Verify the operating system:

```bash
cat /etc/os-release
```

Update the system:

```bash
sudo apt update
sudo apt full-upgrade -y
```

Reboot:

```bash
sudo reboot
```

Reconnect after the system has restarted.

---

# 4. Network Configuration

The Raspberry Pi provides infrastructure services, so its address should remain stable.

The preferred approach is a DHCP reservation configured on the router.

Example:

```text
Router
└── DHCP
    └── Address Reservation
        └── Raspberry Pi
```

Reserve an address using the Raspberry Pi's network interface or MAC address.

Use the router-assigned reserved address rather than manually configuring a static address on the operating system unless there is a specific reason to do so.

Verify the current address:

```bash
hostname -I
```

---

# 5. Install Pi-hole

Install Pi-hole using its official installation method.

During installation:

* Select the active network interface.
* Select an upstream DNS provider.
* Enable the default blocklists.
* Enable the web administration interface.
* Confirm the network interface and IP configuration.

After installation, verify Pi-hole:

```bash
pihole status
```

The administration interface should be available through:

```text
http://<PI-IP>/admin
```

Do not commit the actual URL if it contains private network information.

---

# 6. Configure Router DNS

The router should distribute the Raspberry Pi's address as the DNS server through DHCP.

Example:

```text
Router
└── DHCP Server
    └── Primary DNS
        └── <PI-IP>
```

Reconnect clients or renew their DHCP leases after changing the DNS configuration.

A client should now obtain the Raspberry Pi as its DNS server.

---

# 7. Verify DNS Filtering

From a client, check its DNS configuration.

### Linux

```bash
resolvectl status
```

or:

```bash
cat /etc/resolv.conf
```

### Windows

```powershell
ipconfig /all
```

The configured DNS server should point to the Raspberry Pi.

Test DNS resolution:

```bash
nslookup example.com
```

Test Pi-hole directly:

```bash
nslookup example.com <PI-IP>
```

Open the Pi-hole dashboard and verify that DNS queries are appearing.

---

# 8. Configure Additional Blocklists

Additional blocklists can be configured through the Pi-hole administration interface.

The project uses Hagezi DNS Blocklists as an additional source.

Select a list appropriate for the intended balance between filtering and compatibility.

For example:

```text
Hagezi Multi Pro
```

After adding or changing lists, update the Gravity database:

```bash
sudo pihole updateGravity
```

Verify that Gravity completed successfully.

---

# 9. HomeSentinel Repository

Clone or otherwise obtain the HomeSentinel project source on the development machine used to manage the project.

The GitLab repository contains generic project files.

The actual Raspberry Pi deployment should maintain its own environment-specific configuration.

A typical local structure is:

```text
HomeSentinel/
├── api/
├── homepage/
├── scripts/
├── systemd/
└── docs/
```

Do not copy private runtime files into the public repository.

---

# 10. Maintenance Script

The maintenance script performs:

* Operating-system package updates
* Operating-system package upgrades
* Pi-hole updates
* Pi-hole Gravity updates

The generic repository version is:

```text
scripts/update.sh
```

Make the script executable:

```bash
chmod +x scripts/update.sh
```

Run it manually:

```bash
./scripts/update.sh
```

Verify the exit code:

```bash
echo $?
```

A successful run should return:

```text
0
```

The script also creates persistent maintenance logs and a machine-readable result file.

---

# 11. Health Check Script

The health-check script validates the most important parts of the infrastructure.

It checks:

1. Internet connectivity
2. DNS resolution
3. Pi-hole FTL service
4. Pi-hole DNS
5. Pi-hole blocking
6. Upstream DNS
7. Disk usage
8. Memory usage
9. CPU temperature
10. System uptime

The generic repository template is:

```text
scripts/health_check.sh.example
```

Create the local deployment version:

```text
scripts/health_check.sh
```

Make it executable:

```bash
chmod +x scripts/health_check.sh
```

Run it manually:

```bash
./scripts/health_check.sh
```

A healthy system should finish with an overall successful result.

The script generates structured health information for consumption by the HomeSentinel API.

---

# 12. Required System Packages

The health-check implementation requires the utilities used by the individual checks.

Depending on the Raspberry Pi OS installation, additional packages may be required.

Typical utilities include:

```bash
curl
dig
jq
```

Install missing packages with:

```bash
sudo apt install <PACKAGE>
```

Verify availability:

```bash
command -v curl
command -v dig
command -v jq
```

---

# 13. systemd Maintenance Service

The repository contains:

```text
systemd/pi-hole-network-update.service.example
```

Create the local service:

```text
/etc/systemd/system/pi-hole-network-update.service
```

The service should execute the local maintenance script.

Example structure:

```ini
[Unit]
Description=Pi-hole Network Maintenance
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/path/to/scripts/update.sh
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Test the service:

```bash
sudo systemctl start pi-hole-network-update.service
```

Check the result:

```bash
sudo systemctl status pi-hole-network-update.service
```

View service logs:

```bash
sudo journalctl -u pi-hole-network-update.service
```

---

# 14. systemd Maintenance Timer

The repository contains:

```text
systemd/pi-hole-network-update.timer.example
```

Create:

```text
/etc/systemd/system/pi-hole-network-update.timer
```

Example:

```ini
[Unit]
Description=Run Pi-hole Network Maintenance Periodically

[Timer]
OnCalendar=Sun 03:00
Persistent=true
RandomizedDelaySec=30min

[Install]
WantedBy=timers.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable the timer:

```bash
sudo systemctl enable --now pi-hole-network-update.timer
```

Check the timer:

```bash
systemctl list-timers
```

The timer should appear as active and have a future trigger time.

---

# 15. systemd Health Service

The repository contains:

```text
systemd/pi-hole-network-health.service.example
```

Create the local service:

```text
/etc/systemd/system/pi-hole-network-health.service
```

Example:

```ini
[Unit]
Description=Pi-hole Network Health Check
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=/path/to/scripts/health_check.sh
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Run the service manually:

```bash
sudo systemctl start pi-hole-network-health.service
```

Check its status:

```bash
sudo systemctl status pi-hole-network-health.service
```

---

# 16. systemd Health Timer

The repository contains:

```text
systemd/pi-hole-network-health.timer.example
```

Example:

```ini
[Unit]
Description=Run Pi-hole Network Health Check Periodically

[Timer]
OnBootSec=5min
OnUnitActiveSec=15min
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now pi-hole-network-health.timer
```

Verify:

```bash
systemctl list-timers
```

The health timer should now periodically execute the health-check service.

---

# 17. HomeSentinel API

The API is implemented using Python and FastAPI.

The reference deployment uses a dedicated directory:

```text
/opt/homesentinel-api
```

Create the directory:

```bash
sudo mkdir -p /opt/homesentinel-api
```

Assign ownership to the Linux user that will run the API:

```bash
sudo chown <USERNAME>:<USERNAME> /opt/homesentinel-api
```

---

# 18. Python Virtual Environment

Enter the API directory:

```bash
cd /opt/homesentinel-api
```

Create the virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

The virtual environment should be activated whenever installing Python dependencies or manually working with the FastAPI application.

Install dependencies:

```bash
pip install -r requirements.txt
```

Verify FastAPI:

```bash
python -c "import fastapi; print(fastapi.__version__)"
```

---

# 19. API Application

The repository contains:

```text
api/main.py
api/requirements.txt
```

Copy the API source to the deployment directory or deploy it using the project's chosen delivery process.

The API currently provides:

```text
GET  /health
POST /health

GET  /maintenance
POST /update

POST /reboot

GET  /control
```

Run the API manually for testing:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API should then be reachable from the local network at:

```text
http://<PI-IP>:8000
```

Do not expose this service directly to the public internet.

---

# 20. API systemd Service

The repository contains:

```text
systemd/homesentinel-api.service.example
```

Create:

```text
/etc/systemd/system/homesentinel-api.service
```

Configure:

* The Linux user running the API
* The API installation directory
* The virtual-environment path

Example:

```ini
[Unit]
Description=HomeSentinel API
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=<USERNAME>
Group=<USERNAME>
WorkingDirectory=/path/to/homesentinel-api
ExecStart=/path/to/homesentinel-api/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable and start:

```bash
sudo systemctl enable --now homesentinel-api.service
```

Verify:

```bash
sudo systemctl status homesentinel-api.service
```

View logs:

```bash
sudo journalctl -u homesentinel-api.service
```

---

# 21. API Verification

Check the health endpoint:

```bash
curl http://<PI-IP>:8000/health
```

Check maintenance status:

```bash
curl http://<PI-IP>:8000/maintenance
```

The returned data should match the corresponding local result files.

Trigger a health check:

```bash
curl -X POST http://<PI-IP>:8000/health
```

Trigger maintenance:

```bash
curl -X POST http://<PI-IP>:8000/update
```

The API should return the resulting structured status.

---

# 22. Restricted sudo Permissions

The API runs as an unprivileged Linux user.

It requires limited sudo access for specific infrastructure operations.

The repository contains:

```text
systemd/homesentinel-api-sudoers.example
```

Create a local sudoers configuration:

```text
/etc/sudoers.d/homesentinel-api
```

Replace `<USERNAME>` with the Linux user running the API.

The permitted operations should be limited to:

```text
/usr/bin/systemctl start pi-hole-network-health.service
/usr/bin/systemctl start pi-hole-network-update.service
/usr/local/bin/homesentinel-reboot
```

Validate the configuration:

```bash
sudo visudo -cf /etc/sudoers.d/homesentinel-api
```

The configuration must pass validation before the API is restarted.

---

# 23. Controlled Reboot

The repository contains:

```text
scripts/homesentinel-reboot.example
```

Create the local executable:

```text
/usr/local/bin/homesentinel-reboot
```

The script should contain only the controlled reboot operation.

Make it executable:

```bash
sudo chmod 755 /usr/local/bin/homesentinel-reboot
```

Test the command locally before enabling the API action:

```bash
sudo /usr/local/bin/homesentinel-reboot
```

The Raspberry Pi should reboot normally.

After the system restarts, verify:

```bash
systemctl list-timers
```

and:

```bash
sudo systemctl status homesentinel-api.service
```

The health and maintenance timers should remain enabled.

---

# 24. Install Docker

Install Docker using the official installation method appropriate for the Raspberry Pi OS version.

Verify:

```bash
docker --version
```

Verify Docker Compose:

```bash
docker compose version
```

Test the installation:

```bash
docker run --rm hello-world
```

If the Docker user-group configuration is changed, reconnect the SSH session before testing Docker commands without `sudo`.

---

# 25. Homepage

Homepage is deployed as a Docker container.

A typical deployment directory is:

```text
/opt/homepage
```

Example structure:

```text
/opt/homepage/
├── compose.yaml
└── config/
    ├── bookmarks.yaml
    ├── custom.css
    ├── custom.js
    ├── docker.yaml
    ├── kubernetes.yaml
    ├── proxmox.yaml
    ├── services.yaml
    ├── settings.yaml
    └── widgets.yaml
```

Only the configuration files required by the deployment need to be maintained.

---

# 26. Homepage Docker Compose

The repository contains:

```text
homepage/compose.yaml.example
```

The deployment-specific compose file should contain the actual environment values locally.

The generic configuration uses:

```yaml
services:
  homepage:
    image: ghcr.io/gethomepage/homepage:latest
    container_name: homepage
    ports:
      - "3000:3000"
    environment:
      HOMEPAGE_ALLOWED_HOSTS: <PI-IP>:3000
      HOMEPAGE_VAR_PIHOLE_PASSWORD: ${PIHOLE_PASSWORD}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - ./config:/app/config
    restart: unless-stopped
```

The Pi-hole password must be supplied through the local environment rather than committed to GitLab.

---

# 27. Homepage Configuration

The repository provides generic configuration templates:

```text
homepage/
├── services.yaml.example
├── settings.yaml.example
├── widgets.yaml.example
└── compose.yaml.example
```

The dashboard should include:

```text
Network Services
└── Pi-hole

HomeSentinel
├── Health Monitor
├── Maintenance
└── Control Panel
```

The HomeSentinel API is accessed from the Homepage container through:

```text
host.docker.internal
```

because the API runs on the Raspberry Pi host.

---

# 28. Start Homepage

From the Homepage deployment directory:

```bash
cd /opt/homepage
```

Start the container:

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs
```

The dashboard should be available at:

```text
http://<PI-IP>:3000
```

---

# 29. Verify Docker-to-Host Communication

Homepage must be able to reach the HomeSentinel API running on the host.

From inside the container:

```bash
docker exec homepage wget -qO- http://host.docker.internal:8000/health
```

If `jq` is installed:

```bash
docker exec homepage wget -qO- http://host.docker.internal:8000/health | jq
```

A valid health JSON response confirms that Docker-to-host communication is working.

---

# 30. Verify the Complete System

After deployment, verify each layer independently.

### Operating system

```bash
uptime
```

### Network

```bash
hostname -I
```

### DNS

```bash
nslookup example.com
```

### Pi-hole

```bash
pihole status
```

### Health service

```bash
sudo systemctl start pi-hole-network-health.service
```

### Health timer

```bash
systemctl list-timers
```

### Maintenance service

```bash
sudo systemctl start pi-hole-network-update.service
```

### Maintenance timer

```bash
systemctl list-timers
```

### HomeSentinel API

```bash
curl http://<PI-IP>:8000/health
```

### Docker

```bash
docker ps
```

### Homepage

Open:

```text
http://<PI-IP>:3000
```

### Control panel

Open:

```text
http://<PI-IP>:8000/control
```

---

# 31. Final Verification Checklist

```text
[ ] Raspberry Pi OS installed
[ ] SSH access works
[ ] Router DHCP reservation configured
[ ] Pi-hole installed
[ ] Router distributes Pi-hole as DNS
[ ] DNS filtering verified
[ ] Additional blocklists configured
[ ] update.sh tested
[ ] health_check.sh tested
[ ] Maintenance systemd service tested
[ ] Maintenance timer enabled
[ ] Health systemd service tested
[ ] Health timer enabled
[ ] Health JSON generated
[ ] Maintenance result generated
[ ] FastAPI installed
[ ] FastAPI virtual environment configured
[ ] API systemd service enabled
[ ] API endpoints verified
[ ] Restricted sudo configuration validated
[ ] Controlled reboot tested
[ ] Docker installed
[ ] Homepage container running
[ ] Homepage-to-host API communication verified
[ ] Pi-hole dashboard integration verified
[ ] HomeSentinel dashboard verified
[ ] Control panel verified
```

---

# 32. Deployment Principles

The deployment should follow these principles:

* Test components individually before integrating them.
* Keep private configuration outside GitLab.
* Validate systemd files before enabling them.
* Validate sudoers files with `visudo`.
* Keep the API running as an unprivileged user.
* Do not expose the API directly to the internet.
* Keep credentials out of Docker Compose files committed to GitLab.
* Verify timers after every major system change.
* Verify service recovery after reboot.
* Maintain backups before major storage or operating-system changes.

---

## Related Documentation

* [Architecture](architecture.md)
* [Operations](operations.md)
* [Security](security.md)
* [Roadmap](roadmap.md)
