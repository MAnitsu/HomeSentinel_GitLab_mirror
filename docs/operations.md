# HomeSentinel Operations Guide

This document describes the day-to-day operation, monitoring, maintenance, troubleshooting, and administration of a deployed HomeSentinel system.

For initial deployment, see [Setup](setup.md).

For system design and component relationships, see [Architecture](architecture.md).

---

# 1. Operational Overview

HomeSentinel consists of several independently managed components:

```text id="8l2v6s"
                    Raspberry Pi
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
     Pi-hole         HomeSentinel       Docker
                        API               │
                         │                ▼
                         │            Homepage
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
        Health system          Maintenance
              │                     │
              ▼                     ▼
        health.json          update-result
```

The primary operational tools are:

* `systemctl`
* `journalctl`
* `pihole`
* `docker`
* `curl`
* `jq`

---

# 2. Check Overall System Status

Start with the main services:

```bash id="9w6v4m"
sudo systemctl status homesentinel-api.service
```

```bash id="k4x8t9"
sudo systemctl status pi-hole-network-health.service
```

```bash id="m8kq2v"
sudo systemctl status pi-hole-network-update.service
```

Check the timers:

```bash id="7w5q0f"
systemctl list-timers
```

The health and maintenance timers should be enabled and scheduled for their next execution.

---

# 3. Check Pi-hole

Check Pi-hole status:

```bash id="zj8r7k"
pihole status
```

The Pi-hole dashboard can also be opened through:

```text
http://<PI-IP>/admin
```

Verify that queries are being received.

The dashboard can be used to inspect:

* Total queries
* Blocked queries
* Block percentage
* Clients
* Frequently requested domains
* Frequently blocked domains

---

# 4. Check Network Connectivity

Check the Raspberry Pi's network address:

```bash id="1kq4yr"
hostname -I
```

Test the local gateway:

```bash id="t4z9jx"
ping -c 4 <GATEWAY-IP>
```

Test internet connectivity:

```bash id="v5n0px"
ping -c 4 1.1.1.1
```

Test DNS:

```bash id="5y6q8r"
dig example.com
```

A system can have internet connectivity while DNS is unavailable, so both should be tested separately.

---

# 5. Health Monitoring

Health monitoring is normally executed automatically by the systemd health timer.

Check the timer:

```bash id="r7w2z4"
systemctl list-timers
```

Run a health check manually:

```bash id="4x7m1k"
sudo systemctl start pi-hole-network-health.service
```

Check the result:

```bash id="j8v5q2"
sudo systemctl status pi-hole-network-health.service
```

---

# 6. Health Result

The latest health result is stored as structured JSON.

The deployment uses a local runtime path similar to:

```text id="v6h3x1"
/var/lib/pi-hole-network/health.json
```

Inspect it:

```bash id="b9n2c7"
sudo cat /var/lib/pi-hole-network/health.json
```

If `jq` is available:

```bash id="m5w8k3"
sudo jq . /var/lib/pi-hole-network/health.json
```

A healthy result has:

```json id="f1q9s6"
{
  "status": "ok",
  "passed": 10,
  "failed": 0
}
```

The exact number of checks may change as the monitoring system evolves.

---

# 7. Health Logs

The health script writes a persistent log.

Example location:

```text id="r4x7k2"
/var/log/pi-hole-network/health.log
```

View the entire log:

```bash id="j2m8q5"
sudo cat /var/log/pi-hole-network/health.log
```

View the latest entries:

```bash id="x9v4c1"
sudo tail -n 50 /var/log/pi-hole-network/health.log
```

Follow the log in real time:

```bash id="k7p3d8"
sudo tail -f /var/log/pi-hole-network/health.log
```

---

# 8. Individual Health Checks

The health script currently checks:

```text id="w4k7z2"
Internet connectivity
DNS resolution
Pi-hole FTL service
Pi-hole DNS
Pi-hole blocking
Upstream DNS
Disk usage
Memory usage
CPU temperature
System uptime
```

