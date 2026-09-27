# HomeSentinel — Self-Hosted Home Network Monitoring

HomeSentinel is a self-hosted home-network infrastructure project built around a **Raspberry Pi, Pi-hole, automated monitoring, a local REST API, and a web dashboard**.

The project combines network-wide DNS filtering with infrastructure automation and monitoring. It is designed as a practical environment for developing skills in **Linux administration, networking, DNS, Bash, Python, REST APIs, systemd, Docker, monitoring, and CI/CD**.

The Raspberry Pi contains the actual deployment and environment-specific configuration, while GitLab contains generic and reusable project components.

---

## Features

* Network-wide DNS filtering with Pi-hole
* Additional DNS blocklists
* Automated system and Pi-hole maintenance
* Automated infrastructure health monitoring
* Structured JSON health results
* Persistent monitoring and maintenance logs
* systemd services and timers
* Local FastAPI infrastructure API
* Homepage web dashboard
* Docker-based dashboard deployment
* Controlled health-check and maintenance actions
* Controlled Raspberry Pi reboot
* Least-privilege sudo configuration
* Generic configuration templates for GitLab
* Separation between source code and private runtime configuration

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
                     DNS requests
                            │
                            ▼
                 ┌─────────────────────┐
                 │    Raspberry Pi     │
                 │                     │
                 │      Pi-hole        │
                 │       DNS           │
                 │                     │
                 │   HomeSentinel      │
                 │                     │
                 │   Health Checks     │
                 │   Maintenance      │
                 │   FastAPI           │
                 │   Homepage         │
                 └──────────┬──────────┘
                            │
                     Allowed DNS
                            │
                            ▼
                      Upstream DNS
                            │
                            ▼
                         Internet
```

### Monitoring flow

```text
systemd timer
      │
      ▼
health_check.sh
      │
      ▼
health.json
      │
      ▼
HomeSentinel API
      │
      ▼
Homepage Dashboard
```

### Maintenance flow

```text
systemd timer
      │
      ▼
update.sh
      │
      ├── APT
      ├── Pi-hole
      └── Gravity / blocklists
              │
              ▼
        Result + logs
```

---

## Technology Stack

| Area                  | Technology                  |
| --------------------- | --------------------------- |
| Hardware              | Raspberry Pi 3B+            |
| Operating system      | Raspberry Pi OS Lite 64-bit |
| DNS filtering         | Pi-hole                     |
| Blocklists            | Hagezi DNS Blocklists       |
| Scripting             | Bash                        |
| API                   | Python / FastAPI            |
| API server            | Uvicorn                     |
| Scheduling            | systemd                     |
| Dashboard             | Homepage                    |
| Containers            | Docker                      |
| Remote administration | SSH                         |
| Version control       | Git / GitLab                |
| Future remote access  | Tailscale                   |
| Future notifications  | ntfy                        |
| Future CI/CD          | GitLab CI                   |

---

## HomeSentinel API

The local API provides a controlled interface between the monitoring system and the dashboard.

Current endpoints:

```text
GET  /health
POST /health

GET  /maintenance
POST /update

POST /reboot

GET  /control
```

The API reads structured monitoring results and can trigger predefined infrastructure actions.

Privileged operations do **not** receive unrestricted sudo access. The API is allowed to execute only specific systemd services and a dedicated reboot wrapper.

---

## Dashboard

Homepage provides the main monitoring interface.

Current sections include:

```text
Homepage
│
├── System
│   ├── CPU
│   ├── Memory
│   ├── Disk
│   ├── Temperature
│   └── Uptime
│
├── Network Services
│   └── Pi-hole
│
└── HomeSentinel
    ├── Health Monitor
    ├── Maintenance
    └── Control Panel
```

The HomeSentinel cards are arranged horizontally for a compact dashboard layout.

The **Control Panel** provides controlled actions such as:

* Running a health check
* Running maintenance
* Rebooting the Raspberry Pi

---

## Repository Structure

```text
HomeSentinel/
├── README.md
│
├── api/
│   ├── main.py
│   └── requirements.txt
│
├── homepage/
│   ├── compose.yaml.example
│   ├── services.yaml.example
│   ├── settings.yaml.example
│   └── widgets.yaml.example
│
├── scripts/
│   ├── health_check.sh.example
│   ├── homesentinel-reboot.example
│   └── update.sh
│
├── systemd/
│   ├── homesentinel-api.service.example
│   ├── homesentinel-api-sudoers.example
│   ├── pi-hole-network-health.service.example
│   ├── pi-hole-network-health.timer.example
│   ├── pi-hole-network-update.service.example
│   └── pi-hole-network-update.timer.example
│
└── docs/
    ├── architecture.md
    ├── setup.md
    ├── operations.md
    ├── security.md
    └── roadmap.md
