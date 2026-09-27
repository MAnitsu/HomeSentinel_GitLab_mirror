import json
import subprocess
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse


app = FastAPI(
    title="HomeSentinel API",
    description="Local API for HomeSentinel monitoring and automation.",
    version="0.1.0",
)


HEALTH_FILE = Path("/var/lib/pi-hole-network/health.json")
MAINTENANCE_FILE = Path("/var/lib/pi-hole-network/update-result")


@app.get("/health")
def get_health():
    if not HEALTH_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Health result is unavailable.",
        )

    try:
        with HEALTH_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        raise HTTPException(
            status_code=500,
            detail="Unable to read health result.",
        )


@app.get("/maintenance")
def get_maintenance():
    if not MAINTENANCE_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Maintenance result is unavailable.",
        )

    try:
        with MAINTENANCE_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (OSError, json.JSONDecodeError):
        raise HTTPException(
            status_code=500,
            detail="Unable to read maintenance result.",
        )


@app.post("/health")
def run_health_check():
    try:
        result = subprocess.run(
            [
                "sudo",
                "systemctl",
                "start",
                "pi-hole-network-health.service",
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail="Health check failed to start.",
            )

        if not HEALTH_FILE.exists():
            raise HTTPException(
                status_code=500,
                detail="Health check completed but no result is available.",
            )

        try:
            with HEALTH_FILE.open("r", encoding="utf-8") as file:
                health_result = json.load(file)
        except (OSError, json.JSONDecodeError):
            raise HTTPException(
                status_code=500,
                detail="Health check completed but the result could not be read.",
            )

        return health_result

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Health check request timed out.",
        )


@app.post("/update")
def run_maintenance():
    try:
        result = subprocess.run(
            [
                "sudo",
                "systemctl",
                "start",
                "pi-hole-network-update.service",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            raise HTTPException(
                status_code=500,
                detail="Maintenance failed to start.",
            )

        if not MAINTENANCE_FILE.exists():
            raise HTTPException(
                status_code=500,
                detail="Maintenance completed but no result is available.",
            )

        try:
            with MAINTENANCE_FILE.open("r", encoding="utf-8") as file:
                maintenance_result = json.load(file)
        except (OSError, json.JSONDecodeError):
            raise HTTPException(
                status_code=500,
                detail="Maintenance completed but the result could not be read.",
            )

        return maintenance_result

    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="Maintenance request timed out.",
        )


@app.post("/reboot", status_code=202)
def reboot_system():
    try:
        subprocess.Popen(
            [
                "sudo",
                "/usr/local/bin/homesentinel-reboot",
            ],
            start_new_session=True,
        )

        return {
            "status": "rebooting",
            "message": "System reboot initiated.",
        }

    except OSError:
        raise HTTPException(
            status_code=500,
            detail="Unable to initiate system reboot.",
        )


@app.get("/control", response_class=HTMLResponse)
def control_panel():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>HomeSentinel Control Panel</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 40px;

            background: #111318;
            color: #f3f4f6;

            font-family:
                -apple-system,
                BlinkMacSystemFont,
                "Segoe UI",
                sans-serif;
        }

        .container {
            max-width: 1100px;
            margin: 0 auto;
        }

        h1 {
            margin-bottom: 8px;
            font-size: 30px;
        }

        .subtitle {
            margin-top: 0;
            margin-bottom: 30px;

            color: #9ca3af;
            font-size: 14px;
        }

        .grid {
            display: grid;

            grid-template-columns:
                minmax(0, 2fr)
                minmax(280px, 1fr);

            gap: 20px;

            align-items: start;
        }

        .card {
            padding: 24px;

            background: #181b21;

            border: 1px solid #292d36;
            border-radius: 14px;
        }

        .card-health {
            grid-row: span 2;
        }

        h2 {
            margin-top: 0;
            margin-bottom: 10px;

            font-size: 19px;
        }

        .card-description {
            margin-top: 0;
            margin-bottom: 20px;

            color: #9ca3af;

            font-size: 13px;
            line-height: 1.5;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;

            margin-bottom: 16px;

            font-size: 13px;
            font-weight: 600;
        }

        .status-dot {
            width: 8px;
            height: 8px;

            background: #86efac;

            border-radius: 50%;
        }

        .checks {
            margin: 18px 0;

            border-top: 1px solid #292d36;
        }

        .check-row {
            display: flex;
            justify-content: space-between;
            align-items: center;

            padding: 9px 0;

            border-bottom: 1px solid #292d36;

            font-size: 13px;
        }

        .check-row span:first-child {
            color: #d1d5db;
        }

        .check-pass {
            color: #86efac;
        }

        .check-fail {
            color: #fca5a5;
        }

        button {
            width: 100%;

            padding: 11px 16px;

            background: #252932;
            color: #f3f4f6;

            border: 1px solid #383d48;
            border-radius: 8px;

            font-size: 14px;
            font-weight: 600;

            cursor: pointer;
        }

        button:hover {
            background: #2d323d;
        }

        .result {
            min-height: 20px;

            margin-top: 14px;

            color: #9ca3af;

            font-size: 13px;
        }

        @media (max-width: 700px) {
            body {
                padding: 20px;
            }

            h1 {
                font-size: 24px;
            }

            .grid {
                grid-template-columns: 1fr;
            }

            .card-health {
                grid-row: auto;
            }
        }
    </style>
</head>

