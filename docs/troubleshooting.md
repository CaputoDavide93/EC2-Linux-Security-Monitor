# 🛠️ Troubleshooting

Find your symptom, then follow the fix. When none fits, open an issue with the diagnostics listed in [CONTRIBUTING.md](../CONTRIBUTING.md#-reporting-an-environment-or-a-bug).

## The dashboard says "No scan data available"

The dashboard reads `/var/lib/security-monitor/status.json`, which the first scan writes, and it needs `jq`. Run a scan, and check `jq` is installed:

```bash
sudo security-monitor scan
command -v jq
```

## The dashboard shows "Scan Timer: Not active"

The timer is stopped or was never enabled. The health check re-enables it:

```bash
sudo security-manager health
systemctl list-timers 'security-monitor-*'
sudo systemctl enable --now security-monitor-scan.timer
```

## Compliance is below 100%

The dashboard lists the failing checks. The score is five checks worth 20 points: no infected files, scan timer active, a recent scan, fresh signatures, automatic updates enabled. Fix the listed item, or change `SCAN_MAX_AGE_HOURS` or `DB_MAX_AGE_DAYS` in the config file if the threshold does not suit the host.

## "Freshclam had issues (may be in cooldown)"

ClamAV rate-limits definition downloads. The scan continues with the current database and freshclam retries on its own. Read the log:

```bash
sudo tail /var/log/clamav/freshclam.log
```

## "Virus definitions missing" or "stale"

Download them by hand, then run the health check:

```bash
sudo freshclam
sudo security-manager health
```

## "Unsupported operating system"

`install` supports Ubuntu, Debian and Amazon Linux 2023. On other distributions the package and service names differ, so it refuses instead of guessing.

## A scan was skipped while the instance was off

That is expected to catch up. Both timers use `Persistent=true`, so the missed run starts at the next boot. Check with `journalctl -u security-monitor-scan.service`.

## An application broke after a scan

ClamAV flagged a file the application needs and the scan moved it. Restore it from quarantine, and set `QUARANTINE_ENABLED="no"` if you want reports without moves:

```bash
sudo ls -l /var/lib/security-monitor/quarantine
sudo mv /var/lib/security-monitor/quarantine/FILE /original/path
```

## A schedule change did nothing

`SCAN_SCHEDULE`, `HEALTH_SCHEDULE` and `SCAN_MODE` are baked into the timer units. Run `sudo security-manager install` again after editing them.

## Alerts never arrive

`ALERT_COMMAND` runs only when a scan finds infected files, and it runs as root with the findings on stdin. Test it with the EICAR file from [setup](setup.md#6-set-up-alerts), and read the scan log in `/var/log/security-monitor/`.
