# HomeSentinel - A Pi-hole Network Ad Blocker

A self-hosted network-wide DNS filtering solution using **Raspberry Pi, Pi-hole, and Quad9 DNS**.

The project provides centralized DNS-level ad and tracker blocking for devices connected to the home network, while also serving as a practical exercise in Linux administration, networking, DNS, Bash scripting, automation, and infrastructure maintenance.

---

## Architecture

```text
                    Internet
                       │
                       ▼
                ┌──────────────┐
                │ TP-Link      │
                │ Router       │
                │ DHCP / DNS   │
                └──────┬───────┘
                       │
              DNS queries sent
                 to Pi-hole
                       │
                       ▼
              ┌─────────────────┐
              │ Raspberry Pi    │
              │ Raspberry Pi OS │
              │                 │
              │    Pi-hole      │
              │   DNS Filter    │
              └────────┬────────┘
                       │
                 Allowed DNS
                       │
                       ▼
                  Quad9 DNS
                       │
                       ▼
                   Internet
```

### Request flow

1. Devices connect to the home network through the router.
2. The router advertises the Raspberry Pi as the DNS server through DHCP.
3. DNS queries are sent to Pi-hole.
4. Pi-hole checks each domain against its configured blocklists.
5. Blocked domains are rejected.
6. Allowed DNS queries are forwarded to Quad9.
7. The requested service is reached through the internet.

---

## Project Goals

The main goals of HomeSentinel are:

* Learn and demonstrate Linux administration.
* Build a network-wide DNS filtering solution.
* Understand DNS resolution and upstream DNS providers.
* Automate routine system maintenance.
* Monitor the health of the Raspberry Pi and Pi-hole.
* Build a self-hosted dashboard.
* Implement secure remote access.
* Add notifications for important failures.
* Validate reusable scripts and configuration through GitLab CI/CD.
* Create a practical infrastructure project suitable for a technical portfolio.

---

## Repository vs Raspberry Pi

The GitLab repository contains **generic and reusable project components**.

The Raspberry Pi contains the **environment-specific configuration, installed systemd units, and runtime data**.

The repository should **not** contain:

* Private IP addresses
* Local usernames
* Passwords or credentials
* Authentication tokens
* Machine-specific paths
* Local logs
* Runtime result files
* Router-specific private configuration
* Personal network information
* Tailscale authentication data
* Environment-specific secrets

Example systemd files are stored in the repository using the `.example` extension.

For example:

```text
GitLab repository
    │
    │ copy and customize
    ▼
Raspberry Pi
/etc/systemd/system/
```

The repository version remains generic, while the Raspberry Pi contains the actual local configuration.

---

## Project Structure

```text
HomeSentinel/
├── README.md
├── scripts/
│   └── update.sh
└── systemd/
    ├── pi-hole-network-update.service.example
    └── pi-hole-network-update.timer.example
```

The project structure will grow as additional monitoring, dashboard, notification, remote-access, and CI/CD functionality is implemented.

---

# Hardware

Current hardware:

* Raspberry Pi 3B+
* 64 GB microSD card
* Raspberry Pi power supply
* Ethernet connection
* Home router with DHCP configuration access

Other Raspberry Pi models and storage devices can be used.

An SSD is planned as a future reliability improvement.

---

# Software

Current software stack:

* Raspberry Pi OS Lite 64-bit
* Pi-hole
* Quad9 DNS
* Bash
* systemd
* SSH
* Git
* GitLab

Future components may include:

* Homepage
* Tailscale
* ntfy
* GitLab CI/CD
* ShellCheck
* Additional monitoring tools

---

# Setup

## 1. Install Raspberry Pi OS

Use **Raspberry Pi Imager** to install:

* Raspberry Pi OS Lite 64-bit
* Hostname: `pi-hole`
* Local username and password
* SSH enabled
* Wi-Fi configured if required

Ethernet is recommended for the Raspberry Pi when possible.

---

## 2. Connect through SSH

After the Raspberry Pi starts:

```bash
ssh <username>@pi-hole.local
```

