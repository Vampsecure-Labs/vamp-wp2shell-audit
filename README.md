<!-- © VampSecure Studios — VampSecure Labs Security Research Division -->
<h1 align="center">vamp-wp2shell-audit</h1>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT"/>
  <img src="https://img.shields.io/badge/VampSecure-Labs-magenta" alt="VampSecure Labs"/>
  <img src="https://github.com/Vampsecure-Labs/vamp-wp2shell-audit/actions/workflows/ci.yml/badge.svg" alt="CI"/>
</p>

## Overview

`vamp-wp2shell-audit` is an async, multi-target WordPress security auditor focused on upload vectors, vulnerable plugin detection, and attack surface enumeration. It fingerprints installed plugins and themes against a curated CVE database (CVSS 7.0–9.8), probes for XML-RPC, REST API user enumeration, open upload directories, and active SQLi parameters. An optional canary upload phase — using a PHP-inert file with auto-deletion — confirms whether file-write exploitation is achievable on a live target. Also supports Joomla (CVE-2023-23752) and Drupal (CVE-2018-7600 Drupalgeddon 2) fingerprinting.

## Features

- Async concurrent scanning with configurable semaphore (`-c/--concurrency`, default 5)
- Plugin CVE database: 10 plugins including wp-file-manager (CVE-2020-25213, CVSS 9.8), WooCommerce Payments (CVE-2023-28121), Essential Addons for Elementor (CVE-2023-32243), and more
- Theme CVE coverage and version fingerprinting via `readme.txt` / `style.css` Stable tag
- Attack surface checks: XML-RPC, REST API user enumeration, uploads directory listing, `WP_DEBUG` active
- Basic SQLi vector probing on public URL parameters
- Multi-CMS detection: WordPress, Joomla, Drupal with version fingerprinting
- Canary upload test: PHP-inert file (no syscalls, `die()` guard), auto-deleted via REST API DELETE
- Scope file enforcement — targets outside scope are skipped (`-s/--scope`)
- Risk scoring formula: composite CVSS × version-confidence factor + surface bonuses (XML-RPC +0.5, canary confirmed +3.0)
- Export to JSON, HTML (dark-theme), and unified VampSecure Labs client report (HTML + PDF)

## Requirements

- Python 3.9 or later
- `aiohttp >= 3.9.0`
- `rich >= 13.7.0`
- Optional: `fpdf2 >= 2.7` for `--report-pdf`

## Installation


```bash
pip install vamp-wp2shell-audit
# o con Homebrew:
brew install vampsecure-labs/labs/vamp-wp2shell-audit
```

```bash
git clone https://github.com/belky-me/vamp-wp2shell-audit.git
cd vamp-wp2shell-audit
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

```
python3 vamp_wp2shell_audit.py --help
```

```
usage: vamp_wp2shell_audit.py [-h] [-t URL [URL ...]] [-i FICHERO] [-s FICHERO]
                               [-c CONCURRENCY] [--timeout TIMEOUT]
                               [--canary] [--force]
                               [-o FICHERO] [--html FICHERO] [-v]
                               [--client CLIENT] [--engagement ENGAGEMENT]
                               [--auditor AUDITOR] [--report-scope SCOPE]
                               [--report-html FILE] [--report-pdf FILE]

vamp-wp2shell-audit — WordPress Upload Vector Auditor (VampSecure Labs)
```

## Examples

```bash
# Audit a single WordPress site
python3 vamp_wp2shell_audit.py -t https://example.com

# Audit multiple targets from file
python3 vamp_wp2shell_audit.py -i targets.txt

# Audit with scope restriction and canary upload test
python3 vamp_wp2shell_audit.py -t https://example.com -s scope.txt --canary

# Concurrent batch scan with JSON and HTML output
python3 vamp_wp2shell_audit.py -i targets.txt -c 10 -o results.json --html report.html

# Force audit even if WordPress is not detected
python3 vamp_wp2shell_audit.py -t https://example.com --force

# Generate client-ready engagement report (HTML + PDF)
python3 vamp_wp2shell_audit.py -t https://example.com \
    --client "Acme Corp" --engagement "WordPress Security Review Q3 2026" \
    --auditor "J. Smith" --report-html client_report.html --report-pdf client_report.pdf
