# Guía de Interpretación de Resultados de Pruebas INVISAP

Esta guía explica paso a paso cómo leer los resultados de cada tipo de prueba, qué significa cada salida en consola y cómo tomar capturas de pantalla como evidencia.

---

## 1. Preparación del Entorno

### 1.1 Instalar dependencias
```powershell
# Desde la carpeta my-app
.venv\Scripts\Activate.ps1
python -m pip install -r tests\requirements-test.txt
python -m playwright install chromium
```

### 1.2 Iniciar la aplicación (requerido para UI, Aceptación, Rendimiento, Postman)
```powershell
# Terminal 1
python run.py
# La app escucha en http://127.0.0.1:5600
```

### 1.3 Configurar variables de entorno (para UI, Locust, Postman)
```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
$env:INVISAP_PERF_SESSION_COOKIE = "session=COOKIE_DE_PRUEBA"  # Solo para Locust
```

---

## 2. Pruebas Unitarias (tests\unit)

### 2.1 Qué validan
- Lógica aislada, validaciones y modelos
- Usan "dobles de prueba" (mocks) para no necesitar base de datos real
- 36 archivos, uno por módulo + transversales

### 2.2 Comando individual por módulo
```powershell
python -m pytest tests\unit\test_usuarios.py -v
python -m pytest tests\unit\test_gravedad_obra.py -v
# ... sustituye el nombre del archivo según la tabla del README
```

### 2.3 Comando para todas las unitarias
```powershell
python -m pytest tests\unit -v
```

### 2.4 Cómo leer la salida en consola

**Durante la ejecución (pytest_runtest_setup):**
```
[PRUEBA UNITARIA] Usuarios: limpieza segura del nombre del archivo de respaldo.
[PRUEBA UNITARIA] Usuarios: validación y limpieza del nombre y cargo del empleado.
```

**Al concluir cada caso (pytest_runtest_logreport):**
```
Concluyó prueba de Usuarios — Tipo: Prueba unitaria — Resultado: APROBADA.
Concluyó prueba de Usuarios — Tipo: Prueba unitaria — Resultado: FALLIDA.
Concluyó prueba de Usuarios — Tipo: Prueba unitaria — Resultado: OMITIDA.
```

**Resumen final (pytest_terminal_summary):**
```
================================= RESUMEN DE PRUEBAS UNITARIAS POR MÓDULO =================================
Concluyó prueba de Usuarios — Tipo: Prueba unitaria — APROBADA: 12 aprobadas, 0 fallidas, 0 omitidas.
Concluyó prueba de Empleados — Tipo: Prueba unitaria — REVISAR: 8 aprobadas, 1 fallidas, 0 omitidas.
```

### 2.5 Qué buscar para evidencia
- **APROBADA**: Todas las aserciones pasaron ✓
- **FALLIDA**: Revisar el traceback (línea de código, valor esperado vs obtenido)
- **OMITIDA**: Marcada con `@pytest.mark.skip` o condicional
- **REVISAR en resumen**: Hay al menos una fallida u omitida en ese módulo

### 2.6 Captura de pantalla sugerida
- Pantalla completa de la terminal mostrando el resumen final
- Si hay fallos, capturar el traceback completo de cada fallo

---

## 3. Pruebas de Integración (tests\integration)

### 3.1 Qué validan
- Contratos de rutas Flask: regla, endpoint, método HTTP, generación de URL
- No ejecutan peticiones reales ni sustituyen pruebas con BD real
- 20 archivos (uno por módulo) + `test_contrataciones_bitacora.py`

### 3.2 Comando individual por módulo
```powershell
python -m pytest tests\integration\test_integracion_usuarios.py -v
python -m pytest tests\integration\test_integracion_solicitudes.py -v
```

### 3.3 Comando para todas
```powershell
python tests\integration\run_all_integration.py
```

### 3.4 Cómo leer la salida

**Durante la ejecución:**
```
[PRUEBA DE INTEGRACIÓN] Inspecciones: comprobando la ruta Flask, el endpoint, el método HTTP y la generación de URL.
```

**Al concluir:**
```
Concluyó prueba de Inspecciones — Tipo: Prueba de integración — Resultado: APROBADA.
```

