# © VampSecure Studios — VampSecure Labs Security Research Division
"""
Tests unitarios para vamp-wp2shell-audit.
Cubre: WPDetector.detect, WP_VERSION_RE, VulnMapper.mapear,
       VulnMapper._parsear_version, PLUGIN_VULN_DB integridad,
       detección de indicadores, versiones en rango afectado.
"""

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vamp_wp2shell_audit import (
    WPDetector,
    VulnMapper,
    PLUGIN_VULN_DB,
    THEME_VULN_DB,
    WP_VERSION_RE,
)


# ---------------------------------------------------------------------------
# Tests de WPDetector.detect
# ---------------------------------------------------------------------------

class TestWPDetector:
    """Verifica la detección de WordPress a partir de HTML y cabeceras."""

    def test_detecta_wordpress_por_meta_generator(self, html_wordpress_581):
        """El tag meta generator de WordPress debe ser suficiente para detectarlo."""
        es_wp, version = WPDetector.detect(html_wordpress_581, {})
        assert es_wp is True

    def test_extrae_version_de_meta_generator(self, html_wordpress_581):
        """La versión extraída del meta generator debe ser 5.8.1."""
        _, version = WPDetector.detect(html_wordpress_581, {})
        assert version == "5.8.1"

    def test_detecta_wordpress_por_wp_content(self):
        """/wp-content/ en el HTML es suficiente indicador."""
        html = '<link href="/wp-content/themes/test/style.css" />'
        es_wp, _ = WPDetector.detect(html, {})
        assert es_wp is True

    def test_detecta_wordpress_por_wp_includes(self):
        """Script en /wp-includes/ indica WordPress."""
        html = '<script src="/wp-includes/js/jquery.min.js"></script>'
        es_wp, _ = WPDetector.detect(html, {})
        assert es_wp is True

    def test_no_detecta_sitio_no_wp(self, html_no_wordpress, cabeceras_vacias):
        """HTML sin indicadores WordPress debe devolver (False, None)."""
        es_wp, version = WPDetector.detect(html_no_wordpress, cabeceras_vacias)
        assert es_wp is False
        assert version is None

    def test_detecta_por_wp_login_en_html(self):
        """Link a wp-login.php indica WordPress."""
        html = '<a href="/wp-login.php">Acceder</a>'
        es_wp, _ = WPDetector.detect(html, {})
        assert es_wp is True

    def test_version_none_si_no_hay_indicador_version(self):
        """WordPress detectado pero sin versión visible → versión None."""
        html = '<script src="/wp-includes/js/test.js"></script>'
        _, version = WPDetector.detect(html, {})
        # No hay indicador de versión → puede ser None o string vacío
        assert version is None or version == ""


# ---------------------------------------------------------------------------
# Tests de WP_VERSION_RE
# ---------------------------------------------------------------------------

class TestWPVersionRE:
    """Verifica las expresiones regulares de extracción de versión."""

    def test_meta_generator_extrae_version(self):
        """El primer regex debe extraer versión del meta generator."""
        html = '<meta name="generator" content="WordPress 5.8.1" />'
        for rx in WP_VERSION_RE:
            m = rx.search(html)
            if m:
                assert m.group(1) == "5.8.1"
                return
        pytest.fail("Ningún WP_VERSION_RE detectó la versión en meta generator")

    def test_ver_en_css_extrae_version(self):
        """El regex de ?ver= en CSS debe capturar la versión."""
        html = '/wp-includes/css/test.css?ver=6.0.3'
        for rx in WP_VERSION_RE:
            m = rx.search(html)
            if m:
                assert m.group(1) == "6.0.3"
                return
        pytest.fail("Ningún WP_VERSION_RE detectó la versión en URL de CSS")


# ---------------------------------------------------------------------------
# Tests de VulnMapper._parsear_version
# ---------------------------------------------------------------------------

class TestParsearVersion:
    """Verifica la conversión de versiones a tuplas comparables."""

    def test_version_tres_partes(self):
        assert VulnMapper._parsear_version("5.8.1") == (5, 8, 1)

    def test_version_dos_partes(self):
        assert VulnMapper._parsear_version("6.9") == (6, 9)

    def test_version_una_parte(self):
        assert VulnMapper._parsear_version("7") == (7,)

    def test_version_invalida_devuelve_cero(self):
        result = VulnMapper._parsear_version("invalida")
        assert result == (0,)

    def test_comparacion_semantica_correcta(self):
        """10.0 debe ser mayor que 9.0 (comparación semántica, no lexicográfica)."""
        v10 = VulnMapper._parsear_version("10.0")
        v9 = VulnMapper._parsear_version("9.0")
        assert v10 > v9