```

## CLI Reference

| Flag | Default | Description |
|------|---------|-------------|
| `-t / --target URL [URL ...]` | — | One or more target WordPress URLs |
| `-i / --input FILE` | — | Text file with one URL per line |
| `-s / --scope FILE` | — | Scope file — targets outside scope are skipped |
| `-c / --concurrency N` | 5 | Maximum concurrent scans |
| `--timeout N` | 10 | Per-request timeout in seconds |
| `--canary` | off | Enable canary upload test on confirmed endpoints |
| `--force` | off | Audit even if WordPress is not detected |
| `-o / --output FILE` | — | Save results to JSON |
| `--html FILE` | — | Save dark-theme HTML report |
| `-v / --verbose` | off | Verbose output |
| `--client TEXT` | — | Client name for VSL engagement report |
| `--engagement TEXT` | — | Engagement title for VSL engagement report |
| `--auditor TEXT` | — | Auditor name for VSL engagement report |
| `--report-scope TEXT` | — | Scope description for VSL engagement report |
| `--report-html FILE` | — | Export unified VSL client report (HTML) |
| `--report-pdf FILE` | — | Export unified VSL client report (PDF, requires fpdf2) |

## Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Console | (default) | Rich-colored table + per-target finding panels |
| JSON | `-o / --output FILE` | Machine-readable full result set |
| HTML | `--html FILE` | Dark-theme standalone report with finding cards |
| Client HTML | `--report-html FILE` | Unified VampSecure Labs engagement report |
| Client PDF | `--report-pdf FILE` | PDF version of the VSL client report |

## Exit Codes

| Code | Meaning | CI/CD Behavior |
|------|---------|----------------|
| `0` | No critical or high findings | Pipeline passes |
| `1` | High-severity findings detected | Pipeline fails — review required |
| `2` | Critical-severity findings detected | Pipeline fails — immediate action required |

## Sample Output

```
$ python3 vamp_wp2shell_audit.py \
    -t https://blog.example.com https://shop.example.com \
    -c 5 --canary -o results.json

╭──────────────────────────────────────────────────────────────────╮
│  vamp-wp2shell-audit v1.1 — WordPress Upload Vector Auditor      │
│  VampSecure Labs Security Research Division                      │
╰──────────────────────────────────────────────────────────────────╯

[+] Targets: 2  · Concurrency: 5  · Canary: ON

── blog.example.com ──────────────────────────────────────────────
[+] CMS detected : WordPress 6.3.1
[+] Theme        : Astra 3.7.4 (via readme.txt)
[+] Plugins found: 7

╭─ CRITICAL — WP-003 ─────────────────────────────────────────────╮
│ wp-file-manager 6.0 (CVE-2020-25213, CVSS 9.8)                   │
│ Unauthenticated arbitrary file upload / RCE                       │
│ Installed: 6.0 · Fixed: >= 6.9                                   │
│ Path: /wp-content/plugins/wp-file-manager/                       │
╰──────────────────────────────────────────────────────────────────╯

╭─ HIGH — WP-001 ─────────────────────────────────────────────────╮
│ WordPress version disclosed in meta generator tag                │
│ <meta name="generator" content="WordPress 6.3.1"/>               │
│ Exposes patch lag; combine with plugin CVEs for exploitation     │
╰──────────────────────────────────────────────────────────────────╯

╭─ HIGH — WP-005 ─────────────────────────────────────────────────╮
│ XML-RPC endpoint reachable (system.listMethods → HTTP 200)       │
│ URL: https://blog.example.com/xmlrpc.php                         │
│ Risk: brute-force amplification (multicall) and SSRF pivot       │
╰──────────────────────────────────────────────────────────────────╯

╭─ CRITICAL — WP-CANARY ──────────────────────────────────────────╮
│ Canary upload confirmed — file write achievable                  │
│ Upload path  : /wp-content/uploads/2026/10/vsl_canary_test.txt  │
│ HTTP response: 200 · Auto-deleted via REST DELETE ✓              │
│ Risk score   : 9.8 (CVE) + 3.0 (canary confirmed) = 12.8 / 13.0 │
╰──────────────────────────────────────────────────────────────────╯

── shop.example.com ──────────────────────────────────────────────
[+] CMS detected: WordPress 6.5.2
[+] Plugins: WooCommerce Payments 5.6.1 (CVE-2023-28121, CVSS 9.8)

╭─ CRITICAL — WP-003 ─────────────────────────────────────────────╮
│ WooCommerce Payments 5.6.1 (CVE-2023-28121)                      │
│ Unauthenticated privilege escalation to administrator            │
│ Fix: upgrade to >= 5.6.2                                         │
╰──────────────────────────────────────────────────────────────────╯

