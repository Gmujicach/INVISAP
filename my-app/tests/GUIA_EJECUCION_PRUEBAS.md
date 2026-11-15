# Guía de ejecución de pruebas de INVISAP

Ejecuta los comandos desde PowerShell, en la carpeta `my-app`. Usa una base de
datos y cuentas de prueba; no ejecutes pruebas de carga ni de seguridad contra
producción.

## Preparación

Las herramientas quedan registradas en `tests\requirements-test.txt`. Para
instalarlas tanto en el Python global de esta computadora como en el entorno
del proyecto, desde CMD en `my-app`:

```cmd
C:\Python314\python.exe -m pip install -r tests\requirements-test.txt
.venv\Scripts\python.exe -m pip install -r tests\requirements-test.txt
C:\Python314\python.exe -m playwright install chromium
```

El último comando instala Chromium para Playwright en el perfil de Windows
actual. Para correr pruebas usa siempre el mismo intérprete en el que las
instalaste; se recomienda `.venv`:

```cmd
.venv\Scripts\python.exe -m pytest
```

Activa el entorno virtual del proyecto y verifica las herramientas:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest --version
locust --version
bandit --version
```

Para instalar de una vez las herramientas de prueba listadas en el manifiesto:

```powershell
python -m pip install -r tests\requirements-test.txt
python -m playwright install chromium
```

`pytest-cov` permite generar cobertura; `pip-audit` revisa vulnerabilidades
conocidas en dependencias; Selenium es una alternativa de navegador. Estos
complementan, pero no sustituyen, las pruebas existentes. Locust no reemplaza
Playwright para validar la interfaz.

Inicia la aplicación en una terminal separada:

```powershell
python run.py
```

El servidor escucha en `http://127.0.0.1:5600`. Para las pruebas de navegador
y Locust, en otra terminal define:

```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
```

## Resumen de tipos y comandos

| Tipo | Cobertura y comando individual |
|---|---|
| Unitarias | Caja blanca: lógica aislada, validaciones y modelos con dobles. `python -m pytest tests\unit\test_gravedad_obra.py` |
| Integración | Contratos de rutas Flask y un flujo entre módulos. `python -m pytest tests\integration\test_integracion_gravedad_obra.py` |
| Backend/API | Caja negra HTTP con cliente Flask y dependencias simuladas. `python -m pytest tests\api\test_api_solicitudes.py` |
| Humo | Disponibilidad básica de ruta. `python -m pytest tests\smoke\test_login_smoke.py` |
| Interfaz | Navegador real con Playwright. `python -m pytest tests\ui\test_login_ui.py` |
| Usabilidad | Etiquetas asociadas, campos requeridos, tipo de contraseña y acción visible; mismo archivo de interfaz: `python -m pytest tests\ui\test_login_ui.py::test_formulario_de_acceso_tiene_etiquetas_y_acciones_comprensibles` |
| Aceptación | Recorrido de inicio de sesión y consulta autorizada. `python -m pytest tests\acceptance\test_login_acceptance.py` |
| Inyección | Rechazo de identificadores no permitidos y parametrización de valores SQL. `python -m pytest tests\unit\test_sql_filter_allowlists.py` |
| Seguridad estática | Análisis de código Python con Bandit: `bandit -r app.py controllers models routers services -ll` |
| Seguridad/penetración controlada | Regresiones no destructivas de sesión/autorización y entradas SQL: `python -m pytest tests\api\test_api_permisos_por_rol.py tests\api\test_api_usuarios.py tests\unit\test_sql_filter_allowlists.py` |
| Rendimiento | Carga HTTP con Locust, no pytest ni automatización visual de la interfaz: `python tests\performance\run_performance.py --module solicitudes --profile quick` |
| Automatización | Ejecuta todas las pruebas pytest: `python -m pytest`; la carga Locust se ejecuta por separado. |

