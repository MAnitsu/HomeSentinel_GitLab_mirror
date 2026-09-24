#!/bin/bash

# Do not stop automatically on an unset variable.
# We handle command failures explicitly inside run_step().
set -u


# Directory where maintenance logs will be stored.
LOG_DIR="/var/log/pi-hole-network"

# File containing the complete maintenance log.
LOG_FILE="$LOG_DIR/update.log"

# File containing only the result of the most recent maintenance run.
# This can later be consumed by the dashboard.
RESULT_FILE="/var/lib/pi-hole-network/update-result"


# Create the required directories if they do not already exist.
# The -p option also prevents an error if the directories already exist.
mkdir -p "$LOG_DIR"
mkdir -p "$(dirname "$RESULT_FILE")"


# Send both standard output and errors to:
# 1. The terminal, so we can see what is happening when running manually.
# 2. The log file, so the result is preserved for later troubleshooting.
exec > >(tee -a "$LOG_FILE") 2>&1


# Display a header showing when the maintenance process started.
echo "========================================"
echo "Pi-hole Network Maintenance"
echo "Started: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"


# Run a maintenance command and report whether it succeeded or failed.
#
# The first argument is a human-readable description.
# The remaining arguments are the command that should be executed.
#
# Example:
#   run_step "Updating Pi-hole" pihole updatePihole
#
# The function returns:
#   0 if the command succeeds
#   1 if the command fails
run_step() {
    local description="$1"
    shift

    echo
    echo "[START] $description"

    if "$@"; then
        echo "[PASS] $description"
        return 0
    else
        echo "[FAIL] $description"
        return 1
    fi
}


# Update the local APT package index.
# This downloads the latest package information from the configured repositories.
if ! run_step "Updating operating system package lists" apt update; then
    echo "FAILURE" > "$RESULT_FILE"
    exit 1
fi


# Upgrade installed packages to their latest available versions.
# The -y option automatically confirms the package manager's prompts.
if ! run_step "Upgrading operating system packages" apt full-upgrade -y; then
    echo "FAILURE" > "$RESULT_FILE"
    exit 1
fi


# Update the Pi-hole software itself.
if ! run_step "Updating Pi-hole" pihole updatePihole; then
    echo "FAILURE" > "$RESULT_FILE"
    exit 1
fi


# Update Pi-hole's gravity database.
# This downloads and processes the configured blocklists.
if ! run_step "Updating Pi-hole blocklists" pihole updateGravity; then
    echo "FAILURE" > "$RESULT_FILE"
    exit 1
fi


# All maintenance tasks completed successfully.
echo
echo "========================================"
echo "Maintenance completed successfully."
echo "Finished: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"


# Store the result of the latest successful maintenance run.
# The dashboard can later read this file without parsing the full log.
echo "SUCCESS" > "$RESULT_FILE"


# Exit with code 0 to tell systemd or another caller that maintenance succeeded.
exit 0