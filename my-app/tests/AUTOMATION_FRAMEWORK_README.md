# INVISAP - Framework de Automatización de Pruebas con Evidencia

Este documento describe el framework completo de automatización de pruebas para el sistema INVISAP (Sistema de Gestión e Información para el Seguimiento y Control de Solicitudes con módulo de Análisis y Priorización), implementado según los requisitos del Capítulo IV y V del Informe del Sistema INVILARA - Proyecto III.

## 📋 Resumen de Características

- **7 tipos de pruebas**: Unidad, Integración, API/Backend, Humo, Interfaz (UI), Rendimiento, Aceptación
- **Evidencia automática**: Capturas de pantalla, reportes HTML, JSON, CSV organizados por matriz de trazabilidad
- **Nomenclatura estructurada**: `tipoPrueba_modulo_IDcaso_nombrePrueba_resultado_timestamp.ext`
- **CI/CD integrado**: GitHub Actions con artifacts de evidencia (30-90 días de retención)
- **Trazabilidad completa**: Vinculación automática con Matriz_Trazabilidad_Pruebas_INVISAP.docx
- **Generación de informes**: Word consolidado para Capítulo IV y V

## 🏗️ Estructura del Proyecto

```
tests/
├── conftest.py                      # Configuración pytest + fixtures + hooks de evidencia
├── evidence_organizer.py            # Organizador de evidencia por matriz de trazabilidad
├── generate_consolidated_report.py  # Generador de informe Word Capítulo IV & V
├── evidence/                        # Directorio base de evidencia (auto-generado)
│   ├── unit/                        # Pruebas unitarias
│   ├── integration/                 # Pruebas de integración
│   ├── api/                         # Pruebas API (pytest + Postman)
│   ├── smoke/                       # Pruebas de humo
│   ├── ui/                          # Capturas Playwright/Selenium
│   ├── performance/                 # Reportes Locust
│   ├── acceptance/                  # Pruebas de aceptación
│   ├── organized/                   # Evidencia organizada por trazabilidad
│   └── evidence_summary.json        # Resumen consolidado
├── unit/                            # 20 suites + 3 transversales (427 casos)
├── integration/                     # 20 contratos + 2 flujos (22 casos)
├── api/                             # 20 suites + parametrización (33 casos)
├── smoke/                           # 20 módulos + acceso (21 casos)
├── ui/                              # Playwright + Selenium (1 caso actual)
├── performance/                     # 20 escenarios Locust
│   ├── locust_with_evidence.py      # Locust con captura de evidencia
│   └── run_performance.py           # Ejecutor de rendimiento
├── api/
│   └── postman_evidence_capture.py  # Postman/Newman con evidencia
└── documentation/
    ├── generate_traceability_matrix.py
    └── Matriz_Trazabilidad_Pruebas_INVISAP.docx
```

## 🎯 Nomenclatura de Evidencia

Todos los archivos siguen el patrón: **`tipoPrueba_modulo_IDcaso_nombrePrueba_resultado_timestamp.ext`**

| Tipo de Prueba | Prefijo | Ejemplo |
|----------------|---------|---------|
| Unidad | `unit` | `unit_Solicitudes_CP-UNI-RF01-01_test_crear_solicitud_PASSED_20261120_103000.png` |
| Integración | `integration` | `integration_GravedadObra_CP-INT-RF02-01_test_contrato_ruta_PASSED_20261120_103005.html` |
| API/Backend | `api` | `api_Solicitudes_CP-API-RF01-01_test_api_listar_PASSED_20261120_103010.json` |
| Humo | `smoke` | `smoke_Usuarios_CP-HUM-RF04-01_test_humo_usuarios_PASSED_20261120_103015.png` |
| Interfaz (UI) | `ui` | `ui_Login_CP-UI-RNF01_test_formulario_acceso_FAILED_20261120_103020.png` |
| Rendimiento | `performance` | `performance_Solicitudes_CP-LOC-RF01_locust_solicitudes_PASSED_20261120_103025.html` |
| Postman | `api` | `api_Solicitudes_CP-POST-RF01_postman_solicitudes_PASSED_20261120_103030.json` |
| Aceptación | `acceptance` | `acceptance_Solicitudes_CP-ACE-RF01_test_flujo_completo_PASSED_20261120_103035.pdf` |

