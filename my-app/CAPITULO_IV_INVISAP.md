# CAPÍTULO IV. Recomendaciones y evolución previsible del sistema

Este capítulo presenta el plan de verificación de INVISAP, las metodologías y
técnicas aplicadas por nivel y tipo de prueba, las evidencias disponibles y los
resultados medidos. La existencia de una prueba automatizada no significa por
sí sola que un requerimiento haya sido aprobado por el usuario: la validación
funcional y la firma de los responsables deben quedar registradas en los
formatos del proyecto.

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
| Unidad | Caja blanca sobre reglas y caja negra sobre entradas/salidas. Se usaron particiones de equivalencia, límites, casos válidos/inválidos y parametrización; ciclo Preparar-Actuar-Verificar. Se aíslan dependencias externas con fixtures y mocks. | Python/pytest (`pytest.mark.parametrize`), sin PHPUnit (INVISAP es Flask/Python). | 20 archivos de módulo en `tests/unit` y pruebas transversales. Valida unidades aisladas, no persistencia o despliegue. |
| Integración | Enfoque incremental: un contrato de ruta Flask por módulo (regla, endpoint, método y URL) y dos pruebas de flujo Contratación→Bitácora/modelo, incluyendo una colisión de ID inyectada para verificar reintento. | Python/pytest, cliente de Flask, mocks/dobles y fallo controlado. | 20 contratos + 2 flujos en `tests/integration`. No se hizo transacción CRUD con MySQL en la ejecución del 05/11. |
| Backend/API | Pruebas de contrato HTTP positivas/negativas: estado, JSON, autenticación/autorización, parámetros, filtros, paginación y llamadas a dependencias. Reportes PDF/Excel son formularios HTTP; no se presentan como API JSON. | Python/pytest + `app.test_client()`; mocks de modelos. Postman no está instalado/ejecutado en el entorno documentado; Guzzle y PHPUnit son herramientas PHP, no aplicables a Flask. | Un archivo por módulo y archivo adicional parametrizado de reportes en `tests/api`. Los dobles no sustituyen la prueba contra una API y base reales. |
| Humo | Selección basada en riesgo: petición rápida a una ruta esencial por módulo; se considera humo si no responde 404/500. Un 302/401 de sesión solo demuestra disponibilidad de la ruta, no una operación correcta autenticada. | Python/pytest + cliente Flask; en la ejecución histórica se complementó con HTTP en vivo y Playwright para `/login`. | 20 archivos de módulo y uno de acceso en `tests/smoke`; alcance superficial, no valida todo el flujo. |
| Interfaz | Prueba de navegador de caja negra: cargar acceso, comprobar HTTP/título/formulario/campos y ausencia de mensaje incorrecto; guardar captura. No se ejercitaron formularios autenticados de los 20 módulos. | Playwright 1.64/Chromium para la evidencia del 23/10; pytest/Playwright en `tests/ui` requiere URL y navegador. Selenium estaba instalado históricamente, pero no se usó. | Hay un escenario común de acceso, no un archivo UI por módulo. El run del 05/11 se omitió por falta de `INVISAP_TEST_URL`. |
| Rendimiento | Carga de lectura: definir concurrencia/duración, medir solicitudes, errores, tasa y tiempos; separar el smoke/baseline de estrés/pico. Comparar únicamente mediciones con alcance y entorno equivalentes. | Locust 2.46.7. Evidencia histórica: 20 usuarios y 195 s sobre `/` y `/login`; escenarios individuales `locust_<modulo>.py` y ejecutor global para módulos. | La carga histórica no cubre los 20 módulos. El intento API de Solicitudes del 29/10 devolvió 401 en las 3 peticiones; no es una medición autenticada ni demuestra un defecto funcional. |
| Aceptación | Caja negra basada en requisito aprobado e historia Dado/Cuando/Entonces; ejecutar flujo completo con usuario representativo, evaluar resultado, registrar incidencia/retest y conformidad. | Se propone Playwright + validación guiada del personal y especificación firmada. | No hay criterios/acta de aceptación ni pruebas automatizadas de aceptación ejecutadas; pendiente de la comunidad. |

#### Organización de archivos y ejecución por módulo

Las suites de unidad, integración, API y humo son **individuales por módulo**:
cada módulo tiene su archivo `test_*.py`; no se usa un único archivo que
contenga los veinte módulos. API y humo, además, disponen de ejecutores globales.
Rendimiento también tiene veinte escenarios Locust individuales y un ejecutor
global que los corre secuencialmente. Interfaz solo tiene un escenario común
para acceso; aceptación no tiene todavía escenarios automatizados.

