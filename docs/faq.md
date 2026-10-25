# ❓ FAQ

## Which systems does it support?

Ubuntu, Debian and Amazon Linux 2023, on any machine with systemd, not only EC2. The installer detects the distribution and refuses anything else. The scan and dashboard code also recognise RHEL, CentOS and Fedora, but the installer does not set those up and they are untested.

## Does it need AWS or an AWS account?

No. It uses no AWS API and reads no instance metadata. The name says where it was built for: EC2 instances running Ubuntu or Amazon Linux. The only AWS-specific example is an optional `ALERT_COMMAND` that publishes to SNS, which needs your own credentials or instance role.

## Does it send data anywhere?

No. There is no telemetry. Data leaves the host only through downloads of ClamAV signatures and OS packages, and through `ALERT_COMMAND` if you set one.

## Does it delete infected files?

No. With `QUARANTINE_ENABLED="yes"` (the default) it moves them to a root-owned `0700` quarantine directory, so a false positive is recoverable. With `"no"` it only reports them.

## How long does a scan take?

A quick scan takes about 30 to 90 seconds, and a full scan 10 to 30 minutes, on small instances. Your numbers depend on the instance size and how many files the paths contain.

## Will it slow my server down?

The scheduled scan runs at `Nice=10` with idle I/O priority, which keeps it behind your workload. A full scan still reads a lot of files, so choose a quiet hour in `SCAN_SCHEDULE`.

## Does it apply updates without asking?

Yes. Every scan applies pending package updates, and the installer enables the distribution's unattended-update tool. Some updates restart services. Do not install it on a host where that is unacceptable.

## How do I get alerts by email, Slack or SNS?

Set `ALERT_COMMAND` to any shell command that reads the alert on stdin. Examples for local mail, SNS and a webhook are in the [README](../README.md).

## How do I check it works without real malware?

Create the EICAR test file and run a scan. The steps are in [setup](setup.md#6-set-up-alerts).

## Can I run it on a fleet?

Each host installs and runs on its own. The scan timer adds up to 15 minutes of random delay so a fleet does not scan at the same second. There is no central console.

## How do I remove it?

Run `sudo security-manager uninstall`. It removes the timers, scripts, config, data and logs, and warns first if files are still quarantined. ClamAV packages stay installed.

## How do I report a system that works or breaks?

Open an issue with the details in [CONTRIBUTING.md](../CONTRIBUTING.md#-reporting-an-environment-or-a-bug). Reports from distributions and instance types not listed in the README are the most useful.