If the overall health check fails, inspect the individual check results first.

For example:

```bash id="p5r8m1"
sudo jq '.checks' /var/lib/pi-hole-network/health.json
```

This makes it possible to identify the failing subsystem without manually inspecting the entire log.

---

# 9. Maintenance

Maintenance is normally executed automatically by the systemd update timer.

Check the timer:

```bash id="f8q2m5"
systemctl list-timers
```

Run maintenance manually:

```bash
sudo systemctl start pi-hole-network-update.service
```

Check the service:

```bash
sudo systemctl status pi-hole-network-update.service
```

---

# 10. Maintenance Result

The latest maintenance result is stored locally.

Example:

```text id="m4v7k9"
/var/lib/pi-hole-network/update-result
```

Inspect it:

```bash
sudo cat /var/lib/pi-hole-network/update-result
```

Or:

```bash
sudo jq . /var/lib/pi-hole-network/update-result
```

A successful result contains:

```json id="s7k2p4"
{
  "status": "success",
  "timestamp": "<timestamp>"
}
```

---

# 11. Maintenance Logs

Maintenance logs are stored separately from health logs.

Example:

```text id="q6w3n8"
/var/log/pi-hole-network/update.log
```

View the latest entries:

```bash
sudo tail -n 50 /var/log/pi-hole-network/update.log
```

Follow the log:

```bash
sudo tail -f /var/log/pi-hole-network/update.log
```

---

# 12. Manual Maintenance Script

The maintenance script can also be executed directly.

```bash
./scripts/update.sh
```

The script performs:

```text id="h8q3m6"
APT update
    │
    ▼
APT full-upgrade
    │
    ▼
Pi-hole update
    │
    ▼
Pi-hole Gravity update
```

The script returns a non-zero exit code when a required operation fails.

Check the exit code:

```bash
echo $?
```

A successful execution returns:

```text
0
```

---

# 13. systemd Service Management

Useful commands for HomeSentinel services:

### Start

```bash
sudo systemctl start <SERVICE>
```

### Stop

```bash
sudo systemctl stop <SERVICE>
```

### Restart

```bash
sudo systemctl restart <SERVICE>
```

### Status

```bash
sudo systemctl status <SERVICE>
```

### Enable at boot

```bash
sudo systemctl enable <SERVICE>
```

### Disable at boot

```bash
sudo systemctl disable <SERVICE>
```

### View logs

```bash
sudo journalctl -u <SERVICE>
```

### Follow logs

```bash
sudo journalctl -u <SERVICE> -f
```

---

# 14. Health Timer

Check:

```bash
systemctl status pi-hole-network-health.timer
```

List upcoming executions:

```bash
systemctl list-timers pi-hole-network-health.timer
```

If the timer was modified:

```bash
sudo systemctl daemon-reload
```

Restart it:

```bash
sudo systemctl restart pi-hole-network-health.timer
```

---

# 15. Maintenance Timer

Check:

```bash
systemctl status pi-hole-network-update.timer
```

List upcoming executions:

```bash
systemctl list-timers pi-hole-network-update.timer
```