**Resumen final:**
```
================================= RESUMEN DE PRUEBAS DE INTEGRACIÓN POR MÓDULO =================================
Concluyó prueba de Inspecciones — Tipo: Prueba de integración — APROBADA: 1 aprobadas, 0 fallidas, 0 omitidas.
```

### 3.5 Qué buscar para evidencia
- Cada módulo tiene 1 prueba que verifica el contrato de ruta
- **APROBADA**: El endpoint existe, método correcto, URL genera bien
- **FALLIDA**: Ruta no registrada, método incorrecto, o nombre de endpoint erróneo

---

## 4. Pruebas de Backend/API (tests\api)

### 4.1 Qué validan
- Endpoints HTTP del backend (caja negra)
- Cliente de pruebas Flask + dependencias simuladas
- Verifican: respuestas JSON, códigos HTTP, control de sesión, autorización, propagación de filtros
- 20 archivos + `test_parametrizacion_reportes.py`

### 4.2 Comando individual por módulo
```powershell
python -m pytest tests\api\test_api_usuarios.py -v
python -m pytest tests\api\test_api_solicitudes.py -v
python -m pytest tests\api\test_api_reportes_pdf.py -v
```

### 4.3 Comando para todas (20 módulos + parametrización)
```powershell
python tests\api\run_all_api.py
```

### 4.4 Cómo leer la salida

**Durante la ejecución:**
```
[PRUEBA DE BACKEND/API] Usuarios: comprobando autenticación, permiso y usuario inexistente.
[PRUEBA DE BACKEND/API] Solicitudes: comprobando JSON autenticado y control de sesión.
[PRUEBA DE BACKEND/API] Reportes PDF: comprobando autenticación y módulo no válido.
```

**Al concluir:**
```
Concluyó prueba de Usuarios — Tipo: Prueba de backend (API) — Resultado: APROBADA.
Concluyó prueba de Solicitudes — Tipo: Prueba de backend (API) — Resultado: APROBADA.
```

**Resumen final:**
```
================================= RESUMEN DE PRUEBAS DE BACKEND/API POR MÓDULO =================================
Concluyó prueba de Usuarios — Tipo: Prueba de backend (API) — APROBADA: 2 aprobadas, 0 fallidas, 0 omitidas.
Concluyó prueba de Solicitudes — Tipo: Prueba de backend (API) — APROBADA: 3 aprobadas, 0 fallidas, 0 omitidas.
```

### 4.5 Qué buscar para evidencia
- **Módulos normales**: Pruebas de endpoints JSON (GET/POST) con sesión simulada
- **Reportes PDF/Excel**: Reciben formularios HTTP (no JSON); pruebas verifican autenticación y rechazo de módulos inválidos
- **Parametrización**: Verifica propagación de filtros de formularios a reportes

### 4.6 Captura de pantalla sugerida
- Terminal con resumen final de `run_all_api.py`
- Para módulos individuales: salida completa con todos los casos

---

## 5. Pruebas de Humo / Smoke (tests\smoke)

### 5.1 Qué validan
- Disponibilidad básica de ruta (no 404 ni 500)
- Redirección 302 se considera válida (acceso protegido)
- No prueban funcionalidad completa ni sesión/BD real
- 20 archivos + `test_login_smoke.py`

### 5.2 Comando individual por módulo
```powershell
python -m pytest tests\smoke\test_humo_usuarios.py -v
python -m pytest tests\smoke\test_login_smoke.py -v
```

### 5.3 Comando para todas (21 módulos)
```powershell
python tests\smoke\run_all_smoke.py
```

### 5.4 Cómo leer la salida

**Durante la ejecución (login):**
```
[PRUEBA DE HUMO] Acceso de INVISAP: solicitando GET /login y comprobando HTTP 200 y ausencia de aviso de sesión incorrecto.
```

**Durante la ejecución (otros módulos):**
```
[PRUEBA DE HUMO] Usuarios: solicitando GET /usuarios y comprobando que no responda HTTP 404 ni 500.
```

**Al concluir:**
```
Concluyó prueba de Acceso de INVISAP — Tipo: Prueba de humo (smoke) — Resultado: APROBADA.
Concluyó prueba de Usuarios — Tipo: Prueba de humo (smoke) — Resultado: APROBADA.
```

