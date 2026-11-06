# CAPÍTULO IV. Recomendaciones y evolución previsible del sistema

Este capítulo presenta el plan de verificación de INVISAP, las metodologías
aplicadas por nivel y tipo de prueba, y los resultados de las ejecuciones
automatizadas documentadas. La existencia de una prueba automatizada no
significa por sí sola que un requerimiento haya sido aprobado por el usuario:
la validación funcional y la firma de los responsables deben quedar registradas
en los formatos de este proyecto.

## 4.7 Plan de Pruebas

### Objetivo

Verificar progresivamente los componentes, sus conexiones y el comportamiento
del sistema INVISAP, registrar los resultados observados, facilitar la
reproducción de errores y dejar trazabilidad entre requisitos funcionales,
casos de prueba y correcciones.

### Alcance y niveles

El alcance comprende los veinte módulos: Solicitudes, Gravedad de Obra,
Prioridad, Proyectos, Maquinaria, Contratación, Empresa, Obras, Empleados,
Inspecciones, Evidencias, Informe de Avance de Obra, Publicaciones, Reportes
PDF, Reportes Excel, Reportes Estadísticos, Usuarios, Permisos por Rol,
Administración de Respaldos y Bitácora.

La planificación sigue tres niveles:

1. **Unidad:** verifica funciones y reglas pequeñas de manera aislada.
2. **Integración:** verifica contratos y conexiones entre componentes, de forma
   incremental. La integración con una base de datos real se ejecuta en un
   ambiente de pruebas separado.
3. **Sistema:** verifica el producto ensamblado desde sus interfaces HTTP y
   visuales. Incluye humo, API, interfaz y rendimiento; la aceptación requiere
   además criterios y conformidad de los usuarios responsables.

### Metodología diferenciada

| Tipo | Objetivo y metodología | Herramientas y datos | Evidencia y límites |
|---|---|---|---|
| Unidad | Caja blanca sobre ramas y reglas; caja negra sobre entradas/salidas. Se aplican particiones de equivalencia, límites, casos válidos/inválidos parametrizados y Preparar-Actuar-Verificar con fixtures/mocks. | Pytest, `pytest.mark.parametrize`, fixtures y mocks. | `tests/unit`: 20 suites por módulo y 3 suites transversales. Comprueba componentes aislados; no acredita persistencia ni despliegue. |
| Integración | Integración incremental: 20 contratos Flask y dos flujos Contratación→Bitácora. Se verifica colaboración y auditoría; una colisión de ID inyectada comprueba el reintento. Los dobles aíslan dependencias. | Pytest, cliente Flask, mocks y fallo controlado. | `tests/integration`: 22 casos aprobados. No equivale a transacciones reales contra MySQL. |
| Backend/API | Contratos HTTP positivos y negativos: estado, JSON, autenticación/autorización, filtros, paginación y parámetros propagados al servicio/modelo. PDF/Excel verifican formularios GET; no generan archivos. | Pytest y cliente Flask con modelos simulados. Postman no estaba instalado ni se utilizó en las ejecuciones documentadas; Guzzle corresponde a PHP y no aplica a este backend Python. | `tests/api`: 20 suites por módulo y casos parametrizados de reportes. No sustituye una prueba desplegada con datos reales autorizados. |
| Humo | Una ruta esencial por módulo; comprobación rápida de respuesta HTTP sin error 404/500. Un 401/302 de autenticación confirma que se alcanzó una ruta protegida, no que la función autenticada opere correctamente. | Pytest y cliente Flask; HTTP real o navegador complementan cuando hay servidor activo. | `tests/smoke`: 20 módulos y acceso. Distinguir la suite local de las verificaciones HTTP en vivo documentadas por separado. |
| Interfaz | Extremo a extremo desde navegador: abrir pantalla, comprobar respuesta y controles visibles, descartar mensajes incorrectos y guardar captura. No se intenta una navegación autenticada en el caso existente. | Playwright + Chromium; Selenium estaba instalado en la ejecución histórica, pero no se utilizó. | `tests/ui`: un caso de acceso. La ejecución actual se omitió por falta de `INVISAP_TEST_URL`; existe una ejecución histórica aprobada solo para `/login`. |
| Rendimiento | Solicitudes GET de solo lectura por módulo con perfiles `quick`, `baseline`, `stress` y `spike`; se registran solicitudes, fallos y percentiles. Antes de interpretar tiempos se requiere acceso autenticado y carga/datos controlados. | Locust, cookie de sesión de prueba e identificadores existentes cuando la ruta los requiere. | Se ejecutaron dos series `quick` para los 20 módulos y una `baseline` para Solicitudes. En la serie más reciente, 18 módulos devolvieron 401/302 y dos 200; no es una medición autenticada aprobada. |
| Aceptación | Caja negra basada en requisito e historia: Dado/Cuando/Entonces, flujo completo, resultado observable y evaluación del validador. Registrar errores, correcciones, retest y firma. | Pytest con Playwright/Selenium puede apoyar el recorrido; la decisión final requiere el formato de especificación y acta firmados por usuarios. | Pendiente: no hay criterios firmados, validador designado ni acta de aceptación; no se ejecutó una suite de aceptación. |

