# HomeSentinel Architecture

This document describes the architecture, components, data flows, and security boundaries of the HomeSentinel home-network infrastructure project.

HomeSentinel is designed as a modular self-hosted system where DNS filtering, monitoring, maintenance automation, an infrastructure API, and a web dashboard operate as separate components.

---

## 1. High-Level Architecture

```text
                              Internet
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     Router      │
                         │                 │
                         │ DHCP / Network  │
                         │ DNS assignment  │
                         └────────┬────────┘
                                  │
                           DNS queries
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │     Raspberry Pi        │
                    │                         │
                    │      Raspberry Pi OS    │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │      Pi-hole      │  │
                    │  │    DNS filtering  │  │
                    │  └─────────┬─────────┘  │
                    │            │            │
                    │            ▼            │
                    │      Upstream DNS       │
                    │                         │
                    │  ┌───────────────────┐  │
                    │  │   HomeSentinel    │  │
                    │  │      API         │  │
                    │  └─────────┬─────────┘  │
                    │            │            │
                    │  ┌─────────▼─────────┐  │
                    │  │ Health /          │  │
                    │  │ Maintenance data  │  │
                    │  └─────────┬─────────┘  │
                    │            │            │
                    │  ┌─────────▼─────────┐  │
                    │  │     Homepage      │  │
                    │  │    Dashboard      │  │
                    │  └───────────────────┘  │
                    │                         │
                    └─────────────────────────┘
```

The Raspberry Pi is the central infrastructure node.

Pi-hole handles DNS filtering, while HomeSentinel provides automation, monitoring, API control, and dashboard integration.

---

## 2. Component Overview

| Component          | Responsibility                                |
| ------------------ | --------------------------------------------- |
| Router             | DHCP, LAN connectivity, DNS server assignment |
| Raspberry Pi       | Infrastructure host                           |
| Raspberry Pi OS    | Operating system                              |
| Pi-hole            | Network-wide DNS filtering                    |
| Upstream DNS       | Resolves DNS requests allowed by Pi-hole      |
| Hagezi blocklists  | Additional DNS filtering rules                |
| Bash scripts       | Maintenance and health automation             |
| systemd            | Service management and scheduling             |
| Health JSON        | Stores latest health-check result             |
| Maintenance result | Stores latest maintenance result              |
| FastAPI            | Provides the HomeSentinel REST API            |
| Docker             | Runs the Homepage dashboard                   |
| Homepage           | Provides the web dashboard                    |
| sudoers            | Restricts privileged API operations           |

---

# 3. Network Architecture

The router remains the primary network gateway.

Clients receive their network configuration through DHCP. The router advertises the Raspberry Pi as the DNS server for the network.

```text
Client
  │
  │ DNS query
  ▼
Router
  │
  │ DNS → Raspberry Pi
  ▼
Pi-hole
  │
  ├── Blocked → Response returned
  │
  └── Allowed
        │
        ▼
   Upstream DNS
        │
        ▼
     Internet
```

This means DNS filtering is centralized rather than configured individually on every client.

### Advantages

* One configuration point for the home network
* Centralized blocklists
* Visibility into DNS activity
* Reduced configuration on individual devices
* Consistent filtering across supported clients

### Consideration

If Pi-hole becomes unavailable and clients are configured exclusively to use it as their DNS server, DNS resolution may stop working.

This makes Pi-hole availability an important monitoring target.

---

# 4. Pi-hole Architecture

Pi-hole is responsible for DNS filtering.

The filtering process is:

```text
DNS Request
     │
     ▼
  Pi-hole
     │
     ▼
Check blocklists
     │
     ├── Blocked ──► Reject / block
     │
     └── Allowed
            │
            ▼
       Upstream DNS
            │
            ▼
         Response
```

HomeSentinel does not replace Pi-hole's DNS functionality.

Instead, it monitors Pi-hole and provides automation around the service.

---

# 5. Health Monitoring Architecture

Health monitoring is based on a shell script executed periodically by systemd.

```text
             systemd timer
                   │
                   ▼
           health_check.sh
                   │
          ┌────────┴─────────┐
          │                  │
          ▼                  ▼
      Run checks        Record results
          │                  │
          └────────┬─────────┘
                   ▼
              health.json
                   │
                   ▼
            HomeSentinel API
                   │
                   ▼
              Homepage
```

The health-check script currently validates:

1. Internet connectivity
2. DNS resolution
3. Pi-hole FTL service
4. Pi-hole DNS availability
5. Pi-hole blocking functionality
6. Upstream DNS availability
7. Disk usage
8. Memory usage
9. CPU temperature
10. System uptime

Each check produces a pass/fail result.

The overall health result is represented by a structured JSON document.

Example:

```json
{
  "status": "ok",
  "timestamp": "<timestamp>",
  "passed": 10,
  "failed": 0,
  "checks": {
    "internet": "pass",
    "dns": "pass",
    "pihole_service": "pass",
    "pihole_dns": "pass",
    "pihole_blocking": "pass",
    "upstream_dns": "pass",
    "disk": "pass",
    "memory": "pass",
    "temperature": "pass",
    "uptime": "pass"
  }
}
```

