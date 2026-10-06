# HomeSentinel Architecture

HomeSentinel is a Raspberry Pi-based home-network monitoring system combining DNS filtering, automation, monitoring, network discovery, remote access, and a local dashboard.

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
                 │                     │
                 │     Tailscale       │
                 └─────────────────────┘
                            ▲
                            │
                       Tailscale VPN
                            │
                         Phone
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
* Tailscale management
* HomeSentinel Control Panel

The Control Panel communicates with the HomeSentinel API through the same network path used to access Homepage.

When Homepage is accessed through the LAN address, the Control Panel uses the LAN API address.

When Homepage is accessed through Tailscale, the Control Panel uses the Tailscale API address.

This is handled by a small Homepage custom JavaScript configuration, allowing the same dashboard configuration to work in both environments without requiring a reverse proxy.

### Tailscale

Tailscale provides secure remote access to the Raspberry Pi without exposing HomeSentinel services directly to the public internet.

The current implementation uses direct access to the Raspberry Pi over its Tailscale address.

Subnet routing and exit-node functionality are not required.

## Remote Pi-hole DNS

Tailscale is also configured to use the Raspberry Pi as a DNS nameserver for connected clients.

The remote DNS flow is:

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

This allows connected remote devices to use the same Pi-hole filtering and blocklists as devices on the home network.

Only DNS requests use the Pi-hole path.

Normal internet traffic continues through the remote device's existing network connection. The Raspberry Pi is not configured as a Tailscale exit node.

This provides remote DNS filtering without routing all device traffic through the home network.

## Remote Access Flow

```text
Phone
  │
  │ Tailscale
  ▼
Raspberry Pi
  ├── Homepage
  ├── HomeSentinel API
  └── Pi-hole
```

## LAN and Remote Dashboard Access

HomeSentinel supports both local LAN access and remote access through Tailscale.

### LAN

```text
Browser
   │
   ▼
Homepage :3000
   │
   ▼
HomeSentinel API :8000
```

### Tailscale

```text
Phone
   │
   │ Tailscale
   ▼
Homepage :3000
   │
   ▼
HomeSentinel API :8000
```

The Homepage Control Panel dynamically determines the host address from the URL used to access the dashboard.

This means the same Homepage configuration works locally and remotely without exposing the API publicly or introducing a reverse proxy.

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

| Component               | Status   |
| ----------------------- | -------- |
| Pi-hole                 | Complete |
| Health monitoring       | Complete |
| Maintenance automation  | Complete |
| FastAPI                 | Complete |
| Homepage                | Complete |
| Nmap discovery          | Complete |
| Tailscale remote access | Complete |
| Remote Pi-hole DNS      | Complete |
| Trading 212             | Local    |
| Notifications           | Planned  |
| GitLab CI/CD            | Planned  |
| SSD migration           | Planned  |

## Design Principles

* Keep runtime data separate from source code.
* Automate recurring tasks with systemd.
* Use controlled API actions instead of arbitrary commands.
* Keep private configuration on the Raspberry Pi.
* Keep the GitLab repository generic and reusable.
* Use Tailscale instead of exposing internal services through router port forwarding.
* Use Pi-hole as the remote DNS resolver for authorized Tailscale clients.
* Do not route all remote client traffic through the Raspberry Pi unless an exit-node configuration is intentionally introduced.