### Organización de las suites por módulo

Las pruebas no están concentradas en un único archivo. Unidad, integración,
API y humo tienen un archivo independiente para cada módulo; los nombres
exactos se indican abajo. El ejecutor `pytest` descubre y ejecuta esas suites
por categoría o todas juntas. Locust también tiene un escenario por módulo,
pero `run_performance.py --all` los ejecuta secuencialmente. Las comprobaciones
de interfaz actuales son transversales al formulario de acceso y no hay casos
automatizados de aceptación por módulo.

| Módulo | Unidad: archivo y técnica principal | Integración | Backend/API | Humo | Rendimiento |
|---|---|---|---|---|---|
| Solicitudes | `tests/unit/test_solicitudes.py`: categorías y catálogos válidos/inválidos. | `tests/integration/test_integracion_solicitudes.py` | `tests/api/test_api_solicitudes.py` | `tests/smoke/test_humo_solicitudes.py` | `tests/performance/locust_solicitudes.py` |
| Gravedad de Obra | `tests/unit/test_gravedad_obra.py`: límites 0, 50, 51 y 100, tipo y rango inválidos. | `tests/integration/test_integracion_gravedad_obra.py` | `tests/api/test_api_gravedad_obra.py` | `tests/smoke/test_humo_gravedad_obra.py` | `tests/performance/locust_gravedad_obra.py` |
| Prioridad | `tests/unit/test_prioridad.py`: redondeo, límites inválidos y origen permitido. | `tests/integration/test_integracion_prioridad.py` | `tests/api/test_api_prioridad.py` | `tests/smoke/test_humo_prioridad.py` | `tests/performance/locust_prioridad.py` |
| Proyectos | `tests/unit/test_proyectos.py`: serialización, compatibilidad heredada y formato de métricas. | `tests/integration/test_integracion_proyectos.py` | `tests/api/test_api_proyectos.py` | `tests/smoke/test_humo_proyectos.py` | `tests/performance/locust_proyectos.py` |
| Maquinaria | `tests/unit/test_maquinaria.py`: nombre y tipo aceptados/rechazados. | `tests/integration/test_integracion_maquinaria.py` | `tests/api/test_api_maquinaria.py` | `tests/smoke/test_humo_maquinaria.py` | `tests/performance/locust_maquinaria.py` |
| Contratación | `tests/unit/test_contratacion.py`: obligatoriedad de datos, catálogos y fechas. | `tests/integration/test_integracion_contratacion.py` | `tests/api/test_api_contratacion.py` | `tests/smoke/test_humo_contratacion.py` | `tests/performance/locust_contratacion.py` |
| Empresa | `tests/unit/test_empresa.py`: duplicidad activa y RIF con entradas parametrizadas. | `tests/integration/test_integracion_empresa.py` | `tests/api/test_api_empresa.py` | `tests/smoke/test_humo_empresa.py` | `tests/performance/locust_empresa.py` |
| Obras | `tests/unit/test_obras.py`: texto, número, caracteres y orden cronológico. | `tests/integration/test_integracion_obras.py` | `tests/api/test_api_obras.py` | `tests/smoke/test_humo_obras.py` | `tests/performance/locust_obras.py` |
| Empleados | `tests/unit/test_empleados.py`: limpieza de campos y entradas inválidas parametrizadas. | `tests/integration/test_integracion_empleados.py` | `tests/api/test_api_empleados.py` | `tests/smoke/test_humo_empleados.py` | `tests/performance/locust_empleados.py` |
| Inspecciones | `tests/unit/test_inspecciones.py`: datos aceptados/rechazados y catálogo. | `tests/integration/test_integracion_inspecciones.py` | `tests/api/test_api_inspecciones.py` | `tests/smoke/test_humo_inspecciones.py` | `tests/performance/locust_inspecciones.py` |
| Evidencias | `tests/unit/test_evidencias.py`: archivo/URL válidos y rechazo de traversal. | `tests/integration/test_integracion_evidencias.py` | `tests/api/test_api_evidencias.py` | `tests/smoke/test_humo_evidencias.py` | `tests/performance/locust_evidencias.py` |
| Informe de Avance de Obra | `tests/unit/test_informe_avance.py`: límites, normalización y rechazo de estado. | `tests/integration/test_integracion_informe_avance.py` | `tests/api/test_api_informe_avance.py` | `tests/smoke/test_humo_informe_avance.py` | `tests/performance/locust_informe_avance.py` |
| Publicaciones | `tests/unit/test_publicaciones.py`: consulta por identificador y parámetro SQL. | `tests/integration/test_integracion_publicaciones.py` | `tests/api/test_api_publicaciones.py` | `tests/smoke/test_humo_publicaciones.py` | `tests/performance/locust_publicaciones.py` |
| Reportes PDF | `tests/unit/test_reportes_pdf.py`: filtros, lista permitida y parámetros. | `tests/integration/test_integracion_reportes_pdf.py` | `tests/api/test_api_reportes_pdf.py` | `tests/smoke/test_humo_reportes_pdf.py` | `tests/performance/locust_reportes_pdf.py` |
| Reportes Excel | `tests/unit/test_reportes_excel.py`: columnas permitidas y rechazo de columnas no mapeadas. | `tests/integration/test_integracion_reportes_excel.py` | `tests/api/test_api_reportes_excel.py` | `tests/smoke/test_humo_reportes_excel.py` | `tests/performance/locust_reportes_excel.py` |
| Reportes Estadísticos | `tests/unit/test_reportes_estadisticos.py`: lista permitida de columnas agrupables. | `tests/integration/test_integracion_reportes_estadisticos.py` | `tests/api/test_api_reportes_estadisticos.py` | `tests/smoke/test_humo_reportes_estadisticos.py` | `tests/performance/locust_reportes_estadisticos.py` |
| Usuarios | `tests/unit/test_usuarios.py`: avatar predeterminado. | `tests/integration/test_integracion_usuarios.py` | `tests/api/test_api_usuarios.py` | `tests/smoke/test_humo_usuarios.py` | `tests/performance/locust_usuarios.py` |
| Permisos por Rol | `tests/unit/test_permisos_por_rol.py`: URL y nombre de rol permitidos. | `tests/integration/test_integracion_permisos_por_rol.py` | `tests/api/test_api_permisos_por_rol.py` | `tests/smoke/test_humo_permisos_por_rol.py` | `tests/performance/locust_permisos_por_rol.py` |
| Administración de Respaldos | `tests/unit/test_administracion_respaldos.py`: limpieza de nombre y formato de tamaño. | `tests/integration/test_integracion_administracion_respaldos.py` | `tests/api/test_api_administracion_respaldos.py` | `tests/smoke/test_humo_administracion_respaldos.py` | `tests/performance/locust_administracion_respaldos.py` |
| Bitácora | `tests/unit/test_bitacora.py`: texto/usuario válidos y rechazo de caracteres. | `tests/integration/test_integracion_bitacora.py` | `tests/api/test_api_bitacora.py` | `tests/smoke/test_humo_bitacora.py` | `tests/performance/locust_bitacora.py` |