**Resumen final:**
```
================================= RESUMEN DE PRUEBAS DE HUMO POR MÓDULO =================================
Concluyó prueba de Acceso de INVISAP — Tipo: Prueba de humo (smoke) — APROBADA: 1 aprobadas, 0 fallidas, 0 omitidas.
Concluyó prueba de Usuarios — Tipo: Prueba de humo (smoke) — APROBADA: 1 aprobadas, 0 fallidas, 0 omitidas.
```

### 5.5 Qué buscar para evidencia
- **APROBADA**: Ruta responde (200, 302, etc.) y no es 404/500
- **FALLIDA**: Ruta devuelve 404 (no existe) o 500 (error servidor)
- **Nota**: 302 (redirección a login) = APROBADA en smoke

---

## 6. Pruebas de Interfaz / UI (tests\ui)

### 6.1 Qué validan
- Navegador real con Playwright (Chromium headless)
- Visual: formulario se muestra, campos presentes, etiquetas, tipo password
- Usabilidad: labels asociados, campos required, botón visible

### 6.2 Requisitos previos
```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
# App debe estar corriendo en run.py
```

### 6.3 Comando
```powershell
python -m pytest tests\ui -v
```

### 6.4 Cómo leer la salida

**Caso 1 - Formulario se muestra:**
```
tests\ui\test_login_ui.py::test_formulario_de_acceso_se_muestra_en_el_navegador PASSED
```

**Caso 2 - Usabilidad (etiquetas y acciones):**
```
tests\ui\test_login_ui.py::test_formulario_de_acceso_tiene_etiquetas_y_acciones_comprensibles PASSED
```

**Si se omite (sin URL o sin Playwright):**
```
tests\ui\test_login_ui.py::test_formulario_de_acceso_se_muestra_en_el_navegador SKIPPED
```

### 6.5 Archivo de evidencia automático
- Playwright guarda captura en: `tmp_path/playwright_login.png` (ruta temporal)
- Para capturar manualmente: agregar `page.screenshot(path="evidencia_login.png", full_page=True)` en el test

### 6.6 Qué buscar para evidencia
- **PASSED**: Página carga, formulario visible, ≥2 inputs, sin mensaje de error
- **Usabilidad PASSED**: Labels "Usuario" y "Clave de Acceso" visibles, required, type=password, botón "Iniciar Sesión"
- **SKIPPED**: Falta `INVISAP_TEST_URL` o Playwright/Chromium no instalado

---

## 7. Pruebas de Aceptación (tests\acceptance)

### 7.1 Qué validan
- Recorridos completos según criterios de negocio
- Login + consulta autorizada en un flujo real

### 7.2 Comando
```powershell
python -m pytest tests\acceptance -v
```

### 7.3 Cómo leer la salida
```
tests\acceptance\test_login_acceptance.py::test_usuario_inicia_sesion_y_consulta_solicitudes_autorizadas PASSED
```

### 7.4 Qué valida el caso actual
1. GET /login → 200
2. POST /login con credenciales + recaptcha → 302 (redirección)
3. Sesión tiene `conectado=True` y `name_surname` correcto
4. GET /api/obtener-solicitudes-json → 200 + JSON esperado

### 7.5 Captura de pantalla sugerida
- Terminal con el test PASSED
- Opcional: capturar en Postman el flujo completo

---

## 8. Pruebas de Rendimiento / Performance (tests\performance)

### 8.1 Qué validan
- Carga HTTP con Locust (NO pytest, NO interfaz visual)
- Endpoints de solo lectura por módulo
- Métricas: req/s, latencia (promedio, mediano, p95), fallos HTTP

### 8.2 Requisitos previos
```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
$env:INVISAP_PERF_SESSION_COOKIE = "session=COOKIE_DE_PRUEBA"
# Variables opcionales para IDs específicos (ver performance/README.md)
```

### 8.3 Comando individual por módulo (perfil quick = verificación rápida)
```powershell
python tests\performance\run_performance.py --module usuarios --profile quick
python tests\performance\run_performance.py --module solicitudes --profile quick
```

### 8.4 Comando para todos los módulos
```powershell
# Verificación rápida (1 usuario, 5 seg por módulo)
python tests\performance\run_performance.py --all --profile quick

# Carga de referencia (5 usuarios, 30 seg por módulo)
python tests\performance\run_performance.py --all --profile baseline
```

