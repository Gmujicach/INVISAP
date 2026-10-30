# Pruebas de INVISAP con pytest

Desde PowerShell, ejecuta los comandos en `my-app`. Pytest muestra cada caso
con su nombre y el porcentaje de avance; el resumen final indica cuántos
pasaron, fallaron o fueron omitidos.

```powershell
python -m pytest
```

## Carpetas

- `unit`: validaciones y lógica de un módulo aislado.
- `integration`: contratos de rutas Flask por módulo; también contiene una
  prueba de flujo de contratación y bitácora.
- `api`: pruebas de endpoints HTTP del backend.
- `smoke`: comprobaciones rápidas de que una parte esencial de la aplicación
  responde.
- `ui`: pruebas del navegador con Playwright.
- `performance`: reservado para pruebas de carga con Locust. Locust es una
  herramienta aparte y estas pruebas no se ejecutan con pytest.
- `acceptance`: reservado para recorridos completos según criterios de
  aceptación definidos por el negocio.

## Ejecutar una categoría

```powershell
python -m pytest tests\unit
python -m pytest tests\integration
python -m pytest tests\api
python -m pytest tests\smoke
python -m pytest tests\ui
```

## Pruebas de backend/API

La carpeta `tests\api` contiene un archivo por cada uno de los 20 módulos.
Las pruebas usan el cliente HTTP de Flask, verifican respuestas JSON, códigos
HTTP, control de sesión y autorización donde corresponda, además de la
propagación de parámetros y filtros. Las dependencias de modelos se sustituyen
por dobles de prueba para no necesitar una base de datos real.

Ejecuta un módulo:

```powershell
python -m pytest tests\api\test_api_solicitudes.py
python -m pytest tests\api\test_api_gravedad_obra.py
python -m pytest tests\api\test_api_prioridad.py
python -m pytest tests\api\test_api_proyectos.py
python -m pytest tests\api\test_api_maquinaria.py
python -m pytest tests\api\test_api_contratacion.py
python -m pytest tests\api\test_api_empresa.py
python -m pytest tests\api\test_api_obras.py
python -m pytest tests\api\test_api_empleados.py
python -m pytest tests\api\test_api_inspecciones.py
python -m pytest tests\api\test_api_evidencias.py
python -m pytest tests\api\test_api_informe_avance.py
python -m pytest tests\api\test_api_publicaciones.py
python -m pytest tests\api\test_api_reportes_pdf.py
python -m pytest tests\api\test_api_reportes_excel.py
python -m pytest tests\api\test_api_reportes_estadisticos.py
python -m pytest tests\api\test_api_usuarios.py
python -m pytest tests\api\test_api_permisos_por_rol.py
python -m pytest tests\api\test_api_administracion_respaldos.py
python -m pytest tests\api\test_api_bitacora.py
```

Para recorrer los 20 módulos y las pruebas de parametrización de reportes de
una sola vez:

```powershell
python tests\api\run_all_api.py
```

La consola muestra el tipo de prueba backend/API, qué comportamiento verifica
cada módulo y el mensaje `Concluyó prueba de ...` al terminar cada caso.
Los módulos PDF y Excel reciben formularios HTTP (no son endpoints JSON); sus
pruebas comprueban autenticación y rechazo de módulos inválidos. La suite de
parametrización existente también comprueba filtros válidos de esos reportes.

Para un módulo, indica su archivo. Por ejemplo:

```powershell
python -m pytest tests\unit\test_gravedad_obra.py
python -m pytest tests\unit\test_prioridad.py
python -m pytest tests\unit\test_proyectos.py
```

## Pruebas de integración

Cada uno de los 20 módulos tiene un archivo en `tests\integration`. Estos
casos comprueban la integración de enrutamiento Flask: la regla, el endpoint,
el método HTTP permitido y la generación de la URL. No ejecutan una petición
ni sustituyen pruebas que integren el controlador, el modelo y una base de
datos real.