Además de los archivos por módulo, hay tres suites unitarias transversales:
`test_informe_validacion.py` (3 casos), `test_security_controls.py` (2) y
`test_sql_filter_allowlists.py` (8). `test_contrataciones_bitacora.py`
contiene dos casos de flujo integrador; `test_parametrizacion_reportes.py`
aporta 13 casos API; `test_login_smoke.py` añade un caso de humo del acceso.

En cada suite de integración, el contrato de ruta verifica el registro Flask,
el endpoint, el método HTTP y la construcción de URL. Las suites API usan el
cliente Flask con dependencias simuladas y comprueban respuesta/código HTTP,
datos o parámetros del módulo, filtros y controles de acceso que correspondan.
Las suites de humo hacen una petición básica con ese cliente y detectan
respuestas gruesas; no repiten las reglas unitarias ni acreditan una operación
persistida. Los escenarios Locust son GET de solo lectura y evalúan solamente
el endpoint enumerado aquí:

| Módulo | Endpoint de lectura Locust |
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
| Reportes PDF | `/reportes/reporte-pdf` (formulario GET; no genera PDF) |
| Reportes Excel | `/reportes/reporte-excel` (formulario GET; no genera Excel) |
| Reportes Estadísticos | `/reporte-estadistico/data` |
| Usuarios | `/api/users/<id>` |
| Permisos por Rol | `/api/seguridad/permisos/obtener/<id_rol>` |
| Administración de Respaldos | `/respaldo/api/listar-json` |
| Bitácora | `/api/obtener-bitacora-json` |

El proyecto probado es Python: no se ejecutaron PHPUnit, Guzzle, Codeception ni
JMeter; Guzzle/PHPUnit/Codeception pertenecen al stack PHP. Postman no se usó
en las ejecuciones documentadas, y Selenium estaba disponible pero no fue el
automatizador de la corrida de interfaz. Los resultados informados corresponden
a Pytest, Playwright y Locust según el tipo de prueba.

### Planificación de Unidad, Integración y Sistema

La tabla siguiente constituye el plan de trabajo. Las fechas futuras, el lugar
de validación y los nombres del responsable funcional deben completarse con el
tutor y los usuarios de la institución antes de una validación formal.

| Nivel | Objetivo específico | Actividades | Lugar / fecha | Responsables | Evidencia / estado |
|---|---|---|---|---|---|
| Unidad | Evaluar reglas y validadores aislados en las 20 suites. | Particiones válidas/inválidas, límites, parametrización, mocks y contraste esperado/observado. | Ejecución local automatizada, 2026-11-05 20:43:33 (UTC−04:00). | Equipo de desarrollo ejecutó; validador funcional por designar. | 62/62 aprobadas; sin aserciones fallidas. |
| Integración | Comprobar contratos Flask y colaboración entre componentes. | 20 contratos de ruta; 2 flujos Contratación/Bitácora, incluido error de duplicado inyectado y reintento. | Ejecución local automatizada, 2026-11-05. | Equipo de desarrollo ejecutó; DBA/tutor deberá validar transacciones reales. | 22/22 aprobadas; no certifica escrituras/transacciones reales de MySQL. |
| Sistema | Verificar el sistema ensamblado y reportar límites de HTTP, UI, carga y aceptación. | Ejecutar API/humo local; UI omitida por falta de URL; revisar los registros Locust del 2026-10-29 y la carga histórica de `/` y `/login` del 2026-10-23; aceptación con usuarios pendiente. | Pytest local el 2026-11-05; Locust contra `127.0.0.1:5600` el 2026-10-29; carga general documentada el 2026-10-23. | Equipo de desarrollo ejecutó; responsables funcionales pendientes. | API 33/33 y humo 21/21; UI 1 omitida; Locust por módulo: 2/20 escenarios HTTP aprobados; 18 no recibieron una respuesta HTTP 200 autenticada; aceptación pendiente. |

