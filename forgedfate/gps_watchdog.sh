#!/bin/bash
# GPS Watchdog - Monitors and restarts GPS services if needed

GPS_DEVICE="/dev/gps0"
GPSD_SERVICE="gpsd"
LOG_FILE="/var/log/gps_watchdog.log"

log_message() {
    echo "$(date): $1" >> "$LOG_FILE"
}

# Check if GPS device exists
if [ ! -e "$GPS_DEVICE" ]; then
    log_message "GPS device $GPS_DEVICE not found, reloading udev rules"
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    sleep 5
fi

# Check if gpsd is running
if ! systemctl is-active --quiet "$GPSD_SERVICE"; then
    log_message "gpsd service not running, restarting"
    sudo systemctl restart "$GPSD_SERVICE"
    sleep 10
fi

# Test GPS data availability
if ! timeout 10s cat "$GPS_DEVICE" | head -1 > /dev/null 2>&1; then
    log_message "No GPS data available, restarting gpsd"
    sudo systemctl restart "$GPSD_SERVICE"
fi

log_message "GPS watchdog check completed"