Las suites individuales por módulo están en `tests\unit`, `tests\integration`,
`tests\api` y `tests\smoke`. Por ejemplo, sustituye el nombre de módulo en
`python -m pytest tests\<carpeta>\<archivo>.py`. Los archivos `run_all_*.py`
permiten ejecutar categorías completas; para Locust usa
`tests\performance\run_performance.py`.

### Ejecutar archivos individuales por módulo

| Módulo | Unitarias | Integración | API | Humo |
|---|---|---|---|---|
| Solicitudes | `python -m pytest tests\unit\test_solicitudes.py` | `python -m pytest tests\integration\test_integracion_solicitudes.py` | `python -m pytest tests\api\test_api_solicitudes.py` | `python -m pytest tests\smoke\test_humo_solicitudes.py` |
| Gravedad de Obra | `python -m pytest tests\unit\test_gravedad_obra.py` | `python -m pytest tests\integration\test_integracion_gravedad_obra.py` | `python -m pytest tests\api\test_api_gravedad_obra.py` | `python -m pytest tests\smoke\test_humo_gravedad_obra.py` |
| Prioridad | `python -m pytest tests\unit\test_prioridad.py` | `python -m pytest tests\integration\test_integracion_prioridad.py` | `python -m pytest tests\api\test_api_prioridad.py` | `python -m pytest tests\smoke\test_humo_prioridad.py` |
| Proyectos | `python -m pytest tests\unit\test_proyectos.py` | `python -m pytest tests\integration\test_integracion_proyectos.py` | `python -m pytest tests\api\test_api_proyectos.py` | `python -m pytest tests\smoke\test_humo_proyectos.py` |
| Maquinaria | `python -m pytest tests\unit\test_maquinaria.py` | `python -m pytest tests\integration\test_integracion_maquinaria.py` | `python -m pytest tests\api\test_api_maquinaria.py` | `python -m pytest tests\smoke\test_humo_maquinaria.py` |
| Contratación | `python -m pytest tests\unit\test_contratacion.py` | `python -m pytest tests\integration\test_integracion_contratacion.py` | `python -m pytest tests\api\test_api_contratacion.py` | `python -m pytest tests\smoke\test_humo_contratacion.py` |
| Empresa | `python -m pytest tests\unit\test_empresa.py` | `python -m pytest tests\integration\test_integracion_empresa.py` | `python -m pytest tests\api\test_api_empresa.py` | `python -m pytest tests\smoke\test_humo_empresa.py` |
| Obras | `python -m pytest tests\unit\test_obras.py` | `python -m pytest tests\integration\test_integracion_obras.py` | `python -m pytest tests\api\test_api_obras.py` | `python -m pytest tests\smoke\test_humo_obras.py` |
| Empleados | `python -m pytest tests\unit\test_empleados.py` | `python -m pytest tests\integration\test_integracion_empleados.py` | `python -m pytest tests\api\test_api_empleados.py` | `python -m pytest tests\smoke\test_humo_empleados.py` |
| Inspecciones | `python -m pytest tests\unit\test_inspecciones.py` | `python -m pytest tests\integration\test_integracion_inspecciones.py` | `python -m pytest tests\api\test_api_inspecciones.py` | `python -m pytest tests\smoke\test_humo_inspecciones.py` |
| Evidencias | `python -m pytest tests\unit\test_evidencias.py` | `python -m pytest tests\integration\test_integracion_evidencias.py` | `python -m pytest tests\api\test_api_evidencias.py` | `python -m pytest tests\smoke\test_humo_evidencias.py` |
| Informe de Avance | `python -m pytest tests\unit\test_informe_avance.py` | `python -m pytest tests\integration\test_integracion_informe_avance.py` | `python -m pytest tests\api\test_api_informe_avance.py` | `python -m pytest tests\smoke\test_humo_informe_avance.py` |
| Publicaciones | `python -m pytest tests\unit\test_publicaciones.py` | `python -m pytest tests\integration\test_integracion_publicaciones.py` | `python -m pytest tests\api\test_api_publicaciones.py` | `python -m pytest tests\smoke\test_humo_publicaciones.py` |
| Reportes PDF | `python -m pytest tests\unit\test_reportes_pdf.py` | `python -m pytest tests\integration\test_integracion_reportes_pdf.py` | `python -m pytest tests\api\test_api_reportes_pdf.py` | `python -m pytest tests\smoke\test_humo_reportes_pdf.py` |
| Reportes Excel | `python -m pytest tests\unit\test_reportes_excel.py` | `python -m pytest tests\integration\test_integracion_reportes_excel.py` | `python -m pytest tests\api\test_api_reportes_excel.py` | `python -m pytest tests\smoke\test_humo_reportes_excel.py` |
| Reportes Estadísticos | `python -m pytest tests\unit\test_reportes_estadisticos.py` | `python -m pytest tests\integration\test_integracion_reportes_estadisticos.py` | `python -m pytest tests\api\test_api_reportes_estadisticos.py` | `python -m pytest tests\smoke\test_humo_reportes_estadisticos.py` |
| Usuarios | `python -m pytest tests\unit\test_usuarios.py` | `python -m pytest tests\integration\test_integracion_usuarios.py` | `python -m pytest tests\api\test_api_usuarios.py` | `python -m pytest tests\smoke\test_humo_usuarios.py` |
| Permisos por Rol | `python -m pytest tests\unit\test_permisos_por_rol.py` | `python -m pytest tests\integration\test_integracion_permisos_por_rol.py` | `python -m pytest tests\api\test_api_permisos_por_rol.py` | `python -m pytest tests\smoke\test_humo_permisos_por_rol.py` |
| Respaldos | `python -m pytest tests\unit\test_administracion_respaldos.py` | `python -m pytest tests\integration\test_integracion_administracion_respaldos.py` | `python -m pytest tests\api\test_api_administracion_respaldos.py` | `python -m pytest tests\smoke\test_humo_administracion_respaldos.py` |
| Bitácora | `python -m pytest tests\unit\test_bitacora.py` | `python -m pytest tests\integration\test_integracion_bitacora.py` | `python -m pytest tests\api\test_api_bitacora.py` | `python -m pytest tests\smoke\test_humo_bitacora.py` |