### Criterios de entrada, salida y gestión de defectos

- **Entrada:** versión de código identificada; ambiente y datos de prueba
  autorizados; requerimiento y resultado esperado trazables; dependencias de
  las pruebas disponibles.
- **Salida por caso:** resultado observado registrado, evidencia conservada,
  error vinculado a un identificador y reejecución después de cualquier
  corrección.
- **Salida de unidad/integración automatizadas:** ninguna prueba fallida; los
  warnings y las limitaciones de entorno se reportan, no se ocultan.
- **Salida de sistema/aceptación:** todos los criterios acordados ejecutados,
  defectos bloqueantes resueltos, retest satisfactorio y aprobación del
  validador funcional registrada. Estos últimos criterios aún no cuentan con
  firma de usuario.
- **Rendimiento:** no se define un umbral de milisegundos arbitrario. El
  tutor/comunidad debe acordarlo antes de interpretar una carga como aprobada.

Las plantillas editables para completar el plan y cada caso funcional están en
[`tests/documentation`](tests/documentation/).

## 4.7.1 Bitácora de Pruebas

### Datos de ejecución

- **Fecha y hora de la suite completa:** 2026-11-05 20:43:33 (UTC−04:00).
- **Ambiente:** ejecución local automatizada en Windows, Python 3.14.7 y
  pytest 9.1.1.
- **Responsable técnico:** equipo de desarrollo (ejecución automatizada).
- **Validador funcional:** pendiente de designación y firma del tutor/usuarios
  responsables.
- **Alcance de datos:** los casos de unidad, API y flujos integrados usan
  fixtures/dobles para aislar dependencias; esta ejecución no certifica
  persistencia contra una base real.
- **Comando:** `python -m pytest` con salida JUnit temporal para el desglose por
  categoría; se ejecutó la misma suite que descubre pytest.
- **Duración:** 4.63 s informados por pytest; 7.59 s de duración total del
  proceso de ejecución y recolección de resultados.

### Resultados observados

| Nivel / categoría | Comando ejecutado | Resultado | Duración | Observaciones |
|---|---|---:|---:|---|
| Unidad | `python -m pytest` (grupo `tests\unit`) | 62 aprobadas, 0 fallidas, 0 omitidas | Incluida en 4.63 s | 20 módulos y 13 pruebas transversales (validación, controles de seguridad y filtros). |
| Integración | Mismo comando (grupo `tests\integration`) | 22 aprobadas, 0 fallidas, 0 omitidas | Incluida en 4.63 s | 20 contratos de ruta y 2 flujos Contratación/Bitácora; no valida transacciones reales de MySQL. |
| Backend/API | Mismo comando (grupo `tests\api`) | 33 aprobadas, 0 fallidas, 0 omitidas | Incluida en 4.63 s | 20 suites por módulo y 13 casos parametrizados de reportes. |
| Humo | Mismo comando (grupo `tests\smoke`) | 21 aprobadas, 0 fallidas, 0 omitidas | Incluida en 4.63 s | 20 módulos y un caso de acceso; no es un recorrido integral. |
| Interfaz | Mismo comando (grupo `tests\ui`) | 0 aprobadas, 0 fallidas, 1 omitida | Incluida en 4.63 s | Omitida por falta de `INVISAP_TEST_URL`; esta corrida no abrió navegador. |
| Rendimiento | `python tests\performance\run_performance.py --all --profile quick` (corridas históricas del 2026-10-29) | Última serie: 2 módulos con HTTP 200 y 18 para revisar por HTTP 401/302 | 2 series de 5 s por módulo | La bitácora no permite confirmar una sesión autorizada; las latencias de respuestas rechazadas no constituyen línea base de rendimiento aprobada. |
| Aceptación | Recorrido de usuario según requisito aprobado | Pendiente | — | Sin criterios validados ni aprobación/evidencia de usuario. |

La ejecución completa recogió **138 aprobadas, 0 fallidas y 1 omitida** en
4.63 s (pytest; 7.59 s de proceso total), con **14 advertencias**. Las
advertencias son `DeprecationWarning` de `openpyxl` por usar
`datetime.datetime.utcnow()` al generar Excel; no son fallos de aserción. La
omisión de interfaz se debe a la falta de URL. Rendimiento y aceptación se
registran con sus propios resultados y límites, separados de esta corrida.

### Resultado exacto por módulo

Cada cifra indica casos aprobados en esta ejecución. En Integración, la
columna cuenta el contrato Flask (1 por módulo); además hubo dos casos de flujo
Contratación/Bitácora. En API, Reportes PDF suma 6 casos de parametrización y
Reportes Excel 7, además de su caso API por módulo. La columna Humo incluye el
caso de ruta por módulo; hay un caso adicional para la pantalla de acceso.

