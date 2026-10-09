<!-- © VampSecure Studios — VampSecure Labs Security Research Division -->

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9%2B-blue?logo=python&logoColor=white" alt="Python 3.9+"/>
  <img src="https://img.shields.io/badge/platform-linux%20%7C%20macOS%20%7C%20windows-lightgrey" alt="Platform"/>
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License MIT"/>
  <img src="https://img.shields.io/badge/VampSecure-Labs-magenta" alt="VampSecure Labs"/>
  <img src="https://github.com/Vampsecure-Labs/vamp-wp2shell-audit/actions/workflows/ci.yml/badge.svg" alt="CI"/>
</p>

# vamp-wp2shell-audit

**VampSecure Labs · Security Research Division**

> 🇬🇧 [English](#english) · 🇪🇸 [Español](#español)

---

<a name="english"></a>
## 🇬🇧 English

`vamp-wp2shell-audit` is an async, multi-target WordPress security auditor focused on upload vectors, vulnerable plugin detection, and attack surface enumeration. It fingerprints installed plugins and themes against a curated CVE database (CVSS 7.0–9.8), probes for XML-RPC, REST API user enumeration, open upload directories, and active SQLi parameters. An optional canary upload phase — using a PHP-inert file with auto-deletion — confirms whether file-write exploitation is achievable on a live target. Also supports Joomla (CVE-2023-23752) and Drupal (CVE-2018-7600 Drupalgeddon 2) fingerprinting.

### Features

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

### Requirements

- Python 3.9 or later
- `aiohttp >= 3.9.0`
- `rich >= 13.7.0`
- Optional: `fpdf2 >= 2.7` for `--report-pdf`

### Installation

```bash
pip install vamp-wp2shell-audit
# or with Homebrew:
brew install vampsecure-labs/labs/vamp-wp2shell-audit
```

```bash
git clone https://github.com/belky-me/vamp-wp2shell-audit.git
cd vamp-wp2shell-audit
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Usage

```
python3 vamp_wp2shell_audit.py --help
```

```
usage: vamp_wp2shell_audit.py [-h] [-t URL [URL ...]] [-i FILE] [-s FILE]
                               [-c CONCURRENCY] [--timeout TIMEOUT]
                               [--canary] [--force]
                               [-o FILE] [--html FILE] [-v]
                               [--client CLIENT] [--engagement ENGAGEMENT]
                               [--auditor AUDITOR] [--report-scope SCOPE]
                               [--report-html FILE] [--report-pdf FILE]

vamp-wp2shell-audit — WordPress Upload Vector Auditor (VampSecure Labs)
```

### Examples

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

### CLI Reference

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

### Output Formats

| Format | Flag | Description |
|--------|------|-------------|
| Console | (default) | Rich-colored table + per-target finding panels |
| JSON | `-o / --output FILE` | Machine-readable full result set |
| HTML | `--html FILE` | Dark-theme standalone report with finding cards |
| Client HTML | `--report-html FILE` | Unified VampSecure Labs engagement report |
| Client PDF | `--report-pdf FILE` | PDF version of the VSL client report |

### Exit Codes

| Code | Meaning | CI/CD Behavior |
|------|---------|----------------|
| `0` | No critical or high findings | Pipeline passes |
| `1` | High-severity findings detected | Pipeline fails — review required |
| `2` | Critical-severity findings detected | Pipeline fails — immediate action required |

### Sample Output

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

### Why vamp-wp2shell-audit vs. WPScan · Nikto · Wordfence CLI

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

### Check Coverage

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

### Version History

| Version | Main changes |
|---------|-------------|
| v1.2 | Bilingual README (EN/ES) |
| v1.1 | Sample Output, Why comparison, Check Coverage |
| v1.0 | Initial release — async multi-target, canary upload, CVE database, multi-CMS |

### Legal Notice

Use exclusively on systems you own or for which you hold explicit written authorization from the system owner. The `--canary` flag performs a real write operation against the target server. VampSecure Studios assumes no liability for unauthorized use.

### Part of VampSecure Labs Toolkit

`vamp-wp2shell-audit` is one tool in the VampSecure Labs security research toolkit. For the full toolkit including the orchestrator that runs all tools in sequence and aggregates findings into a single engagement report, see:

- Portfolio: [github.com/belky-me](https://github.com/belky-me)
- Orchestrator: [github.com/belky-me/vamp-orchestrator](https://github.com/belky-me/vamp-orchestrator)

---

© VampSecure Studios — VampSecure Labs Security Research Division  
For use in authorized audits only. Unauthorized use is illegal.

---
---

<a name="español"></a>
## 🇪🇸 Español

`vamp-wp2shell-audit` es un auditor de seguridad WordPress asíncrono y multi-objetivo, centrado en vectores de subida de ficheros, detección de plugins vulnerables y enumeración de la superficie de ataque. Realiza fingerprinting de los plugins y temas instalados contra una base de datos CVE curada (CVSS 7.0–9.8), sondea XML-RPC, enumeración de usuarios por la REST API, directorios de subida abiertos y parámetros SQLi activos. Una fase opcional de subida canary — usando un fichero PHP-inerte con auto-borrado — confirma si la explotación de escritura de ficheros es viable en el objetivo real. También soporta fingerprinting de Joomla (CVE-2023-23752) y Drupal (CVE-2018-7600 Drupalgeddon 2).

### Características

- Escaneo concurrente asíncrono con semáforo configurable (`-c/--concurrency`, por defecto 5)
- Base de datos CVE de plugins: 10 plugins incluyendo wp-file-manager (CVE-2020-25213, CVSS 9.8), WooCommerce Payments (CVE-2023-28121), Essential Addons for Elementor (CVE-2023-32243) y más
- Cobertura CVE de temas y fingerprinting de versión mediante `readme.txt` / `style.css` Stable tag
- Checks de superficie de ataque: XML-RPC, enumeración de usuarios por REST API, listado de directorio de subidas, `WP_DEBUG` activo
- Sondeo básico de vectores SQLi en parámetros de URL públicos
- Detección multi-CMS: WordPress, Joomla, Drupal con fingerprinting de versión
- Test de subida canary: fichero PHP-inerte (sin syscalls, guardia `die()`), auto-borrado vía REST API DELETE
- Aplicación de fichero de scope — los objetivos fuera de scope se omiten (`-s/--scope`)
- Fórmula de puntuación de riesgo: CVSS compuesto × factor de confianza de versión + bonificaciones de superficie (XML-RPC +0.5, canary confirmado +3.0)
- Exportación a JSON, HTML (dark-theme) e informe de cliente unificado VampSecure Labs (HTML + PDF)

### Requisitos

- Python 3.9 o superior
- `aiohttp >= 3.9.0`
- `rich >= 13.7.0`
- Opcional: `fpdf2 >= 2.7` para `--report-pdf`

### Instalación

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

### Uso

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

### Ejemplos

```bash
# Auditar un único sitio WordPress
python3 vamp_wp2shell_audit.py -t https://example.com

# Auditar múltiples objetivos desde fichero
python3 vamp_wp2shell_audit.py -i targets.txt

# Auditar con restricción de scope y test de subida canary
python3 vamp_wp2shell_audit.py -t https://example.com -s scope.txt --canary

# Escaneo batch concurrente con salida JSON y HTML
python3 vamp_wp2shell_audit.py -i targets.txt -c 10 -o results.json --html report.html

# Forzar auditoría aunque WordPress no sea detectado
python3 vamp_wp2shell_audit.py -t https://example.com --force

# Generar informe de cliente listo para entrega (HTML + PDF)
python3 vamp_wp2shell_audit.py -t https://example.com \
    --client "Acme Corp" --engagement "WordPress Security Review Q3 2026" \
    --auditor "J. Smith" --report-html client_report.html --report-pdf client_report.pdf
```

### Referencia CLI

| Flag | Por defecto | Descripción |
|------|-------------|-------------|
| `-t / --target URL [URL ...]` | — | Una o más URLs WordPress objetivo |
| `-i / --input FICHERO` | — | Fichero de texto con una URL por línea |
| `-s / --scope FICHERO` | — | Fichero de scope — los objetivos fuera de scope se omiten |
| `-c / --concurrency N` | 5 | Máximo de escaneos concurrentes |
| `--timeout N` | 10 | Timeout por petición en segundos |
| `--canary` | off | Activar test de subida canary en endpoints confirmados |
| `--force` | off | Auditar aunque WordPress no sea detectado |
| `-o / --output FICHERO` | — | Guardar resultados en JSON |
| `--html FICHERO` | — | Guardar informe HTML dark-theme |
| `-v / --verbose` | off | Salida detallada |
| `--client TEXTO` | — | Nombre del cliente para informe de encargo VSL |
| `--engagement TEXTO` | — | Título del encargo para informe de encargo VSL |
| `--auditor TEXTO` | — | Nombre del auditor para informe de encargo VSL |
| `--report-scope TEXTO` | — | Descripción del scope para informe de encargo VSL |
| `--report-html FICHERO` | — | Exportar informe de cliente VSL unificado (HTML) |
| `--report-pdf FICHERO` | — | Exportar informe de cliente VSL unificado (PDF, requiere fpdf2) |

### Formatos de salida

| Formato | Flag | Descripción |
|---------|------|-------------|
| Consola | (por defecto) | Tabla coloreada Rich + paneles de hallazgos por objetivo |
| JSON | `-o / --output FICHERO` | Conjunto completo de resultados legible por máquinas |
| HTML | `--html FICHERO` | Informe standalone dark-theme con tarjetas de hallazgos |
| Cliente HTML | `--report-html FICHERO` | Informe de encargo VampSecure Labs unificado |
| Cliente PDF | `--report-pdf FICHERO` | Versión PDF del informe de cliente VSL |

### Exit codes

| Código | Significado | Comportamiento CI/CD |
|--------|-------------|----------------------|
| `0` | Sin hallazgos críticos o altos | Pipeline pasa |
| `1` | Hallazgos de severidad HIGH detectados | Pipeline falla — revisión requerida |
| `2` | Hallazgos de severidad CRITICAL detectados | Pipeline falla — acción inmediata requerida |

### Ejemplo de salida

```
$ python3 vamp_wp2shell_audit.py \
    -t https://blog.example.com https://shop.example.com \
    -c 5 --canary -o results.json

╭──────────────────────────────────────────────────────────────────╮
│  vamp-wp2shell-audit v1.1 — WordPress Upload Vector Auditor      │
│  VampSecure Labs Security Research Division                      │
╰──────────────────────────────────────────────────────────────────╯

[+] Objetivos: 2  · Concurrencia: 5  · Canary: ON

── blog.example.com ──────────────────────────────────────────────
[+] CMS detectado: WordPress 6.3.1
[+] Tema         : Astra 3.7.4 (via readme.txt)
[+] Plugins encontrados: 7

╭─ CRITICAL — WP-003 ─────────────────────────────────────────────╮
│ wp-file-manager 6.0 (CVE-2020-25213, CVSS 9.8)                   │
│ Subida de fichero arbitraria / RCE sin autenticación              │
│ Instalado: 6.0 · Corregido: >= 6.9                               │
│ Ruta: /wp-content/plugins/wp-file-manager/                       │
╰──────────────────────────────────────────────────────────────────╯

╭─ HIGH — WP-001 ─────────────────────────────────────────────────╮
│ Versión WordPress revelada en meta generator tag                 │
│ <meta name="generator" content="WordPress 6.3.1"/>               │
│ Expone el retraso en parcheo; combinar con CVEs de plugins       │
╰──────────────────────────────────────────────────────────────────╯

╭─ HIGH — WP-005 ─────────────────────────────────────────────────╮
│ Endpoint XML-RPC accesible (system.listMethods → HTTP 200)       │
│ URL: https://blog.example.com/xmlrpc.php                         │
│ Riesgo: amplificación brute-force (multicall) y pivot SSRF       │
╰──────────────────────────────────────────────────────────────────╯

╭─ CRITICAL — WP-CANARY ──────────────────────────────────────────╮
│ Subida canary confirmada — escritura de fichero viable           │
│ Ruta subida : /wp-content/uploads/2026/10/vsl_canary_test.txt   │
│ Respuesta   : 200 · Auto-borrado via REST DELETE ✓               │
│ Puntuación  : 9.8 (CVE) + 3.0 (canary confirmado) = 12.8 / 13.0 │
╰──────────────────────────────────────────────────────────────────╯

── shop.example.com ──────────────────────────────────────────────
[+] CMS detectado: WordPress 6.5.2
[+] Plugins: WooCommerce Payments 5.6.1 (CVE-2023-28121, CVSS 9.8)

╭─ CRITICAL — WP-003 ─────────────────────────────────────────────╮
│ WooCommerce Payments 5.6.1 (CVE-2023-28121)                      │
│ Escalada de privilegios a administrador sin autenticación        │
│ Solución: actualizar a >= 5.6.2                                  │
╰──────────────────────────────────────────────────────────────────╯

┌──────────┬──────────────────────────────────────────────────────┐
│ Severity │ Count (2 objetivos)                                  │
├──────────┼──────────────────────────────────────────────────────┤
│ CRITICAL │ 4                                                    │
│ HIGH     │ 5                                                    │
│ MEDIUM   │ 3                                                    │
│ LOW      │ 2                                                    │
│ PASS     │ 8                                                    │
└──────────┴──────────────────────────────────────────────────────┘
[+] Resultados exportados → results.json
Exit code: 2 (CRITICAL findings — immediate action required)
```

### Por qué vamp-wp2shell-audit vs. WPScan · Nikto · Wordfence CLI

| Característica | vamp-wp2shell-audit | WPScan | Nikto | Wordfence CLI |
|----------------|:-------------------:|:------:|:-----:|:-------------:|
| Escaneo batch asíncrono multi-objetivo | ✅ async + semáforo | ❌ un solo objetivo | ❌ un solo objetivo | ❌ |
| Confirmación de subida canary (PHP-inerte, auto-borrado) | ✅ | ❌ | ❌ | ❌ |
| Fingerprinting Joomla + Drupal en la misma herramienta | ✅ | ❌ solo WP | ✅ | ❌ solo WP |
| Aplicación de fichero de scope (objetivos fuera de scope omitidos) | ✅ | ⚠️ | ❌ | ❌ |
| Informe de encargo para cliente (HTML + PDF) | ✅ | ❌ | ❌ | ❌ |
| Hallazgos alineados con OWASP Top 10 A05 / CWE-78 | ✅ | ⚠️ parcial | ⚠️ parcial | ❌ |
| Sin clave API requerida para la funcionalidad principal | ✅ | ❌ token API WPScan | ✅ | ❌ premium |
| Fórmula de puntuación de riesgo (CVSS × confianza + bonificaciones de superficie) | ✅ | ❌ | ❌ | ⚠️ |

- **Test de subida canary**: a diferencia de WPScan o Nikto, `vamp-wp2shell-audit` va más allá de la enumeración — `--canary` intenta una escritura de fichero PHP-inerte y lo borra inmediatamente vía el endpoint REST API DELETE, aportando prueba definitiva de que la explotación de subida es viable en el objetivo.
- **Multi-objetivo asíncrono**: construido sobre `aiohttp` con semáforo configurable, un lote de 50 objetivos se escanea en el tiempo que WPScan tarda en cinco; la aplicación de scope garantiza que no se toca nada fuera del perímetro del encargo.
- **Entregable listo para el cliente**: los campos `--client`, `--engagement` y `--auditor` alimentan un informe unificado HTML + PDF, listo para entregar al cliente sin postprocesado.
- **Multi-CMS en un solo binario**: el fingerprinting de Joomla (CVE-2023-23752) y Drupal (CVE-2018-7600 Drupalgeddon 2) está integrado — útil cuando una lista de activos objetivo incluye instalaciones CMS mixtas.

### Cobertura de checks

| Check ID | Descripción | Estándar | Severidad |
|----------|-------------|----------|-----------|
| WP-001 | Versión del núcleo WordPress revelada mediante meta generator tag | OWASP WSTG-INFO-02 | MEDIUM |
| WP-002 | Versión del núcleo WordPress desactualizada — CVEs conocidos en la versión instalada | OWASP Top 10 A06:2021 | HIGH |
| WP-003 | Coincidencia CVE de plugin — versión instalada dentro del rango vulnerable | OWASP Top 10 A06:2021 | CRITICAL / HIGH |
| WP-004 | Coincidencia CVE de tema — versión detectada via readme.txt / style.css | OWASP Top 10 A06:2021 | MEDIUM |
| WP-005 | Endpoint XML-RPC accesible (amplificación brute-force / pivot SSRF) | OWASP WSTG-CONF-02 | HIGH |
| WP-006 | Enumeración de usuarios REST API expuesta (/wp-json/wp/v2/users) | OWASP WSTG-IDNT-04 | MEDIUM |
| WP-007 | Interfaz de login wp-admin accesible directamente sin restricción IP | OWASP Top 10 A05 (Security Misconfiguration) | MEDIUM |
| WP-008 | Listado de directorio de subidas habilitado — enumeración de ficheros posible | OWASP WSTG-CONF-03 | HIGH |
| WP-009 | WP_DEBUG activo en producción — revelación de errores detallados | OWASP WSTG-CONF-07 | MEDIUM |
| WP-010 | Sondeo de parámetro SQLi en argumentos URL públicos | CWE-89 · OWASP WSTG-INPV-05 | HIGH |
| WP-011 | Subida canary confirma ruta real de explotación de escritura | CWE-434 · OWASP Top 10 A05 | CRITICAL |
| WP-012 | Patrón de web shell detectado en subidas (eval / base64 / llamadas a sistema) | CWE-78 · OWASP Top 10 A03:2021 | CRITICAL |

### Historial de versiones

| Versión | Cambios principales |
|---------|---------------------|
| v1.2 | README bilingüe (EN/ES) |
| v1.1 | Sample Output, comparativa Why, cobertura de checks |
| v1.0 | Versión inicial — multi-objetivo asíncrono, subida canary, base de datos CVE, multi-CMS |

### Aviso legal

Usar exclusivamente en sistemas de tu propiedad o para los que dispongas de autorización escrita explícita del propietario del sistema. El flag `--canary` realiza una operación de escritura real contra el servidor objetivo. VampSecure Studios no asume ninguna responsabilidad por el uso no autorizado.

### Parte del toolkit VampSecure Labs

`vamp-wp2shell-audit` es una herramienta del toolkit de investigación de seguridad VampSecure Labs. Para el toolkit completo, incluyendo el orquestador que ejecuta todas las herramientas en secuencia y agrega los hallazgos en un único informe de encargo, consulta:

- Portfolio: [github.com/belky-me](https://github.com/belky-me)
- Orquestador: [github.com/belky-me/vamp-orchestrator](https://github.com/belky-me/vamp-orchestrator)

---

© VampSecure Studios — VampSecure Labs Security Research Division  
Uso exclusivo en auditorías autorizadas. El uso no autorizado es ilegal.
