# © VampSecure Studios — VampSecure Labs Security Research Division
"""
Fixtures compartidos para los tests de vamp-wp2shell-audit.
Proporciona HTML de WordPress, cabeceras simuladas y ScanResult de prueba.
"""

import os
import sys
from datetime import datetime, timezone

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vamp_wp2shell_audit import (
    ScanResult,
)

# ---------------------------------------------------------------------------
# Fixtures de HTML WordPress
# ---------------------------------------------------------------------------

@pytest.fixture()
def html_wordpress_581():
    """HTML típico de un WordPress 5.8.1 con indicadores estándar."""
    return """<!DOCTYPE html>
<html>
<head>
<meta name="generator" content="WordPress 5.8.1" />
<link rel="stylesheet" href="/wp-content/themes/twentytwentyone/style.css?ver=5.8.1" />
<script src="/wp-includes/js/jquery/jquery.min.js?ver=3.6.0"></script>
</head>
<body>
<a href="/wp-login.php">Login</a>
</body>
</html>"""


@pytest.fixture()
def html_no_wordpress():
    """HTML de un sitio que NO es WordPress."""
    return """<!DOCTYPE html>
<html>
<head><title>Mi sitio Drupal</title></head>
<body>
<link rel="stylesheet" href="/themes/bootstrap/style.css" />
<p>Bienvenido a Drupal</p>
</body>
</html>"""


@pytest.fixture()
def cabeceras_wordpress():
    """Cabeceras HTTP típicas de un servidor WordPress."""
    return {
        "Server": "Apache/2.4.51 (Ubuntu)",
        "X-Powered-By": "PHP/7.4.28",
        "Content-Type": "text/html; charset=UTF-8",
        "Link": '<https://example.com/wp-json/>; rel="https://api.w.org/"',
    }


@pytest.fixture()
def cabeceras_vacias():
    """Cabeceras HTTP sin indicadores de WordPress."""
    return {
        "Content-Type": "text/html",
        "Server": "nginx/1.20.0",
    }


# ---------------------------------------------------------------------------
# Fixtures de ScanResult
# ---------------------------------------------------------------------------

@pytest.fixture()
def scan_result_wordpress():
    """ScanResult de un WordPress 5.8.1 con plugin vulnerable."""
    r = ScanResult(target="https://example.com")
    r.timestamp = datetime.now(timezone.utc).isoformat()
    r.is_wordpress = True
    r.wp_version = "5.8.1"
    r.xmlrpc_enabled = True
    r.rest_api_exposed = True
    r.upload_dir_exposed = False
    r.debug_mode = False
    r.installed_plugins = {"wp-file-manager": "6.8"}
    r.installed_themes = {}
    r.plugin_findings = []
    r.theme_findings = []
    r.sqli_vectors = []
    r.canary = None
    r.risk_score = 0.0
    r.risk_level = "NONE"
    r.error = None
    return r


@pytest.fixture()
def scan_result_vacio():
    """ScanResult de un sitio sin WordPress."""
    r = ScanResult(target="https://nowordpress.example.com")
    r.timestamp = datetime.now(timezone.utc).isoformat()
    r.is_wordpress = False
    r.wp_version = None
    r.xmlrpc_enabled = False
    r.rest_api_exposed = False
    r.upload_dir_exposed = False
    r.debug_mode = False
    r.installed_plugins = {}
    r.installed_themes = {}
    r.plugin_findings = []
    r.theme_findings = []
    r.sqli_vectors = []
    r.canary = None
    r.risk_score = 0.0
    r.risk_level = "NONE"
    r.error = None
    return r
