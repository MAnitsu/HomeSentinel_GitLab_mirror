# HomeSentinel

**Self-hosted home-network monitoring and infrastructure dashboard running on a Raspberry Pi.**

HomeSentinel combines Pi-hole, automated health monitoring, maintenance automation, a local FastAPI API, Nmap network discovery, and a Homepage dashboard.

The project is built as a practical Linux/infrastructure project and demonstrates networking, automation, Python, Bash, Docker, systemd, API development, and basic security monitoring.

---

## Architecture

```text
                         Internet
                            │
                            ▼
                     ┌─────────────┐
                     │   Router    │
                     │ DHCP / LAN  │
                     └──────┬──────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Raspberry Pi     │
                 │                     │
                 │      Pi-hole        │
                 │                     │
                 │  Health Monitoring  │
                 │    Maintenance      │
                 │   HomeSentinel API  │
                 │   Nmap Discovery    │
                 │                     │
                 │     Homepage        │
                 │      Docker         │
                 └─────────────────────┘
```

---

## Features

* Network-wide DNS filtering with **Pi-hole**
* Hagezi DNS blocklists
* Automated system and Pi-hole maintenance
* Automated health monitoring
* Structured JSON health results
* systemd services and timers
* Local **FastAPI** infrastructure API
* Homepage dashboard
* Docker-based dashboard deployment
* Controlled health and maintenance actions
* Controlled Raspberry Pi reboot
* Least-privilege sudo configuration
* Nmap LAN host discovery
* Network Security Scan in the Control Panel
* Local Trading 212 portfolio integrations

---

## Technology

| Area              | Technology           |
| ----------------- | -------------------- |
| Hardware          | Raspberry Pi 3B+     |
| OS                | Raspberry Pi OS Lite |
| DNS               | Pi-hole              |
| Scripting         | Bash                 |
| API               | Python, FastAPI      |
| Scheduling        | systemd              |
| Dashboard         | Homepage             |
| Containers        | Docker               |
| Network discovery | Nmap                 |
| Version control   | GitLab               |

---

## API

The HomeSentinel API currently provides:

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

The API is intended for local-network use.

---

## Network Discovery

HomeSentinel uses Nmap for LAN host discovery.

```text
Control Panel
      │
      ▼
HomeSentinel API
      │
      ▼
Nmap
      │
      ▼
Structured JSON result
```

The current scanner uses `nmap -sn` and identifies active hosts on the configured private network.

It is a network inventory feature, not a vulnerability scanner.

---

## Dashboard

Homepage provides a single place to view:

* Raspberry Pi resources
* Pi-hole statistics
* Health status
* Maintenance status
* Network discovery
* Personal integrations

The HomeSentinel Control Panel provides controlled actions such as:

* Run health check
* Run maintenance
* Run network scan
* Reboot Raspberry Pi

---

## Repository Structure

```text
HomeSentinel/
├── api/
├── homepage/
├── scripts/
├── systemd/
├── docs/
└── README.md
```

The repository contains reusable source code, templates and documentation.

Private deployment configuration remains on the Raspberry Pi.

---

## Security

HomeSentinel follows a few simple security principles:

* No secrets in GitLab
* API runs as a non-root user
* Privileged actions use restricted sudo rules
* No arbitrary shell commands through the API
* Nmap scanning is limited to the configured LAN
* Internal services are not exposed directly to the internet

Remote access is planned through Tailscale.

See [`docs/security.md`](docs/security.md).

---

## Project Status

**Core infrastructure:** Complete

**Automation:** Complete

**Health monitoring:** Complete

**HomeSentinel API:** Complete

**Nmap network discovery:** Complete

**Dashboard:** In progress

**Remote access:** Planned

**Notifications:** Planned

**CI/CD validation:** Planned

---

## Documentation

* [Architecture](docs/architecture.md)
* [Setup](docs/setup.md)
* [Operations](docs/operations.md)
* [Security](docs/security.md)
* [Roadmap](docs/roadmap.md)

---

## What This Project Demonstrates

HomeSentinel is primarily a learning and portfolio project covering:

* Linux administration
* Networking and DNS
* Bash scripting
* Python
* REST APIs
* systemd
* Docker
* Infrastructure monitoring
* Network discovery
* GitLab
* Security fundamentals
* Automation

The project is intentionally built incrementally on real hardware rather than as a purely theoretical infrastructure exercise.

---

## Author

Mihai A. Nițu

GitLab: https://gitlab.com/MAnitsu

LinkedIn: https://www.linkedin.com/in/mihai-alexandru-nitu-b8035a16/