### 8.5 Interfaz web de Locust (manual)
```powershell
locust -f tests\performance\locust_usuarios.py --host http://127.0.0.1:5600
# Abrir http://127.0.0.1:8089
# Configurar usuarios y tasa, pulsar "Start swarming"
```

### 8.6 Cómo leer la salida (ejecutor run_performance.py)

**Durante ejecución:**
```
[PRUEBA DE RENDIMIENTO] Usuarios: consultando /api/users/1 (consulta de detalle de usuario)
```

**Al concluir módulo:**
```
Concluyó prueba de Usuarios — Tipo: Prueba de rendimiento — Resultado: APROBADA.
```

**Resumen final (también en results/bitacora_rendimiento.csv):**
```
Módulo          | Endpoint                    | Reqs  | Fallos | Req/s | Avg(ms) | Med(ms) | P95(ms)
Usuarios        | /api/users/1                | 50    | 0      | 10.2  | 45      | 42      | 78
Solicitudes     | /api/obtener-solicitudes-json| 150  | 0      | 5.1   | 120     | 115     | 210
```

### 8.7 Qué buscar para evidencia
- **CSV generado**: `results/bitacora_rendimiento.csv` + CSVs individuales en `results/`
- **Tabla actualizada**: `CAPITULO_IV_INVISAP.md` (se actualiza automáticamente)
- **Captura sugerida**: Terminal con tabla final + archivo CSV abierto en Excel

### 8.8 Perfiles disponibles
| Perfil | Usuarios | Duración | Uso |
|--------|----------|----------|-----|
| quick | 1 | 5s | Verificación conectividad |
| baseline | 5 | 30s | Carga de referencia |
| stress | 20 | 60s | Solo entorno preparado |
| spike | 30 (inmediato) | 30s | Solo entorno preparado |

---

## 9. Pruebas de Seguridad

### 9.1 Inyección SQL (Caja blanca)
```powershell
python -m pytest tests\unit\test_sql_filter_allowlists.py -v
python -m pytest tests\unit\test_security_controls.py -v
```
- Verifican listas permitidas y parametrización SQL sin modificar datos

### 9.2 Seguridad estática (Bandit)
```powershell
bandit -r app.py controllers models routers services -ll
```
- Detecta patrones sospechosos en código Python
- Revisar cada hallazgo antes de clasificar como vulnerabilidad

### 9.3 Regresiones de sesión/autorización (Caja negra)
```powershell
python -m pytest tests\api\test_api_permisos_por_rol.py tests\api\test_api_usuarios.py tests\unit\test_sql_filter_allowlists.py -v
```

### 9.4 Postman (Pruebas de contrato HTTP)
Ver sección **Postman** en `GUIA_EJECUCION_PRUEBAS.md`:
1. Importar colección `postman\collections\INVISAP - Pruebas de Contrato HTTP`
2. Configurar entorno `INVISAP pruebas` con `baseUrl=http://127.0.0.1:5600`
3. Definir variables: `login_username`, `login_password`, `recaptcha_token`, IDs de prueba
4. Ejecutar: "Acceso API sin sesión" → "Login" → Consultas protegidas
5. **Evidencia**: Pestaña **Test Results** en Postman (guardar sin contraseñas/cookies)

---

## 10. Tabla Resumen de Comandos por Tipo

| Tipo | Comando Individual | Comando Todo | Herramienta |
|------|-------------------|--------------|-------------|
| Unitarias | `pytest tests\unit\test_<modulo>.py` | `pytest tests\unit` | pytest |
| Integración | `pytest tests\integration\test_integracion_<modulo>.py` | `python tests\integration\run_all_integration.py` | pytest |
| Backend/API | `pytest tests\api\test_api_<modulo>.py` | `python tests\api\run_all_api.py` | pytest |
| Humo | `pytest tests\smoke\test_humo_<modulo>.py` | `python tests\smoke\run_all_smoke.py` | pytest |
| Interfaz | `pytest tests\ui` | `pytest tests\ui` | Playwright |
| Aceptación | `pytest tests\acceptance` | `pytest tests\acceptance` | pytest |
| Rendimiento | `python tests\performance\run_performance.py --module <modulo> --profile quick` | `python tests\performance\run_performance.py --all --profile baseline` | Locust |
| Seguridad SQL | `pytest tests\unit\test_sql_filter_allowlists.py` | - | pytest |
| Estática | `bandit -r app.py controllers models routers services -ll` | - | Bandit |
| Postman | Colección Postman manual | - | Postman |