| Categoría | Archivos por módulo | Ejecución global / organización |
|---|---|---|
| Unidad | `tests/unit/test_<modulo>.py` | `python -m pytest tests\unit`; también incluye pruebas transversales de validación, reCAPTCHA y filtros SQL. |
| Integración | `tests/integration/test_integracion_<modulo>.py` | `python -m pytest tests\integration`; `test_contrataciones_bitacora.py` contiene dos flujos adicionales. |
| Backend/API | `tests/api/test_api_<modulo>.py` | `python tests\api\run_all_api.py`; incluye `test_parametrizacion_reportes.py`. |
| Humo | `tests/smoke/test_humo_<modulo>.py` | `python tests\smoke\run_all_smoke.py`; también prueba `/login`. |
| Interfaz | No hay archivo individual por módulo. | `tests/ui/test_login_ui.py`; solo pantalla de acceso. |
| Rendimiento | `tests/performance/locust_<modulo>.py` | `python tests\performance\run_performance.py --all --profile quick`; Locust, no pytest. |
| Aceptación | Ninguno ejecutable por módulo. | Pendiente de requisitos/criterios aprobados y validadores de INVILARA. |

### Planificación de Unidad, Integración y Sistema

La tabla siguiente constituye el plan de trabajo. Las fechas futuras, el lugar
de validación y los nombres del responsable funcional deben completarse con el
tutor y los usuarios de la institución antes de una validación formal.

| Nivel | Objetivo específico | Actividades | Lugar / fecha | Responsables | Evidencia / estado |
|---|---|---|---|---|---|
| Unidad | Evaluar reglas y validadores aislados. | Particiones válidas/inválidas, límites, parametrización, mocks y contraste esperado/observado. | Ejecución local automatizada, 05/11/2026 20:26–20:28 (UTC−04:00). | Equipo de desarrollo ejecutó; validador funcional por designar. | 62/62 aprobadas. |
| Integración | Comprobar contratos Flask y colaboración de módulos. | 20 contratos de ruta; 2 flujos Contratación/Bitácora con colisión inyectada y reintento. | Ejecución local automatizada, 05/11/2026. | Equipo de desarrollo ejecutó; responsable de BD/tutor para la siguiente etapa. | 22/22 aprobadas; no certifica transacciones reales MySQL. |
| Sistema | Verificar el producto ensamblado desde HTTP/UI, además de rendimiento y aceptación. | API y humo locales; navegador/carga contra despliegue y evaluación de usuarios como etapas separadas. | Local el 05/11; ambiente institucional para validar UI, carga y aceptación. | Equipo de desarrollo; usuarios/validador funcional por designar. | API 33/33, humo 21/21; UI omitida este día. Se conservan evidencias históricas limitadas de UI y Locust del 23/10; aceptación pendiente. |

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

- **Fecha y hora de la ejecución actual:** 2026-11-05, 20:26:47–20:28:06
  (UTC−04:00).
- **Ambiente:** ejecución local automatizada en Windows, Python 3.14.7 y
  pytest 9.1.1.
- **Responsable técnico:** equipo de desarrollo (ejecución automatizada).
- **Validador funcional:** pendiente de designación y firma del tutor/usuarios
  responsables.
- **Alcance de datos:** los casos de unidad, API y flujos integrados usan
  fixtures/dobles para aislar dependencias; la ejecución actual no certifica
  escrituras/transacciones contra MySQL.
- **Comando:** `python -m pytest --junitxml=<archivo-temporal>`; el XML
  temporal permitió desglosar la única ejecución por carpetas y módulos.
- **Duración:** 65.40 s informados por pytest; 79.05 s de reloj total,
  incluyendo el resumen XML.
- **Servidor de pruebas en esta ejecución:** no disponible en
  `127.0.0.1:5600`; por eso UI quedó omitida y no se ejecutó carga Locust
  contra el servidor en esta fecha.

### Resultados observados