| Módulo | Unidad | Contrato integración | API | Humo |
|---|---:|---:|---:|---:|
| Solicitudes | 3/3 | 1/1 | 1/1 | 1/1 |
| Gravedad de Obra | 6/6 | 1/1 | 1/1 | 1/1 |
| Prioridad | 5/5 | 1/1 | 1/1 | 1/1 |
| Proyectos | 3/3 | 1/1 | 1/1 | 1/1 |
| Maquinaria | 2/2 | 1/1 | 1/1 | 1/1 |
| Contratación | 2/2 | 1/1 | 1/1 | 1/1 |
| Empresa | 2/2 | 1/1 | 1/1 | 1/1 |
| Obras | 3/3 | 1/1 | 1/1 | 1/1 |
| Empleados | 4/4 | 1/1 | 1/1 | 1/1 |
| Inspecciones | 3/3 | 1/1 | 1/1 | 1/1 |
| Evidencias | 2/2 | 1/1 | 1/1 | 1/1 |
| Informe de Avance de Obra | 3/3 | 1/1 | 1/1 | 1/1 |
| Publicaciones | 1/1 | 1/1 | 1/1 | 1/1 |
| Reportes PDF | 1/1 | 1/1 | 7/7 | 1/1 |
| Reportes Excel | 1/1 | 1/1 | 8/8 | 1/1 |
| Reportes Estadísticos | 1/1 | 1/1 | 1/1 | 1/1 |
| Usuarios | 1/1 | 1/1 | 1/1 | 1/1 |
| Permisos por Rol | 2/2 | 1/1 | 1/1 | 1/1 |
| Administración de Respaldos | 2/2 | 1/1 | 1/1 | 1/1 |
| Bitácora | 2/2 | 1/1 | 1/1 | 1/1 |

Las 13 pruebas unitarias transversales corresponden a validación de informes,
controles de reCAPTCHA y listas permitidas de filtros SQL. Los 2 casos extra
de integración cubren auditoría y recuperación ante colisión de ID. La suite
de humo suma un caso para acceso de INVISAP.

### Resultados exactos de rendimiento por módulo

La bitácora `tests/performance/results/bitacora_rendimiento.csv` conserva 41
registros: dos series `quick` de los 20 módulos y una serie `baseline` de
Solicitudes. La tabla resume la segunda serie completa, ejecutada el
2026-10-29 entre 22:44:23 y 22:46:14 (UTC−04:00), con un usuario durante 5 s
por módulo. “Fallos” son respuestas distintas de HTTP 200 detectadas por el
escenario; el promedio y P95 son tiempos de respuesta observados aun cuando
la solicitud no fue autorizada.

| Módulo | Solicitudes / fallos | Fallos | Promedio (ms) | P95 (ms) | Evaluación |
|---|---:|---:|---:|---:|---|
| Solicitudes | 3 / 3 | 100 % | 11.44 | 14 | Revisar: HTTP 401 |
| Gravedad de Obra | 3 / 3 | 100 % | 8.72 | 10 | Revisar: HTTP 401 |
| Prioridad | 4 / 4 | 100 % | 8.40 | 9 | Revisar: HTTP 401 |
| Proyectos | 3 / 3 | 100 % | 8.76 | 12 | Revisar: HTTP 401 |
| Maquinaria | 3 / 3 | 100 % | 8.34 | 9 | Revisar: HTTP 401 |
| Contratación | 3 / 3 | 100 % | 11.05 | 14 | Revisar: HTTP 401 |
| Empresa | 3 / 3 | 100 % | 9.36 | 11 | Revisar: HTTP 401 |
| Obras | 3 / 3 | 100 % | 9.14 | 12 | Revisar: HTTP 401 |
| Empleados | 3 / 3 | 100 % | 8.58 | 12 | Revisar: HTTP 401 |
| Inspecciones | 3 / 3 | 100 % | 7.46 | 10 | Revisar: HTTP 401 |
| Evidencias | 3 / 0 | 0 % | 28.62 | 37 | HTTP 200; respuesta funcional no validada por Locust |
| Informe de Avance de Obra | 3 / 3 | 100 % | 11.21 | 16 | Revisar: HTTP 401 |
| Publicaciones | 3 / 0 | 0 % | 25.10 | 33 | HTTP 200; respuesta funcional no validada por Locust |
| Reportes PDF | 3 / 3 | 100 % | 10.44 | 11 | Revisar: HTTP 302 |
| Reportes Excel | 3 / 3 | 100 % | 9.67 | 11 | Revisar: HTTP 302 |
| Reportes Estadísticos | 3 / 3 | 100 % | 9.61 | 13 | Revisar: HTTP 401 |
| Usuarios | 4 / 4 | 100 % | 10.16 | 12 | Revisar: HTTP 401 |
| Permisos por Rol | 4 / 4 | 100 % | 10.05 | 14 | Revisar: HTTP 401 |
| Administración de Respaldos | 3 / 3 | 100 % | 9.74 | 12 | Revisar: HTTP 401 |
| Bitácora | 3 / 3 | 100 % | 11.27 | 17 | Revisar: HTTP 401 |

