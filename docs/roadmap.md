# HomeSentinel Roadmap

This document describes the planned evolution of HomeSentinel.

The roadmap is intentionally divided into completed and planned phases so that the project documentation reflects the actual implementation state.

---

# 1. Current Status

HomeSentinel currently provides:

```text
Network Foundation
        │
        ▼
      Pi-hole
        │
        ▼
  Automated Health
        │
        ▼
Automated Maintenance
        │
        ▼
   HomeSentinel API
        │
        ▼
 Homepage Dashboard
```

The core monitoring, maintenance, API, dashboard, and controlled system-action functionality is implemented.

---

# 2. Phase 1 — Network Foundation

**Status: Complete**

Implemented:

* Raspberry Pi deployment
* Raspberry Pi OS Lite
* SSH access
* Router DHCP configuration
* Reserved Raspberry Pi address
* Pi-hole
* Router DNS integration
* DNS filtering
* Additional blocklists
* GitLab project
* Generic configuration templates

---

# 3. Phase 2 — Automation & Dashboard

**Status: Complete**

Implemented:

### Maintenance

* Bash maintenance script
* Operating-system updates
* Pi-hole updates
* Gravity/blocklist updates
* Structured maintenance result
* Persistent maintenance logs
* systemd maintenance service
* systemd maintenance timer

### Health Monitoring

* Bash health-check script
* Internet connectivity check
* DNS check
* Pi-hole service check
* Pi-hole DNS check
* Pi-hole blocking check
* Upstream DNS check
* Disk check
* Memory check
* CPU temperature check
* Uptime check
* Structured JSON health result
* Persistent health logs
* systemd health service
* systemd health timer

### HomeSentinel API

* FastAPI application
* Health endpoint
* Maintenance endpoint
* Manual health execution
* Manual maintenance execution
* Controlled reboot
* Browser control panel
* Restricted sudo configuration

### Dashboard

* Docker
* Homepage
* System resource widgets
* Pi-hole integration
* Health monitoring card
* Maintenance card
* HomeSentinel control panel
* Responsive dashboard layout

---

# 4. Phase 3 — Secure Remote Access

**Status: Planned**

Introduce secure remote access to the HomeSentinel infrastructure.

Planned components:

* Tailscale
* Remote access from mobile devices
* Tailscale ACLs
* Administrative access policy
* Limited-user access
* Secure access to Homepage
* Secure access to HomeSentinel API
* Remote access to Pi-hole administration

Target architecture:

```text id="d8v1hm"
Mobile Device
      │
      ▼
  Tailscale
      │
      ▼
Home Network
      │
      ▼
Raspberry Pi
      │
 ┌────┴─────┐
 ▼          ▼
Homepage  HomeSentinel
             API
```

The API should remain inaccessible from the public internet.

---

# 5. Phase 4 — Notifications & Monitoring

**Status: Planned**

Add proactive notifications when important infrastructure events occur.

Planned components:

* ntfy
* Health failure notifications
* Health recovery notifications
* Maintenance failure notifications
* Maintenance completion notifications
* API/service failure notifications
* Optional resource alerts

Example:

```text id="byx8sj"
Health Timer
     │
     ▼
Health Check
     │
     ├── Healthy ──► No alert
     │
     └── Failed
          │
          ▼
        ntfy
          │
          ▼
       Mobile
```

Notifications should be generated from machine-readable health and maintenance results rather than parsing human-readable logs.

---

# 6. Phase 5 — GitLab CI/CD

**Status: Planned**

Introduce automated validation for the GitLab repository.

Planned checks:

```text id="k1b7n2"
GitLab Push
     │
     ▼
GitLab CI
     │
     ├── ShellCheck
     ├── Bash validation
     ├── Python tests
     ├── API validation
     ├── YAML/config validation
     ├── Secret scanning
     └── Documentation checks
```

Potential improvements:

* Automated API tests
* Script syntax validation
* Configuration linting
* Security scanning
* Dependency checks
* Automated test reports
* Pipeline artifacts

The goal is to ensure reusable project components remain valid before deployment.

---

# 7. Phase 6 — Security Monitoring

**Status: Planned**

Expand beyond availability monitoring into basic infrastructure security monitoring.

Potential features:

* Network port scanning
* Service exposure checks
* SSH configuration checks
* Firewall validation
* Configuration integrity checks
* Suspicious DNS activity monitoring
* Dependency vulnerability scanning
* Security-focused CI checks

The Raspberry Pi's hardware limitations should be considered before introducing resource-intensive security platforms.

Heavy vulnerability-scanning solutions should only be added if their operational cost is justified.

---

# 8. Phase 7 — Storage & Reliability

**Status: Planned**

Improve the physical reliability of the Raspberry Pi deployment.