| Nivel / categoría | Herramienta y método realmente ejecutado | Resultado observado | Observaciones / límite |
|---|---|---|---|
| Unidad | Pytest 9.1.1; `tests/unit` dentro de la ejecución integral. | 62 aprobadas, 0 fallidas, 0 omitidas. | 49 casos distribuidos en los 20 archivos de módulo y 13 casos transversales de informes, reCAPTCHA y listas permitidas SQL. |
| Integración | Pytest + cliente Flask para contratos, más flujos con dobles. | 22 aprobadas, 0 fallidas, 0 omitidas. | 20 contratos de ruta y 2 casos Contratación/Bitácora. No es una prueba CRUD transaccional con MySQL. |
| Backend/API | Pytest + `app.test_client()`, respuestas HTTP y dependencias simuladas. | 33 aprobadas, 0 fallidas, 0 omitidas. | 20 pruebas de endpoint (una por módulo) y 13 casos parametrizados de reportes. Postman no fue ejecutado. |
| Humo | Pytest + cliente Flask, 20 rutas de módulo y `/login`. | 21 aprobadas, 0 fallidas, 0 omitidas. | Verifica disponibilidad básica/no 404/500; no equivale a flujos completos autenticados. |
| Interfaz | Pytest + Playwright/Chromium en `tests/ui`. | 0 aprobadas, 0 fallidas, 1 omitida el 05/11. | Motivo: `INVISAP_TEST_URL` no estaba definido. Hay una ejecución histórica Playwright aprobada el 23/10, registrada abajo. |
| Rendimiento | Locust 2.46.7; consulta HTTP de `/` y `/login` documentada el 23/10; intento API Solicitudes del 29/10. | Carga general histórica: 0 fallos/1,875 en CSV. API Solicitudes: 3/3 fallos HTTP 401. | No hay una medición autenticada de los 20 módulos. La carga general solo cubre home/login. |
| Aceptación | Validación guiada por usuarios con Pytest/Playwright propuesta. | Pendiente, 0 casos aceptados registrados. | No se suministró acta, criterios aprobados ni evidencia de participantes. |

La ejecución integral del 05/11 terminó con **138 aprobadas, 0 fallidas y
1 omitida**, en **65.40 s** de pytest (79.05 s de reloj total), con **14
advertencias**. Las advertencias observadas son `DeprecationWarning` de
`openpyxl` al llamar `datetime.datetime.utcnow()` durante la escritura de
Excel; no son fallos de aserción. El XML temporal agrupó las pruebas existentes;
no se sustituyeron ni ocultaron fallos.

### Resultado exacto por módulo

Cada cifra indica casos aprobados en esta ejecución. En Integración, la
columna cuenta el contrato Flask (1 por módulo); además hubo dos casos de flujo
Contratación/Bitácora. En API, Reportes PDF suma 6 casos de parametrización y
Reportes Excel 7, además de su caso API por módulo. La columna Humo incluye el
caso de ruta por módulo; hay un caso adicional para la pantalla de acceso.