# ---------------------------------------------------------------------------
# Tests de VulnMapper.mapear
# ---------------------------------------------------------------------------

class TestVulnMapper:
    """Verifica el mapeo de plugins/temas a CVEs según versión."""

    def test_version_afectada_produce_finding(self):
        """wp-file-manager 6.8 está afectado por CVE-2020-25213 (< 6.9)."""
        findings = VulnMapper.mapear("wp-file-manager", "6.8", PLUGIN_VULN_DB)
        assert len(findings) >= 1
        cves = [f["cve"] for f in findings]
        assert "CVE-2020-25213" in cves

    def test_version_no_afectada_no_produce_finding(self):
        """wp-file-manager >= 6.9 no está afectado."""
        findings = VulnMapper.mapear("wp-file-manager", "6.9", PLUGIN_VULN_DB)
        confirmados = [f for f in findings if f.get("version_confirmed") is True]
        assert len(confirmados) == 0

    def test_version_none_produce_finding_no_confirmado(self):
        """Plugin detectado sin versión → finding version_confirmed=False."""
        findings = VulnMapper.mapear("wp-file-manager", None, PLUGIN_VULN_DB)
        assert len(findings) >= 1
        assert all(f["version_confirmed"] is False for f in findings)

    def test_slug_inexistente_retorna_lista_vacia(self):
        """Slug que no está en la BD → lista vacía."""
        findings = VulnMapper.mapear("plugin-inexistente", "1.0", PLUGIN_VULN_DB)
        assert findings == []

    def test_contact_form_7_afectado_por_cve_2023_6449(self):
        """contact-form-7 < 5.8.4 afectado."""
        findings = VulnMapper.mapear("contact-form-7", "5.8.3", PLUGIN_VULN_DB)
        assert any(f["cve"] == "CVE-2023-6449" for f in findings)

    def test_contact_form_7_parcheado_no_afectado(self):
        """contact-form-7 >= 5.8.4 no afectado."""
        findings = VulnMapper.mapear("contact-form-7", "5.8.4", PLUGIN_VULN_DB)
        confirmados = [f for f in findings if f.get("version_confirmed") is True]
        assert len(confirmados) == 0

    def test_woocommerce_payments_cvss_98(self):
        """CVE-2023-28121 debe tener CVSS 9.8."""
        findings = VulnMapper.mapear("woocommerce-payments", "5.6.0", PLUGIN_VULN_DB)
        assert any(f["cvss"] == 9.8 for f in findings)

    def test_tema_jupiter_afectado(self):
        """jupiter < 6.10.2 → CVE-2022-1654."""
        findings = VulnMapper.mapear("jupiter", "6.10.1", THEME_VULN_DB)
        assert any(f["cve"] == "CVE-2022-1654" for f in findings)


# ---------------------------------------------------------------------------
# Tests de integridad de PLUGIN_VULN_DB
# ---------------------------------------------------------------------------

class TestPluginVulnDBIntegridad:
    """Verifica la estructura de la base de datos de vulnerabilidades."""

    def test_wp_file_manager_tiene_cve(self):
        assert "wp-file-manager" in PLUGIN_VULN_DB
        entry = PLUGIN_VULN_DB["wp-file-manager"][0]
        assert "cve" in entry
        assert entry["cve"] == "CVE-2020-25213"

    def test_todos_los_entries_tienen_cvss(self):
        """Cada entrada debe tener un campo cvss numérico."""
        for slug, vulns in PLUGIN_VULN_DB.items():
            for vuln in vulns:
                assert "cvss" in vuln, f"Falta cvss en {slug}"
                assert isinstance(vuln["cvss"], (int, float))

    def test_todos_los_entries_tienen_severity(self):
        """Cada entrada debe tener severity válida."""
        niveles_validos = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        for slug, vulns in PLUGIN_VULN_DB.items():
            for vuln in vulns:
                assert vuln.get("severity") in niveles_validos

    def test_contiene_al_menos_5_plugins(self):
        assert len(PLUGIN_VULN_DB) >= 5
