# HomeSentinel Architecture

HomeSentinel is a Raspberry Pi-based home-network monitoring system combining DNS filtering, automation, monitoring, network discovery, and a local dashboard.

## Overview

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
                 │  Health Monitoring  │
                 │    Maintenance      │
                 │   HomeSentinel API  │
                 │   Nmap Discovery    │
                 │                     │
                 │     Homepage        │
                 │      Docker         │
                 └─────────────────────┘
```

## Components

### Pi-hole

Provides network-wide DNS filtering and forwards allowed queries to the configured upstream DNS provider.

### Health Monitoring

A Bash script checks:

* Internet connectivity
* DNS
* Pi-hole
* System resources
* CPU temperature
* Uptime

Results are stored as JSON.

### Maintenance

A Bash script performs:

* OS updates
* Pi-hole updates
* Gravity/blocklist updates

systemd timers run maintenance and health checks automatically.

### HomeSentinel API

A small FastAPI application provides a controlled interface to the system.

```text
health.json
     │
     ▼
HomeSentinel API
     │
     ▼
Homepage
```

The API also exposes controlled actions such as health checks, maintenance, reboot, and network scanning.

### Network Discovery

Nmap performs LAN host discovery.

```text
Homepage
   │
   ▼
API
   │
   ▼
Nmap
   │
   ▼
network-scan.json
```

Only the configured private network is scanned.

### Homepage

Homepage provides the dashboard for:

* Raspberry Pi resources
* Pi-hole
* Health status
* Maintenance status
* Network discovery
* Personal integrations

## Runtime Flow

```text
systemd timer
     │
     ▼
Bash script
     │
     ▼
JSON result
     │
     ▼
FastAPI
     │
     ▼
Homepage
```

## Security Boundary

```text
GitLab
  │
  │ generic code/templates
  ▼
Raspberry Pi
  │
  ├── Private configuration
  ├── Credentials
  ├── Runtime data
  └── Services
```

The repository contains reusable code and templates.

Environment-specific configuration, credentials, logs, and runtime results remain on the Raspberry Pi.

The API runs as a non-root user and uses restricted sudo permissions for privileged actions.

## Project Structure

```text
HomeSentinel/
├── api/
├── homepage/
├── scripts/
├── systemd/
├── docs/
└── README.md
```

## Current State

| Component              | Status      |
| ---------------------- | ----------- |
| Pi-hole                | Complete    |
| Health monitoring      | Complete    |
| Maintenance automation | Complete    |
| FastAPI                | Complete    |
| Homepage               | In progress |
| Nmap discovery         | Complete    |
| Trading 212            | Local       |
| Tailscale              | Planned     |
| Notifications          | Planned     |
| GitLab CI/CD           | Planned     |

## Design Principles

* Keep runtime data separate from source code.
* Automate recurring tasks with systemd.
* Use controlled API actions instead of arbitrary commands.
* Keep private configuration on the Raspberry Pi.
* Keep the GitLab repository generic and reusable.