---

## 11. Módulos Disponibles (20 módulos de negocio)

| Módulo | Archivo Unitario | Archivo Integración | Archivo API | Archivo Humo | Archivo Performance |
|--------|------------------|---------------------|-------------|--------------|---------------------|
| Solicitudes | test_solicitudes.py | test_integracion_solicitudes.py | test_api_solicitudes.py | test_humo_solicitudes.py | locust_solicitudes.py |
| Gravedad de Obra | test_gravedad_obra.py | test_integracion_gravedad_obra.py | test_api_gravedad_obra.py | test_humo_gravedad_obra.py | locust_gravedad_obra.py |
| Prioridad | test_prioridad.py | test_integracion_prioridad.py | test_api_prioridad.py | test_humo_prioridad.py | locust_prioridad.py |
| Proyectos | test_proyectos.py | test_integracion_proyectos.py | test_api_proyectos.py | test_humo_proyectos.py | locust_proyectos.py |
| Maquinaria | test_maquinaria.py | test_integracion_maquinaria.py | test_api_maquinaria.py | test_humo_maquinaria.py | locust_maquinaria.py |
| Contratación | test_contratacion.py | test_integracion_contratacion.py | test_api_contratacion.py | test_humo_contratacion.py | locust_contratacion.py |
| Empresa | test_empresa.py | test_integracion_empresa.py | test_api_empresa.py | test_humo_empresa.py | locust_empresa.py |
| Obras | test_obras.py | test_integracion_obras.py | test_api_obras.py | test_humo_obras.py | locust_obras.py |
| Empleados | test_empleados.py | test_integracion_empleados.py | test_api_empleados.py | test_humo_empleados.py | locust_empleados.py |
| Inspecciones | test_inspecciones.py | test_integracion_inspecciones.py | test_api_inspecciones.py | test_humo_inspecciones.py | locust_inspecciones.py |
| Evidencias | test_evidencias.py | test_integracion_evidencias.py | test_api_evidencias.py | test_humo_evidencias.py | locust_evidencias.py |
| Informe de Avance | test_informe_avance.py | test_integracion_informe_avance.py | test_api_informe_avance.py | test_humo_informe_avance.py | locust_informe_avance.py |
| Publicaciones | test_publicaciones.py | test_integracion_publicaciones.py | test_api_publicaciones.py | test_humo_publicaciones.py | locust_publicaciones.py |
| Reportes PDF | test_reportes_pdf.py | test_integracion_reportes_pdf.py | test_api_reportes_pdf.py | test_humo_reportes_pdf.py | locust_reportes_pdf.py |
| Reportes Excel | test_reportes_excel.py | test_integracion_reportes_excel.py | test_api_reportes_excel.py | test_humo_reportes_excel.py | locust_reportes_excel.py |
| Reportes Estadísticos | test_reportes_estadisticos.py | test_integracion_reportes_estadisticos.py | test_api_reportes_estadisticos.py | test_humo_reportes_estadisticos.py | locust_reportes_estadisticos.py |
| Usuarios | test_usuarios.py | test_integracion_usuarios.py | test_api_usuarios.py | test_humo_usuarios.py | locust_usuarios.py |
| Permisos por Rol | test_permisos_por_rol.py | test_integracion_permisos_por_rol.py | test_api_permisos_por_rol.py | test_humo_permisos_por_rol.py | locust_permisos_por_rol.py |
| Respaldos | test_administracion_respaldos.py | test_integracion_administracion_respaldos.py | test_api_administracion_respaldos.py | test_humo_administracion_respaldos.py | locust_administracion_respaldos.py |
| Bitácora | test_bitacora.py | test_integracion_bitacora.py | test_api_bitacora.py | test_humo_bitacora.py | locust_bitacora.py |

---

## 12. Checklist para Evidencia por Captura de Pantalla

Para cada caso de prueba ejecuta y captura:

