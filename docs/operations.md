# Operations

Quick reference for managing HomeSentinel on the Raspberry Pi.

## Service Status

```bash
systemctl status homesentinel-api.service
systemctl status pi-hole-network-health.timer
systemctl status pi-hole-network-update.timer
docker compose -f /opt/homepage/compose.yaml ps
```

## Health Check

Run manually:

```bash
sudo systemctl start pi-hole-network-health.service
```

View the latest result:

```bash
jq . /var/lib/pi-hole-network/health.json
```

View logs:

```bash
journalctl -u pi-hole-network-health.service --no-pager
```

## Maintenance

Run manually:

```bash
sudo systemctl start pi-hole-network-update.service
```

View the latest result:

```bash
cat /var/lib/pi-hole-network/update-result
```

View logs:

```bash
journalctl -u pi-hole-network-update.service --no-pager
```

## Network Scan

Run a LAN discovery scan:

```bash
curl -X POST http://127.0.0.1:8000/network/scan
```

View the latest result:

```bash
curl http://127.0.0.1:8000/network/scan | jq
```

## API

Check API health:

```bash
curl http://127.0.0.1:8000/health
```

Open the Control Panel:

```text
http://<PI-IP>:8000/control
```

## Homepage

```bash
cd /opt/homepage
docker compose ps
docker compose restart
```

Dashboard:

```text
http://<PI-IP>:3000
```

## Logs

API:

```bash
journalctl -u homesentinel-api.service --no-pager
```

Health monitoring:

```bash
tail -f /var/log/pi-hole-network/health.log
```

Maintenance:

```bash
tail -f /var/log/pi-hole-network/update.log
```

## Useful Checks

```bash
pihole status
docker ps
systemctl --failed
df -h
free -h
```

## Restart

Restart the API:

```bash
sudo systemctl restart homesentinel-api.service
```

Restart Homepage:

```bash
cd /opt/homepage
docker compose restart
```

Reboot the Raspberry Pi only when required:

```bash
sudo reboot
```