After changing the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl restart pi-hole-network-update.timer
```

---

# 16. HomeSentinel API

Check the API service:

```bash
sudo systemctl status homesentinel-api.service
```

View recent API logs:

```bash
sudo journalctl -u homesentinel-api.service -n 50
```

Follow API logs:

```bash
sudo journalctl -u homesentinel-api.service -f
```

Check the API directly:

```bash
curl http://<PI-IP>:8000/health
```

---

# 17. API Endpoints

Current endpoints:

| Method | Endpoint       | Purpose                          |
| ------ | -------------- | -------------------------------- |
| GET    | `/health`      | Return latest health result      |
| POST   | `/health`      | Run a health check               |
| GET    | `/maintenance` | Return latest maintenance result |
| POST   | `/update`      | Run maintenance                  |
| POST   | `/reboot`      | Trigger controlled reboot        |
| GET    | `/control`     | Open control panel               |

---

# 18. API Health Check

Read the latest result:

```bash
curl http://<PI-IP>:8000/health
```

Trigger a new health check:

```bash
curl -X POST http://<PI-IP>:8000/health
```

The POST operation starts the existing systemd health service rather than implementing another health-check mechanism inside the API.

This keeps the health-check logic centralized in the Bash script.

---

# 19. API Maintenance

Read the latest maintenance result:

```bash
curl http://<PI-IP>:8000/maintenance
```

Trigger maintenance:

```bash
curl -X POST http://<PI-IP>:8000/update
```

The API delegates the operation to the existing systemd maintenance service.

---

# 20. Control Panel

The HomeSentinel control panel is available at:

```text
http://<PI-IP>:8000/control
```

It provides:

### Health Check

Runs the health-check service and displays the resulting status.

### Maintenance

Starts the maintenance service.

### System

Provides a controlled reboot action.

The control panel is intentionally kept separate from Homepage.

Homepage provides the dashboard, while the HomeSentinel API provides the control functionality.

---

# 21. Controlled Reboot

The reboot action should only be used when the Raspberry Pi can safely be restarted.

The request flow is:

```text id="z7m4p2"
Control Panel
      │
      ▼
POST /reboot
      │
      ▼
HomeSentinel API
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

The API uses a detached process because the system shuts down immediately after the request is accepted.

After rebooting, verify:

```bash
systemctl list-timers
```

Then verify the API:

```bash
sudo systemctl status homesentinel-api.service
```

And Docker:

```bash
docker ps
```

Finally verify the Homepage dashboard.

---

# 22. Docker Operations

Check running containers:

```bash
docker ps
```

Check all containers:

```bash
docker ps -a
```

For Homepage:

```bash
cd /opt/homepage
```

Check the Compose deployment:

```bash
docker compose ps
```

View logs:

```bash
docker compose logs
```

Follow logs:

```bash
docker compose logs -f
```

Restart Homepage:

```bash
docker compose restart
```

Stop Homepage:

```bash
docker compose down
```

Start Homepage:

```bash
docker compose up -d
```

---

# 23. Verify Homepage-to-API Connectivity

The Homepage container needs access to the HomeSentinel API running on the Raspberry Pi host.

Test from inside the container:

```bash
docker exec homepage wget -qO- http://host.docker.internal:8000/health
```

If `jq` is available:

```bash
docker exec homepage wget -qO- http://host.docker.internal:8000/health | jq
```

A valid JSON response confirms that:

```text id="y6r1w9"
Homepage container
        │
        ▼
host.docker.internal
        │
        ▼
HomeSentinel API
```

is functioning correctly.

---

# 24. Homepage Configuration

Homepage configuration is stored under the deployment directory:

```text id="v5k3q8"
/opt/homepage/config/
```

Important files include:

```text id="r8w2m5"
services.yaml
settings.yaml
widgets.yaml
```

After configuration changes, restart Homepage:

```bash
docker compose restart
```

Check the logs immediately afterward:

```bash
docker compose logs --tail 100
```

Configuration errors should be resolved before continuing.

---

# 25. Check Disk Usage

Check filesystem usage:

```bash
df -h
```

Check the root filesystem specifically:

```bash
df -h /
```

Find large directories:

```bash
sudo du -h -d 1 /var 2>/dev/null | sort -h
```

Logs should be monitored because HomeSentinel maintains persistent health and maintenance logs.

---

# 26. Check Memory

Check memory usage:

```bash
free -h
```

For a more detailed view:

```bash
top
```

or:

```bash
htop
```

if installed.

Memory pressure should be investigated if health checks begin reporting failures.

---

# 27. Check CPU Temperature

Read the CPU temperature:

```bash
vcgencmd measure_temp
```