Ejecuta un módulo:

```powershell
python -m pytest tests\integration\test_integracion_gravedad_obra.py
python -m pytest tests\integration\test_integracion_prioridad.py
python -m pytest tests\integration\test_integracion_solicitudes.py
```

Para escanear los 20 módulos de integración en una sola ejecución:

```powershell
python tests\integration\run_all_integration.py
```

El resumen de consola identifica cada módulo y muestra cuántas pruebas de
integración pasaron o fallaron.

## Pruebas de humo

Cada uno de los 20 módulos tiene una prueba HTTP en `tests\smoke`. La petición
se hace con el cliente de pruebas de Flask y confirma que la ruta no responda
404 ni 500. Un redireccionamiento de acceso, como HTTP 302, se considera una
respuesta válida para esta comprobación básica; no prueba la funcionalidad
completa del módulo ni sustituye pruebas con sesión y base de datos.

Ejecuta un módulo:

```powershell
python -m pytest tests\smoke\test_humo_gravedad_obra.py
python -m pytest tests\smoke\test_humo_prioridad.py
python -m pytest tests\smoke\test_humo_solicitudes.py
```

Para ejecutar los 20 módulos y mostrar su estado HTTP en una sola sesión:

```powershell
python tests\smoke\run_all_smoke.py
```

La consola describe cada petición como una **prueba de humo (smoke)** y
presenta un resumen por módulo.

Comando individual de cada módulo:

| Módulo | Comando |
|---|---|
| Solicitudes | `python -m pytest tests\smoke\test_humo_solicitudes.py` |
| Gravedad de Obra | `python -m pytest tests\smoke\test_humo_gravedad_obra.py` |
| Prioridad | `python -m pytest tests\smoke\test_humo_prioridad.py` |
| Proyectos | `python -m pytest tests\smoke\test_humo_proyectos.py` |
| Maquinaria | `python -m pytest tests\smoke\test_humo_maquinaria.py` |
| Contratación | `python -m pytest tests\smoke\test_humo_contratacion.py` |
| Empresa | `python -m pytest tests\smoke\test_humo_empresa.py` |
| Obras | `python -m pytest tests\smoke\test_humo_obras.py` |
| Empleados | `python -m pytest tests\smoke\test_humo_empleados.py` |
| Inspecciones | `python -m pytest tests\smoke\test_humo_inspecciones.py` |
| Evidencias | `python -m pytest tests\smoke\test_humo_evidencias.py` |
| Informe de Avance de Obra | `python -m pytest tests\smoke\test_humo_informe_avance.py` |
| Publicaciones | `python -m pytest tests\smoke\test_humo_publicaciones.py` |
| Reportes PDF | `python -m pytest tests\smoke\test_humo_reportes_pdf.py` |
| Reportes Excel | `python -m pytest tests\smoke\test_humo_reportes_excel.py` |
| Reportes Estadísticos | `python -m pytest tests\smoke\test_humo_reportes_estadisticos.py` |
| Usuarios | `python -m pytest tests\smoke\test_humo_usuarios.py` |
| Permisos por Rol | `python -m pytest tests\smoke\test_humo_permisos_por_rol.py` |
| Administración de Respaldos | `python -m pytest tests\smoke\test_humo_administracion_respaldos.py` |
| Bitácora | `python -m pytest tests\smoke\test_humo_bitacora.py` |

`tests\performance` y `tests\acceptance` documentan categorías que todavía
necesitan escenarios ejecutables. No son pruebas aprobadas mientras no haya
casos implementados en esas carpetas.

## Prueba de interfaz con Playwright

Inicia la aplicación y configura su URL antes de ejecutar la prueba:

```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
python -m pytest tests\ui
```

Si no se define la URL, o Playwright/Chromium no está instalado, pytest marcará
la prueba visual como omitida. No contará como una prueba aprobada.