Update the operating system:

```bash
sudo apt update
sudo apt full-upgrade
```

Reboot:

```bash
sudo reboot
```

Reconnect through SSH after the Raspberry Pi has restarted.

---

## 3. Configure a Reserved IP Address

The Raspberry Pi should have a predictable IP address because other devices will use it as their DNS server.

The recommended approach is to configure a **DHCP address reservation on the router**.

The exact menu names depend on the router manufacturer.

Common locations include:

* Network
* LAN
* DHCP
* Address Reservation
* DHCP Reservation

### Example: TP-Link routers

On many TP-Link routers, the relevant settings can be found under the router's network or DHCP configuration.

Create a reservation for the Raspberry Pi based on its MAC address.

The Raspberry Pi should then consistently receive the same local IP address.

Do not commit the actual IP address to the repository.

---

# 4. Install Pi-hole

Install Pi-hole using the official installation method.

During installation:

* Select the correct network interface.
* Choose the desired upstream DNS provider.
* Enable the web administration interface.
* Keep the default blocklists initially.
* Complete the installation.

After installation, verify that Pi-hole is running.

Example:

```bash
pihole status
```

---

# 5. Configure the Router DNS

Configure the router's DHCP settings so that clients receive the Raspberry Pi's IP address as their DNS server.

The exact configuration depends on the router manufacturer.

The general configuration is:

```text
DHCP DNS Server
       │
       ▼
Raspberry Pi / Pi-hole
```

After applying the configuration, reconnect client devices or renew their DHCP leases if necessary.

DNS requests should then begin appearing in the Pi-hole dashboard.

---

# 6. Update Pi-hole Gravity

Pi-hole uses its Gravity database to determine which domains should be blocked.

Update Gravity manually with:

```bash
sudo pihole updateGravity
```

Verify the results through the Pi-hole dashboard.

---

# Additional Blocklists

The project can use **Hagezi DNS Blocklists** as an additional blocklist source.

Hagezi provides multiple blocklist variants with different levels of filtering.

A suitable list can be added through the Pi-hole administration interface:

```text
Pi-hole Dashboard
    │
    └── Domains on Lists
          │
          └── Manage lists
```

After adding a blocklist, update Gravity:

```bash
sudo pihole updateGravity
```

The exact blocklist selected should depend on the desired balance between filtering and compatibility.

---

# Maintenance Automation

Routine maintenance is automated using a Bash script and systemd.

The maintenance process currently performs:

1. Update APT package lists.
2. Upgrade operating system packages.
3. Update Pi-hole.
4. Update Pi-hole Gravity/blocklists.
5. Record the result of the maintenance run.
6. Store a complete maintenance log.

Automatic rebooting is intentionally not performed.

---

## Manual Maintenance

The maintenance script can be executed manually:

```bash
sudo ./scripts/update.sh
```

The script returns:

```text
0 = success
1 = failure
```

A successful run produces a result file containing:

```text
SUCCESS
```

A failed run produces:

```text
FAILURE
```

---

## Maintenance Script

The reusable maintenance script is located at:

```text
scripts/update.sh
```

The script uses explicit error handling rather than relying on an automatic reboot or silently continuing after a failed maintenance operation.

The script also records structured status information that can later be consumed by monitoring or dashboard components.

---

# systemd Automation

systemd is used instead of cron for scheduled maintenance.

This allows the project to take advantage of:

* systemd service management
* journal logging
* service status reporting
* dependency management
* network availability requirements
* failure detection
* timer scheduling
* persistent timers
* randomized execution delays

The repository contains generic example files:

```text
systemd/
├── pi-hole-network-update.service.example
└── pi-hole-network-update.timer.example
```

---

## systemd Service

The service is responsible for executing the maintenance script.

Conceptually:

```text
systemd service
      │
      ▼
scripts/update.sh
      │
      ├── Update operating system
      ├── Update Pi-hole
      └── Update blocklists
             │
             ▼
       Result + log
```

