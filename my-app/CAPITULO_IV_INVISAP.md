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
| Unidad | Caja blanca sobre ramas/reglas y caja negra sobre entradas/salidas. Definir particiones de equivalencia y valores límite, parametrizar casos válidos e inválidos, y ejecutar Preparar-Actuar-Verificar con fixtures/mocks. | Pytest, `pytest.mark.parametrize`, fixtures y mocks; datos representativos y extremos. | `tests/unit`. Evalúa funciones aisladas; no acredita persistencia ni despliegue. |
| Integración | Integración incremental en dos vías: contratos de rutas para verificar ensamblaje Flask y pruebas de flujo vertical Contratación→Bitácora; inyectar una colisión de ID para ejercitar recuperación/reintento. Los dobles aíslan servicios externos. La siguiente etapa es integración con MySQL de pruebas y rollback/limpieza. | Pytest, cliente Flask, mocks y fallo controlado. | `tests/integration`: 20 contratos y 2 casos de flujo. No equivale a validar una base de datos real. |
| Backend/API | Pruebas de contrato por petición HTTP: clases positivas/negativas, códigos, JSON, autenticación/autorización, filtros, paginación y parámetros propagados al servicio/modelo. PDF/Excel se prueban como formularios HTTP, no como JSON. | Pytest y cliente Flask con modelos simulados; Postman se reserva para exploración del despliegue. | `tests/api`. Los casos locales no sustituyen una prueba de API desplegada con datos reales autorizados. |
| Humo | Selección basada en riesgo de una ruta esencial por módulo y verificación rápida de que la aplicación la atiende sin 404/500. Un redirect de autenticación solo confirma disponibilidad de ruta, no funcionalidad autenticada. | Pytest y cliente Flask; navegador puede complementar la ruta crítica. | `tests/smoke`. Detecta fallos gruesos, no demuestra reglas de negocio ni cobertura exhaustiva. |
| Interfaz | Prueba de extremo a extremo desde navegador: cargar pantalla, comprobar respuesta/elementos visibles/estados, guardar captura y evitar mutaciones. Separar evidencia de UI de la aceptación funcional del usuario. | Playwright + Chromium y `INVISAP_TEST_URL`; Selenium es alternativa si se configura. | `tests/ui`: un caso de acceso. Requiere servidor externo activo y Chromium. |
| Rendimiento | Prueba no funcional de lectura con línea base, carga, estrés y pico; comparar concurrencia, rendimiento, fallos y percentiles, manteniendo perfil/datos/ambiente controlados. No declarar aprobación sin umbrales acordados. | Locust, perfiles `quick`, `baseline`, `stress`, `spike`, datos no destructivos y cookie de cuenta de pruebas. | `tests/performance`. Hay escenarios por módulo, pero no una medición contra INVISAP en esta ejecución. |
| Aceptación | Caja negra guiada por requisito e historia: Dado/Cuando/Entonces, flujo completo, resultado observable y evaluación del usuario validador. Registrar rechazados, corrección, retest y firma. | Playwright/Selenium para evidencia del recorrido y formato de especificación firmado. | Pendiente: faltan criterios aprobados y validador/evidencia de usuarios; no se declara aceptación completada. |

### Planificación de Unidad, Integración y Sistema

La tabla siguiente constituye el plan de trabajo. Las fechas futuras, el lugar
de validación y los nombres del responsable funcional deben completarse con el
tutor y los usuarios de la institución antes de una validación formal.

| Nivel | Objetivo específico | Actividades | Lugar / fecha | Responsables | Evidencia / estado |
|---|---|---|---|---|---|
| Unidad | Evaluar reglas y validadores aislados. | Particiones válidas/inválidas, límites, parametrización, mocks y contraste esperado/observado. | Ejecución local automatizada, 2026-11-01 02:59:58–03:00:07 (UTC−04:00). | Equipo de desarrollo ejecutó; validador funcional por designar. | 62/62 aprobadas; sin aserciones fallidas. |
| Integración | Comprobar contratos Flask y colaboración de módulos. | 20 contratos de ruta; 2 flujos Contratación/Bitácora, incluido error de duplicado inyectado y reintento. | Ejecución local automatizada, 2026-11-01. | Equipo de desarrollo ejecutó; DBA/tutor deberá validar conexión real. | 22/22 aprobadas; la conexión/persistencia real de MySQL no queda certificada por esta suite. |
| Sistema | Verificar el sistema ensamblado desde HTTP/UI y planificar propiedades no funcionales y aceptación. | Ejecutar backend/API y humo; cubrir UI cuando haya URL/browser; rendimiento Locust contra servidor de pruebas; validar aceptación con requisitos aprobados. | Ejecución local automatizada para API/humo; UI, Locust y aceptación requieren ambiente/usuarios. | Equipo de desarrollo ejecutó; responsables funcionales pendientes de designación. | API 33/33; humo 21/21; UI 0/1 (omitida); rendimiento y aceptación pendientes de validación contra sistema/usuarios. |

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