| Módulo | Unidad (`archivo`: casos) | Integración (archivo) | API (archivo: casos) | Humo (archivo) | Rendimiento (escenario) |
|---|---|---|---|---|---|
| Solicitudes | `test_solicitudes.py`: 3/3 | `test_integracion_solicitudes.py`: 1/1 | `test_api_solicitudes.py`: 1/1 | `test_humo_solicitudes.py`: 1/1 | `locust_solicitudes.py`: 3 peticiones, 3 HTTP 401 el 29/10; revisar abajo |
| Gravedad de Obra | `test_gravedad_obra.py`: 6/6 | `test_integracion_gravedad_obra.py`: 1/1 | `test_api_gravedad_obra.py`: 1/1 | `test_humo_gravedad_obra.py`: 1/1 | `locust_gravedad_obra.py`: no ejecutado contra el módulo |
| Prioridad | `test_prioridad.py`: 5/5 | `test_integracion_prioridad.py`: 1/1 | `test_api_prioridad.py`: 1/1 | `test_humo_prioridad.py`: 1/1 | `locust_prioridad.py`: no ejecutado contra el módulo |
| Proyectos | `test_proyectos.py`: 3/3 | `test_integracion_proyectos.py`: 1/1 | `test_api_proyectos.py`: 1/1 | `test_humo_proyectos.py`: 1/1 | `locust_proyectos.py`: no ejecutado contra el módulo |
| Maquinaria | `test_maquinaria.py`: 2/2 | `test_integracion_maquinaria.py`: 1/1 | `test_api_maquinaria.py`: 1/1 | `test_humo_maquinaria.py`: 1/1 | `locust_maquinaria.py`: no ejecutado contra el módulo |
| Contratación | `test_contratacion.py`: 2/2 | `test_integracion_contratacion.py`: 1/1 | `test_api_contratacion.py`: 1/1 | `test_humo_contratacion.py`: 1/1 | `locust_contratacion.py`: no ejecutado contra el módulo |
| Empresa | `test_empresa.py`: 2/2 | `test_integracion_empresa.py`: 1/1 | `test_api_empresa.py`: 1/1 | `test_humo_empresa.py`: 1/1 | `locust_empresa.py`: no ejecutado contra el módulo |
| Obras | `test_obras.py`: 3/3 | `test_integracion_obras.py`: 1/1 | `test_api_obras.py`: 1/1 | `test_humo_obras.py`: 1/1 | `locust_obras.py`: no ejecutado contra el módulo |
| Empleados | `test_empleados.py`: 4/4 | `test_integracion_empleados.py`: 1/1 | `test_api_empleados.py`: 1/1 | `test_humo_empleados.py`: 1/1 | `locust_empleados.py`: no ejecutado contra el módulo |
| Inspecciones | `test_inspecciones.py`: 3/3 | `test_integracion_inspecciones.py`: 1/1 | `test_api_inspecciones.py`: 1/1 | `test_humo_inspecciones.py`: 1/1 | `locust_inspecciones.py`: no ejecutado contra el módulo |
| Evidencias | `test_evidencias.py`: 2/2 | `test_integracion_evidencias.py`: 1/1 | `test_api_evidencias.py`: 1/1 | `test_humo_evidencias.py`: 1/1 | `locust_evidencias.py`: no ejecutado contra el módulo |
| Informe de Avance de Obra | `test_informe_avance.py`: 3/3 | `test_integracion_informe_avance.py`: 1/1 | `test_api_informe_avance.py`: 1/1 | `test_humo_informe_avance.py`: 1/1 | `locust_informe_avance.py`: no ejecutado contra el módulo |
| Publicaciones | `test_publicaciones.py`: 1/1 | `test_integracion_publicaciones.py`: 1/1 | `test_api_publicaciones.py`: 1/1 | `test_humo_publicaciones.py`: 1/1 | `locust_publicaciones.py`: no ejecutado contra el módulo |
| Reportes PDF | `test_reportes_pdf.py`: 1/1 | `test_integracion_reportes_pdf.py`: 1/1 | `test_api_reportes_pdf.py` + parametrización: 7/7 | `test_humo_reportes_pdf.py`: 1/1 | `locust_reportes_pdf.py`: no ejecutado contra el módulo |
| Reportes Excel | `test_reportes_excel.py`: 1/1 | `test_integracion_reportes_excel.py`: 1/1 | `test_api_reportes_excel.py` + parametrización: 8/8 | `test_humo_reportes_excel.py`: 1/1 | `locust_reportes_excel.py`: no ejecutado contra el módulo |
| Reportes Estadísticos | `test_reportes_estadisticos.py`: 1/1 | `test_integracion_reportes_estadisticos.py`: 1/1 | `test_api_reportes_estadisticos.py`: 1/1 | `test_humo_reportes_estadisticos.py`: 1/1 | `locust_reportes_estadisticos.py`: no ejecutado contra el módulo |
| Usuarios | `test_usuarios.py`: 1/1 | `test_integracion_usuarios.py`: 1/1 | `test_api_usuarios.py`: 1/1 | `test_humo_usuarios.py`: 1/1 | `locust_usuarios.py`: no ejecutado contra el módulo |
| Permisos por Rol | `test_permisos_por_rol.py`: 2/2 | `test_integracion_permisos_por_rol.py`: 1/1 | `test_api_permisos_por_rol.py`: 1/1 | `test_humo_permisos_por_rol.py`: 1/1 | `locust_permisos_por_rol.py`: no ejecutado contra el módulo |
| Administración de Respaldos | `test_administracion_respaldos.py`: 2/2 | `test_integracion_administracion_respaldos.py`: 1/1 | `test_api_administracion_respaldos.py`: 1/1 | `test_humo_administracion_respaldos.py`: 1/1 | `locust_administracion_respaldos.py`: no ejecutado contra el módulo |
| Bitácora | `test_bitacora.py`: 2/2 | `test_integracion_bitacora.py`: 1/1 | `test_api_bitacora.py`: 1/1 | `test_humo_bitacora.py`: 1/1 | `locust_bitacora.py`: no ejecutado contra el módulo |

Las 13 pruebas unitarias transversales corresponden a validación de informes,
controles de reCAPTCHA y listas permitidas de filtros SQL. Los 2 casos extra
de integración cubren auditoría y recuperación ante colisión de ID. La suite
de humo suma un caso para acceso de INVISAP. En el API, PDF/Excel añaden
respectivamente 6/7 casos de formularios parametrizados al caso de endpoint
por módulo.

### Casos representativos de unidad e integración