The actual runtime file is stored locally on the Raspberry Pi and is not committed to GitLab.

---

# 6. Maintenance Architecture

System maintenance is also automated through systemd.

```text
             systemd timer
                   │
                   ▼
               update.sh
                   │
          ┌────────┼─────────┐
          ▼        ▼         ▼
        APT     Pi-hole   Gravity
          │        │         │
          └────────┴─────────┘
                   │
                   ▼
          Maintenance result
                   │
                   ▼
              JSON result
```

The maintenance script performs:

* Operating-system package updates
* Operating-system package upgrades
* Pi-hole updates
* Pi-hole Gravity/blocklist updates

The script records:

* Start time
* Individual operation results
* Overall success/failure
* Completion time
* Maintenance logs

A separate result file records the status of the most recent maintenance operation.

---

# 7. systemd Architecture

HomeSentinel uses systemd for both scheduling and service management.

```text
                    systemd
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   Health Timer               Update Timer
          │                         │
          ▼                         ▼
   Health Service            Update Service
          │                         │
          ▼                         ▼
 health_check.sh              update.sh
```

The API is also managed by systemd:

```text
systemd
   │
   ▼
homesentinel-api.service
   │
   ▼
Uvicorn
   │
   ▼
FastAPI
```

This provides:

* Automatic startup
* Service supervision
* Restart handling
* Centralized service status
* Scheduled execution
* Persistent timers
* Standard system logging

---

# 8. HomeSentinel API Architecture

The API acts as the bridge between the underlying infrastructure and the dashboard.

```text
┌──────────────────────┐
│   Infrastructure     │
│                      │
│ Health JSON          │
│ Maintenance result   │
│ systemd services     │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│   HomeSentinel API   │
│                      │
│       FastAPI        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│      Homepage        │
│      Dashboard       │
└──────────────────────┘
```

The API currently provides:

```text
GET  /health
POST /health

GET  /maintenance
POST /update

POST /reboot

GET  /control
```

### Read operations

`GET /health`

Returns the latest health-check result.

`GET /maintenance`

Returns the result of the latest maintenance operation.

### Controlled operations

`POST /health`

Starts the health-check systemd service and returns the resulting health data.

`POST /update`

Starts the maintenance systemd service and returns the resulting maintenance status.

`POST /reboot`

Triggers a controlled Raspberry Pi reboot.

### Control panel

`GET /control`

Provides a browser-based control panel for manually triggering supported HomeSentinel actions.

---

# 9. API Security Boundary

The API runs as a normal Linux user rather than as root.

Privileged actions are exposed through narrowly defined sudo permissions.

```text
FastAPI
   │
   │ normal user
   ▼
sudo
   │
   ├── systemctl start health service
   │
   ├── systemctl start update service
   │
   └── execute controlled reboot wrapper
```

The API does **not** receive unrestricted root privileges.

This prevents an API vulnerability from automatically becoming unrestricted root shell access.

The sudo configuration therefore acts as a security boundary between:

```text
Unprivileged API
        │
        ▼
Approved infrastructure actions
        │
        ▼
Root privileges
```

Only explicitly required commands are permitted.

---

# 10. Controlled Reboot Architecture

Rebooting the Raspberry Pi is intentionally implemented through a dedicated wrapper script.

```text
Homepage
   │
   ▼
POST /reboot
   │
   ▼
FastAPI
   │
   ▼
sudo
   │
   ▼
homesentinel-reboot
   │
   ▼
systemctl reboot
```

The API does not construct or execute arbitrary shell commands.

The dedicated wrapper provides a fixed command path that can be explicitly allowed through sudoers.

This follows the same least-privilege design used for health and maintenance operations.

---

# 11. Dashboard Architecture

Homepage runs inside Docker.

```text
                    Raspberry Pi
                         │
                         │
                 ┌───────▼────────┐
                 │     Docker     │
                 │                │
                 │    Homepage    │
                 └───────┬────────┘
                         │
                         │ HTTP
                         ▼
                HomeSentinel API
                         │
               ┌─────────┴─────────┐
               │                   │
               ▼                   ▼
          Health JSON        Maintenance
                              result
```

Homepage provides:

### System information

* CPU
* Memory
* Disk
* Temperature
* Uptime

### Network Services

* Pi-hole

### HomeSentinel

* Health Monitor
* Maintenance
* Control Panel

The dashboard is intended to provide visibility rather than contain the infrastructure logic itself.

---

# 12. Docker-to-Host Communication

Homepage runs inside a Docker container while the HomeSentinel API runs directly on the Raspberry Pi.

Therefore, the container needs a controlled way to communicate with the host.

The Docker configuration uses:

```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

This allows the Homepage container to access the host-side HomeSentinel API through:

```text
host.docker.internal
```

The resulting architecture is:

```text
Docker container
      │
      │ HTTP
      ▼
host.docker.internal
      │
      ▼
Raspberry Pi host
      │
      ▼