Los casos transversales que no son un módulo de negocio tienen sus propios
archivos, por ejemplo `tests\unit\test_security_controls.py`,
`tests\unit\test_sql_filter_allowlists.py`,
`tests\api\test_parametrizacion_reportes.py` y
`tests\integration\test_contrataciones_bitacora.py`.

## Postman: pruebas de backend/API paso a paso

Los contratos existentes están en
`postman\collections\INVISAP - Pruebas de Contrato HTTP`. Abre esa colección en
el workspace de Postman donde está sincronizada la carpeta del proyecto. Si
Postman no reconoce el formato de archivos de workspace, crea una colección
Postman con el mismo nombre y configura cada solicitud con los URL/métodos
indicados en sus archivos `*.request.yaml`.

1. Inicia el servidor de pruebas con `python run.py` y verifica
   `http://127.0.0.1:5600/login`.
2. Selecciona el entorno `INVISAP pruebas` y define `baseUrl` como
   `http://127.0.0.1:5600`.
3. En las variables locales/Current value del entorno, coloca datos de una
   cuenta exclusiva de pruebas en `login_username`, `login_password` y
   `recaptcha_token`. Define también IDs existentes para las solicitudes que
   usan proyecto, empresa, evidencia, informe, usuario o rol. No guardes
   secretos como Initial value ni los sincronices.
4. Ejecuta primero **Acceso API sin sesión**. La aserción espera HTTP 401 y una
   lista vacía. Si la ruta devuelve otro contrato en tu configuración, confirma
   el estado esperado en el endpoint antes de modificar la aserción.