```

The repository contains reusable source code, scripts, systemd templates, Docker/Homepage configuration templates, and documentation.

---

## Repository vs Raspberry Pi

The GitLab repository is intentionally separated from the actual home-network deployment.

### GitLab contains

* Generic scripts
* API source code
* Configuration templates
* systemd templates
* Docker/Homepage templates
* Documentation
* Tests and CI/CD configuration as the project evolves

### Raspberry Pi contains

* Actual usernames
* Private IP addresses
* Local filesystem paths
* Passwords
* API credentials
* Runtime configuration
* Logs
* Health and maintenance result files
* Private network information

Environment-specific configuration should never be committed to GitLab.

---

## Project Status

### Phase 1 — Network Foundation

**Complete**

* Raspberry Pi OS
* SSH
* Network configuration
* Pi-hole
* Router DNS configuration
* DNS blocklists
* GitLab project
* Generic configuration structure

### Phase 2 — Automation & Dashboard

**Complete**

* Maintenance automation
* Structured maintenance logging
* Maintenance result recording
* systemd maintenance service
* systemd maintenance timer
* Health-check automation
* Structured JSON health results
* Persistent health logging
* systemd health service
* systemd health timer
* FastAPI
* Health and maintenance API endpoints
* Controlled API actions
* Restricted sudo permissions
* Controlled reboot
* Docker
* Homepage
* Pi-hole dashboard integration
* HomeSentinel dashboard
* Control Panel

### Phase 3 — Remote Access

**Planned**

* Tailscale
* Remote iPhone access
* Access-control policies
* Secure remote dashboard access

### Phase 4 — Monitoring & Notifications

**Planned**

* ntfy
* Health failure notifications
* Recovery notifications
* Maintenance failure notifications

### Phase 5 — GitLab CI/CD

**Planned**

* ShellCheck
* Bash validation
* API validation
* Configuration validation
* Automated tests
* Documentation checks

### Phase 6 — Storage & Reliability

**Planned**

* SSD migration
* Backup strategy
* Recovery procedure
* SD-card fallback
* Disaster recovery documentation

---

## Documentation

Detailed documentation is separated from the main project overview:

* **[Architecture](docs/architecture.md)** — system design and component relationships
* **[Setup](docs/setup.md)** — installation and deployment
* **[Operations](docs/operations.md)** — maintenance, monitoring, commands, and troubleshooting
* **[Security](docs/security.md)** — secrets, permissions, API security, and network exposure
* **[Roadmap](docs/roadmap.md)** — planned features and future phases

---

## Skills Demonstrated

**Linux:** Raspberry Pi OS, SSH, package management, systemd

**Networking:** DHCP, DNS, upstream DNS, network troubleshooting

**Automation:** Bash scripting, scheduled maintenance, health checks

**Backend:** Python, FastAPI, REST APIs, JSON

**Infrastructure:** Pi-hole, Docker, Homepage, service management

**Security:** Least-privilege sudo, secret separation, controlled system actions

**DevOps:** Git, GitLab, configuration templates, CI/CD planning

**Monitoring:** Health checks, structured results, logging, dashboard integration

---

## Design Principles

### Separate source code from runtime data

Private configuration, credentials, logs, and generated results remain on the Raspberry Pi.

### Automate repetitive operations

Recurring maintenance and health monitoring are handled through scripts and systemd timers.

### Fail visibly

Scripts return meaningful exit codes and record failures instead of silently continuing.

### Keep components modular

Monitoring, maintenance, the API, dashboard, notifications, and remote access are designed as separate components.

### Minimize privileges

Infrastructure actions are exposed through predefined interfaces rather than arbitrary shell execution.

### Avoid unnecessary network exposure

Local services are intended to remain on the home network. Secure remote access will be provided through a VPN rather than direct public exposure.

### Keep the repository reusable

The GitLab project demonstrates the architecture without exposing details specific to one home network.

---

## Disclaimer

HomeSentinel is designed for educational and personal home-network use.

DNS filtering can occasionally block domains required by websites or applications. Blocklists should therefore be selected and maintained according to the requirements of the network.

## Author

Mihai A. Nițu

GitLab: https://gitlab.com/MAnitsu

LinkedIn: https://www.linkedin.com/in/mihai-alexandru-nitu-b8035a16/