┌──────────┬──────────────────────────────────────────────────────┐
│ Severity │ Count (2 targets)                                    │
├──────────┼──────────────────────────────────────────────────────┤
│ CRITICAL │ 4                                                    │
│ HIGH     │ 5                                                    │
│ MEDIUM   │ 3                                                    │
│ LOW      │ 2                                                    │
│ PASS     │ 8                                                    │
└──────────┴──────────────────────────────────────────────────────┘
[+] Results exported → results.json
Exit code: 2 (CRITICAL findings — immediate action required)
```

## Why vamp-wp2shell-audit vs. WPScan · Nikto · Wordfence CLI

| Feature | vamp-wp2shell-audit | WPScan | Nikto | Wordfence CLI |
|---------|:-------------------:|:------:|:-----:|:-------------:|
| Multi-target async batch scan | ✅ async + semaphore | ❌ single target | ❌ single target | ❌ |
| Canary upload confirmation (PHP-inert, auto-deleted) | ✅ | ❌ | ❌ | ❌ |
| Joomla + Drupal fingerprinting in same tool | ✅ | ❌ WP only | ✅ | ❌ WP only |
| Scope file enforcement (out-of-scope targets skipped) | ✅ | ⚠️ | ❌ | ❌ |
| Client engagement report (HTML + PDF) | ✅ | ❌ | ❌ | ❌ |
| OWASP Top 10 A05 / CWE-78 aligned findings | ✅ | ⚠️ partial | ⚠️ partial | ❌ |
| No API key required for core functionality | ✅ | ❌ WPScan API token | ✅ | ❌ premium |
| Risk scoring formula (CVSS × confidence + surface bonuses) | ✅ | ❌ | ❌ | ⚠️ |

- **Canary upload test**: unlike WPScan or Nikto, `vamp-wp2shell-audit` goes beyond enumeration — `--canary` attempts a PHP-inert file write and immediately auto-deletes it via the REST API DELETE endpoint, giving definitive proof that file upload exploitation is feasible on the target.
- **Async multi-target**: built on `aiohttp` with a configurable semaphore, a batch of 50 targets scans in the time WPScan takes for five; scope enforcement ensures nothing outside the engagement boundary is touched.
- **Engagement-ready deliverable**: `--client`, `--engagement`, and `--auditor` fields feed a unified HTML + PDF client report, ready to hand to the customer without post-processing.
- **Multi-CMS in one binary**: Joomla (CVE-2023-23752) and Drupal (CVE-2018-7600 Drupalgeddon 2) fingerprinting are built in — useful when a target asset list includes mixed CMS installations.

## Check Coverage

| Check ID | Description | Standard | Severity |
|----------|-------------|----------|----------|
| WP-001 | WordPress core version disclosed via meta generator tag | OWASP WSTG-INFO-02 | MEDIUM |
| WP-002 | WordPress core version outdated — known CVEs in installed version | OWASP Top 10 A06:2021 | HIGH |
| WP-003 | Plugin CVE match — installed version within vulnerable range | OWASP Top 10 A06:2021 | CRITICAL / HIGH |
| WP-004 | Theme CVE match — version fingerprinted via readme.txt / style.css | OWASP Top 10 A06:2021 | MEDIUM |
| WP-005 | XML-RPC endpoint reachable (brute-force amplification / SSRF pivot) | OWASP WSTG-CONF-02 | HIGH |
| WP-006 | REST API user enumeration exposed (/wp-json/wp/v2/users) | OWASP WSTG-IDNT-04 | MEDIUM |
| WP-007 | wp-admin login interface directly accessible without IP restriction | OWASP Top 10 A05 (Security Misconfiguration) | MEDIUM |
| WP-008 | Uploads directory listing enabled — file enumeration possible | OWASP WSTG-CONF-03 | HIGH |
| WP-009 | WP_DEBUG active in production — verbose error disclosure | OWASP WSTG-CONF-07 | MEDIUM |
| WP-010 | SQLi parameter probe on public URL arguments | CWE-89 · OWASP WSTG-INPV-05 | HIGH |
| WP-011 | Canary upload confirms real file-write exploitation path | CWE-434 · OWASP Top 10 A05 | CRITICAL |
| WP-012 | Web shell pattern detected in uploads (eval / base64 / system calls) | CWE-78 · OWASP Top 10 A03:2021 | CRITICAL |

## Legal Notice

Use exclusively on systems you own or for which you hold explicit written authorization from the system owner. The `--canary` flag performs a real write operation against the target server. VampSecure Studios assumes no liability for unauthorized use.

## Part of VampSecure Labs Toolkit

`vamp-wp2shell-audit` is one tool in the VampSecure Labs security research toolkit. For the full toolkit including the orchestrator that runs all tools in sequence and aggregates findings into a single engagement report, see:

- Portfolio: [github.com/belky-me](https://github.com/belky-me)
- Orchestrator: [github.com/belky-me/vamp-orchestrator](https://github.com/belky-me/vamp-orchestrator)

---

© VampSecure Studios — VampSecure Labs Security Research Division

## Versión
v1.1 — VampSecure Labs Security Research Division
