# Security

HomeSentinel is designed for use on a private home network.

## Secrets

Private credentials and configuration stay on the Raspberry Pi.

The GitLab repository must not contain:

* API keys or secrets
* Passwords
* Private IP addresses
* Private hostnames
* Runtime logs
* Runtime JSON results

Environment-specific values are stored locally in `.env` and protected with:

```bash
chmod 600 /opt/homesentinel-api/.env
```

## API Security

The FastAPI application runs as a normal Linux user, not as root.

The API exposes predefined actions rather than arbitrary command execution.

For example:

```text
POST /health
POST /update
POST /reboot
POST /network/scan
```

The API does not accept arbitrary shell commands or Nmap arguments.

## Privileged Actions

Only the operations that require elevated privileges are allowed through sudo:

```text
Health check service
Maintenance service
Controlled reboot
```

The sudo configuration is restricted to these specific commands.

Validate it with:

```bash
sudo visudo -cf /etc/sudoers.d/homesentinel-api
```

## Network Scanning

Nmap is currently used only for host discovery:

```bash
nmap -sn <PRIVATE-LAN-CIDR>
```

The network range is configured locally.

The API cannot be used to execute arbitrary Nmap commands.

The scan is intended only for networks the user owns or is authorized to test.

## Network Exposure

HomeSentinel services are intended to remain on the private network.

The HomeSentinel API should not be exposed directly to the internet.

Future remote access will use Tailscale rather than router port forwarding.

## Docker

Homepage runs in Docker and communicates with the HomeSentinel API.

Homepage does not receive unrestricted host access or privileged Docker mode.

## Current Limitations

HomeSentinel is a personal infrastructure project, not a hardened enterprise platform.

Application-level authentication for the Control Panel is not currently implemented.

Future security work includes:

* Tailscale access controls
* Notifications
* GitLab security checks
* Additional service scanning
* Firewall and SSH checks
* Dependency/security monitoring