### Unitarias / Integración / API / Humo / Aceptación
- [ ] Terminal completa con comando ejecutado
- [ ] Salida durante ejecución (líneas `[PRUEBA ...]`)
- [ ] Resumen final (`Concluyó prueba de ... — Resultado: ...`)
- [ ] Tabla de resumen por módulo (`RESUMEN DE PRUEBAS ... POR MÓDULO`)
- [ ] Si hay fallos: traceback completo

### Interfaz (UI)
- [ ] Terminal con test PASSED
- [ ] Archivo `playwright_login.png` generado (o captura manual del navegador headless)
- [ ] Verificar que no aparece "SKIPPED" (requiere app corriendo + URL + Playwright)

### Rendimiento (Locust)
- [ ] Terminal con tabla final de métricas
- [ ] Archivo `results/bitacora_rendimiento.csv` abierto en Excel
- [ ] Tabla actualizada en `CAPITULO_IV_INVISAP.md`
- [ ] Opcional: Captura de la UI web de Locust (http://127.0.0.1:8089) con gráficas

### Postman
- [ ] Colección ejecutada con pestaña **Test Results** visible
- [ ] Captura sin mostrar contraseñas ni cookies
- [ ] Cada request con estado PASS/FAIL visible

### Seguridad (Bandit)
- [ ] Terminal con salida de `bandit -r ... -ll`
- [ ] Captura de cada hallazgo (línea, severidad, descripción)

---

## 13. Interpretación Rápida de Códigos de Salida

| Símbolo/Estado | Significado |
|----------------|-------------|
| `PASSED` / `APROBADA` | Test pasó correctamente |
| `FAILED` / `FALLIDA` | Test falló (revisar traceback) |
| `SKIPPED` / `OMITIDA` | Test omitido intencionalmente (condición no cumplida) |
| `ERROR` | Error en setup/teardown del test |
| `REVISAR` (en resumen) | Módulo con al menos 1 fallida u omitida |
| `APROBADA` (en resumen) | Todas las pruebas del módulo pasaron |

---

## 14. Ejemplo de Flujo Completo de Ejecución Manual

```powershell
# 1. Preparar
cd C:\laragon\www\INVISAP\my-app
.venv\Scripts\Activate.ps1
python -m pip install -r tests\requirements-test.txt
python -m playwright install chromium

# 2. Iniciar app (terminal separada)
python run.py

# 3. Configurar URL
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"

# 4. Ejecutar por categorías y capturar cada una:

# Unitarias
python -m pytest tests\unit -v
# → Capturar resumen final

# Integración
python tests\integration\run_all_integration.py
# → Capturar resumen final

# API
python tests\api\run_all_api.py
# → Capturar resumen final

# Humo
python tests\smoke\run_all_smoke.py
# → Capturar resumen final

# UI
python -m pytest tests\ui -v
# → Capturar terminal + playwright_login.png

# Aceptación
python -m pytest tests\acceptance -v
# → Capturar terminal

# Rendimiento (quick)
python tests\performance\run_performance.py --all --profile quick
# → Capturar tabla final + CSV + CAPITULO_IV_INVISAP.md

# Seguridad SQL
python -m pytest tests\unit\test_sql_filter_allowlists.py -v
# → Capturar terminal

# Seguridad estática
bandit -r app.py controllers models routers services -ll
# → Capturar terminal

# Postman (manual en GUI)
# → Capturar Test Results
```

---

## 15. Notas Importantes

1. **Base de datos**: Usar siempre una copia de pruebas, nunca producción
2. **Credenciales**: Cuentas exclusivas de pruebas; no guardar secretos en Initial value de Postman
3. **Cookies de sesión**: No sincronizar ni publicar; solo Current value en entorno local
4. **Perfiles de carga**: `stress` y `spike` solo en entorno aislado y autorizado
5. **Playwright/Selenium**: Si se omite, registrar como "no concluyente", no como aprobado
6. **Evidencia válida**: Una prueba definida no es evidencia hasta ejecutarla contra el servidor de pruebas

---

*Guía generada basada en la estructura de `tests/`, `conftest.py`, `README.md`, `GUIA_EJECUCION_PRUEBAS.md` y los archivos de prueba de cada categoría.*