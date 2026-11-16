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
- `performance`: escenarios de carga con Locust por módulo; se ejecutan con
  su ejecutor, no con pytest, y registran resultados en el complemento del
  Capítulo IV.
- `acceptance`: recorridos automatizados de aceptación técnica; los criterios
  funcionales y la aprobación formal aún requieren validación de usuarios.

## Ejecutar una categoría

```powershell
python -m pytest tests\unit --confcutdir=tests\unit
python -m pytest tests\integration
python -m pytest tests\api
python -m pytest tests\smoke
python -m pytest tests\ui
python -m pytest tests\acceptance
```

Las pruebas unitarias complementarias de consultas/delegación de los 20
módulos se ejecutan individualmente con:

```powershell
python -m pytest tests\unit\test_model_query_methods.py
```

Los casos exhaustivos de métodos están agrupados por área. Cada grupo cubre
constructores, accesores, métodos públicos y privados activos, con dobles para
SQL y pruebas de límites/rutas de error:

```powershell
python -m pytest tests\unit\test_all_methods_core_models.py --confcutdir=tests\unit
python -m pytest tests\unit\test_all_methods_entity_audit.py --confcutdir=tests\unit
python -m pytest tests\unit\test_all_methods_inspection_evidence.py --confcutdir=tests\unit
python -m pytest tests\unit\test_all_methods_reports_security.py --confcutdir=tests\unit
python -m pytest tests\unit\test_base_model.py --confcutdir=tests\unit
```

Las dependencias para las herramientas automatizadas están listadas en
`tests\requirements-test.txt`. Instálalas dentro del entorno virtual del
proyecto con `python -m pip install -r tests\requirements-test.txt`. Para
cobertura de líneas, añade `--cov=models --cov-report=term-missing` al comando
de pytest; una cobertura de líneas no equivale a que cada método/ramificación
esté probado.

### Preparar las herramientas en `.venv` (CMD)

Desde la carpeta `my-app`, activa el entorno virtual e instala las dependencias
de pruebas:

```bat
.venv\Scripts\activate.bat
python -m pip install -r tests\requirements-test.txt
python -m playwright install chromium
```

El archivo de requisitos incluye Pytest, pytest-cov, Selenium, Playwright,
Locust y herramientas de análisis estático. Selenium 4 usa Selenium Manager
para resolver el controlador del navegador; Edge o Chrome debe estar instalado.
Playwright necesita Chromium instalado una vez dentro del entorno.

Postman es una aplicación de escritorio, no un paquete instalable en `.venv`.
Se ejecuta por separado contra el servidor local de pruebas; los archivos
`.request.yaml` del repositorio describen solicitudes y, si la versión de
Postman no los importa directamente, deben recrearse en la colección. Para
automatización HTTP desde Python, las suites API usan el cliente Flask de
Pytest y las dependencias HTTP del proyecto.

Las suites formales de aceptación con participantes/acta son distintas de las
pruebas automatizadas: comprueba que `tests\acceptance` tenga casos ejecutables
antes de invocar Pytest en esa carpeta.

Para comprobar que las pruebas entran en cada método activo de los modelos
listados, ejecuta la cobertura de ramas y después el auditor de métodos:

```powershell
python -m pytest tests\unit --confcutdir=tests\unit --cov=models --cov-branch --cov-report=term-missing
python tests\unit\check_model_method_coverage.py
```

El auditor comprueba que se ejecutó el cuerpo de cada método activo, incluidos
los pares getter/setter de propiedades y las funciones auxiliares incluidas;
también imprime la cobertura de ramas filtrada a esos modelos. No sustituye
las aserciones de comportamiento de cada prueba. `--confcutdir` evita cargar
el `conftest.py` raíz, cuya inicialización intenta conectarse a MySQL; las
pruebas unitarias usan dobles y no validan persistencia real.

Las pruebas de rendimiento se ejecutan con Locust, no con pytest:

```powershell
python tests\performance\run_performance.py --all --profile quick
```

Consulta [tests/performance/README.md](performance/README.md) para comandos por
módulo, configuración de sesión y perfiles de carga.

La carpeta `postman\collections\INVISAP - Pruebas de Contrato HTTP` contiene
solicitudes Postman por endpoint. Configura las credenciales solo en las
variables locales del entorno y ejecuta la colección contra un servidor de
pruebas autorizado; la presencia de archivos `.request.yaml` no es evidencia
de que se haya ejecutado una prueba HTTP real.

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

El recorrido técnico de `tests\acceptance` no sustituye los criterios acordados
ni el acta de aprobación de negocio. Las pruebas de `tests\performance` se
ejecutan con Locust; sus resultados solo se consideran evidencia cuando se
ejecutan contra el servidor de pruebas y se revisa la bitácora.

## Prueba de interfaz con Playwright

Inicia la aplicación y configura su URL antes de ejecutar la prueba:

```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
python -m pytest tests\ui
```

Si no se define la URL, o Playwright/Chromium no está instalado, pytest marcará
la prueba visual como omitida. No contará como una prueba aprobada.
