# HomeSentinel Security

This document describes the security model used by HomeSentinel and the principles applied when deploying, operating, and extending the system.

HomeSentinel is designed for a private home network. Its security model focuses on **least privilege, limited network exposure, separation of secrets, controlled system actions, and safe handling of reusable configuration**.

---

# 1. Security Model

The current architecture follows these principles:

```text
                    Security Boundary
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
   Least Privilege   Secret Separation   Limited Exposure
        │                  │                  │
        ▼                  ▼                  ▼
   Restricted sudo   Local credentials    LAN-only API
        │
        ▼
 Controlled Actions
```

The main security goals are:

1. Prevent unnecessary root access.
2. Prevent credentials from entering source control.
3. Avoid exposing infrastructure services directly to the internet.
4. Restrict API actions to predefined operations.
5. Keep runtime configuration separate from reusable project files.
6. Make security boundaries explicit and auditable.

---

# 2. Private Network Scope

HomeSentinel is intended to operate inside a private home network.

The main infrastructure components are:

```text
Home LAN
│
├── Router
│
├── Client devices
│
└── Raspberry Pi
    ├── Pi-hole
    ├── HomeSentinel API
    └── Homepage
```

The HomeSentinel API is not intended to be publicly exposed.

Direct port forwarding from the router to the API should not be used as the remote-access mechanism.

Future remote access is planned through a VPN-based architecture using Tailscale.

---

# 3. Repository and Runtime Separation

One of the most important security controls is separating reusable source code from private runtime information.

```text
                    HomeSentinel
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
           GitLab               Raspberry Pi
              │                     │
        Public/reusable          Private
              │                     │
        ┌─────┴─────┐       ┌───────┴────────┐
        │           │       │                │
     Source      Templates  Credentials     Logs
     Code        Examples   Runtime data     IPs
     Docs        Config     Private URLs     Results
```

GitLab should contain only generic or intentionally public information.

The Raspberry Pi contains environment-specific information.

---

# 4. Information That Must Not Be Committed

The following should remain outside GitLab:

* Private IP addresses
* Local usernames
* Passwords
* API keys
* API tokens
* Authentication secrets
* Pi-hole credentials
* Private URLs
* Runtime logs
* Health result files
* Maintenance result files
* Private network information
* Device-specific identifiers where unnecessary

Configuration examples should use placeholders such as:

```text
<USERNAME>
<PI-IP>
<HOSTNAME>
<API-KEY>
<PASSWORD>
```

Never replace these placeholders with real values in files intended for the repository.

---

# 5. Secret Management

Secrets should be supplied at runtime rather than hard-coded into source files.

For example, Homepage uses an environment variable for the Pi-hole password:

```yaml
environment:
  HOMEPAGE_VAR_PIHOLE_PASSWORD: ${PIHOLE_PASSWORD}
```

The actual value belongs in the local deployment environment.

It should not be written directly into:

```text
services.yaml
compose.yaml
README.md
```

or any other GitLab-tracked file.

---

# 6. API Privilege Model

The HomeSentinel API runs as an unprivileged Linux user.

It does not run as root.

```text
FastAPI
   │
   │ unprivileged user
   ▼
sudo
   │
   ├── Health service
   ├── Maintenance service
   └── Controlled reboot
```

This creates a deliberate privilege boundary.

If the API were compromised, the attacker would not automatically receive unrestricted root privileges through the API process.

---

# 7. Restricted sudoers Configuration

The API requires elevated privileges for a small number of system operations.

The sudoers configuration therefore allows only explicitly required commands.

Conceptually:

```text
<USERNAME>
   │
   └── NOPASSWD
        │
        ├── systemctl start health service
        ├── systemctl start maintenance service
        └── execute reboot wrapper
```

The API does not receive:

```text
ALL=(ALL) NOPASSWD: ALL
```

or another unrestricted sudo rule.

The repository contains a generic template:

```text
systemd/homesentinel-api-sudoers.example
```

The deployment-specific version belongs on the Raspberry Pi.

---

# 8. Validate sudoers Configuration

Never modify sudoers without validating the syntax.

Use:

```bash
sudo visudo -cf /etc/sudoers.d/homesentinel-api
```

A successful validation should report that the configuration was parsed successfully.

The effective permissions can be reviewed with:

```bash
sudo -n -l
```

Verify that only the intended commands are permitted.

---

# 9. Controlled System Actions

The API exposes a small number of privileged actions:

```text
POST /health
POST /update
POST /reboot
```

These actions map to predefined system operations.

The API does not provide an endpoint such as:

```text
POST /execute
```

where arbitrary shell commands could be supplied.

This distinction is important.

The API provides **capabilities**, not arbitrary command execution.

---

# 10. Controlled Reboot

The reboot operation uses a dedicated wrapper:

```text
/usr/local/bin/homesentinel-reboot
```

The wrapper performs a fixed system reboot operation.

The flow is:

```text
Client
  │
  ▼
POST /reboot
  │
  ▼
FastAPI
  │
  ▼
Restricted sudo
  │
  ▼
Reboot wrapper
  │
  ▼
systemctl reboot
```

The wrapper allows the sudoers rule to reference one specific executable instead of granting the API permission to execute arbitrary system commands.

---

# 11. API Network Exposure

The API currently listens on the Raspberry Pi's local network interface.

Example:

```text
http://<PI-IP>:8000
```

The service is intended for LAN access only.

It should not be exposed through:

* Router port forwarding
* Public DNS
* Reverse proxies accessible from the internet
* Direct public IP access

The future remote-access design will use Tailscale.

---

# 12. Why VPN-Based Remote Access

When remote administration is eventually required, the preferred architecture is:

```text
Phone
  │
  │ encrypted VPN
  ▼
Tailscale
  │
  ▼
Home Network
  │
  ▼
Raspberry Pi
  │
  ├── Homepage
  └── HomeSentinel API
```

This avoids making infrastructure administration endpoints publicly reachable.

Access-control policies can then determine which devices or users are allowed to reach specific services.

---

# 13. Future Access Control

The planned Tailscale implementation should distinguish between different levels of access.

For example:

```text
Administrator
    │
    ├── Homepage
    ├── HomeSentinel Control Panel
    ├── Pi-hole
    └── SSH

Limited User
    │
    └── Homepage
```

The exact ACL design will be defined when remote access is implemented.

Privileged administrative operations such as rebooting or maintenance should not automatically be available to every remote user.

---

# 14. Dashboard Security

Homepage provides visibility and links into HomeSentinel services.

The dashboard itself should not be treated as a security boundary.

Instead:

```text
Homepage
   │
   ▼
HomeSentinel API
   │
   ▼
Restricted system actions
```

Security decisions should therefore be enforced at the API and network layers rather than relying only on the dashboard interface.

---

# 15. Docker Security

Homepage runs inside Docker.

The container communicates with the Raspberry Pi host through:

```text
host.docker.internal
```

The container does not need unrestricted access to the host filesystem.

The deployment should avoid unnecessary Docker privileges such as:

```text
--privileged
```

unless a future component has a documented requirement for them.

Docker configuration should follow the principle of granting containers only the access they actually need.

---

# 16. API Authentication

The current API is designed for a trusted local network and does not yet implement a dedicated application authentication layer.

This is an important limitation.

The API should therefore remain LAN-only.

Before exposing HomeSentinel remotely, an authentication and authorization strategy should be implemented.

Possible future approaches include:

* Tailscale identity/access controls
* Application-level authentication
* Reverse proxy authentication
* Additional API authorization

Remote exposure should not be enabled before an appropriate access-control mechanism is in place.

---

# 17. Input Handling

The API should avoid passing user-controlled values directly to shell commands.

For privileged operations, commands should be defined explicitly in application code.

For example, the API should invoke:

```text
systemctl start pi-hole-network-health.service
```

rather than accepting:

```text
<arbitrary user command>
```

as input.

This reduces the risk of command injection and keeps the available capabilities narrowly defined.

---

# 18. File Permissions

Runtime files should have appropriate ownership and permissions.

Sensitive files should not be world-readable.

Examples of files requiring attention include:

```text
/var/lib/pi-hole-network/
/var/log/pi-hole-network/
/etc/sudoers.d/homesentinel-api
/usr/local/bin/homesentinel-reboot
/opt/homesentinel-api/
```

Sudoers configuration requires particularly careful permissions.

After creating or modifying privileged configuration, verify:

```bash
ls -l /etc/sudoers.d/homesentinel-api
```

---

# 19. Logging and Security

Logs are useful for detecting failures and investigating unexpected behavior.

HomeSentinel maintains separate logs for:

* Health checks
* Maintenance operations
* API/systemd activity

Useful commands include:

```bash
sudo journalctl -u homesentinel-api.service
```

```bash
sudo journalctl -u pi-hole-network-health.service
```

```bash
sudo journalctl -u pi-hole-network-update.service
```

When investigating unexpected behavior, compare:

1. API logs
2. systemd logs
3. health results
4. maintenance results
5. Pi-hole activity

---

# 20. Update Strategy

Keeping the operating system and infrastructure software updated is part of the security model.

HomeSentinel automates:

```text
APT updates
     │
     ▼
Pi-hole update
     │
     ▼
Gravity / blocklist update
```

The maintenance process should be monitored rather than assumed to be successful.

The latest maintenance result can be inspected through:

```text
GET /maintenance
```

or the local result file.

---

# 21. Health Monitoring as a Security Support Mechanism

The health system is primarily an availability mechanism, but it also provides useful security-adjacent visibility.

For example, unexpected changes in:

* DNS behavior
* Pi-hole availability
* System resource usage
* Service state

can indicate that something on the system requires investigation.