En ambas series `quick` los mismos 18 escenarios protegidos no recibieron una
respuesta HTTP 200 autenticada: 16 devolvieron HTTP 401 y los formularios PDF/Excel
redirigieron con HTTP 302. Evidencias y Publicaciones devolvieron HTTP 200. No
se puede comprobar desde la bitácora si faltó la cookie de sesión, si expiró o
si no autorizaba esos endpoints, porque el valor y el rol no se almacenan. Por
ello, el resultado no permite concluir que los 18 módulos tengan defectos
funcionales o de velocidad. Debe repetirse con una cuenta de pruebas y los
identificadores requeridos, sin registrar la cookie.

El 2026-10-29 también se ejecutó `baseline` solo para Solicitudes: 5 usuarios
durante 30 s, 91 solicitudes, 91 fallos (100 %), promedio 6.15 ms y P95 de
10 ms, todos por HTTP 401. No es una línea base válida de carga autenticada.

Como evidencia histórica independiente, el informe completo del proyecto
registra Locust 2.46.7 el 2026-10-23 sobre GET `/` y `/login` con usuarios
anónimos: 20 usuarios, 195 s totales (185 s estables), 0 fallos; el resumen de
terminal indicó 1,880 solicitudes, promedio 8 ms y máximo 31 ms, mientras que
el CSV indicó 1,875, promedio 8.25 ms y máximo 31.9 ms. La diferencia de cinco
solicitudes se conserva como observación. Esa ejecución aprobó el umbral
documentado para esas dos rutas solamente; no representa los 20 módulos.

### Casos representativos de unidad e integración

| ID de seguimiento (provisional) | Nivel | Requerimiento/función observada | Entradas y procedimiento | Resultado esperado / observado | Errores asociados y corrección | Evaluación |
|---|---|---|---|---|---|---|
| UT-GRA-001 | Unidad | Clasificación del nivel de gravedad a partir de criticidad. | Valores parametrizados 0, 50, 51 y 100; invocar `_calcular_nivel_gravedad`. | Límites bajos y altos devuelven respectivamente “Bajo” y “Alto”; los cuatro casos pasaron. | Ningún defecto detectado en esta ejecución; no se necesitó corrección. | Aprobada automáticamente; pendiente de conformidad funcional. |
| UT-GRA-002 | Unidad | Rechazo de criticidad fuera del rango admitido. | Enviar 101 a `set_criticidad`; verificar `ValueError`. | Se rechaza el valor inválido; caso aprobado. | Ningún defecto detectado; sin corrección requerida. | Aprobada automáticamente. |
| IT-ROUTE-01 | Integración | Contrato de la ruta API de Gravedad de Obra. | Inspeccionar `/api/gravedad/listar`, endpoint, método HTTP y construcción de URL Flask. | Ruta y endpoint registrados y URL generada según el contrato; caso aprobado. | Sin error de contrato observado; sin corrección requerida. | Aprobada dentro del alcance del contrato de rutas; no cubre BD. |
| IT-CON-01 | Integración | Registro de contratación y auditoría de la acción. | Enviar POST de contratación usando modelo y servicio de bitácora simulados; verificar llamada de auditoría. | Respuesta esperada y registro `CREAR` en Bitácora; caso aprobado. | Ningún defecto detectado en el flujo simulado; sin corrección requerida. | Aprobada dentro del alcance de los dobles de prueba. |
| IT-CON-02 | Integración | Recuperación ante colisión de identificador al registrar contratación. | Simular colisión de clave primaria y comprobar el reintento con nuevo ID. | El primer error simulado aparece en consola; el reintento termina con registro exitoso. | La colisión es una falla inyectada deliberadamente para probar recuperación, no un defecto pendiente. No se hizo corrección en esta ejecución. | Aprobada; persistencia real pendiente de probar con BD de pruebas. |

### Experiencia de ejecución, errores y acciones

Durante la corrida del 2026-11-05 no se detectaron fallos de aserción en
Unidad, Integración, API ni Humo. Los fixtures y dobles permiten reproducir
validaciones, contratos HTTP y colaboración entre componentes, pero no
certifican persistencia real. Para completar esa evidencia se requiere una
fase de integración con MySQL de pruebas y rollback/limpieza de datos.

No se atribuye una corrección de código a los resultados de pytest del
2026-11-05. Las correcciones siguientes constan en ejecuciones anteriores del
informe completo y no deben confundirse con hallazgos de esta corrida: se
ajustó la verificación estricta de reCAPTCHA, se corrigió el aviso falso de
sesión al abrir `/login`, se implementó el reintento tras colisión de ID, se
restringieron permisos de directorios de carga y se parametrizaron consultas
y listas permitidas de identificadores SQL. El mensaje `Duplicate entry '5'`
que aparece en
`test_registrar_contratacion_reintenta_si_hay_id_duplicado` es el error
inyectado por el caso para comprobar que el modelo reintenta con otro ID; el
resultado final fue aprobado (2/2 casos del archivo integrador). Las 14
advertencias de `openpyxl` se originan en el uso obsoleto de `utcnow()` al
generar Excel; no se corrigió en esta ejecución.