- **Fecha y hora:** 2026-11-01, 02:59:58–03:00:07 (UTC−04:00).
- **Ambiente:** ejecución local automatizada en Windows, Python 3.14.7 y
  pytest 9.1.1.
- **Responsable técnico:** equipo de desarrollo (ejecución automatizada).
- **Validador funcional:** pendiente de designación y firma del tutor/usuarios
  responsables.
- **Alcance de datos:** los casos de unidad, API y flujos integrados usan
  fixtures/dobles para aislar dependencias; esta ejecución no certifica
  persistencia contra una base real.
- **Comando:** `python -m pytest --junitxml=<archivo-temporal>`; el XML
  permitió separar los resultados por carpeta sin ejecutar pruebas distintas.
- **Duración:** 5.07 s informados por pytest; 8.49 s de duración total del
  proceso de prueba y recolección de resultados.

### Resultados observados

| Nivel / categoría | Comando ejecutado | Resultado | Duración | Observaciones |
|---|---|---:|---:|---|
| Unidad | `python -m pytest --junitxml=<archivo-temporal>` (grupo `tests\unit`) | 62 aprobadas, 0 fallidas, 0 omitidas | Incluida en 5.07 s | 20 módulos y 13 pruebas transversales (validación, seguridad y filtros). |
| Integración | Mismo comando (grupo `tests\integration`) | 22 aprobadas, 0 fallidas, 0 omitidas | Incluida en 5.07 s | 20 contratos de ruta y 2 escenarios integrados Contratación/Bitácora; no valida MySQL real. |
| Backend/API | Mismo comando (grupo `tests\api`) | 33 aprobadas, 0 fallidas, 0 omitidas | Incluida en 5.07 s | 20 módulos y 13 casos parametrizados de reportes. |
| Humo | Mismo comando (grupo `tests\smoke`) | 21 aprobadas, 0 fallidas, 0 omitidas | Incluida en 5.07 s | 20 módulos y pantalla de acceso; respuesta básica HTTP, no flujo integral. |
| Interfaz | Mismo comando (grupo `tests\ui`) | 0 aprobadas, 0 fallidas, 1 omitida | Incluida en 5.07 s | Omitida por falta de `INVISAP_TEST_URL`; no se ejecutó en navegador. |
| Rendimiento | `python tests\performance\run_performance.py --all --profile quick` | No ejecutado contra INVISAP | — | Escenarios creados, pero no se midió el servidor del producto en esta ejecución. |
| Aceptación | Recorrido de usuario según requisito aprobado | Pendiente | — | Sin criterios validados ni aprobación/evidencia de usuario. |

La ejecución completa recogió **138 aprobadas, 0 fallidas y 1 omitida** en
5.07 s (pytest), con **14 advertencias**. Las advertencias son `DeprecationWarning`
de `openpyxl` al usar `datetime.datetime.utcnow()` durante la escritura de
archivos Excel; no son fallos de aserción. El caso de interfaz se omitió por
falta de URL, y no se inventan resultados para rendimiento ni aceptación.

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

### Casos representativos de unidad e integración

| ID de seguimiento (provisional) | Nivel | Requerimiento/función observada | Entradas y procedimiento | Resultado esperado / observado | Errores asociados y corrección | Evaluación |
|---|---|---|---|---|---|---|
| UT-GRA-001 | Unidad | Clasificación del nivel de gravedad a partir de criticidad. | Valores parametrizados 0, 50, 51 y 100; invocar `_calcular_nivel_gravedad`. | Límites bajos y altos devuelven respectivamente “Bajo” y “Alto”; los cuatro casos pasaron. | Ningún defecto detectado en esta ejecución; no se necesitó corrección. | Aprobada automáticamente; pendiente de conformidad funcional. |
| UT-GRA-002 | Unidad | Rechazo de criticidad fuera del rango admitido. | Enviar 101 a `set_criticidad`; verificar `ValueError`. | Se rechaza el valor inválido; caso aprobado. | Ningún defecto detectado; sin corrección requerida. | Aprobada automáticamente. |
| IT-ROUTE-01 | Integración | Contrato de la ruta API de Gravedad de Obra. | Inspeccionar `/api/gravedad/listar`, endpoint, método HTTP y construcción de URL Flask. | Ruta y endpoint registrados y URL generada según el contrato; caso aprobado. | Sin error de contrato observado; sin corrección requerida. | Aprobada dentro del alcance del contrato de rutas; no cubre BD. |
| IT-CON-01 | Integración | Registro de contratación y auditoría de la acción. | Enviar POST de contratación usando modelo y servicio de bitácora simulados; verificar llamada de auditoría. | Respuesta esperada y registro `CREAR` en Bitácora; caso aprobado. | Ningún defecto detectado en el flujo simulado; sin corrección requerida. | Aprobada dentro del alcance de los dobles de prueba. |
| IT-CON-02 | Integración | Recuperación ante colisión de identificador al registrar contratación. | Simular colisión de clave primaria y comprobar el reintento con nuevo ID. | El primer error simulado aparece en consola; el reintento termina con registro exitoso. | La colisión es una falla inyectada deliberadamente para probar recuperación, no un defecto pendiente. No se hizo corrección en esta ejecución. | Aprobada; persistencia real pendiente de probar con BD de pruebas. |