Health monitoring should not be considered a security detection system by itself.

It is an operational monitoring layer that can support broader security monitoring in the future.

---

# 22. Future Security Monitoring

Potential future additions include:

* Authentication for the API
* Tailscale ACLs
* SSH key-only authentication
* Firewall configuration
* Service exposure auditing
* Port scanning
* Configuration integrity checks
* Suspicious DNS monitoring
* Notification on service failures
* Notification on unexpected system changes
* Security-focused CI checks
* Dependency vulnerability scanning

These should be introduced incrementally rather than adding unnecessary complexity to the Raspberry Pi.

---

# 23. GitLab Security

The repository should be reviewed before every commit.

Check for:

```text
[ ] IP addresses
[ ] Usernames
[ ] Passwords
[ ] API keys
[ ] Tokens
[ ] Private URLs
[ ] Authentication credentials
[ ] Runtime logs
[ ] Health result files
[ ] Maintenance result files
[ ] Device-specific secrets
```

Generic examples should use placeholders.

For example:

```text
<PI-IP>
<USERNAME>
<PASSWORD>
<API-KEY>
```

rather than actual values.

---

# 24. Security Review Before Publishing

Before making the repository public, perform a manual review of:

```text
README.md
api/
homepage/
scripts/
systemd/
docs/
```

Search for potentially sensitive information:

```bash
grep -RniE 'password|passwd|secret|token|api.?key|private|192\.168\.|10\.|172\.(1[6-9]|2[0-9]|3[0-1])\.' .
```

This is only a basic check and should not be considered a complete secret scanner.

A dedicated secret-scanning tool should eventually be integrated into GitLab CI.

---

# 25. CI/CD Security

The planned GitLab CI pipeline should eventually validate the repository for common security problems.

Potential checks:

```text
GitLab CI
   │
   ├── ShellCheck
   ├── Python tests
   ├── Configuration validation
   ├── Secret scanning
   └── Documentation checks
```

The CI environment must also avoid exposing secrets through:

* Logs
* Job output
* Artifacts
* Test reports
* Generated files

Secrets required by CI should be stored using the appropriate GitLab protected/masked variable mechanisms.

---

# 26. Backup and Recovery

Security also includes the ability to recover from system failure.

Important configuration should be reproducible from:

* GitLab source
* Deployment documentation
* Router configuration
* Backup data

The project should eventually document:

```text
Raspberry Pi failure
        │
        ▼
Restore OS
        │
        ▼
Restore configuration
        │
        ▼
Restore services
        │
        ▼
Restore DNS
        │
        ▼
Verify HomeSentinel
```

SSD migration and disaster-recovery documentation are planned future improvements.

---

# 27. Security Trade-offs

HomeSentinel deliberately favors a simple architecture suitable for a Raspberry Pi home environment.

For example:

* The API currently relies on network isolation rather than application authentication.
* Homepage is intended for local access.
* The Raspberry Pi is not intended to host heavy security-monitoring platforms.
* Advanced security tooling can be added later if the hardware and requirements justify it.

The objective is to maintain a reasonable security boundary without introducing unnecessary operational complexity.

---

# 28. Security Checklist

### Repository

```text
[ ] No passwords committed
[ ] No API keys committed
[ ] No authentication tokens committed
[ ] No private IPs committed
[ ] No private URLs committed
[ ] No runtime logs committed
[ ] No generated health/maintenance files committed
[ ] Generic templates use placeholders
```

### Raspberry Pi

```text
[ ] Operating system updated
[ ] Pi-hole updated
[ ] HomeSentinel updated
[ ] SSH secured
[ ] API runs as unprivileged user
[ ] sudoers configuration restricted
[ ] Reboot wrapper restricted
[ ] Sensitive files have appropriate permissions
```

### Network

```text
[ ] API is LAN-only
[ ] No unnecessary port forwarding
[ ] Router administration remains protected
[ ] DNS configuration is intentional
[ ] Remote access uses VPN
```

### Remote access

```text
[ ] Tailscale configured
[ ] ACLs defined
[ ] Administrative access restricted
[ ] API not publicly exposed
[ ] Authentication strategy reviewed
```

---

# 29. Security Principles Summary

HomeSentinel follows a defense-in-depth approach:

```text
                  ┌──────────────────────┐
                  │   Private Network    │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │     Limited API      │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │  Unprivileged User   │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │   Restricted sudo    │
                  └──────────┬───────────┘
                             │
                  ┌──────────▼───────────┐
                  │ Controlled Actions   │
                  └──────────────────────┘
```

The most important principle is that every layer should have only the access required for its responsibility.

HomeSentinel therefore avoids treating the dashboard, API, or Raspberry Pi as inherently trusted components. Instead, permissions and capabilities are explicitly constrained wherever practical.

---

## Related Documentation

* [Architecture](architecture.md)
* [Setup](setup.md)
* [Operations](operations.md)
* [Roadmap](roadmap.md)