El informe completo registra además un smoke HTTP en vivo con GET `/` y
`/login` en HTTP 200, y una prueba Playwright/Chromium anterior para `/login`
(1 formulario y 2 campos visibles, captura
`test-results/playwright_login.png`). Son evidencias históricas de esas rutas;
la corrida actual omitió UI por falta de `INVISAP_TEST_URL`. La aceptación con
usuarios continúa pendiente.

### Bitácora dinámica de rendimiento

El resumen por módulo anterior refleja los registros históricos disponibles.
Las nuevas ejecuciones se agregarán automáticamente desde el CSV. Para una
medición autenticada, prepare un servidor de pruebas, configure la cookie
temporal de una cuenta de prueba según `tests/performance/README.md` y use
identificadores de registros existentes.

<!-- PERFORMANCE_RESULTS_START -->
_Resumen de la segunda serie `quick` y sus límites descritos arriba. El CSV conserva las 41 ejecuciones históricas; la próxima ejecución de Locust actualizará esta bitácora automáticamente._
<!-- PERFORMANCE_RESULTS_END -->

## 4.8 Plan de Instalación

### Registro disponible

El informe integral y la Agenda JAD registran una actividad de instalación
local en la institución el **2026-09-07**, a cargo del equipo de proyecto con
participación de la tutora Ing. Jhoanly Hernandez. Ese registro documenta una
actividad realizada, pero no certifica que el servicio siga disponible ni que
se hayan repetido todos los pasos en la versión examinada el 2026-11-05. La
conexión MySQL comprobada en el informe llegó a ejecutar `SELECT 1`; no se
registraron escrituras, restauración de respaldo ni pruebas CRUD completas.

### Procedimiento previsto para una instalación reproducible

| Fase | Actividad y evidencia de salida | Responsable |
|---|---|---|
| Preparación | Identificar versión/commit, equipo y sistema operativo; confirmar disponibilidad, autorización, puertos y acceso a MySQL. | Administrador de infraestructura y equipo del proyecto. |
| Respaldo | Crear respaldo de la base existente y comprobar que pueda restaurarse en un entorno aislado antes de importar o migrar datos. | Administrador de base de datos. |
| Dependencias | Instalar la versión de Python documentada para el proyecto (Python 3.14), crear el entorno virtual e instalar `requirements.txt`; instalar por separado `tests/performance/requirements.txt` para Locust. Instalar Playwright/Chromium solo si se ejecutará UI. | Soporte técnico. |
| Configuración | Configurar conexión a MySQL, URL, secretos, cuentas y datos ficticios de prueba; importar `BD/invilara.sql` solo en una base aprobada. No copiar credenciales, cookies ni datos productivos sin autorización. | Administrador/DBA. |
| Verificación | Iniciar la aplicación y comprobar primero el acceso; después ejecutar unidad, integración, API y humo. Ejecutar UI con URL disponible y carga solo en ambiente autorizado, con sesión de prueba e identificadores válidos. | Equipo técnico y validadores. |
| Cierre/reversión | Registrar versión, fecha, responsables, errores, evidencia y resultado; documentar cómo restaurar el respaldo o revertir la versión. | Responsable de instalación. |

El informe fuente propone MySQL 9.4; la versión debe confirmarse con el
administrador antes de instalar, pues no se verificó aquí el servidor
institucional. En el checkout actual existen `BD/invilara.sql` y `run.py`,
pero no se encontraron `Containerfile`, `Dockerfile` ni directorio `wheels/`.
Por tanto, una instalación offline en contenedor no está demostrada y debe
resolverse o descartarse formalmente antes de presentarla como procedimiento
reproducible.

## 4.9 Plan de Capacitación

### Estado y objetivo

La Agenda JAD registra una fecha asociada a instalación/capacitación el
2026-09-07, pero los documentos revisados no incluyen asistencia, duración,
temario impartido ni evaluación. Por ello, no se presenta la capacitación
como completada. La siguiente agenda es una **propuesta** para capacitar a
usuarios finales, administradores y personal de soporte antes de la aceptación.

El objetivo es que cada participante pueda operar las funciones pertinentes a
su rol, reconocer restricciones de acceso, completar procesos con datos
ficticios y comunicar incidencias con evidencia suficiente para reproducirlas.
La metodología combina explicación breve, demostración guiada, práctica por
rol en un ambiente de prueba, preguntas y ejercicio de cierre.

### Agenda propuesta