### Experiencia de ejecución, errores y acciones

Durante la ejecución se observó que los fixtures y dobles permiten reproducir
validaciones, contratos HTTP y colaboración entre componentes sin tratar el
resultado como prueba de persistencia real. Para completar esa evidencia debe
ejecutarse una fase de integración con una base de datos de pruebas y rollback/
limpieza de datos.

No se detectaron fallos de aserción en Unidad ni Integración en la ejecución
del 2026-11-01; tampoco hubo fallos de aserción en API ni Humo. En consecuencia,
no se atribuye una corrección de código a los resultados de esta ejecución. El
mensaje `Duplicate entry '5'` que aparece en
`test_registrar_contratacion_reintenta_si_hay_id_duplicado` es el error
inyectado por el caso para comprobar que el modelo reintenta con otro ID; el
resultado final fue aprobado (2/2 casos del archivo integrador). Las 14
advertencias de `openpyxl` se originan en el uso obsoleto de `utcnow()` al
generar Excel; no se modificó esa dependencia porque no causó un fallo de
producto y no se realizó una corrección en esta ejecución.

### Bitácora dinámica de rendimiento

Las ejecuciones reales de Locust se agregan en las filas siguientes. Si la
tabla está vacía, significa que todavía no se ha medido el servidor INVISAP.

<!-- PERFORMANCE_RESULTS_START -->
_Sin ejecuciones registradas contra INVISAP. Inicie el servidor de pruebas y ejecute `python tests\performance\run_performance.py --all --profile quick`._
<!-- PERFORMANCE_RESULTS_END -->

## 4.8 Plan de Instalación

1. Identificar versión de código, configuración y respaldo de la base de
   datos; preparar una instalación aislada de pruebas.
2. Instalar dependencias del sistema (`pip install -r requirements.txt`),
   Locust (`pip install -r tests\performance\requirements.txt`) y, para UI,
   Playwright/Chromium conforme a las instrucciones de pruebas.
3. Configurar la conexión a una base de datos de pruebas, URL de la aplicación
   y cuentas/datos controlados. No reutilizar cookies ni credenciales de
   producción.
4. Ejecutar en orden unidad, integración, API, humo e interfaz; ejecutar
   rendimiento después de comprobar estabilidad y autorización del ambiente.
5. Realizar respaldo y verificar restauración conforme al procedimiento
   institucional antes de poner una versión en servicio.
6. Registrar versión, fecha, responsables, incidentes y resultado de cada
   actividad; mantener reversión documentada.

## 4.9 Plan de Capacitación

Capacitar por perfiles antes de la aceptación:

- **Desarrollo/soporte:** ejecutar comandos por categoría, parametrizar casos,
  interpretar fallos y warnings, inspeccionar bitácoras y hacer retest.
- **Administración de infraestructura:** instalar dependencias, preparar el
  ambiente separado, revisar logs, respaldar/restaurar datos y controlar las
  cargas de Locust.
- **Usuarios validadores:** recorrer historias funcionales, ingresar datos de
  prueba, comparar resultado observado con criterios acordados y registrar
  aprobación o rechazo en las plantillas.

La asistencia, fecha, contenido y responsable de cada capacitación deben
registrarse en el formato institucional; esos datos no fueron proporcionados
para esta edición.

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
- Formatos de planificación y especificación de pruebas compartidos por el
  solicitante. Las hojas de cálculo editables de este repositorio los adaptan
  y amplían con trazabilidad y evidencia automatizada.
- Pytest Documentation; Locust Documentation; Playwright Documentation.