| ID de seguimiento (provisional) | Nivel | Requerimiento/función observada | Entradas y procedimiento | Resultado esperado / observado | Errores asociados y corrección | Evaluación |
|---|---|---|---|---|---|---|
| UT-GRA-001 | Unidad | Clasificación del nivel de gravedad a partir de criticidad. | Valores parametrizados 0, 50, 51 y 100; invocar `_calcular_nivel_gravedad`. | Límites bajos y altos devuelven respectivamente “Bajo” y “Alto”; los cuatro casos pasaron. | Ningún defecto detectado en esta ejecución; no se necesitó corrección. | Aprobada automáticamente; pendiente de conformidad funcional. |
| UT-GRA-002 | Unidad | Rechazo de criticidad fuera del rango admitido. | Enviar 101 a `set_criticidad`; verificar `ValueError`. | Se rechaza el valor inválido; caso aprobado. | Ningún defecto detectado; sin corrección requerida. | Aprobada automáticamente. |
| IT-ROUTE-01 | Integración | Contrato de la ruta API de Gravedad de Obra. | Inspeccionar `/api/gravedad/listar`, endpoint, método HTTP y construcción de URL Flask. | Ruta y endpoint registrados y URL generada según el contrato; caso aprobado. | Sin error de contrato observado; sin corrección requerida. | Aprobada dentro del alcance del contrato de rutas; no cubre BD. |
| IT-CON-01 | Integración | Registro de contratación y auditoría de la acción. | Enviar POST de contratación usando modelo y servicio de bitácora simulados; verificar llamada de auditoría. | Respuesta esperada y registro `CREAR` en Bitácora; caso aprobado. | Ningún defecto detectado en el flujo simulado; sin corrección requerida. | Aprobada dentro del alcance de los dobles de prueba. |
| IT-CON-02 | Integración | Recuperación ante colisión de identificador al registrar contratación. | Simular colisión de clave primaria y comprobar el reintento con nuevo ID. | El primer error simulado aparece en consola; el reintento termina con registro exitoso. | La colisión es una falla inyectada deliberadamente para probar recuperación, no un defecto pendiente. No se hizo corrección en esta ejecución. | Aprobada; persistencia real pendiente de probar con BD de pruebas. |

### Experiencia de ejecución, errores y acciones

La experiencia de ejecución muestra que los tests parametrizados permiten
repetir entradas límite y que fixtures/dobles mantienen aisladas las llamadas
a modelos y permisos. Esa estrategia produjo resultados reproducibles, pero
no permite concluir que todos los flujos escriben correctamente en MySQL. La
siguiente integración debe ejecutarse en una base de pruebas con transacciones,
datos controlados y rollback/limpieza.

El 05/11 no hubo fallos de aserción en Unidad, Integración, API ni Humo; por
ello no se asignó una corrección nueva a esa ejecución. El mensaje `Duplicate
entry '5'` de `test_registrar_contratacion_reintenta_si_hay_id_duplicado` es
un error inyectado deliberadamente para probar el reintento, no un defecto
pendiente. Las 14 advertencias son deprecaciones de `openpyxl` al usar
`datetime.utcnow()` al generar Excel; no se corrigió una dependencia en esta
ejecución.

El informe PDF del sistema documenta además una corrección anterior del
formulario de acceso: el mensaje incorrecto «Primero debes iniciar sesión» se
mostraba al abrir `GET /login`. La corrección eliminó ese aviso para GET y
conservó el control de POST incompleto; el informe registra HTTP 200 y
verificación por humo/Playwright el 23/10/2026. No hay un ID de incidencia
formal asociado en la evidencia suministrada.

### Registros adicionales de sistema, interfaz y rendimiento

Estos resultados tienen fecha y alcance propios; no se suman a las 138
aprobaciones de Pytest del 05/11:

| Fecha | Tipo y método | Resultado exacto | Errores / corrección / límite |
|---|---|---|---|
| 23/10/2026 | Humo HTTP en vivo: `GET /` y `GET /login`. | Ambas rutas respondieron HTTP 200; el conector de la aplicación ejecutó `SELECT 1` contra MySQL. | No se hicieron escrituras CRUD ni transacciones reales. El acceso falso en GET `/login` se corrigió previamente; no se reportó ID de incidencia. |
| 23/10/2026 | Interfaz: Playwright 1.64 + Chromium; apertura de `/login`. | Aprobada para pantalla de acceso: HTTP 200, título «Sistema Invilara», 1 formulario, 2 campos y sin aviso incorrecto. Evidencia: [playwright_login.png](test-results/playwright_login.png). | No se inició sesión ni se recorrieron los módulos autenticados. El 05/11 el caso actual de UI se omitió por falta de `INVISAP_TEST_URL`. |
| 23/10/2026 | Rendimiento: Locust 2.46.7, `GET /` y `GET /login`, anónimo, 20 usuarios, spawn 2/s, 3m15s de ejecución configurada; 195 s reportados (185 s estables con 20 usuarios). | Criterio documentado: promedio <2 s y 0% errores. Resumen de terminal: 1.880 solicitudes, 0 fallidas, promedio 8 ms, máximo 31 ms. CSV: 1.875 solicitudes, 0 fallidas; promedio 8.250638080002197 ms, mediana 8 ms, mínimo 2.6343999998061918 ms, máximo 31.893100000161212 ms, 9.678561993552991 solicitudes/s; 636 a `/` y 1.239 a `/login`. | Diferencia observada de 5 entre el resumen de terminal y CSV. Aprobada solo para estas dos rutas públicas, no para los 20 módulos ni para flujos autenticados. Evidencia: [locust-rnf-final-20261023_stats.csv](test-results/locust-rnf-final-20261023_stats.csv). |
| 29/10/2026 22:36 (UTC−04:00) | Rendimiento API Solicitudes: escenario `locust_solicitudes.py`; se esperaba HTTP 200. | CSV: 3 solicitudes, 3 fallidas (100%), todas HTTP 401; promedio 15.300266665993453 ms, mediana 7 ms, mínimo 5.088999998406507 ms, máximo 34.30569999909494 ms, 0.9257400196611693 solicitudes/s. | No se registró cookie/sesión de usuario de pruebas en el escenario; el endpoint protegido rechazó solicitudes anónimas. Es una ejecución fallida/inconclusa de rendimiento autenticado, no evidencia suficiente de defecto funcional. No se modificó el código; se requiere cookie de pruebas y retest. Evidencia: [20261029_223612_775569_solicitudes_stats.csv](tests/performance/results/20261029_223612_775569_solicitudes_stats.csv), [20261029_223612_775569_solicitudes_failures.csv](tests/performance/results/20261029_223612_775569_solicitudes_failures.csv). |
| 05/11/2026 | Interfaz y rendimiento contra localhost:5600. | No ejecutados en vivo; TCP `127.0.0.1:5600` no aceptó conexión. | Pytest omitió UI por falta de URL. No se intentó carga Locust sobre un servidor que no estaba activo. |