Planned work:

* Migrate from MicroSD to SSD
* Verify SSD boot
* Keep the existing SD card as a fallback initially
* Document the migration process
* Document recovery procedures
* Improve backup strategy
* Document disaster recovery
* Test service recovery after storage failure

Target architecture:

```text id="b1l5xm"
Raspberry Pi
     │
     ▼
    SSD
     │
     ├── OS
     ├── Pi-hole
     ├── HomeSentinel
     └── Homepage

SD Card
   │
   └── Backup / fallback
```

The migration should be performed only after a verified backup and a confirmed SSD boot.

---

# 9. Phase 8 — Infrastructure Integrations

**Status: Planned**

Add optional integrations with external services where they provide useful dashboard information.

Potential integrations include:

* Trading 212
* Kraken
* Additional infrastructure APIs

The intended architecture is:

```text id="g7v0b3"
External Service
      │
      │ Read-only API
      ▼
HomeSentinel Integration
      │
      ▼
Homepage Dashboard
```

API credentials must remain local to the Raspberry Pi.

GitLab should contain only:

* Generic integration code
* Configuration templates
* Placeholder values
* Documentation

Actual API keys and secrets must never be committed.

---

# 10. Future Dashboard

The dashboard is intended to evolve into a single infrastructure overview.

Potential sections:

```text id="z5d2j8"
HomeSentinel
│
├── System
│   ├── CPU
│   ├── Memory
│   ├── Disk
│   ├── Temperature
│   └── Uptime
│
├── Network
│   ├── Pi-hole
│   ├── DNS Health
│   └── Network Health
│
├── Automation
│   ├── Health Checks
│   └── Maintenance
│
├── Security
│   ├── Service Status
│   └── Security Checks
│
├── External Services
│   ├── Trading 212
│   └── Kraken
│
└── Controls
    ├── Health Check
    ├── Maintenance
    └── Reboot
```

The dashboard should remain a presentation and control layer rather than becoming the location where core infrastructure logic is implemented.

---

# 11. Architecture Evolution

The intended long-term architecture is:

```text id="r7f4c1"
                         Internet
                            │
                            ▼
                       Home Router
                            │
                            ▼
                    ┌─────────────────┐
                    │  Raspberry Pi   │
                    │                 │
                    │     Pi-hole     │
                    │                 │
                    │  HomeSentinel   │
                    │      API        │
                    │        │        │
                    │   ┌────┴────┐   │
                    │   │         │   │
                    │   ▼         ▼   │
                    │ Health   Maintenance
                    │   │         │   │
                    │   └────┬────┘   │
                    │        │        │
                    │        ▼        │
                    │    Homepage     │
                    │                 │
                    └────────┬────────┘
                             │
                       Tailscale VPN
                             │
                    ┌────────┴────────┐
                    │                 │
                 Admin              User
                    │                 │
                    ▼                 ▼
               Full access       Limited access
```

Future notifications and external integrations will connect to the HomeSentinel API or supporting services without changing the fundamental monitoring architecture.

---

# 12. Implementation Principles

Future features should follow the same principles used by the current system.

### Keep components modular

New features should have clearly defined responsibilities.

### Prefer automation

Recurring tasks should be automated through systemd, scripts, or CI/CD where appropriate.

### Keep privileged actions restricted

New administrative capabilities should use explicit permissions rather than unrestricted root access.

### Keep secrets local

Credentials should never be required in the public repository.

### Keep the API controlled

New API endpoints should expose predefined capabilities rather than arbitrary system execution.

### Keep the Raspberry Pi lightweight

New services should be evaluated against the hardware's CPU, memory, storage, and maintenance requirements.

### Test before documenting

New features should be implemented and verified on the Raspberry Pi before their generic components are added to GitLab.

---

# 13. Roadmap Priorities

The roadmap is not a strict requirement to implement every feature.

The general order is:

```text id="7w3q8m"
Core Infrastructure
        │
        ▼
Automation
        │
        ▼
Monitoring
        │
        ▼
Dashboard
        │
        ▼
Remote Access
        │
        ▼
Notifications
        │
        ▼
CI/CD & Security
        │
        ▼
Reliability
        │
        ▼
Optional Integrations
```

Features should be added when they provide a meaningful improvement rather than simply increasing the number of technologies used by the project.

---

# 14. Current Focus

The core HomeSentinel platform is currently implemented.

The next major development areas are:

1. Secure remote access with Tailscale
2. Mobile access and access-control policies
3. Notifications with ntfy
4. GitLab CI/CD validation
5. SSD migration and recovery documentation
6. Additional security monitoring
7. Optional external-service integrations

Each feature should be implemented incrementally, tested locally, and then synchronized with the generic GitLab project.
