# HomeSentinel Security

HomeSentinel is designed for a private home network and follows a least-privilege approach.

## Secrets

* Credentials and API keys remain on the Raspberry Pi.
* Secrets are stored in `.env` with restricted permissions.
* Secrets and private configuration are not committed to GitLab.
* Runtime logs and results remain local.

## API Security

The HomeSentinel API runs as a non-root user.

Privileged operations are restricted through `sudoers` to specific commands:

* Run health check
* Run maintenance
* Reboot Raspberry Pi

The API does not provide arbitrary shell execution.

## Network Security

* Nmap scans are limited to the configured private LAN.
* Pi-hole, Homepage and the HomeSentinel API are intended for internal use.
* Services are not directly exposed to the public internet.
* There is no router port forwarding for DNS port 53.
* Router DMZ is disabled.
* Docker containers are limited to their required access.
* SSH should use strong authentication and preferably SSH keys.

## Remote Access

Tailscale provides remote access to the Raspberry Pi without exposing HomeSentinel services directly to the internet.

Current remote access includes:

* Homepage
* HomeSentinel Control Panel
* Pi-hole administration
* Pi-hole DNS for connected Tailscale clients

Tailscale DNS allows remote devices to use Pi-hole for DNS filtering without routing their normal internet traffic through the Raspberry Pi.

Subnet routing and exit-node configuration are not required.

Additional Tailscale users and access policies may be configured later if required.

## Current Limitations

HomeSentinel is a personal infrastructure project rather than a hardened production environment.

Future security improvements may include:

* SSH security auditing
* Firewall monitoring
* Dependency vulnerability checks
* API authentication for privileged actions
* Network-change alerts
* Security-focused GitLab CI checks
* More detailed service scanning

## Security Principle

HomeSentinel follows a simple rule:

> Keep services private, minimize privileges, keep secrets local, and expose only the functionality that is required.