<body>
    <div class="container">

        <h1>HomeSentinel Control Panel</h1>

        <p class="subtitle">
            Local system monitoring and controlled actions.
        </p>

        <div class="grid">

            <div class="card card-health">
                <h2>Health Check</h2>

                <p class="card-description">
                    Run all HomeSentinel health checks and verify
                    the current state of the network and system.
                </p>

                <div class="status">
                    <span class="status-dot"></span>
                    <span id="health-status">Ready</span>
                </div>

                <div id="health-checks" class="checks">
                    <div class="check-row">
                        <span>Internet connectivity</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>DNS resolution</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Pi-hole service</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Pi-hole DNS</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Pi-hole blocking</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Upstream DNS</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Disk usage</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>Memory usage</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>CPU temperature</span>
                        <span>—</span>
                    </div>

                    <div class="check-row">
                        <span>System uptime</span>
                        <span>—</span>
                    </div>
                </div>

                <p id="health-summary" class="result"></p>

                <button onclick="runHealthCheck()">
                    Run Health Check
                </button>

                <p id="health-result" class="result"></p>
            </div>


            <div class="card">
                <h2>Maintenance</h2>

                <p class="card-description">
                    Update the operating system, Pi-hole
                    and configured DNS blocklists.
                </p>

                <div class="status">
                    <span class="status-dot"></span>
                    <span id="maintenance-status">Ready</span>
                </div>

                <button onclick="runMaintenance()">
                    Run Maintenance
                </button>

                <p id="maintenance-result" class="result"></p>
            </div>


            <div class="card">
                <h2>System</h2>

                <p class="card-description">
                    Perform controlled system-level actions
                    on the HomeSentinel Raspberry Pi.
                </p>

                <div class="status">
                    <span class="status-dot"></span>
                    <span id="reboot-status">Ready</span>
                </div>

                <button onclick="rebootSystem()">
                    Reboot System
                </button>

                <p id="reboot-result" class="result"></p>
            </div>

        </div>
    </div>


    <script>
        async function runHealthCheck() {
            const result =
                document.getElementById("health-result");

            const summary =
                document.getElementById("health-summary");

            const status =
                document.getElementById("health-status");

            result.textContent = "";
            summary.textContent = "";
            status.textContent = "Running...";

            try {
                const response = await fetch("/health", {
                    method: "POST"
                });

                const data = await response.json();

                if (!response.ok) {
                    status.textContent = "Failed";
                    result.textContent =
                        "Health check failed.";
                    return;
                }

                const checkNames = {
                    internet: "Internet connectivity",
                    dns: "DNS resolution",
                    pihole_service: "Pi-hole service",
                    pihole_dns: "Pi-hole DNS",
                    pihole_blocking: "Pi-hole blocking",
                    upstream_dns: "Upstream DNS",
                    disk: "Disk usage",
                    memory: "Memory usage",
                    temperature: "CPU temperature",
                    uptime: "System uptime"
                };

                const checksContainer =
                    document.getElementById("health-checks");

                checksContainer.innerHTML = "";

                for (const [key, value] of Object.entries(data.checks)) {
                    const row =
                        document.createElement("div");

                    row.className = "check-row";

                    const name =
                        document.createElement("span");

                    name.textContent =
                        checkNames[key] || key;

                    const checkStatus =
                        document.createElement("span");

                    if (value === "pass") {
                        checkStatus.textContent = "✓ PASS";
                        checkStatus.className = "check-pass";
                    } else {
                        checkStatus.textContent = "✗ FAIL";
                        checkStatus.className = "check-fail";
                    }

                    row.appendChild(name);
                    row.appendChild(checkStatus);

                    checksContainer.appendChild(row);
                }

                status.textContent =
                    data.status.toUpperCase();

                summary.textContent =
                    `Passed: ${data.passed} | Failed: ${data.failed}`;

            } catch (error) {
                status.textContent = "Unavailable";

                result.textContent =
                    "Unable to contact HomeSentinel API.";
            }
        }


        async function runMaintenance() {
            const result =
                document.getElementById("maintenance-result");

            const status =
                document.getElementById("maintenance-status");

            result.textContent = "";
            status.textContent = "Running...";

            try {
                const response = await fetch("/update", {
                    method: "POST"
                });

                const data = await response.json();

                if (!response.ok) {
                    status.textContent = "Failed";
                    result.textContent =
                        "Maintenance failed.";
                    return;
                }

                status.textContent =
                    data.status.toUpperCase();

                result.textContent =
                    `Last run: ${data.timestamp}`;

            } catch (error) {
                status.textContent = "Unavailable";

                result.textContent =
                    "Unable to contact HomeSentinel API.";
            }
        }


        async function rebootSystem() {
            const confirmed = confirm(
                "Are you sure you want to reboot the Raspberry Pi?"
            );

            if (!confirmed) {
                return;
            }

            const result =
                document.getElementById("reboot-result");

            const status =
                document.getElementById("reboot-status");

            result.textContent = "";
            status.textContent = "Rebooting...";

            try {
                const response = await fetch("/reboot", {
                    method: "POST"
                });

                const data = await response.json();

                if (!response.ok) {
                    status.textContent = "Failed";

                    result.textContent =
                        "Unable to initiate reboot.";

                    return;
                }

                status.textContent = "REBOOTING";

                result.textContent =
                    "The Raspberry Pi is restarting...";

            } catch (error) {
                /*
                 * The API may become unavailable immediately
                 * because the Raspberry Pi is shutting down.
                 * A network error at this point is therefore
                 * expected.
                 */

                status.textContent = "REBOOTING";

                result.textContent =
                    "The Raspberry Pi is restarting...";
            }
        }
    </script>
</body>
</html>
"""