The exact command may vary depending on the Raspberry Pi OS configuration.

The health-check script provides a standardized temperature check for HomeSentinel.

If temperature begins approaching the configured threshold consistently, investigate:

* Cooling
* Case airflow
* CPU load
* Ambient temperature
* Dust accumulation

---

# 28. Check Uptime

```bash
uptime
```

Or:

```bash
uptime -p
```

Unexpectedly short uptime may indicate:

* Recent reboot
* Power interruption
* System crash
* Manual restart

Use the system logs when investigating unexpected restarts.

---

# 29. Inspect System Logs

View recent system messages:

```bash
sudo journalctl -n 100
```

View logs from the current boot:

```bash
sudo journalctl -b
```

View logs from the previous boot:

```bash
sudo journalctl -b -1
```

This is particularly useful after unexpected reboots or service failures.

---

# 30. Troubleshooting: Devices Have No Internet

Start by checking whether the problem is DNS or general network connectivity.

### 1. Test IP connectivity

```bash
ping -c 4 1.1.1.1
```

If this fails, investigate the network connection or router.

### 2. Test DNS

```bash
dig example.com
```

If IP connectivity works but DNS fails, inspect Pi-hole.

### 3. Check Pi-hole

```bash
pihole status
```

### 4. Check the health result

```bash
sudo jq . /var/lib/pi-hole-network/health.json
```

### 5. Check Pi-hole logs/dashboard

Inspect recent DNS activity and blocked queries.

---

# 31. Troubleshooting: Pi-hole Is Unavailable

Check the service:

```bash
pihole status
```

Check listening ports:

```bash
sudo ss -lntup
```

Check systemd services:

```bash
systemctl --type=service | grep -i pihole
```

Check system logs:

```bash
sudo journalctl -b | grep -i pihole
```

If the service is unavailable, the health check should report a failure.

---

# 32. Troubleshooting: Health Check Fails

Run the health service manually:

```bash
sudo systemctl start pi-hole-network-health.service
```

Check the result:

```bash
sudo jq . /var/lib/pi-hole-network/health.json
```

Identify the failing check:

```bash
sudo jq '.checks' /var/lib/pi-hole-network/health.json
```

Then inspect the corresponding subsystem.

For example:

### DNS failure

```bash
dig example.com
```

### Pi-hole failure

```bash
pihole status
```

### Disk failure

```bash
df -h
```

### Memory issue

```bash
free -h
```

### Temperature issue

```bash
vcgencmd measure_temp
```

---

# 33. Troubleshooting: Maintenance Fails

Run the service manually:

```bash
sudo systemctl start pi-hole-network-update.service
```

Check:

```bash
sudo systemctl status pi-hole-network-update.service
```

Read the maintenance log:

```bash
sudo tail -n 100 /var/log/pi-hole-network/update.log
```

Check the result:

```bash
sudo cat /var/lib/pi-hole-network/update-result
```

The maintenance script executes several independent operations.

Identify which step generated:

```text
[FAIL]
```

and investigate that operation separately.

---

# 34. Troubleshooting: API Is Unavailable

Check:

```bash
sudo systemctl status homesentinel-api.service
```

View logs:

```bash
sudo journalctl -u homesentinel-api.service -n 100
```

Check whether port 8000 is listening:

```bash
sudo ss -lntup | grep 8000
```

Test locally:

```bash
curl http://127.0.0.1:8000/health
```

If localhost works but another device cannot connect, investigate:

* Raspberry Pi network connectivity
* Listening address
* Firewall configuration
* Client network configuration

---

# 35. Troubleshooting: Homepage Is Unavailable

Check Docker:

```bash
docker ps
```

Check Homepage:

```bash
cd /opt/homepage
docker compose ps
```

Check logs:

```bash
docker compose logs --tail 100
```

Check port 3000:

```bash
sudo ss -lntup | grep 3000
```

Test locally:

```bash
curl http://127.0.0.1:3000
```

If the container is running but Homepage cannot reach the HomeSentinel API, test:

```bash
docker exec homepage wget -qO- http://host.docker.internal:8000/health
```

---

# 36. Troubleshooting: Homepage Configuration Errors

After changing Homepage configuration:

```bash
docker compose restart
```

Immediately inspect:

```bash
docker compose logs --tail 100
```

Common causes include:

* Invalid YAML indentation
* Incorrect property names
* Incorrect API URL
* Missing environment variable
* Invalid Pi-hole credentials
* Incorrect Homepage configuration structure

Keep the generic configuration in GitLab and environment-specific values locally.

---

# 37. Troubleshooting: API Actions Return Permission Errors

If `POST /health`, `POST /update`, or `POST /reboot` fails, inspect the sudo configuration.

Validate:

```bash
sudo visudo -cf /etc/sudoers.d/homesentinel-api
```

Check allowed commands:

```bash
sudo -n -l
```

The API user should have access only to the explicitly configured commands.

Verify the commands independently:

```bash
sudo systemctl start pi-hole-network-health.service
```

```bash
sudo systemctl start pi-hole-network-update.service
```

and:

```bash
sudo /usr/local/bin/homesentinel-reboot
```

Do not solve permission issues by granting unrestricted sudo access to the API user.

---

# 38. After Reboot Verification

After restarting the Raspberry Pi, verify the complete stack.

### 1. Timers

```bash
systemctl list-timers
```

### 2. API

```bash
sudo systemctl status homesentinel-api.service
```

### 3. Docker

```bash
docker ps
```

### 4. Pi-hole

```bash
pihole status
```

### 5. Health result

```bash
sudo jq . /var/lib/pi-hole-network/health.json
```

### 6. API

```bash
curl http://<PI-IP>:8000/health
```

### 7. Homepage

Open:

```text
http://<PI-IP>:3000
```

A successful reboot should leave all persistent services and timers operational.

---

# 39. Operational Safety

Before performing potentially disruptive operations:

* Check whether other devices depend on Pi-hole.
* Avoid rebooting during important network activity.
* Confirm that the Raspberry Pi has stable power.
* Verify that maintenance scripts are not already running.
* Check available disk space.
* Keep backups before major configuration changes.

Do not expose the HomeSentinel API directly to the public internet.

Remote access should use the planned secure VPN architecture.

---

# 40. Routine Maintenance Checklist

### Weekly

```text id="c2v7m5"
[ ] Review health status
[ ] Review maintenance status
[ ] Check systemd timers
[ ] Check Pi-hole dashboard
[ ] Review recent health/maintenance logs
[ ] Check disk usage
```

### Monthly

```text id="n6x4q8"
[ ] Review blocklists
[ ] Review system resource usage
[ ] Review Docker containers
[ ] Review API logs
[ ] Review system logs
[ ] Check backups
[ ] Review project documentation
```

### After major changes

```text id="r5m8k2"
[ ] Test affected service
[ ] Test health check
[ ] Check systemd status
[ ] Check logs
[ ] Verify API
[ ] Verify Homepage
[ ] Verify Pi-hole
[ ] Test reboot recovery if applicable
[ ] Synchronize generic changes to GitLab
```

---

# 41. Operational Principle

HomeSentinel should be operated from the bottom of the stack upward:

```text id="y3m7q1"
Network
   │
   ▼
Operating System
   │
   ▼
Pi-hole
   │
   ▼
Health / Maintenance
   │
   ▼
HomeSentinel API
   │
   ▼
Docker / Homepage
```

When troubleshooting, start with the lowest affected layer rather than immediately changing the dashboard or API.

This makes failures easier to isolate and prevents one component from hiding an underlying infrastructure problem.

---

## Related Documentation

* [Architecture](architecture.md)
* [Setup](setup.md)
* [Security](security.md)
* [Roadmap](roadmap.md)