The service is a `Type=oneshot` service, meaning it starts, performs the maintenance operation, and exits when the operation is complete.

The service does not remain running continuously.

---

## systemd Timer

The timer controls when the maintenance service runs.

The current schedule is:

```text
Every Sunday at approximately 03:00
```

A randomized delay is used so the task does not necessarily start at exactly the same second every week.

The timer also uses:

```ini
Persistent=true
```

This means that if the Raspberry Pi is powered off when the scheduled execution occurs, systemd can run the missed task when the system becomes available again.

---

# Installing the systemd Maintenance Automation

Copy the generic service and timer examples to the systemd directory:

```bash
sudo cp systemd/pi-hole-network-update.service.example \
    /etc/systemd/system/pi-hole-network-update.service

sudo cp systemd/pi-hole-network-update.timer.example \
    /etc/systemd/system/pi-hole-network-update.timer
```

Edit the service:

```bash
sudo nano /etc/systemd/system/pi-hole-network-update.service
```

Change:

```ini
ExecStart=/path/to/project/scripts/update.sh
```

to the actual location of the script on the Raspberry Pi.

For example:

```ini
ExecStart=/home/<username>/scripts/update.sh
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable and start the timer:

```bash
sudo systemctl enable --now pi-hole-network-update.timer
```

Verify the timer:

```bash
systemctl status pi-hole-network-update.timer
```

List scheduled timers:

```bash
systemctl list-timers --all
```

---

# Maintenance Logs

The maintenance script stores its complete log at:

```text
/var/log/pi-hole-network/update.log
```

The most recent maintenance result is stored at:

```text
/var/lib/pi-hole-network/update-result
```

Possible result values are:

```text
SUCCESS
FAILURE
```

These files are local runtime data and should not be committed to GitLab.

---

# systemd Maintenance Commands

Manually start the maintenance service:

```bash
sudo systemctl start pi-hole-network-update.service
```

Check the service status:

```bash
sudo systemctl status pi-hole-network-update.service
```

View the service journal:

```bash
sudo journalctl -u pi-hole-network-update.service
```

Check the timer:

```bash
systemctl status pi-hole-network-update.timer
```

List all timers:

```bash
systemctl list-timers --all
```

---

# Verification

After installation, verify the following.

### Pi-hole

```bash
pihole status
```

### DNS resolution

```bash
nslookup example.com
```

or:

```bash
dig example.com
```

### Maintenance script

```bash
sudo ./scripts/update.sh
```

### Maintenance result

```bash
cat /var/lib/pi-hole-network/update-result
```

Expected successful result:

```text
SUCCESS
```

### systemd timer

```bash
systemctl status pi-hole-network-update.timer
```

### Scheduled execution

```bash
systemctl list-timers --all
```

The timer should appear as active and waiting for its next scheduled execution.

---

# Troubleshooting

## Pi-hole is not receiving DNS queries

Check:

```bash
pihole status
```

Then verify that the router is advertising the Raspberry Pi as the DNS server.

Also check the Pi-hole query log.

---

## DNS resolution does not work

Test the Raspberry Pi directly:

```bash
dig example.com
```

Check whether the Pi-hole service is running:

```bash
pihole status
```

Verify the configured upstream DNS provider.

---

## Maintenance service fails

Check the service:

```bash
sudo systemctl status pi-hole-network-update.service
```

View detailed logs:

```bash
sudo journalctl -u pi-hole-network-update.service
```

Also inspect:

```bash
cat /var/log/pi-hole-network/update.log
```

---

## Timer does not appear to run

Check:

```bash
systemctl status pi-hole-network-update.timer
```

Then:

```bash
systemctl list-timers --all
```

If necessary, reload systemd:

```bash
sudo systemctl daemon-reload
```

Then restart the timer:

```bash
sudo systemctl restart pi-hole-network-update.timer
```

---

# Security Considerations

HomeSentinel is intended to run on a trusted home network.

Important considerations include:

* Use strong passwords.
* Disable unnecessary services.
* Keep Raspberry Pi OS updated.
* Keep Pi-hole updated.
* Avoid exposing Pi-hole's administration interface directly to the internet.
* Prefer SSH keys over password authentication where practical.
* Do not commit secrets to GitLab.
* Do not commit private network information.
* Keep environment-specific configuration on the Raspberry Pi.
* Remote access should use a secure VPN rather than exposing services directly.

Tailscale is planned for remote access in a future phase.

---

# Current Architecture

The current system consists of:

```text
                        Internet
                           │
                           ▼
                    ┌─────────────┐
                    │   Router    │
                    │ DHCP + DNS  │
                    └──────┬──────┘
                           │
                           │ DNS
                           ▼
                  ┌─────────────────┐
                  │  Raspberry Pi   │
                  │                 │
                  │    Pi-hole      │
                  │      DNS        │
                  └────────┬────────┘
                           │
                           │ Allowed queries
                           ▼
                       ┌───────┐
                       │ Quad9 │
                       └───┬───┘
                           │
                           ▼
                       Internet