## 🚀 Ejecución Local

### Prerrequisitos
```bash
# Instalar dependencias
pip install -r tests/requirements-test.txt
pip install -r tests/performance/requirements.txt
pip install playwright pytest-html pytest-json-report python-docx
playwright install chromium
playwright install-deps chromium

# Para Postman/Newman
npm install -g newman newman-reporter-htmlextra
```

### Ejecutar todas las pruebas con evidencia
```bash
# Desde el directorio my-app
cd C:\laragon\www\INVISAP\my-app

# Pruebas unitarias
python -m pytest tests/unit -v --html=tests/evidence/unit/report.html --self-contained-html

# Pruebas de integración
python -m pytest tests/integration -v --html=tests/evidence/integration/report.html --self-contained-html

# Pruebas API
python -m pytest tests/api -v --html=tests/evidence/api/report.html --self-contained-html

# Pruebas de humo
python -m pytest tests/smoke -v --html=tests/evidence/smoke/report.html --self-contained-html

# Pruebas UI (requiere INVISAP_TEST_URL)
set INVISAP_TEST_URL=http://localhost:5600
python -m pytest tests/ui -v --html=tests/evidence/ui/report.html --self-contained-html

# Pruebas de rendimiento
python tests/performance/run_performance.py --all --profile quick

# Postman/Newman
python tests/api/postman_evidence_capture.py --base-url http://localhost:5600
```

### Organizar evidencia por trazabilidad
```bash
python tests/evidence_organizer.py --evidence-dir tests/evidence --matrix tests/documentation/Matriz_Trazabilidad_Pruebas_INVISAP.docx
```

### Generar informe consolidado (Capítulo IV & V)
```bash
python tests/generate_consolidated_report.py --evidence-dir tests/evidence --matrix tests/documentation/Matriz_Trazabilidad_Pruebas_INVISAP.docx --output tests/evidence/Informe_Consolidado_Capitulo_IV_V.docx
```

## 🔄 CI/CD - GitHub Actions

El workflow `.github/workflows/test-with-evidence.yml` ejecuta automáticamente:

1. **Setup**: Python, Playwright, Newman, dependencias
2. **Jobs paralelos**: Unit, Integration, API, Smoke, UI, Performance
3. **Organización**: Evidencia organizada por matriz de trazabilidad
4. **Informe**: Generación de Word consolidado Capítulo IV & V
5. **Artifacts**: Evidencia por tipo (30 días) + Organizada/Informe (90 días)
6. **PR Summary**: Resumen automático en Pull Requests

### Disparadores
- Push a `main`, `develop`, `release/*`
- Pull Request a `main`, `develop`
- Manual (`workflow_dispatch`) con selección de tipo de prueba

### Variables de Entorno
| Variable | Descripción | Por Defecto |
|----------|-------------|-------------|
| `INVISAP_TEST_URL` | URL base para pruebas UI | `http://localhost:5600` |
| `INVISAP_PERF_SESSION_COOKIE` | Cookie de sesión para Locust | (vacío) |

## 📊 Matriz de Trazabilidad

El framework mapea automáticamente cada caso de prueba a su ID en la matriz:

| Requisito | Módulo | IDs de Caso de Prueba |
|-----------|--------|----------------------|
| RF-01 | Solicitudes | CP-UNI-RF01-01..43, CP-INT-RF01-01, CP-API-RF01-01, CP-POST-RF01-01, CP-HUM-RF01-01 |
| RF-02 | Gravedad de Obra | CP-UNI-RF02-01..11, CP-INT-RF02-01, CP-API-RF02-01, CP-POST-RF02-01, CP-HUM-RF02-01 |
| RF-03 | Prioridad | CP-UNI-RF03-01..31, CP-INT-RF03-01, CP-API-RF03-01, CP-POST-RF03-01, CP-HUM-RF03-01 |
| ... | ... | ... |
| RNF-10 | Rendimiento | CP-LOC-RNF10-01 (no concluyente) |

Total: **525 IDs de caso de prueba** en la matriz (incluyendo rangos expandidos).

