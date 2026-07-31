# vamp-wp2shell-audit

**VampSecure Labs — Security Research Division**  
Auditor de seguridad para instalaciones WordPress: plugins vulnerables, vectores de upload y exposición de superficie.

---

## Descripción

Herramienta de auditoría pasiva y semi-activa para evaluar la seguridad de instalaciones
WordPress. Analiza plugins y temas instalados, detecta versiones vulnerables mediante
fingerprinting, y evalúa vectores de subida de archivos sin ejecutar código malicioso.

Utiliza AsyncIO y aiohttp para análisis concurrente de múltiples sitios. Incluye un módulo
opcional de canary upload (inerte, auto-eliminación) para validar controles de tipo MIME.

## Capacidades de análisis

- Detección de 10 plugins vulnerables (`PLUGIN_VULN_DB`) y 2 temas (`THEME_VULN_DB`)
- Fingerprinting por `readme.txt` / `style.css` (Stable tag)
- Evaluación de XML-RPC, REST API (`/wp-json/wp/v2/users`)
- Detección de directorio de uploads abierto
- Comprobación de `WP_DEBUG` habilitado
- Sondas SQLi básicas en parámetros públicos
- Canary Uploader: PHP inerte + MIME spoofed + auto-borrado vía REST API DELETE

## Requisitos

- Python 3.9+
- Dependencias: `aiohttp>=3.9.0`, `rich>=13.7.0`

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Auditar un único sitio WordPress
python3 vamp_wp2shell_audit.py https://misitio.com

# Auditar múltiples sitios desde fichero
python3 vamp_wp2shell_audit.py -f scope.txt

# Con canary upload y generación de informes
python3 vamp_wp2shell_audit.py https://misitio.com --canary --output-json resultado.json --output-html resultado.html
```

## Opciones

| Opción | Descripción |
|--------|-------------|
| `target` | URL del sitio WordPress objetivo |
| `-f / --file` | Fichero con lista de objetivos |
| `--concurrency` | Peticiones concurrentes (por defecto: 5) |
| `--timeout` | Timeout por petición en segundos (por defecto: 15) |
| `--canary` | Activar canary upload (requiere permisos de subida) |
| `--output-json` | Guardar resultados en JSON |
| `--output-html` | Guardar informe en HTML |
| `--no-verify-ssl` | Deshabilitar verificación TLS |

## Base de datos de vulnerabilidades

La herramienta incluye una base de datos local de plugins y temas con CVEs documentados,
niveles de riesgo (CRÍTICO/ALTO/MEDIO) y notas de explotación. Se actualiza manualmente
con cada nueva versión de la herramienta.

## Aviso legal

**Uso exclusivo en sistemas de tu propiedad o con autorización escrita del propietario.**  
El canary upload activa una petición de escritura real en el servidor objetivo. Úsalo solo
en entornos de test o con autorización explícita. VampSecure Studios no se responsabiliza
del uso indebido de esta herramienta.

---

© VampSecure Studios — VampSecure Labs Security Research Division  
Licencia: MIT