```

Maintenance automation runs locally on the Raspberry Pi:

```text
                 systemd timer
                       │
                       │ scheduled
                       ▼
              systemd service
                       │
                       ▼
              scripts/update.sh
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      APT update   Pi-hole      Gravity
                       │
                       ▼
                 Result + log
```

---

# Project Roadmap

## Phase 1 — Network Foundation

* [x] Raspberry Pi OS Lite 64-bit
* [x] Raspberry Pi 3B+
* [x] Static/reserved IP
* [x] SSH
* [x] Pi-hole
* [x] Quad9 upstream DNS
* [x] Hagezi blocklists
* [x] Router configured to use Pi-hole DNS
* [x] GitLab repository
* [x] Generic project documentation
* [x] Keep environment-specific information out of GitLab

---

## Phase 2 — Automation & Dashboard

### Maintenance Automation

* [x] Automated update script
* [x] Structured maintenance logging
* [x] Maintenance failure handling
* [x] Maintenance result recording
* [x] systemd maintenance service
* [x] systemd maintenance timer
* [x] Scheduled automatic maintenance

### Health Monitoring

* [ ] Health-check script
* [ ] DNS resolution monitoring
* [ ] Pi-hole service monitoring
* [ ] Pi-hole DNS functionality monitoring
* [ ] Pi-hole blocking verification
* [ ] Internet connectivity monitoring
* [ ] Disk usage monitoring
* [ ] Memory usage monitoring
* [ ] CPU monitoring
* [ ] Temperature monitoring
* [ ] Health status result file
* [ ] systemd health-check service
* [ ] systemd health-check timer

### Dashboard

* [ ] Install Homepage
* [ ] CPU information
* [ ] RAM information
* [ ] Temperature
* [ ] Disk usage
* [ ] Uptime
* [ ] Network status
* [ ] Pi-hole status
* [ ] Pi-hole statistics
* [ ] Service status
* [ ] Last health check
* [ ] Last maintenance run
* [ ] GitLab link
* [ ] Router link
* [ ] Pi-hole administration link
* [ ] Manual health-check action
* [ ] Manual maintenance action

---

## Phase 3 — Remote Access

* [ ] Install Tailscale
* [ ] Configure secure remote access
* [ ] Connect iPhone
* [ ] Configure access controls
* [ ] Test remote dashboard access
* [ ] Test remote Pi-hole administration
* [ ] Evaluate subnet routing if required

Target architecture:

```text
              iPhone
                 │
                 │ Tailscale VPN
                 ▼
          ┌───────────────┐
          │ Raspberry Pi  │
          │               │
          │   Homepage    │
          │   Pi-hole     │
          └───────┬───────┘
                  │
                  ▼
             Home Network
```

---

# Phase 4 — Monitoring & Notifications

Planned functionality:

* [ ] Install ntfy
* [ ] Health failure notifications
* [ ] Recovery notifications
* [ ] Maintenance failure notifications
* [ ] Notification deduplication
* [ ] Rate limiting
* [ ] Phone notifications

Target flow:

```text
              Health Check
                   │
          ┌────────┴────────┐
          │                 │
        Healthy           Failed
          │                 │
          ▼                 ▼
      Dashboard       Dashboard + ntfy
                            │
                            ▼
                          Phone
