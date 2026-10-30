# Pruebas de rendimiento

Estas pruebas usan **Locust**, no pytest. Los escenarios consultan endpoints
HTTP de solo lectura y usan la misma URL de la aplicación para probar los
módulos por separado. Los formularios de reportes PDF y Excel se consultan con
GET; no se generan archivos durante la carga.

## Preparación

Desde PowerShell, en `my-app`, instala las dependencias del proyecto si aún no
lo has hecho e inicia INVISAP en un entorno de pruebas:

```powershell
pip install -r requirements.txt
pip install -r tests\performance\requirements.txt
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
```

La mayoría de las rutas requieren una sesión autenticada. Para probar el flujo
completo, establece una cookie de sesión de una cuenta **de pruebas** antes de
ejecutar Locust:

```powershell
$env:INVISAP_PERF_SESSION_COOKIE = "session=VALOR_DE_COOKIE_DE_PRUEBAS"
```

No compartas ni guardes esa cookie en el repositorio. Sin cookie, las rutas
protegidas responderán 401/403 o redirigirán al inicio de sesión; el resultado
quedará registrado como fallo del escenario, no como una medición autenticada.
Se recomienda usar una copia de pruebas de la base de datos.

Para endpoints que dependen de registros concretos, configura identificadores
existentes en el entorno de PowerShell (ajusta los valores a los datos de
prueba):

```powershell
$env:INVISAP_PERF_CODIGO_PROYECTO = "CODIGO_DE_PRUEBA"
$env:INVISAP_PERF_EMPRESA_RIF = "RIF_DE_PRUEBA"
$env:INVISAP_PERF_ID_EVIDENCIA = "1"
$env:INVISAP_PERF_ID_INFORME = "1"
$env:INVISAP_PERF_ID_USUARIO = "1"
$env:INVISAP_PERF_ID_ROL = "1"
```

## Tipos de escenario

- `quick`: 1 usuario durante 5 segundos; verificación breve de conectividad.
- `baseline`: 5 usuarios durante 30 segundos; carga de referencia.
- `stress`: 20 usuarios durante 60 segundos; solo en un entorno preparado.
- `spike`: 30 usuarios con aumento inmediato durante 30 segundos; solo en un
  entorno preparado.

Los perfiles son ajustables con `--users`, `--spawn-rate` y `--run-time`.
No ejecutes perfiles `stress` o `spike` contra producción.

## Ejecutar un módulo

Usa el identificador de módulo con el ejecutor para que los resultados
actualicen la bitácora del Capítulo IV:

```powershell
python tests\performance\run_performance.py --module solicitudes --profile baseline
python tests\performance\run_performance.py --module gravedad_obra --profile baseline
python tests\performance\run_performance.py --module prioridad --profile baseline
python tests\performance\run_performance.py --module proyectos --profile baseline
python tests\performance\run_performance.py --module maquinaria --profile baseline
python tests\performance\run_performance.py --module contratacion --profile baseline
python tests\performance\run_performance.py --module empresa --profile baseline
python tests\performance\run_performance.py --module obras --profile baseline
python tests\performance\run_performance.py --module empleados --profile baseline
python tests\performance\run_performance.py --module inspecciones --profile baseline
python tests\performance\run_performance.py --module evidencias --profile baseline
python tests\performance\run_performance.py --module informe_avance --profile baseline
python tests\performance\run_performance.py --module publicaciones --profile baseline
python tests\performance\run_performance.py --module reportes_pdf --profile baseline
python tests\performance\run_performance.py --module reportes_excel --profile baseline
python tests\performance\run_performance.py --module reportes_estadisticos --profile baseline
python tests\performance\run_performance.py --module usuarios --profile baseline
python tests\performance\run_performance.py --module permisos_por_rol --profile baseline
python tests\performance\run_performance.py --module administracion_respaldos --profile baseline
python tests\performance\run_performance.py --module bitacora --profile baseline
```

## Ejecutar todos los módulos

Un perfil breve evita una ejecución demasiado larga mientras se revisa la
configuración:

```powershell
python tests\performance\run_performance.py --all --profile quick
```

Para una carga de referencia completa de los 20 módulos:

```powershell
python tests\performance\run_performance.py --all --profile baseline
```

El ejecutor corre los escenarios secuencialmente, muestra el tipo de prueba y
el endpoint evaluado, y anuncia `Concluyó prueba de ...` al finalizar cada
módulo. No se debe ejecutar `pytest` para estas pruebas.

## Resultados y bitácora del informe

Cada ejecución agrega métricas a `results\bitacora_rendimiento.csv` y actualiza
la tabla de resultados en
[`Capitulo_IV_Rendimiento.md`](Capitulo_IV_Rendimiento.md). Los CSV originales
de Locust también se guardan en `results`. Se registran cantidad de solicitudes,
fallos HTTP, solicitudes por segundo y tiempos de respuesta promedio, mediano y
percentil 95.

Una respuesta HTTP exitosa no significa que se haya alcanzado un objetivo de
rendimiento: el proyecto debe definir los tiempos máximos aceptables con su
tutor/comunidad. No se fijan umbrales arbitrarios en estas pruebas.

## Mapa de escenarios

| Módulo | Endpoint de lectura evaluado |
|---|---|
| Solicitudes | `/api/obtener-solicitudes-json` |
| Gravedad de Obra | `/api/gravedad/listar` |
| Prioridad | `/api/prioridad/listar` |
| Proyectos | `/api/proyecto/validar-codigo/<código>` |
| Maquinaria | `/api/maquinaria/listar` |
| Contratación | `/api/obtener-empresas-json` |
| Empresa | `/api/empresas/<RIF>` |
| Obras | `/api/obra/estados` |
| Empleados | `/empleados/api/listar-json` |
| Inspecciones | `/inspecciones/api/inspectores/listar` |
| Evidencias | `/api/evidencias/validar/<id>` |
| Informe de Avance de Obra | `/api/informes/listar-json` |
| Publicaciones | `/api/publicaciones/validar-informe/<id>` |
| Reportes PDF | `/reportes/reporte-pdf` (formulario GET, sin generar PDF) |
| Reportes Excel | `/reportes/reporte-excel` (formulario GET, sin generar Excel) |
| Reportes Estadísticos | `/reporte-estadistico/data` |
| Usuarios | `/api/users/<id>` |
| Permisos por Rol | `/api/seguridad/permisos/obtener/<id_rol>` |
| Administración de Respaldos | `/respaldo/api/listar-json` |
| Bitácora | `/api/obtener-bitacora-json` |