| Bloque | Tema | Duración | Actividad práctica |
|---|---|---:|---|
| 1 | Introducción, objetivos y navegación del sistema | 30 min | Identificar funciones y canales de soporte. |
| 2 | Acceso, perfiles y permisos | 30 min | Ingresar con una cuenta de capacitación y verificar el alcance del rol. |
| 3 | Solicitudes, gravedad y prioridad | 60 min | Registrar y consultar una solicitud ficticia y revisar su clasificación. |
| 4 | Proyectos, obras, empresas, contratación, maquinaria y empleados | 60 min | Recorrer la gestión relacionada con una obra de práctica. |
| 5 | Inspecciones, evidencias e informes de avance | 75 min | Registrar una inspección ficticia, adjuntar evidencia de prueba y consultar avance. |
| 6 | Publicaciones y reportes PDF, Excel y estadísticos | 45 min | Consultar resultados y reconocer filtros/formatos disponibles. |
| 7 | Seguridad, bitácora y administración de respaldos | 30 min | Revisar permisos, actividad registrada y procedimiento de respaldo. |
| 8 | Administración de usuarios y roles | 30 min | Practicar una tarea administrativa con cuenta autorizada. |
| 9 | Práctica integradora y evaluación | 30 min | Completar una tarea asignada al rol y registrar dudas/observaciones. |
| **Total** | **Dos sesiones propuestas: 3 h y 3 h 30 min** | **6 h 30 min** | **No incluye pausas.** |

### Recursos, responsables y registro

Se requiere un servidor aislado de capacitación, navegador actualizado,
cuentas separadas por rol, datos completamente ficticios, proyector, guía de
usuario y acceso a los recorridos guiados disponibles. Facilitarían el equipo
del proyecto y el responsable institucional del sistema; los nombres,
participantes, fecha, lugar y disponibilidad deben confirmarse con la
institución. La evaluación propuesta combina observación de la práctica,
verificación del resultado esperado y registro de preguntas; no existe aún un
resultado de capacitación ni una calificación que pueda reportarse.

Registrar cada sesión en el formato institucional con introducción,
justificación, objetivos, metodología, temas, logística, facilitadores,
asistencia, resultados esperados y observaciones. Adjuntar la evidencia y
separar claramente una asistencia planificada de una capacitación efectivamente
impartida.

## 6. Recomendaciones y Evolución Previsible del Sistema

1. Vincular cada requisito funcional aprobado con un ID estable y con al menos
   un caso de prueba trazable; no asignar IDs definitivos hasta validar el
   documento de requisitos con el tutor/comunidad.
2. Complementar los contratos de rutas con integración real de controladores,
   modelos y MySQL en una base aislada, con transacciones y limpieza de datos.
3. Definir los criterios de aceptación con usuarios y registrar firma, fecha y
   evidencia antes de declarar entregado el sistema.
4. Ejecutar Playwright en un despliegue local/institucional estable y ampliar
   progresivamente la cobertura de interfaz más allá del formulario de acceso.
5. Ejecutar Locust en un ambiente controlado y determinar umbrales de
   rendimiento con la comunidad; repetir primero los 18 escenarios no
   autorizados con cookie temporal e identificadores de prueba, y conservar
   CSV y bitácora por versión.
6. Revisar periódicamente las 14 advertencias reportadas por pytest y
   actualizar dependencias de forma planificada, validando compatibilidad.
7. Repetir las pruebas de humo después de instalar una versión y las de unidad,
   integración y sistema después de cada cambio significativo.
8. Formalizar la aceptación con criterios y responsables acordados, y realizar
   la capacitación propuesta con asistencia y evaluación registradas.

## Referencias metodológicas

- Célad Álvarez, A. y Ruíz Calle, J. D. (2009). *Metodologías de testing de
  software y su aplicación en el Centro de Informática de la Universidad
  EAFIT*. Universidad EAFIT. Documento suministrado para esta planificación;
  se adaptan sus niveles de prueba (pp. 44–60) y técnicas de caja negra, caja
  blanca, interfaz y desempeño (pp. 60–75).
- *Manual Informe de Proyecto III*, documento suministrado. Estructura usada:
  p. 3: Plan de Pruebas, Bitácora, Plan de Instalación, Plan de Capacitación y
  recomendaciones/evolución.
- *Informe del Sistema INVILARA - Proyecto III* (PDF suministrado), pp. 143–157.
  Fuente de evidencia histórica para la instalación, las pruebas HTTP/UI,
  Locust sobre `/` y `/login`, y las actividades de capacitación registradas.
- Indiring. (s. f.). *Planificación Prueba del Software: Unidad, Integración y
  Sistema* y *Especificación de Pruebas de los Requerimientos Funcionales*.
  Calaméo, perfil compartido por el solicitante:
  <https://www.calameo.com/accounts/6325204>. Se adaptan sus campos de
  objetivos, actividades, responsables, entradas, resultados, errores,
  correcciones y evaluación.
- *Formato del Plan de Capacitación* (PDF suministrado). Se utiliza como guía
  para organizar objetivos, metodología, temas, logística, facilitadores y
  evaluación; no se reporta una sesión impartida sin asistencia/evidencia.
- Gómez Rodríguez, N. (s. f.). PFC suministrado, sección 2.2.1, “Pruebas de
  Componentes”, p. 18. Referencia conceptual; no se toman sus resultados como
  evidencia de INVISAP.
- Las hojas de cálculo editables de `tests/documentation` adaptan los formatos
  de planificación y especificación con trazabilidad y evidencia automatizada.
- Pytest Documentation; Locust Documentation; Playwright Documentation.

Los PDF de proyectos ajenos se usaron únicamente como referencia conceptual y
no como evidencia de resultados de INVISAP. El archivo de pruebas de caja
blanca/caja negra de José Manuel Sánchez Peña está cifrado y no se utilizó
para fundamentar este capítulo.