El intento Locust de Solicitudes no debe presentarse como aprobado ni usarse
para evaluar capacidad/latencia del endpoint: sus 401 reflejan falta de sesión.
Los otros 19 escenarios Locust individuales existen, pero no tienen mediciones
del módulo registradas. El resultado anónimo de `/` y `/login` no los sustituye.

### Bitácora dinámica de rendimiento

Las ejecuciones del perfil por módulo pueden agregarse automáticamente en la
tabla siguiente. La medición general de `/` y `/login` del 23/10 está
documentada arriba, pero no fue generada por el ejecutor por módulo; por eso
no se mezcla en la tabla dinámica.

<!-- PERFORMANCE_RESULTS_START -->
_No hay resultados generados por el ejecutor de perfiles por módulo para esta bitácora. Consulte arriba la carga histórica de `/` y `/login` y el intento no autenticado de Solicitudes. Para una nueva medición, inicie el servidor de pruebas autorizado y ejecute `python tests\performance\run_performance.py --all --profile quick`._
<!-- PERFORMANCE_RESULTS_END -->

## 4.8 Plan de Instalación

### Objetivo y condiciones previas

Instalar INVISAP de manera repetible en un ambiente de validación separado y
verificar que el paquete, la configuración, la base de datos y los servicios
necesarios estén disponibles antes de autorizar su uso. La instalación de
pruebas no debe conectarse a producción ni utilizar sus credenciales o datos
personales.

Antes de comenzar, el responsable técnico debe confirmar y registrar: versión
o commit del código; sistema operativo y versión de Python compatibles;
servidor y versión de MySQL; acceso a los paquetes requeridos; variables de
configuración y secretos suministrados por un canal seguro; ubicación del
respaldo; URL y puerto del ambiente; cuentas/datos de prueba; y responsables
de aplicación, base de datos y aprobación. Las credenciales y valores secretos
no se copian al informe ni al repositorio.

### Secuencia de instalación y verificación

