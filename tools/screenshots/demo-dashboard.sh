#!/bin/bash
# Runs INSIDE the demo container (see take_screenshots.py). Builds a host the
# dashboard can read, then runs the real security-monitor.sh status on it.
#
# Demo fixtures, none of it real: a status.json describing a clean scan six
# hours ago, an empty daily.cvd aged one day, and stand-ins for systemctl and
# sigtool. The dashboard code itself is the repo's, unmodified.
set -euo pipefail

SRC=/src
mkdir -p /etc/security-monitor /var/lib/security-monitor /var/lib/clamav /demo-bin
cp "$SRC/security-monitor.conf" /etc/security-monitor/security-monitor.conf

LAST=$(date -u -d '6 hours ago' +%Y-%m-%dT%H:%M:%S+00:00)
cat > /var/lib/security-monitor/status.json <<JSON
{
  "last_scan": "$LAST",
  "scan_mode": "full",
  "scan_status": "clean",
  "infected_files": 0,
  "scanned_files": 18432,
  "quarantined_files": 0,
  "updates_available": 0,
  "updates_applied": 12
}
JSON

touch -d '1 day ago' /var/lib/clamav/daily.cvd

cat > /demo-bin/systemctl <<'STUB'
#!/bin/bash
# Demo stand-in: the timers, freshclam and unattended-upgrades are "on".
case "$1" in
    is-active)
        for a in "$@"; do
            case "$a" in security-monitor-*|clamav-freshclam) exit 0 ;; esac
        done
        exit 3 ;;
    is-enabled)
        for a in "$@"; do
            case "$a" in unattended-upgrades) exit 0 ;; esac
        done
        exit 1 ;;
    show) date -u -d 'tomorrow 02:00' '+%a %Y-%m-%d %H:%M:%S UTC' ;;
esac
STUB
cat > /demo-bin/sigtool <<'STUB'
#!/bin/bash
# Demo stand-in with made-up numbers.
echo "Version: 27999"
echo "Signatures: 2000000"
STUB
chmod +x /demo-bin/systemctl /demo-bin/sigtool

export PATH="/demo-bin:$PATH" TERM=xterm
exec "$SRC/security-monitor.sh" status