```

---

# Phase 5 — GitLab CI/CD

The GitLab repository will validate generic project components without requiring access to the real Raspberry Pi.

Planned checks:

* [ ] ShellCheck
* [ ] Bash syntax validation
* [ ] Script tests
* [ ] Homepage configuration validation
* [ ] Documentation checks
* [ ] Artifact generation
* [ ] Pipeline status

Planned pipeline:

```text
Git Push
   │
   ▼
GitLab CI
   │
   ├── ShellCheck
   │
   ├── Bash validation
   │
   ├── Configuration validation
   │
   ├── Tests
   │
   └── Documentation checks
           │
           ▼
         PASS
```

The CI pipeline should remain independent from the private home network.

---

# Phase 6 — Storage & Reliability

Planned improvements:

* [ ] Move from microSD to SSD
* [ ] Verify SSD stability
* [ ] Keep microSD as a fallback
* [ ] Document recovery procedure
* [ ] Document backup strategy
* [ ] Test Raspberry Pi recovery
* [ ] Document disaster recovery process

The current 64 GB microSD is sufficient for the current project.

The planned SSD upgrade is primarily focused on reliability and longevity rather than storage performance.

---

# Future Architecture

As HomeSentinel grows, the planned architecture will become:

```text
                              Internet
                                  │
                                  ▼
                         ┌────────────────┐
                         │     Router     │
                         │ DHCP / Network │
                         └───────┬────────┘
                                 │
                                 ▼
                      ┌─────────────────────┐
                      │    Raspberry Pi     │
                      │                     │
                      │      Pi-hole        │
                      │       DNS           │
                      │                     │
                      │      Homepage       │
                      │     Dashboard       │
                      │                     │
                      │    Monitoring       │
                      │                     │
                      │   Health Checks     │
                      │                     │
                      │   Maintenance       │
                      │                     │
                      │     Tailscale       │
                      └──────────┬──────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
             ntfy             GitLab            Phone
          Notifications       CI/CD          Remote Access
```

---

# Design Principles

HomeSentinel follows several principles:

### Keep runtime data separate from source code

Logs, results, credentials, and environment-specific configuration remain on the Raspberry Pi.

### Prefer automation over repetitive manual work

Recurring maintenance and monitoring should be handled by systemd and scripts.

### Fail visibly

Scripts should return meaningful exit codes and record failures rather than silently continuing.

### Keep components modular

Maintenance, health monitoring, dashboard functionality, notifications, and remote access should remain independently manageable.

### Avoid unnecessary exposure

Services should not be exposed directly to the public internet when a secure private-access solution can be used.

### Keep the GitLab repository reusable

The repository should demonstrate the architecture and implementation without exposing details specific to one home network.

---

# Current Status

**Phase 1 — Network Foundation:** Complete

**Phase 2 — Maintenance Automation:** Complete

**Phase 2 — Health Monitoring:** Next

The next implementation milestone is the creation of:

```text
scripts/health_check.sh
```

The health check will verify:

```text
Pi-hole Network Health Check
============================
[PASS] Internet connectivity
[PASS] DNS resolution
[PASS] Pi-hole service
[PASS] Pi-hole DNS
[PASS] Pi-hole blocking
[PASS] Quad9 upstream DNS
[PASS] Disk usage
[PASS] Memory usage
[PASS] CPU / temperature

Health: OK
```

The resulting health status will later become the foundation for the Homepage dashboard and notification system.

---

## Disclaimer

This project is designed for educational and personal home-network use. DNS filtering can occasionally block domains required by websites or applications. Blocklists should therefore be selected and maintained according to the network's requirements.

## Author
Mihai A. Nițu

GitLab: https://gitlab.com/MAnitsu
LinkedIn: https://www.linkedin.com/in/mihai-alexandru-nitu-b8035a16a/