| Paso | Actividad | Responsable | Evidencia / criterio de salida |
|---|---|---|---|
| 1. Preparar | Identificar el artefacto/commit a instalar; reservar un ambiente no productivo; revisar requisitos y puertos; confirmar autorización para pruebas. | Administración técnica y desarrollo, por designar. | Versión, ambiente, fecha y autorización anotados en la bitácora. |
| 2. Respaldar | Generar respaldo de la base destinada a pruebas y comprobar que el archivo sea legible/restaurable según el procedimiento institucional. Si es una instalación inicial, registrar que no hay datos previos que preservar. | Responsable de base de datos, por designar. | Registro del respaldo y resultado de restauración verificada; nunca se reemplaza una copia productiva sin autorización. |
| 3. Instalar dependencias | Crear el ambiente Python aislado e instalar `requirements.txt`. Instalar por separado las dependencias de Locust definidas en `tests\performance\requirements.txt`; instalar Playwright/Chromium según las instrucciones del proyecto solo si se ejecutará UI. | Desarrollo/soporte, por designar. | Instalación completa y versiones registradas; sin incorporar dependencias de prueba al ambiente productivo si no corresponden. |
| 4. Configurar | Proveer configuración local segura para Flask, la base de datos de pruebas y servicios externos; usar datos sintéticos, cuentas con permisos mínimos y URL estable. Mantener secretos fuera del control de versiones. | Administración técnica y base de datos, por designar. | La aplicación inicia y se conecta al ambiente de prueba; una verificación de salud responde según el contrato configurado. |
| 5. Migrar y verificar datos | Aplicar el procedimiento de esquema/migración aprobado y cargar fixtures o datos controlados. No ejecutar altas, bajas o cambios sobre información real. | Responsable de aplicación y base de datos, por designar. | Esquema esperado disponible y datos de prueba identificados; anotar errores o diferencias. |
| 6. Validar versión | Ejecutar unidad, integración, API y humo; comprobar interfaz con `INVISAP_TEST_URL` apuntando al servidor levantado. Después de validar estabilidad y autorización, ejecutar Locust con perfil acordado; efectuar aceptación con usuarios al final. | Desarrollo y validadores funcionales, por designar. | Guardar salida, XML/CSV/capturas, fecha, entorno, perfil y resultado; no declarar aprobada una categoría omitida o no ejecutada. |
| 7. Aceptar o revertir | Comparar resultados con criterios de salida; corregir y repetir pruebas afectadas. Si hay un defecto bloqueante, detener liberación y restaurar el artefacto/base previos siguiendo el procedimiento institucional. | Responsable técnico y validador institucional, por designar. | Acta de aceptación o registro de rechazo, defectos, retest y reversión si aplica. |

Las versiones de dependencias, migraciones y procedimiento real de despliegue
deben ajustarse al entorno institucional; no se afirma aquí que se haya
instalado en producción. La fecha, lugar y responsables de una instalación
formal quedan por coordinar.

## 4.9 Plan de Capacitación

### Justificación y objetivos

La capacitación permitirá que desarrollo/soporte, administración técnica y
usuarios validadores ejecuten sus tareas sin confundir los resultados
automatizados con la aceptación funcional. El objetivo general es preparar a
los participantes para utilizar los módulos de INVISAP, reconocer permisos y
flujos de trabajo, registrar incidencias y validar resultados con datos de
prueba.

Al finalizar, se espera que cada perfil pueda: (1) navegar los módulos que le
corresponden; (2) completar los flujos y validar salidas según criterios
acordados; (3) reportar errores con pasos reproducibles y evidencia; y
(4) consultar las guías de respaldo, seguridad y soporte según sus permisos.
Estos son resultados esperados de una capacitación futura, no resultados ya
obtenidos.

### Metodología y recursos

Se propone una introducción de 30 minutos, seguida de ocho talleres prácticos.
Cada taller combina explicación breve, demostración del facilitador,
ejercicios guiados con cuentas y datos sintéticos, práctica individual o por
rol, preguntas y una comprobación final. Se recogerán asistencia,
observaciones y evaluación; los responsables, la duración de cada taller, las
fechas y el lugar se coordinarán con la institución. Como recursos se
requieren una instancia de pruebas accesible, computadoras y navegador,
proyector o guía digital, cuentas de prueba con permisos diferenciados,
conjunto de datos sintéticos y formatos de especificación/bitácora. No se
utilizarán datos ni credenciales de producción.

### Plan de acción propuesto