5. Ejecuta **Login**. Debe validar el formulario/resultado HTML y guardar en
   `session_cookie` solo el valor de la cookie (sin el prefijo `session=`).
6. Ejecuta una consulta protegida como **Solicitudes** o **Usuarios**. El
   script de colección adjunta el encabezado `Cookie: session=<valor>`.
   Comprueba estado, `Content-Type` y estructura JSON.
7. Ejecuta los demás `*.request.yaml` individualmente desde la colección.
   Sustituye IDs vacíos por registros de prueba válidos; no uses operaciones de
   escritura, eliminación, importación o respaldo sobre producción.
8. Revisa la pestaña **Test Results** y guarda evidencia sin contraseñas ni
   cookies. Una solicitud definida en Postman no es evidencia hasta ejecutarla
   contra el servidor de pruebas.

Los archivos Postman actuales validan principalmente contrato HTTP y JSON; no
demuestran por sí solos persistencia, permisos exhaustivos ni aceptación
funcional. Complementa con `tests\api`.

## Locust: carga HTTP (no prueba visual de interfaz)

Locust genera solicitudes HTTP concurrentes; no controla navegador ni evalúa
disposición visual, accesibilidad o interacción gráfica. Para interfaz usa
Playwright en `tests\ui`; Locust aquí mide rendimiento de endpoints del backend
que sirven a la interfaz.

1. Inicia INVISAP con datos/usuarios de prueba y configura:

   ```powershell
   $env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
   $env:INVISAP_PERF_SESSION_COOKIE = "session=COOKIE_DE_PRUEBA"
   ```

2. Configura los IDs/RIF/código requeridos por el escenario en
   `tests\performance\README.md`. No publiques ni registres la cookie.
3. Ejecuta una comprobación pequeña y un módulo individual:

   ```powershell
   python tests\performance\run_performance.py --module solicitudes --profile quick
   ```

4. Para abrir la interfaz web de Locust y seleccionar el escenario:

   ```powershell
   locust -f tests\performance\locust_solicitudes.py --host http://127.0.0.1:5600
   ```

   Abre `http://127.0.0.1:8089`, configura usuarios y tasa de inicio bajos, y
   pulsa **Start swarming**. Confirma la cookie mediante configuración de
   entorno antes de iniciar carga autenticada; detén la prueba si aparecen
   errores sostenidos.

5. Revisa fallos, latencia y CSV de salida. Usa `baseline`, `stress` o `spike`
   solo en un ambiente aislado y autorizado. La ejecución con perfil quick no
   acredita un objetivo de rendimiento.

## Seguridad, caja blanca/negra y penetración

- **Caja blanca:** inspecciona ramas, validadores y consultas con tests unitarios
  (por ejemplo, `tests\unit\test_sql_filter_allowlists.py`).
- **Caja negra:** comprueba respuestas desde HTTP sin acoplarse a la
  implementación (`tests\api` y Postman).
- **Inyecciones:** la suite de filtros verifica listas permitidas y parámetros
  SQL sin modificar datos; ejecútala con el comando de la tabla. No pegues
  cargas destructivas en Postman.
- **Seguridad estática:** Bandit detecta patrones sospechosos en código Python;
  revisa cada hallazgo antes de clasificarlo como vulnerabilidad.
- **Penetración:** los comandos listados son pruebas de regresión defensivas y
  no equivalen a una auditoría de penetración independiente. Limita las
  verificaciones dinámicas a sistemas propios con autorización explícita,
  cuentas/datos de prueba y alcance acordado. No ejecutes escáneres agresivos,
  estrés ni operaciones destructivas contra producción.

Playwright y Locust pueden omitir/no completar las comprobaciones si el servidor,
Chromium, sesión o datos de prueba no están disponibles. Registra el resultado
como omitido/no concluyente, no como aprobado.
