#!/bin/bash

set -e

echo "Updating operating system..."
sudo apt update
sudo apt full-upgrade -y

echo "Updating Pi-hole..."
sudo pihole updatePihole

echo "Updating Pi-hole blocklists..."
sudo pihole updateGravity

echo "Maintenance completed successfully."
echo "Rebooting..."
sudo reboot