| Sesión / objetivo | Actividades y temáticas | Recursos | Responsables | Fecha / duración | Lugar | Observaciones / evaluación |
|---|---|---|---|---|---|---|
| Introducción: conocer propósito, perfiles y reglas de uso. | Presentación del sistema, acceso al ambiente de prueba, roles, seguridad y método para pedir soporte. | Instancia de pruebas, proyector y guía. | Facilitador técnico y coordinador institucional, por designar. | Fecha por coordinar; 30 min propuestos. | Por coordinar. | Confirmar participantes y asistencia; acordar reglas de uso de datos sintéticos. |
| Taller 1: administrar acceso según rol. | Ingreso y navegación de Usuarios y Permisos por Rol; comprobar acceso autorizado y registrar intento no permitido. | Cuentas de prueba con roles, navegador y casos guiados. | Facilitador y responsable funcional, por designar. | Por coordinar; duración por acordar. | Por coordinar. | No usar cuentas productivas; revisar comprensión de permisos. |
| Taller 2: gestionar solicitudes y su clasificación. | Crear/consultar Solicitudes; asignar Gravedad de Obra y Prioridad según reglas acordadas. | Datos sintéticos y guía de flujos. | Facilitador y responsables de esos módulos, por designar. | Por coordinar; duración por acordar. | Por coordinar. | Comparar salida con criterios funcionales aprobados. |
| Taller 3: consultar y actualizar información de obras. | Recorrido de Proyectos, Obras e Informe de Avance de Obra; consultar estados e ingresar información permitida. | Proyecto de demostración, cuenta de prueba y guía. | Facilitador y usuarios de obras, por designar. | Por coordinar; duración por acordar. | Por coordinar. | No introducir datos reales; registrar hallazgos. |
| Taller 4: administrar recursos y contratación. | Ejercicios de Empresa, Empleados, Maquinaria y Contratación; revisar relaciones entre registros y permisos. | Conjunto de datos sintéticos y ambiente de pruebas. | Facilitador y responsables de recursos/contratación, por designar. | Por coordinar; duración por acordar. | Por coordinar. | Verificar flujo de extremo a extremo con datos de práctica. |
| Taller 5: registrar seguimiento de campo. | Consultar/registrar Inspecciones y asociar Evidencias de ejemplo. | Archivos sintéticos no sensibles, cámara/archivos de muestra si aplica. | Facilitador y responsables de inspección, por designar. | Por coordinar; duración por acordar. | Por coordinar. | Evaluar permisos, carga y consulta de evidencia. |
| Taller 6: consultar y publicar información. | Recorrido de Publicaciones, ciclo de consulta y reglas de comunicación institucional. | Cuenta de prueba, navegador y contenido de demostración. | Facilitador y responsable de publicaciones, por designar. | Por coordinar; duración por acordar. | Por coordinar. | Usar contenido ficticio; identificar quién autoriza publicaciones. |
| Taller 7: generar y revisar reportes. | Ejecutar Reportes PDF, Reportes Excel y Reportes Estadísticos; revisar filtros, contenido y descarga. | Datos sintéticos, lector PDF y hoja de cálculo. | Facilitador y usuarios de reportes, por designar. | Por coordinar; duración por acordar. | Por coordinar. | Comprobar resultados con una muestra esperada. |
| Taller 8: soporte, auditoría y continuidad. | Consultar Bitácora, revisar Administración de Respaldos, reportar incidencia y practicar lectura del plan de reversión (sin restaurar producción). | Ambiente de prueba, guía de soporte y respaldo de práctica. | Facilitador técnico y responsable de infraestructura, por designar. | Por coordinar; duración por acordar. | Por coordinar. | La restauración solo se demuestra en ambiente autorizado; registrar evaluación final y pendientes. |

Este plan es una propuesta para completar con el formato institucional. No se
reportan fechas, asistentes, nombres de facilitadores ni resultados de
capacitación porque no se suministró evidencia de sesiones realizadas.

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
   rendimiento con la comunidad; conservar CSV y bitácora por versión.
6. Revisar periódicamente las 14 advertencias reportadas por pytest y
   actualizar dependencias de forma planificada, validando compatibilidad.
7. Repetir las pruebas de humo después de instalar una versión y las de unidad,
   integración y sistema después de cada cambio significativo.

## Referencias metodológicas

- Célad Álvarez, A. y Ruíz Calle, J. D. (2009). *Metodologías de testing de
  software y su aplicación en el Centro de Informática de la Universidad
  EAFIT*. Universidad EAFIT. Documento suministrado para esta planificación;
  se adaptan sus niveles de prueba (pp. 44–60) y técnicas de caja negra, caja
  blanca, interfaz y desempeño (pp. 60–75).
- *Manual Informe de Proyecto III*, documento suministrado. Estructura usada:
  p. 3: Plan de Pruebas, Bitácora, Plan de Instalación, Plan de Capacitación y
  recomendaciones/evolución.
- *Informe del Sistema INVILARA - Proyeto III.pdf* (nombre exacto del archivo
  suministrado), pp. 143–152:
  plataforma Flask/Python, estrategia de pruebas, resultados históricos y
  limitaciones de interfaz, persistencia y rendimiento. Sus fechas y métricas
  se conservan separadas de la ejecución Pytest del 05/11/2026.
- Formatos de planificación y especificación de pruebas compartidos por el
  solicitante. Las hojas de cálculo editables de este repositorio los adaptan
  y amplían con trazabilidad y evidencia automatizada.
- Formato de Plan de Capacitación suministrado, pp. 3–9: estructura de
  objetivos, metodología de talleres y plan de acción. Los ocho talleres de
  este capítulo son una propuesta adaptada a los módulos de INVISAP, pendiente
  de aprobación y calendarización institucional.
- PFC de Nuria suministrado: ciclo de vida de pruebas de integración
  (planificación, análisis/diseño, implementación/ejecución, evaluación,
  cierre y mejora continua), adaptado a la organización incremental del plan.
  Otro documento PFC cifrado no se usó como fuente porque no se pudo leer.
- Pytest Documentation; Locust Documentation; Playwright Documentation.
