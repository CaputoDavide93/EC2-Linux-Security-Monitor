<div align="center">

<img src="docs/assets/brand/icon.svg" width="96" alt="EC2 Linux Security Monitor icon: a shield with a terminal prompt">

# 🛡️ EC2 Linux Security Monitor

**EC2 Linux servers scanned for malware, patched and self-checked by two Bash scripts and systemd timers, with no agent or cloud service**

![Shell](https://img.shields.io/badge/Shell-Bash%204.0%2B-4EAA25?logo=gnu-bash&logoColor=white)
![ClamAV](https://img.shields.io/badge/ClamAV-on--demand-FF0000?logo=hackaday&logoColor=white)
![Linux](https://img.shields.io/badge/Linux-systemd-FCC624?logo=linux&logoColor=black)
![License: MIT](https://img.shields.io/badge/License-MIT-green)
[![Lint](https://github.com/CaputoDavide93/EC2-Linux-Security-Monitor/actions/workflows/lint.yml/badge.svg)](https://github.com/CaputoDavide93/EC2-Linux-Security-Monitor/actions/workflows/lint.yml)

[Why](#-why-this-exists) • [Install](#install-in-3-steps) • [Features](#-features) • [Docs](docs/README.md) • [Contributing](#-contributing)

</div>

---

## 💡 Why this exists

You launch an EC2 instance, install ClamAV, add a cron line, and a month later nobody knows whether the scan still runs, the signatures are current or the updates were applied. The usual fixes are a hosted security agent with an account and a bill, or a pile of cron jobs you maintain by hand.

This project installs one scan timer and one health timer, and gives you a single command that shows what is true right now: when the last scan finished, whether it was clean, how old the signatures are, and which services are down. The health timer repairs the common failures on its own.

| | EC2 Linux Security Monitor | Hosted security agents | Hand-written cron and ClamAV |
|---|---|---|---|
| Account or subscription | None | Needed | None |
| Data leaves the host | Only what you pipe to `ALERT_COMMAND` | Agent reports to a vendor | Whatever you wrote |
| Extra software on the host | ClamAV, `jq`, `curl`, two scripts | The vendor's agent | ClamAV and your scripts |
| Quarantine, not delete | Built in, `0700`, root-owned | Varies | You write it |
| Package updates | Applied on every scan, plus the distro's unattended tool | Varies | You write it |
| Health repair (dead services, stale signatures, stopped timers) | Every 6 hours | Varies | You write it |
| Status you can read over SSH | `security-monitor status`, no `sudo` | A web console | You write it |
| Central view of many hosts | No | Yes | No |

The trade-off: each host is on its own. There is no console, no fleet-wide report and no real-time protection, only scheduled on-demand scans.

### Install in 3 steps

You need a systemd server running Ubuntu, Debian or Amazon Linux 2023, with `sudo` and outbound internet access.

1. **Get the scripts:** `git clone https://github.com/CaputoDavide93/EC2-Linux-Security-Monitor.git && cd EC2-Linux-Security-Monitor`
2. **Install:** `chmod +x security-monitor.sh security-manager.sh && sudo ./security-manager.sh install`
3. **Scan and look:** `sudo security-monitor scan`, then `security-monitor status`

The [setup guide](docs/setup.md) covers each step, alerts and removal. Read both scripts before installing: they run as root and apply updates unattended.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/screenshots/dashboard-dark.png">
  <img src="docs/assets/screenshots/dashboard-light.png" width="520" alt="The security-monitor status dashboard on demo data: clean scan six hours ago, compliance 100 percent, both timers active, signatures one day old.">
</picture>

---

## ✨ Features

| | Feature | What it does |
|---|---------|--------------|
| 🦠 | **ClamAV scanning** | Quick (30 to 90 s) or full (10 to 30 min) `clamscan` sweeps, non-existent paths skipped automatically |
| 🔒 | **Quarantine** | Infected files are *moved* (never deleted) to a `0700` root-owned directory, excluded from later scans |
| 📣 | **Alerting** | Runs your `ALERT_COMMAND` with the findings on stdin: mail, SNS, a Slack webhook, anything |
| 🔄 | **Auto updates** | Applies pending updates during every scan (apt or dnf) and reports applied against still-available |
| 🧬 | **Fresh definitions** | Runs `freshclam` before each scan, pausing the service so it cannot hold the database lock |
| 📊 | **Status dashboard** | Real state only: scan freshness, 5-point compliance score, services, signature version and age |
| ⏰ | **systemd timers** | Daily scan and 6-hourly health check, `Persistent=true` so a stopped instance catches up |
| 🩺 | **Self-healing health check** | Restarts dead services, refreshes stale definitions, re-enables stopped timers |
| ⚙️ | **Single config file** | One `/etc/security-monitor/security-monitor.conf` drives behaviour and what the dashboard reports |
| 📝 | **Managed logs** | Logrotate for the service logs, age-based pruning for per-scan logs, status as JSON |

### Supported and tested

| System | Status |
|---|---|
| Ubuntu 24.04 (apt) | Scan, EICAR detection, quarantine, `status.json` and the dashboard exercised in a container for this release. The installer and systemd timers were not run there |
| Other Ubuntu and Debian releases (apt) | Supported by the installer. Not re-tested in this release |
| Amazon Linux 2023 (dnf) | Supported by the installer. Not re-tested in this release, unverified |
| Real EC2 instances | Unverified in this release |
| RHEL, CentOS, Fedora | Recognised by the scan and dashboard code, refused by the installer, untested |

Tested a system not listed here? See [Contributing](#-contributing).

---

## 🗺️ Architecture

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/assets/architecture-dark.svg">
  <img src="docs/assets/architecture-light.svg" width="100%"
       alt="The scan timer runs security-monitor, which refreshes definitions and scans with ClamAV, applies package updates with apt or dnf, writes status.json and quarantines infected files, and pipes findings to ALERT_COMMAND; the status dashboard reads status.json, and the health timer runs security-manager, which repairs services, definitions and timers, with both scripts sourcing one config file.">
</picture>

Two scripts. `security-manager` installs and maintains; `security-monitor` scans and reports.
Both read the same config file, so a schedule or path is stated in exactly one place.
[How it works](docs/how-it-works.md) walks through a single scan.

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Notes |
|-------------|-------|
| Linux + systemd | Timers and services are managed with `systemctl`; `install` refuses to run without it |
| Bash 4.0+ | Both scripts are pure Bash |
| Root access | `install`, `uninstall`, `health`, and `scan` need root. `status` does **not** |
| Internet access | To download ClamAV packages and virus definitions |

`install` refuses anything other than Ubuntu, Debian and Amazon Linux with `Unsupported operating system`.

### Install

```bash
git clone https://github.com/CaputoDavide93/EC2-Linux-Security-Monitor.git
cd EC2-Linux-Security-Monitor
chmod +x security-monitor.sh security-manager.sh
sudo ./security-manager.sh install
```

The installer runs nine steps: package lists, ClamAV + `jq` + `curl` + auto-update tooling,
ClamAV configuration, unattended updates, the config file, logrotate, both scripts into
`/usr/local/bin`, the systemd timers, and the shell shortcuts.

Then reload your shell to pick up the shortcuts, run a first scan and view the dashboard:

```bash
source /etc/profile.d/security-monitor.sh
sudo security-monitor scan     # quick scan
security-monitor status        # dashboard, no sudo needed
```

> **Upgrading from v2.x?** `install` removes the old `/etc/cron.d/security-monitor` and
> replaces it with systemd timers. Your existing config is never overwritten.

---

## ⚙️ Configuration

Everything lives in **`/etc/security-monitor/security-monitor.conf`** (installed from
[security-monitor.conf](security-monitor.conf), and never overwritten once present). It is
sourced by both scripts, so a value set here changes behaviour *and* what the dashboard
reports.

| Variable | Purpose | Default |
|---|---|---|
| `SECURITY_DIR` | Runtime data: `status.json`, quarantine | `/var/lib/security-monitor` |
| `LOG_DIR` | Log destination | `/var/log/security-monitor` |
| `QUARANTINE_DIR` | Where infected files are moved | `$SECURITY_DIR/quarantine` |
| `QUARANTINE_ENABLED` | `yes` moves infected files, `no` only reports them | `yes` |
| `ALERT_COMMAND` | Shell command fed the alert on stdin; empty disables alerting | *(empty)* |
| `SCAN_SCHEDULE` | `OnCalendar` for the scan timer | `*-*-* 02:00:00` |
| `HEALTH_SCHEDULE` | `OnCalendar` for the health timer | `*-*-* 00/6:00:00` |
| `SCAN_MODE` | Mode the scheduled scan uses: `quick` or `full` | `full` |
| `QUICK_SCAN_PATHS` | Paths for a quick scan | `/home /root` |
| `FULL_SCAN_PATHS` | Paths for a full scan | `/home /root /opt /tmp /var /usr/local` |
| `DB_MAX_AGE_DAYS` | Definitions older than this are stale | `7` |
| `SCAN_MAX_AGE_HOURS` | Scans older than this are overdue | `48` |
| `LOG_RETENTION_DAYS` | Per-scan logs older than this are deleted after each scan | `30` |

After changing a `*_SCHEDULE` or `SCAN_MODE`, re-run `sudo security-manager install` to
rewrite the timer units. Every other value takes effect on the next scan.

<details>
<summary>📣 Alerting examples</summary>

`ALERT_COMMAND` receives the subject line and the matching `clamscan` output on stdin. It
runs only when a scan finds infected files.

```bash
# Local mail
ALERT_COMMAND="mail -s 'ClamAV alert' root"

# Amazon SNS
ALERT_COMMAND="aws sns publish --topic-arn arn:aws:sns:eu-west-1:123456789012:alerts --message \"\$(cat)\""

# Generic webhook
ALERT_COMMAND="curl -sS -X POST -H 'Content-Type: text/plain' --data-binary @- https://example.com/hook"
```

Verify the plumbing without real malware, using the EICAR test file:

```bash
printf 'X5O!P%%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > /root/eicar.txt
sudo security-monitor scan
```
</details>

<details>
<summary>🔒 Working with quarantined files</summary>

Infected files are **moved, not deleted**, so a false positive is always recoverable:

```bash
sudo ls -l /var/lib/security-monitor/quarantine     # what was caught
sudo mv /var/lib/security-monitor/quarantine/FILE /original/path   # restore
sudo rm /var/lib/security-monitor/quarantine/FILE                 # destroy
```

The directory is `0700` and root-owned, and is excluded from subsequent scans so the same
file is never re-reported. Set `QUARANTINE_ENABLED="no"` to report without moving anything,
safer for hosts where an application might depend on a flagged file.

`uninstall` deletes the data directory, and warns first if anything is still quarantined.
</details>

---

---

## 📖 Usage

### security-monitor

```text
Usage: security-monitor [scan [quick|full]|status|version]

  scan [quick|full]   Run a security scan (default: quick, needs root)
  status              Show the status dashboard (default, no root needed)
  version             Print version
```

| Mode | Paths | Extra limits | Typical duration |
|------|-------|--------------|------------------|
| `quick` (default) | `$QUICK_SCAN_PATHS` | max filesize 50M, scansize 100M, recursion 5 | 30 to 90 seconds |
| `full` | `$FULL_SCAN_PATHS` | none | 10 to 30 minutes |

Both modes exclude `/sys`, `/proc`, `/dev`, the quarantine directory, `.git`,
`node_modules`, and `.cache`.

The `status` dashboard reports scan status and freshness, a 5-point compliance score,
pending and applied updates, ClamAV and timer state, and the signature database version,
signature count, and age. Every figure comes from the live system or the last scan. There
are no placeholder values.

### security-manager

```text
Usage: security-manager [install|uninstall|health|version]

  install     Install the security monitoring system
  uninstall   Remove the security monitoring system
  health      Perform a health check
  version     Print version

Run without arguments for an interactive menu.
```

`health` checks, and where it can repairs, the freshclam service, the ClamAV daemon,
signature age (re-downloads past `DB_MAX_AGE_DAYS`), both systemd timers, and the installed
scripts, config, and shell shortcuts. It exits after reporting how many checks needed
attention.

`uninstall` removes the timers and units, the legacy cron file, both scripts, the logrotate
config, shell shortcuts, config, data, and logs. Shortcut removal detects whether the
`~/.bashrc` block is the current format (with an end marker) or the pre-3.0 format and deletes
only that block, leaving the rest of the file intact. **ClamAV packages stay installed**. Remove
them with `apt-get remove --purge 'clamav*'` or `dnf remove 'clamav*'`.

### Scan results

`$SECURITY_DIR/status.json` (mode `0644`, so `status` works without root) holds the last result. Counts are JSON numbers:

```json
{
  "last_scan": "2026-08-26T02:00:11+00:00",
  "scan_mode": "full",
  "scan_status": "clean",
  "infected_files": 0,
  "scanned_files": 18432,
  "quarantined_files": 0,
  "updates_available": 0,
  "updates_applied": 12
}
```

`scan_status` is `clean`, `attention` (infected files found), or `error` (clamscan failed to
run, exit code 2 or above).

### Automated monitoring

`install` creates and enables two timers:

| Unit | Schedule | Runs |
|---|---|---|
| `security-monitor-scan.timer` | `SCAN_SCHEDULE` (02:00 daily) | `security-monitor scan $SCAN_MODE` |
| `security-monitor-health.timer` | `HEALTH_SCHEDULE` (every 6 h) | `security-manager health` |

Both use `Persistent=true`, so a run missed while the instance was stopped happens on next
boot. The scan service runs at `Nice=10` and `IOSchedulingClass=idle` to stay off the
critical path on small instances, and the scan timer adds `RandomizedDelaySec=15m` so a
fleet doesn't scan in lockstep.

```bash
systemctl list-timers 'security-monitor-*'     # when they next fire
journalctl -u security-monitor-scan.service    # what the last scan did
sudo systemctl start security-monitor-scan     # run one now, out of band
```

Change the schedule in the config file, then re-run `sudo security-manager install`. Editing
the unit files directly works too, but `install` will overwrite them.

---

---

## 📁 Repo structure

```text
EC2-Linux-Security-Monitor/
├── .github/workflows/
│   └── lint.yml              # 🧪 shellcheck, bash -n, diagram check, OnCalendar validation
├── docs/
│   ├── assets/               # 🗺️ diagrams, screenshots, brand icon, social preview
│   ├── README.md             # 📚 docs index
│   ├── setup.md              # 🚀 first install, step by step
│   ├── how-it-works.md       # 🧠 one scan, the timers, the dashboard
│   ├── faq.md                # ❓ quick answers
│   └── troubleshooting.md    # 🛠️ by symptom
├── tools/
│   ├── gen_diagram.py        # 🖌️ draws the diagrams
│   ├── social_preview.py     # 🖼️ draws the social preview image
│   └── screenshots/          # 📸 dashboard screenshots from the real script
├── security-monitor.sh       # 🛡️ scanning, quarantine, alerting, dashboard
├── security-manager.sh       # 🔧 install, uninstall, health check
├── security-monitor.conf     # ⚙️ default config, installed to /etc/security-monitor/
├── Makefile                  # ✅ make check, diagram, screenshots
├── llms.txt                  # 🔎 one-page summary for AI search
├── AGENTS.md                 # 🤖 rules for coding agents
├── CLAUDE.md                 # 🤖 imports AGENTS.md for Claude Code
├── CONTRIBUTING.md           # 🤝 how to contribute and report systems
├── SECURITY.md               # 🔒 vulnerability reporting, what the tool changes
└── LICENSE                   # 📄 MIT
```

---

## 🧪 Testing

There is no automated test suite. CI ([lint.yml](.github/workflows/lint.yml)) lints both
scripts, checks syntax, checks the diagrams are current, and validates the config and timer
schedules on every push to `main` and every pull request. Run the same checks locally:

```bash
make check
```

`make screenshots` retakes the dashboard screenshots (needs Docker and `uv`). See
[CONTRIBUTING.md](CONTRIBUTING.md) for the full local check list.

---

## 🛠️ Troubleshooting

The common symptoms (no scan data, timer not active, compliance below 100%, freshclam
cooldown, unsupported operating system) are in [docs/troubleshooting.md](docs/troubleshooting.md).
Quick answers about support, data and false positives are in [docs/faq.md](docs/faq.md).

---

## 🔒 Security

This tool runs as root, applies package updates unattended, and can move files into
quarantine. Review both scripts before installing them on anything you care about. See
[SECURITY.md](SECURITY.md) for vulnerability reporting and what the tool touches.

---

## 🤝 Contributing

Reports of a distribution, release or instance type that works, or does not, are the most
useful contribution. Open an issue with the OS and version, `bash --version`,
`security-monitor version` and the command you ran. For scheduling problems add
`systemctl list-timers 'security-monitor-*'` and `journalctl -u security-monitor-scan.service`.
Code changes and the local checks are covered in [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📄 License

MIT. See [LICENSE](LICENSE).

---

<p align="center"><sub>Made with ❤️ by <a href="https://github.com/CaputoDavide93">Davide Caputo</a></sub></p>
