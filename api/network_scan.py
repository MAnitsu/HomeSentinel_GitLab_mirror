import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree

from dotenv import load_dotenv


load_dotenv()


NETWORK = os.getenv("HOMESENTINEL_NETWORK", "192.168.1.0/24")

DEVICE_LABELS = {}

for entry in os.getenv("HOMESENTINEL_DEVICE_LABELS", "").split(","):
    if ":" not in entry:
        continue

    ip, label = entry.split(":", 1)
    DEVICE_LABELS[ip.strip()] = label.strip()

RESULT_FILE = Path(
    os.getenv(
        "HOMESENTINEL_NETWORK_SCAN_FILE",
        "/var/lib/homesentinel/network-scan.json",
    )
)


def run_scan():
    """Run Nmap host discovery and return its XML output."""

    result = subprocess.run(
        [
            "nmap",
            "-sn",
            "-oX",
            "-",
            NETWORK,
        ],
        capture_output=True,
        text=True,
        check=True,
        timeout=60,
    )

    return result.stdout


def parse_scan(xml_output):
    """Convert Nmap XML output into a structured Python dictionary."""

    root = ElementTree.fromstring(xml_output)

    hosts = []

    for host in root.findall("host"):
        status = host.find("status")
        address = host.find("address")

        if address is None:
            continue

        hostname_element = host.find("hostnames/hostname")
        ip_address = address.get("addr")

        if (
            hostname_element is not None
            and hostname_element.get("name")
        ):
            hostname = hostname_element.get("name")
        else:
            hostname = DEVICE_LABELS.get(ip_address)

        hosts.append(
            {
                "ip": ip_address,
                "hostname": hostname,
                "status": (
                    status.get("state")
                    if status is not None
                    else "unknown"
                ),
            }
        )

    finished = root.find("runstats/finished")

    return {
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "network": NETWORK,
        "scanner": "nmap",
        "nmap_version": root.get("version"),
        "host_count": len(hosts),
        "hosts": hosts,
        "scan": {
            "status": (
                finished.get("exit")
                if finished is not None
                else "unknown"
            ),
            "duration_seconds": (
                float(finished.get("elapsed"))
                if finished is not None
                else None
            ),
        },
    }


def save_result(result):
    """Save the latest scan result as formatted JSON."""

    RESULT_FILE.parent.mkdir(parents=True, exist_ok=True)

    RESULT_FILE.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )


def main():
    """Run the network scan and save the result."""

    xml_output = run_scan()
    result = parse_scan(xml_output)
    save_result(result)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