HomeSentinel API
```

This avoids hard-coding environment-specific container-to-host addressing into the reusable project templates.

---

# 13. Data Flow

HomeSentinel uses files as a lightweight persistence layer between scheduled scripts and the API.

### Health data

```text
health_check.sh
      │
      ▼
/var/lib/.../health.json
      │
      ▼
FastAPI
      │
      ▼
Homepage
```

### Maintenance data

```text
update.sh
      │
      ▼
/var/lib/.../update-result
      │
      ▼
FastAPI
      │
      ▼
Homepage
```

This approach keeps the monitoring scripts independent from the API.

The scripts can continue operating even if the API or dashboard is unavailable.

---

# 14. Logging

The system maintains separate logs for different operations.

```text
/var/log/
    │
    └── pi-hole-network/
            │
            ├── health.log
            └── update.log
```

The logs contain execution information useful for troubleshooting.

Structured result files are kept separate from human-readable logs.

This allows:

* Humans to inspect detailed logs
* The API to consume structured JSON
* The dashboard to display concise status information

---

# 15. Failure Handling

HomeSentinel is designed to distinguish between individual check failures and overall system state.

For health monitoring:

```text
Individual check
       │
       ├── PASS
       │
       └── FAIL
              │
              ▼
        Overall health
              │
        ┌─────┴─────┐
        ▼           ▼
       OK         FAILED
```

Maintenance operations stop when a required operation fails and record a failure result.

Scripts also return meaningful exit codes so that systemd can determine whether the service completed successfully.

This allows future monitoring and notification systems to react to failures without needing to interpret human-readable logs.

---

# 16. Repository and Runtime Separation

A core architectural principle is the separation between reusable project files and the private deployment.

```text
                   HomeSentinel
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
        GitLab Repo           Raspberry Pi
            │                     │
            │                     │
     Generic templates       Actual config
     Source code             Credentials
     Documentation           Logs
     Examples                Runtime data
     Systemd templates       Private network data
```

### GitLab

Contains reusable artifacts and documentation.

### Raspberry Pi

Contains environment-specific configuration and runtime data.

This makes the project suitable for public portfolio presentation without exposing details about the actual home network.

---

# 17. Current Security Model

The current deployment follows several security principles:

### Local-first

The HomeSentinel API is intended to remain accessible only from the local network.

### No public API exposure

The infrastructure API should not be exposed directly to the public internet.

### Least privilege

The API receives only the sudo permissions required for supported operations.

### No arbitrary command execution

The API exposes predefined actions rather than accepting arbitrary shell commands.

### Secret separation

Credentials and secrets remain outside the GitLab repository.

### Template-based configuration

Environment-specific values are represented by placeholders in the repository.

### Future secure remote access

Remote access is planned through Tailscale rather than direct port forwarding.

---

# 18. Architectural Goals

The architecture is designed around the following goals:

1. **Modularity** — components should have clearly defined responsibilities.
2. **Automation** — repetitive infrastructure tasks should run automatically.
3. **Observability** — system health should be visible and machine-readable.
4. **Security** — privileged operations should be tightly restricted.
5. **Maintainability** — scripts and services should be independently testable.
6. **Reusability** — repository artifacts should be generic rather than tied to one environment.
7. **Recoverability** — failures should be detectable and future recovery mechanisms should be possible.
8. **Extensibility** — future features such as notifications, remote access, CI/CD, monitoring integrations, and storage migration should be possible without redesigning the core architecture.

---

# 19. Future Architecture

The architecture is intended to evolve beyond the current deployment.

Planned additions include:

```text
                         Internet
                            │
                            ▼
                     ┌─────────────┐
                     │   Router    │
                     └──────┬──────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │  Raspberry Pi   │
                    │                 │
                    │     Pi-hole     │
                    │                 │
                    │  HomeSentinel   │
                    │       API       │
                    │        │        │
                    │   ┌────┴─────┐  │
                    │   │          │  │
                    │   ▼          ▼  │
                    │Monitoring  Dashboard
                    │   │          │  │
                    └───┼──────────┼──┘
                        │          │
                        ▼          ▼
                    ntfy        Homepage
                        │
                        ▼
                    Mobile
```

Future components may include:

* Tailscale remote access
* Access-control policies
* ntfy notifications
* GitLab CI/CD
* Additional monitoring
* Portfolio/infrastructure integrations
* SSD-based storage
* Backup and disaster-recovery workflows

These components are planned extensions and are not all part of the current deployment.

---

## 20. Design Summary

HomeSentinel follows a simple architecture:

```text
           AUTOMATION
               │
       ┌───────┴────────┐
       ▼                ▼
   Monitoring       Maintenance
       │                │
       └───────┬────────┘
               ▼
          Runtime Data
               │
               ▼
         HomeSentinel API
               │
               ▼
           Dashboard
```

The Raspberry Pi provides the infrastructure platform, Pi-hole provides DNS filtering, systemd provides service management and scheduling, Bash provides automation, FastAPI provides the control and data interface, and Homepage provides the user-facing dashboard.

The components remain loosely coupled so that monitoring, maintenance, API access, and dashboard functionality can evolve independently.
