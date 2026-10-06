# HomeSentinel

**Self-hosted home-network monitoring and infrastructure dashboard running on a Raspberry Pi.**

HomeSentinel combines **Pi-hole, health monitoring, automated maintenance, FastAPI, Nmap, Docker, Homepage, and Tailscale** into a practical home-infrastructure project.

It demonstrates Linux administration, networking, automation, Python, Bash, systemd, APIs, containers, and security fundamentals.

---

## Architecture

```text
                         Internet
                            │
                            ▼
                         Router
                            │
                            ▼
                  ┌──────────────────┐
                  │   Raspberry Pi   │
                  │                  │
                  │ Pi-hole          │
                  │ Health / Updates │
                  │ FastAPI          │
                  │ Nmap             │
                  │ Homepage/Docker  │
                  │ Tailscale        │
                  └────────┬─────────┘
                           ▲
                           │ VPN
                           │
                          Phone
```

---

## Features

* Network-wide DNS filtering with **Pi-hole**
* Hagezi DNS blocklists
* Automated maintenance and health monitoring
* systemd services and timers
* Local **FastAPI** infrastructure API
* Homepage dashboard
* Docker deployment
* Controlled health, maintenance and reboot actions
* Nmap LAN host discovery
* Network Security Scan in the Control Panel
* **Tailscale remote access**
* Remote Pi-hole DNS filtering through Tailscale
* Local Trading 212 portfolio integration

---

## Technology

| Area              | Technology           |
| ----------------- | -------------------- |
| Hardware          | Raspberry Pi 3B+     |
| OS                | Raspberry Pi OS Lite |
| DNS               | Pi-hole              |
| Scripting         | Bash                 |
| API               | Python / FastAPI     |
| Scheduling        | systemd              |
| Dashboard         | Homepage             |
| Containers        | Docker               |
| Network discovery | Nmap                 |
| Remote access     | Tailscale            |
| Version control   | GitLab               |

---

## API

```text
GET  /health
POST /health

GET  /maintenance
POST /update

POST /reboot

GET  /network/scan
POST /network/scan

GET  /control
```

The API runs locally on the Raspberry Pi and exposes predefined infrastructure actions rather than arbitrary shell commands.

---

## Network Discovery

HomeSentinel uses Nmap for LAN host discovery:

```text
Control Panel
      │
      ▼
FastAPI
      │
      ▼
Nmap
      │
      ▼
JSON result
```

The scanner uses `nmap -sn` on the configured private network. It provides network inventory rather than vulnerability scanning.

---

## Dashboard

Homepage provides:

* Raspberry Pi resources
* Pi-hole statistics
* Health and maintenance status
* Network discovery
* Personal integrations
* Tailscale management

The Control Panel provides:

* Health checks
* Maintenance
* Network scans
* Raspberry Pi reboot

### LAN and remote access

Homepage supports both local LAN access and remote access through Tailscale.

The HomeSentinel Control Panel dynamically uses the same host address through which Homepage was accessed. This allows the same dashboard configuration to work in both environments without requiring a reverse proxy.

---

## Remote Access

Tailscale provides secure remote access to the Raspberry Pi without exposing HomeSentinel services directly to the internet.

Current remote access includes:

* Homepage
* HomeSentinel Control Panel
* Pi-hole administration
* Pi-hole DNS filtering

### Remote DNS filtering

Tailscale is configured to use the HomeSentinel Pi-hole instance as a tailnet DNS nameserver.

When a device is connected to Tailscale:

```text
Remote Device
      │
      │ Tailscale
      ▼
Raspberry Pi
      │
      ▼
   Pi-hole
      │
      ▼
 Upstream DNS
```

DNS requests are therefore filtered by the same Pi-hole blocklists used by the home network.

Normal internet traffic does not need to be routed through the Raspberry Pi. Tailscale provides the path to Pi-hole for DNS resolution while the device continues using its normal network connection for internet traffic.

Subnet routing and exit-node configuration are not required for this setup.

DNS is not exposed through router port forwarding.

---

## Repository

```text
HomeSentinel/
├── api/
├── homepage/
├── scripts/
├── systemd/
├── docs/
└── README.md
```

GitLab contains reusable source code, templates and documentation.

Private configuration, credentials, logs and runtime data remain on the Raspberry Pi.

---

## Security

* No secrets committed to GitLab
* API runs as a non-root user
* Privileged actions use restricted sudo rules
* No arbitrary shell execution through the API
* Nmap scanning is limited to the configured LAN
* Internal services are not publicly exposed
* DNS is not exposed through router port forwarding
* Remote access uses Tailscale
* Tailscale provides the remote DNS path to Pi-hole

See [`docs/security.md`](docs/security.md).

---

## Status

| Component               | Status   |
| ----------------------- | -------- |
| Pi-hole                 | Complete |
| Automation              | Complete |
| Health monitoring       | Complete |
| FastAPI                 | Complete |
| Nmap discovery          | Complete |
| Tailscale remote access | Complete |
| Remote Pi-hole DNS      | Complete |
| Homepage                | Complete |
| Notifications           | Planned  |
| GitLab CI/CD            | Planned  |
| SSD migration           | Planned  |

---

## Documentation

* [Architecture](docs/architecture.md)
* [Setup](docs/setup.md)
* [Operations](docs/operations.md)
* [Security](docs/security.md)
* [Roadmap](docs/roadmap.md)

---

## Author

**Mihai A. Nițu**

GitLab: https://gitlab.com/MAnitsu

LinkedIn: https://www.linkedin.com/in/mihai-alexandru-nitu-b8035a16/
