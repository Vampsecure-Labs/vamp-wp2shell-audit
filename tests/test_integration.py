# © VampSecure Studios — VampSecure Labs Security Research Division
"""
Tests de integración para vamp-wp2shell-audit.
Usa aiohttp mock para simular respuestas HTTP de un sitio WordPress.
Verifica detección end-to-end: WP detect → versión → plugins → CVE mapping.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vamp_wp2shell_audit import (
    PLUGIN_VULN_DB,
    VulnMapper,
    WPDetector,
)

# ---------------------------------------------------------------------------
# Test 1: Flujo detect → versión → mapeo CVE end-to-end
# ---------------------------------------------------------------------------

class TestIntegracionDetectYMapeo:
    """Verifica el flujo completo desde HTML hasta findings de CVE."""

    def test_html_wp_581_detecta_version(self, html_wordpress_581, cabeceras_wordpress):
        """Detectar WordPress 5.8.1 del HTML completo."""
        es_wp, version = WPDetector.detect(html_wordpress_581, cabeceras_wordpress)
        assert es_wp is True
        assert version == "5.8.1"

    def test_plugin_vulnerable_genera_findings(self):
        """wp-file-manager 6.8 debe mapear a CVE-2020-25213."""
        findings = VulnMapper.mapear("wp-file-manager", "6.8", PLUGIN_VULN_DB)
        assert len(findings) >= 1
        assert findings[0]["cve"] == "CVE-2020-25213"
        assert findings[0]["severity"] == "CRITICAL"

    def test_plugin_parcheado_no_genera_findings_confirmados(self):
        """wp-file-manager 6.9 (parcheado) no debe tener findings confirmados."""
        findings = VulnMapper.mapear("wp-file-manager", "6.9", PLUGIN_VULN_DB)
        confirmados = [f for f in findings if f.get("version_confirmed") is True]
        assert len(confirmados) == 0

    def test_html_sin_wp_detecta_correctamente(self, html_no_wordpress, cabeceras_vacias):
        """HTML sin WordPress devuelve (False, None)."""
        es_wp, version = WPDetector.detect(html_no_wordpress, cabeceras_vacias)
        assert es_wp is False
        assert version is None

    def test_scan_result_plugin_vulnerable_wordpress(self, scan_result_wordpress):
        """ScanResult con wp-file-manager 6.8 debe mapear a finding CRITICAL."""
        for slug, version in scan_result_wordpress.installed_plugins.items():
            findings = VulnMapper.mapear(slug, version, PLUGIN_VULN_DB)
            scan_result_wordpress.plugin_findings.extend(findings)

        assert len(scan_result_wordpress.plugin_findings) >= 1
        criticos = [f for f in scan_result_wordpress.plugin_findings
                    if f.get("severity") == "CRITICAL"]
        assert len(criticos) >= 1

    def test_version_comparacion_semantica_no_lexicografica(self):
        """9.9 < 10.0 semánticamente — no debe confundirse con comparación de string."""
        v_antigua = VulnMapper._parsear_version("9.9")
        v_nueva = VulnMapper._parsear_version("10.0")
        assert v_nueva > v_antigua

    def test_multiple_plugins_unos_afectados_otros_no(self):
        """Solo los plugins con versión afectada deben generar findings."""
        plugins = {
            "wp-file-manager": "6.8",         # afectado (< 6.9)
            "contact-form-7": "5.9.0",         # no afectado (>= 5.8.4)
            "woocommerce-payments": "5.5.0",   # afectado (< 5.6.2)
        }
        todos_findings = []
        for slug, version in plugins.items():
            todos_findings.extend(VulnMapper.mapear(slug, version, PLUGIN_VULN_DB))

        confirmados = [f for f in todos_findings if f.get("version_confirmed") is True]
        # wp-file-manager y woocommerce-payments afectados → al menos 2
        assert len(confirmados) >= 2
        cves = [f["cve"] for f in confirmados]
        assert "CVE-2020-25213" in cves
        assert "CVE-2023-28121" in cves