## 📁 Evidencia Generada por Ejecución

Al ejecutar el pipeline completo, se genera:

```
tests/evidence/
├── unit/report_unit.html + screenshots/
├── integration/report_integration.html + screenshots/
├── api/report_api.html + postman_evidence/
├── smoke/report_smoke.html
├── ui/report_ui.html + playwright_login_PASSED/FAILED.png
├── performance/locust_report_*.html + locust_stats_*.csv + JSON evidence/
├── organized/
│   ├── unit/Solicitudes/CP-UNI-RF01-01_*.png
│   ├── integration/GravedadObra/CP-INT-RF02-01_*.html
│   ├── api/Solicitudes/CP-API-RF01-01_*.json
│   ├── ui/Login/CP-UI-RNF01_*.png
│   └── performance/Solicitudes/CP-LOC-RF01_*.html
├── evidence_summary.json
├── traceability_coverage_report_*.json
├── organization_report_*.json
└── Informe_Consolidado_Capitulo_IV_V.docx
```

## 🔧 Configuración Avanzada

### Agregar nuevos casos de prueba con evidencia automática

1. **Crear test en el directorio correspondiente** (`tests/unit/`, `tests/ui/`, etc.)
2. **Nombrar la función de test** siguiendo el patrón: `test_modulo_funcionalidad`
3. **El framework extrae automáticamente** el tipo, módulo y ID de caso del nombre

### Personalizar mapeo de trazabilidad

Editar `TRACEABILITY_MAP` en `tests/conftest.py`:

```python
TRACEABILITY_MAP = {
    "test_mi_nuevo_test": ("unit", "Mi Modulo", "CP-UNI-RFXX-XX"),
    # ...
}
```

### Configurar Selenium (alternativa a Playwright)

```python
# En conftest.py, el fixture `driver` ya está disponible
def test_con_selenium(driver):
    driver.get("http://localhost:5600/login")
    # La captura automática funciona igual que Playwright
```

## 📝 Informe Generado - Contenido

El `Informe_Consolidado_Capitulo_IV_V.docx` incluye:

### Capítulo IV
- 4.1 Plan de Pruebas (Objetivo, Alcance, Metodología, Organización, Planificación, Criterios)
- 4.2 Bitácora de Pruebas (Datos, Resultados, Por Módulo, Rendimiento, Casos Representativos, Experiencia)
- 4.3 Plan de Instalación (Registro, Procedimiento, Registro de Instalación)
- 4.4 Plan de Capacitación (Estado, Agenda, Recursos, Registro)
- 4.5 Evidencia Automatizada y Trazabilidad (Nomenclatura, Estructura, CI/CD)

### Capítulo V
- 8 Recomendaciones priorizadas con plazos
- Evolución previsible (Corto/Mediano/Largo plazo)
- Resumen de evidencia generada
- Cobertura de trazabilidad
- Referencias metodológicas

## ✅ Checklist de Validación

- [ ] Ejecutar `python -m pytest tests/unit` → 427 passed
- [ ] Ejecutar `python -m pytest tests/integration` → 22 passed
- [ ] Ejecutar `python -m pytest tests/api` → 33 passed
- [ ] Ejecutar `python -m pytest tests/smoke` → 21 passed
- [ ] Configurar `INVISAP_TEST_URL` y ejecutar `tests/ui` → 1 passed + screenshot
- [ ] Ejecutar `python tests/performance/run_performance.py --all --profile quick`
- [ ] Ejecutar Postman/Newman con `postman_evidence_capture.py`
- [ ] Ejecutar `evidence_organizer.py` → evidencia organizada en `organized/`
- [ ] Ejecutar `generate_consolidated_report.py` → Word generado
- [ ] Verificar artifacts en GitHub Actions después de push

## 📞 Soporte

Para dudas sobre el framework:
- Revisar `tests/README.md` para detalles técnicos
- Consultar `tests/conftest.py` para hooks y fixtures
- Ver `.github/workflows/test-with-evidence.yml` para CI/CD
- Documentación de pytest, Playwright, Locust, Newman

---

**Versión**: 1.0 | **Fecha**: Noviembre 2026 | **Proyecto**: INVISAP - Trayecto III