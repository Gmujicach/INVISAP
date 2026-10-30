# CAPÍTULO IV. RECOMENDACIONES Y EVOLUCIÓN PREVISIBLE DEL SISTEMA

## Introducción

El Sistema Invilara (INVISAP) automatiza procesos de solicitudes, obras,
inspecciones, contrataciones, evidencias, informes y reportes de la institución.
Este capítulo plantea acciones para mantenerlo seguro y operativo, y una
evolución gradual basada en las actividades registradas en la Agenda JAD y en
las pruebas que fue posible ejecutar en el entorno disponible.

La información de avance se contrastó con la [Agenda JAD de Invilara](https://trello.com/b/3QYNygGb/agenda-jad-invilara), el *Manual Informe de Proyecto III.pdf*, el *Formato del Plan de Capacitación.pdf*, *Pruebas de auditorías del Sistema.pdf* y *Requisitos No funcionales 2026.pdf*.

## 4.1 Recomendaciones

1. **Cerrar la verificación de seguridad antes de aprobar la instalación.**
   Mantener activa la validación de reCAPTCHA y configurar su secreto fuera del
   código. Revisar manualmente las alertas Bandit de consultas SQL dinámicas;
   conservar parámetros para los valores y listas permitidas para nombres de
   tablas y columnas.
2. **Completar las pruebas con la infraestructura real.** La suite automatizada
   ejecutada usa dobles de prueba para aislar la base de datos. Antes de aceptar
   el producto se debe validar lectura, escritura, permisos, reportes y
   restauración contra la instancia MySQL de Invilara.
3. **Formalizar copias de seguridad y recuperación.** Establecer periodicidad,
   responsable, ubicación protegida y retención de respaldos; ejecutar una
   restauración de prueba y dejar constancia del resultado.
4. **Proteger la configuración de despliegue.** Cambiar las contraseñas de
   ejemplo del archivo Compose por secretos propios del servidor, mantenerlos
   fuera del repositorio y restringir el acceso al archivo `.env`.
5. **Completar las evidencias del informe.** Añadir capturas propias de las
   pruebas, la instalación y la capacitación. No presentar una prueba
   planificada como si ya se hubiera ejecutado.
6. **Mantener el manual y la capacitación al día.** Actualizar los pasos cuando
   cambien módulos, roles, permisos o pantallas, y recoger la evaluación de las
   personas usuarias.
7. **Revisar avisos de dependencias.** La ejecución actual terminó sin fallos,
   pero emitió avisos de obsolescencia originados por `openpyxl` al usar
   `datetime.utcnow()`. Revisar una actualización compatible de la dependencia
   y repetir las pruebas antes de cambiar la versión fijada.

## 4.2 Evolución previsible

| Horizonte propuesto | Evolución | Condición para avanzar |
|---|---|---|
| Corto plazo | Completar pruebas con MySQL, verificar autorización por rol, probar los flujos principales y cerrar la revisión de las alertas SAST. | Base de datos disponible, credenciales de producción configuradas y acta de resultados. |
| Corto plazo | Ejecutar una prueba de carga controlada y medir tiempos, errores, CPU y memoria. | Servidor de pruebas autorizado, datos no productivos y métricas guardadas. |
| Mediano plazo | Mejorar índices y consultas de reportes de acuerdo con mediciones; evaluar caché solo donde los datos y permisos lo permitan. | Cuellos de botella demostrados por mediciones, no supuestos. |
| Mediano plazo | Formalizar pruebas de aceptación y usabilidad con personal de Invilara; conservar resultados y solicitudes de mejora. | Participantes, tareas y encuesta SUS acordados con la institución. |
| Continuo | Mantener módulos, manual, recorridos interactivos, respaldos y controles de acceso conforme cambien los procesos institucionales. | Responsable técnico y calendario de mantenimiento definidos. |

La evolución debe ser incremental. Las funciones descritas en el tablero como
mejoras de solicitudes, obras, archivos, vistas de detalle, filtros, reportes,
validaciones y diseño adaptable constituyen una base de mantenimiento; el
tablero no asigna fecha ni responsable individual a cada una de esas notas, por
lo que no se les atribuye aquí una fecha de cierre.

## 4.3 Estado de preparación para aprobación

En la repetición del **23/10/2026**, la aplicación respondió HTTP 200 en `/` y
`/login`; el conector de INVISAP se conectó a MySQL y ejecutó `SELECT 1`. La
suite automatizada pasó y la prueba Locust alcanzó 20 usuarios durante 3
minutos sin errores en las rutas `/` y `/login`, dentro del alcance medido.
**Estos resultados no certifican por sí solos la aprobación del sistema:**
las pruebas de integración y API con pytest siguen usando modelos simulados,
no se recorrieron flujos autenticados de extremo a extremo, Bandit mantiene
alertas medias y bajas por revisar y falta la aceptación formal del personal.
La aceptación final corresponde a la comunidad y a la evaluación académica.

## 4.4 Trazabilidad de actividades registradas en la Agenda JAD

La tabla resume las 27 tarjetas de la lista **Fechas** y las tarjetas de
responsables y observaciones relacionadas. Cuando la Agenda JAD no identifica a
una persona, se conserva la asignación colectiva o por rol; no se deduce un
responsable individual. Las fechas corresponden a lo escrito en las tarjetas,
no a la última fecha en que se editó una tarjeta.

| Fecha indicada en Trello | Actividad realizada | Responsable(s) que registra el tablero | Observación registrada |
|---|---|---|---|
| 06/04/2026 | Entrevista inicial para levantar información de la comunidad. | Equipo de proyecto. | Se realizó el primer encuentro y la entrevista. |
| 07/04/2026 | Diagnóstico e instrumento de recolección de datos. | Equipo de proyecto. | Se reunieron evidencias de la visita y la historia hablada. |
| 08/04/2026 | Cuadro de procesos del negocio. | Líder, analista y especialistas. | Se realizó el cuadro de procesos. |
| 09/04/2026 | Caso de uso del negocio y diagramas de actividades. | Líder, analista y especialistas. | Se elaboraron los diagramas del negocio. |
| 10–11/04/2026 | Plantillas IBM del negocio. | Equipo de proyecto. | Los cortes de electricidad retrasaron el trabajo; se culminó el sábado 11. |
| 14/04/2026 | Visita a la comunidad para continuar el levantamiento de información. | Equipo de proyecto y tutora académica. | La visita fue realizada con acompañamiento de la tutora. |
| 16/04/2026 | Actualización del cuadro de procesos y modelado del negocio. | Equipo de proyecto. | Se comenzó la actualización a partir de la información recabada. |
| 23/04/2026 | Capítulo I del informe. | Equipo de proyecto. | El tablero registra la elaboración del capítulo I. |
| 26/04/2026 | Diseño preliminar de la base de datos. | Líder, especialistas y uno de los desarrolladores. | Se comenzó a planificar el diseño de la base de datos. |
| 01/05/2026 | Modelo entidad-relación (MER). | Especialistas, analista, programador y líder. | El equipo se reunió para elaborar el MER. |
| 07/05/2026 | Documento SRS del sistema. | Equipo de proyecto. | Se elaboró el documento de requisitos del sistema. |
| 08/05/2026 | Inicio del caso de uso del sistema. | Un especialista y el líder. | Se comenzó el diseño; la tarjeta también registra una imagen preliminar del caso de uso. |
| 09/05/2026 | Capítulo II del informe. | El tablero no individualiza responsables para esta fecha. | La lista Fechas registra elaboración del capítulo II. |
| 13/05/2026 | Continuación del caso de uso del sistema. | Un especialista y el líder. | Se retomó el diseño del caso de uso. |
| 16/05/2026 | Capítulo II del informe. | Especialistas y líder. | Se registra otra jornada de elaboración del capítulo II. |
| 17/05/2026 | Cronograma de actividades / diagrama de Gantt. | Gabriel Mujica y el líder. | Se elaboró el cronograma del sistema. |
| 19/05/2026 | Actualización del modelado del sistema. | Equipo de proyecto, distribuido por rol. | David actualizó caso de uso y MER; Freider y Eliot, actividades; Frangher y Gabriel, plantillas IBM. |
| 25/05/2026 | Base de datos, actualización del SRS y diagrama de clases. | Equipo de proyecto. | Se registran los tres productos: base de datos, SRS y diagrama de clases. |
| 01/06/2026 | Continuación del desarrollo con correcciones de modelado de base de datos. | Equipo de proyecto: Frangher, Gabriel, Eliot, Freider y líder, por módulo. | Frangher: gerencias; Gabriel: solicitudes; Eliot: publicaciones; Freider: proyectos, maquinaria y contrataciones; líder: usuarios y reportes. |
| 10/06/2026 | Asesoría de modelado de base de datos. | Equipo de proyecto y profesor José Cadenas. | Asesoría para aplicar reglas al diagrama. |
| 12/06/2026 | Asesoría de modelado de base de datos. | Equipo de proyecto y profesor José Cadenas. | Se recibieron recomendaciones. |
| 13/06/2026 | Asesoría virtual de modelado de base de datos. | Equipo de proyecto y profesor José Cadenas. | Se ajustó el diagrama aplicando reglas de normalización. |
| 12–14/06/2026 | Finalización de módulos transaccionales. | Equipo de proyecto. | Se prepararon los módulos para la defensa indicada el 15/06. |
| 15/06–09/07/2026 | Correcciones del sistema para el conversatorio. | Equipo de proyecto, con tareas por rol. | David corrigió empleados, evidencias e informes de avance; Frangher, empresas y contrataciones; Freider, proyectos, maquinaria, respaldos y bitácora; Eliot, publicaciones, inspecciones y empresas; Gabriel, solicitudes y obras. Las observaciones fechadas señalan avances entre el 18/06 y el 09/07. |
| 07–08/07/2026 | Inclusión del manual de usuario y ayuda interactiva. | Equipo de proyecto. | Se añadió el acceso al manual en el menú lateral. |
| 10/07–01/09/2026 | Continuación del sistema, del 60 % al 100 % según la tarjeta. | Equipo de proyecto. | Las observaciones incluyen cambios de base de datos, mejoras de solicitudes y obras, gestión de archivos, detalles relacionales, filtros, reportes, validaciones, diseño adaptable y recorridos guiados. Las notas no asignan fecha individual a cada mejora. |
| 07/09/2026 | Visita, instalación local y capacitación inicial en la institución. | Equipo de proyecto y tutora Ing. Jhoanly Hernandez. | Se instaló en el servidor local disponible de Invilara. El tablero menciona fotos como tarea, pero no se encontraron archivos adjuntos. |

**Dato incompleto:** otra observación de asesoría dice “el día 27” sin mes ni año.
No se le asigna una fecha exacta hasta confirmarla con el equipo. El tablero
también deja como próxima tarea las pruebas de auditoría; no se encontraron
resultados de esa actividad en la agenda.

---

## 4.5 Plan de Pruebas

La profesora indicó que los planes y resultados de pruebas pertenecen a este
capítulo, aunque el manual los ubique por error en el Capítulo III. Por ello,
el plan de pruebas, su bitácora, el plan de instalación y el plan de
capacitación se presentan aquí.

### Objetivo y alcance

Comprobar, antes de la aceptación, las funciones del backend Flask, las rutas
HTTP, los reportes, los controles de acceso y los requisitos no funcionales de
seguridad, rendimiento, usabilidad y fiabilidad. Para las pruebas automatizadas
se utiliza **pytest con `app.test_client()`**; Postman puede complementar la
verificación manual de API. No se emplean PHPUnit ni otras herramientas de PHP.

### Entorno y criterio general

- Proyecto Flask con MySQL; la aplicación arranca en el puerto **5600** según
  `run.py`.
- Pruebas ejecutadas en Windows, Python **3.14.7**, pytest **9.1.1**.
- Los modelos y permisos se simularon en los casos de prueba que necesitan una
  sesión, por lo que esos resultados no sustituyen una prueba con la base de
  datos real.
- Se considera aprobado un caso si cumple el resultado esperado sin errores
  inesperados. Los criterios cuantitativos de rendimiento se especifican en la
  tabla siguiente.

### Casos y resultados por categoría

El sistema INVISAP está desarrollado en **Python/Flask**. Las herramientas de PHP (PhpUnit, Codeception, Guzzle) no aplican al presente proyecto. Para las pruebas se utilizaron las herramientas indicadas para Python.

| ID | Categoría | Herramienta(s) utilizada(s) | Caso probado / Alcance | Criterio de aceptación | Comando / Evidencia | Resultado / Límites medidos |
|---|---|---|---|---|---|---|
| PT-01 | **Pruebas unitarias** | PyTest (`pytest 9.1.1`) | Validaciones de informes y filtros SQL permitidos. | Resultado esperado ante entradas válidas e identificadores no permitidos. | `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_informe_validacion.py tests\\test_sql_filter_allowlists.py -o addopts= -q --tb=short` | **Aprobada:** 11/11 pruebas. Sin fallas. |
| PT-02 | **Pruebas de integración** | PyTest + `app.test_client()` (con dobles de prueba) | Contratación auditada y reintento ante ID duplicado. | Respuesta y auditoría esperadas; transacción controlada. | `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_contrataciones_bitacora.py -o addopts= -q --tb=short` | **Aprobada:** 2/2 pruebas con dobles. Conector real ejecutó `SELECT 1` a MySQL, pero no se validaron escrituras/transacciones reales en datos institucionales. |
| PT-03 | **Pruebas de Backend/API** | PyTest + cliente Flask de la app. Postman evaluado (no instalado en entorno). | Endpoints de reportes y validación de filtros. | HTTP correcto y filtros entregados al modelo esperado. | `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_parametrizacion_reportes.py -o addopts= -q --tb=short` | **Aprobada:** 13/13 pruebas con modelos simulados. Se verificó vía cliente Flask (Postman pendiente en entorno institucional). |
| PT-04 | **Pruebas de Humo** | PyTest. Verificación HTTP en vivo. | `GET /login` sin errores de servidor; corrección del aviso falso "Primero debes iniciar sesión". | HTTP 200 y página de acceso sin aviso de sesión requerido al abrirla por GET. | `.\\.venv\\Scripts\\python.exe -m pytest tests\\test_security_controls.py::RecaptchaSecurityTestCase::test_login_page_responds_without_server_error -o addopts= -q --tb=short` + verificación HTTP en vivo (`GET /`, `GET /login`) | **Aprobada:** 1 prueba PyTest + HTTP 200 en rutas verificadas. Aviso falso corregido. |
| PT-05 | **Pruebas de Interfaz** | Playwright 1.64.0 (Chromium). Selenium instalado pero no utilizado para esta ejecución. | Apertura de `/login`, presencia de formulario/campos, ausencia de aviso falso. | HTTP 200, formulario visible, controles presentes, sin aviso incorrecto. | Terminal 1: `.\.venv\Scripts\python.exe run.py` / Terminal 2: `.\.venv\Scripts\python.exe .\tests\playwright_ui_smoke.py` | **Aprobada para pantalla de acceso:** 1 formulario, 2 campos. Evidencia: `my-app/test-results/playwright_login.png`. Sin navegación autenticada. |
| PT-06 | **Pruebas de Aceptación** | PyTest + Playwright + validación guiada con usuarios de Invilara (propuesto) | Flujos completos acordados por la institución con roles/permisos reales. | Conformidad documentada en acta de aceptación firmada. | Pendiente de ejecución con cuentas reales. | **Pendiente:** No se ejecutaron con usuarios/acta. Las pruebas técnicas no sustituyen la aceptación formal. |
| PT-07 | **Pruebas de Rendimiento (No funcionales)** | Locust 2.46.7 (`locustfile.py`) | Carga sobre `GET /` y `GET /login` (usuarios anónimos). | RNF: 20 usuarios / 3 minutos; promedio < 2 s; 0% errores. | `.\.venv\Scripts\locust.exe -f locustfile.py --headless -H http://127.0.0.1:5600 -u 20 -r 2 --run-time 3m15s --stop-timeout 10 --csv test-results\locust-rnf-final-20261023 --only-summary` | **Aprobada para estas rutas:** 195 s totales (185 s estables con 20 usuarios). Resumen: 1.880 solicitudes, 0 fallidas (0%), promedio 8 ms, máx. 31 ms. CSV: 1.875 solicitudes, 0 fallidas (0%), promedio 8,25 ms, máx. 31,9 ms. Diferencia 5 solicitudes registrada. No cubre flujos autenticados u otros endpoints. |
| PT-08 | **Seguridad estática** | Bandit 1.9.4 | Análisis sobre código Python de INVISAP (excluidas librerías/entornos/pruebas). | Sin alertas altas; alertas medias/bajas revisadas y justificadas. | `.\.venv\Scripts\bandit.exe -r . -x ".\lib_pdf,...,.\.venv,.\tests,.\locustfile.py,..." -f json -o bandit_report.json` | **Pendiente de revisión:** 113 alertas (0 altas, 56 medias, 57 bajas). 54 B608 (SQL dinámico) requieren revisión individual. B110, B105, B603, B404, B310, B104, B311 entre otras. |
| PT-09 | **Recorridos UI / Verificación de guías** | `verificar_tours.py` (Python) | Selectores de recorridos guiados interactivos. | Cero selectores sin resolver. | `.\.venv\Scripts\python.exe .\verificar_tours.py` | **Aprobada:** 339 pasos comprobados, 0 selectores sin resolver. |

Para cada prueba en el entorno institucional se debe anotar fecha, versión,
persona responsable, datos utilizados, resultado, observación y ruta de la
evidencia. Los datos productivos no deben copiarse a un entorno de prueba sin
autorización y protección adecuada.

### 4.5.1 Bitácora de pruebas

**Fecha de repetición: 23/10/2026.**

| Registro | Resultado observado | Estado | Observación / acción pendiente |
|---|---|---|---|
| Suite completa pytest | **29 aprobadas, 0 fallidas.** | Aprobada para las pruebas automatizadas ejecutadas. | Se emitieron 14 avisos de obsolescencia de `openpyxl`, sin fallos. Los casos de integración/API simulan modelos y permisos; no son una prueba transaccional real de la base. |
| Corrección de la ruta `GET /login` | **Aviso “Primero debes iniciar sesión” ya no aparece al abrir el formulario; el control para POST incompleto se conserva.** | Corregida y verificada. | El smoke de pytest y Playwright confirman HTTP 200 y ausencia del aviso falso. |
| Pruebas unitarias pytest | **11 aprobadas, 0 fallidas.** | Aprobada. | Validaciones de informes y filtros SQL seguros. |
| Pruebas de integración pytest | **2 aprobadas, 0 fallidas.** | Aprobada con dobles de prueba. | Contratación auditada/reintento; no prueba escrituras reales en MySQL. El conector de la aplicación sí se verificó aparte con una conexión real y `SELECT 1`. |
| Backend/API pytest | **13 aprobadas, 0 fallidas.** | Aprobada con modelos simulados. | Endpoints HTTP de reportes; Postman no está instalado en este entorno. |
| Humo pytest y HTTP en vivo | **1 prueba pytest aprobada; `GET /` y `GET /login` respondieron HTTP 200.** | Aprobada para las rutas comprobadas. | La conexión MySQL del sistema también ejecutó `SELECT 1`; esto no equivale a probar todos los módulos ni sus transacciones. |
| Playwright/Chromium | **HTTP 200, título “Sistema Invilara”, 1 formulario y 2 campos.** | Aprobada para humo de interfaz. | Captura actualizada en `my-app/test-results/playwright_login.png`; no se intentó iniciar sesión ni ejecutar recorridos autenticados. |
| Locust, carga RNF | **20 usuarios durante aproximadamente 185 s tras el ramp-up; resumen: 1.880 solicitudes, 0 fallidas, promedio 8 ms y máximo 31 ms.** | Aprobada para `/` y `/login` según umbral de tiempo y errores declarado. | El CSV registró 1.875 solicitudes, 0 fallidas, promedio 8,25 ms y máximo 31,9 ms. Se observó una diferencia de 5 solicitudes entre el resumen de terminal y el CSV; ambos reflejan 0 fallas y tiempos inferiores al umbral. Evidencia: `my-app/test-results/locust-rnf-final-20261023_*`. |
| Bandit (`-r .`) | **113 alertas: 56 medias, 57 bajas y 0 altas.** Reglas: 54 B608, 47 B110, 4 B105, 3 B603, 2 B404; una cada una de B310, B104 y B311. | Revisión SAST pendiente antes de aprobación. | Los 54 B608 son avisos por SQL dinámico, no confirmación automática de vulnerabilidad. Revisar individualmente identificadores y valores; revisar también excepciones vacías, llamadas de red/subprocess y aleatoriedad. |
| Conexión MySQL de la aplicación | Conexión establecida a `localhost` con la configuración de INVISAP; `SELECT 1` devolvió `1`. | Conectividad verificada. | No se realizaron escrituras ni pruebas CRUD sobre datos institucionales; validar los flujos transaccionales con datos de prueba autorizados. |
| Aceptacion formal | No se probo con personal ni se genero acta. | Pendiente. | Requiere usuarios de Invilara, tareas acordadas y conformidad documentada. |

Durante la ejecución de pytest se observaron avisos de obsolescencia de
`openpyxl` relacionados con `datetime.utcnow()` al generar archivos Excel. No
provocaron fallos, pero conviene actualizar la dependencia y volver a probar.

### Comandos reproducibles por categoria

Ejecutar desde `C:\laragon\www\INVISAP\my-app` en PowerShell. En el entorno actual estan instalados pytest 9.1.1, Playwright 1.64.0, Locust 2.46.7 y Bandit 1.9.4. Selenium tambien esta instalado, pero Playwright se uso para la prueba UI; Postman no esta instalado y se uso el cliente Flask para API. pytest, Playwright, Selenium y Locust no estan fijados en `requirements.txt`; estos comandos dependen de los paquetes presentes en `.venv`.

**Unitarias (11 aprobadas):**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_informe_validacion.py tests\test_sql_filter_allowlists.py -o addopts= -q --tb=short
```

**Integracion (2 aprobadas, con dobles de prueba):**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_contrataciones_bitacora.py -o addopts= -q --tb=short
```

**Backend/API (13 aprobadas con modelos simulados):**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_parametrizacion_reportes.py -o addopts= -q --tb=short
```

**Humo (1 aprobada):**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_security_controls.py::RecaptchaSecurityTestCase::test_login_page_responds_without_server_error -o addopts= -q --tb=short
```

**Interfaz con Playwright:** abrir dos terminales. Iniciar el servidor en la primera; ejecutar la prueba en la segunda. La captura se guarda en `test-results\playwright_login.png`.

```powershell
# Terminal 1
.\.venv\Scripts\python.exe run.py

# Terminal 2
.\.venv\Scripts\python.exe .\tests\playwright_ui_smoke.py
```

**Prueba rápida opcional con Locust (no equivale a la medición RNF):**

```powershell
.\.venv\Scripts\locust.exe -f locustfile.py --headless -H http://127.0.0.1:5600 -u 5 -r 1 --run-time 10s --stop-timeout 5 --csv test-results\locust-smoke --only-summary
```

Ejecución del criterio RNF realizada contra el sistema en ejecución. El escenario
solo solicita las rutas GET `/` y `/login`; repetir únicamente en un entorno
autorizado y preferiblemente aislado. La evidencia CSV se guarda bajo
`test-results\locust-rnf-final-20261023_*`.

```powershell
.\.venv\Scripts\locust.exe -f locustfile.py --headless -H http://127.0.0.1:5600 -u 20 -r 2 --run-time 3m15s --stop-timeout 10 --csv test-results\locust-rnf-final-20261023 --only-summary
```

La ejecución real duró 195 s; los 20 usuarios terminaron de iniciar en unos 9 s
y permanecieron activos aproximadamente 185 s. El resumen de terminal fue:
1.880 solicitudes, 0 fallas, promedio 8 ms y máximo 31 ms. El CSV guardó 1.875
solicitudes, 0 fallas, promedio 8,25 ms y máximo 31,9 ms. Registra la
discrepancia de cinco solicitudes al presentar la evidencia; las dos salidas
cumplen el umbral de 0 % de fallas y promedio menor a 2 s para estas rutas.

**Para completar la aceptación técnica:** ejecutar flujos funcionales con
cuentas de prueba autorizadas contra MySQL y documentar su resultado. La
aceptación formal requiere tareas acordadas con usuarios de Invilara y su
conformidad documentada; estos comandos por sí solos no la aprueban.

```powershell
.\.venv\Scripts\python.exe -m pytest tests -o addopts= -q --tb=short
.\.venv\Scripts\python.exe .\tests\playwright_ui_smoke.py
```

**Analisis estatico limitado al codigo de INVISAP:**

```powershell
.\.venv\Scripts\bandit.exe -r . -x ".\lib_pdf,.\static,.\BD,.\conexion,.\.kilo,.\.kombai,.\.qodo,.\.vscode,.\.github,.\__pycache__,.\.git,.\.venv,.\venv,.\node_modules,.\tests,.\test-results,.\generar_vendor_min.py,.\locustfile.py,.\verificar_tours.py" -f json -o bandit_report.json
.\.venv\Scripts\python.exe -c "import json,collections; d=json.load(open('bandit_report.json',encoding='utf-8')); r=d['results']; print('Alertas:',len(r)); print('Por severidad:',dict(collections.Counter(x['issue_severity'] for x in r))); print('Por regla:',dict(collections.Counter(x['test_id'] for x in r)))"
```

Bandit devuelve codigo distinto de cero cuando encuentra alertas; el JSON queda en `bandit_report.json`. Para esta ejecucion fueron 113 alertas. Se excluyeron los nombres reales del repositorio (`conexion` y `.venv`), en vez de los ejemplos `connection` y `venv`.

**Verificacion adicional de recorridos (no sustituye pruebas de navegador):**

```powershell
.\.venv\Scripts\python.exe .\verificar_tours.py
```

Los avisos de obsolescencia de `openpyxl` al generar Excel no provocaron fallos; conviene revisarlos al actualizar la dependencia.

**Correcciones realizadas para dejar esta bitácora reproducible:**

- Se reactivó la verificación real de reCAPTCHA: sin token, sin secreto, ante
  error de red o ante respuesta inválida ya no se concede acceso.
- Se aisló el control de permisos en las pruebas de rutas mediante un fixture de
  prueba; el control de acceso de producción no se desactivó.
- Se alineó la prueba de reintento de contratación con el método de conexión
  heredado por el modelo y se reintenta cuando el duplicado corresponde a la
  clave primaria del ID.
- Se redujo el modo de creación de directorios de carga para no otorgar acceso
  a todos los usuarios del sistema operativo.
- Se eliminaron los fallbacks que interpolaban claves de filtros no reconocidas
  como columnas SQL en estadísticas y reportes Excel/PDF; los valores siguen
  enviados mediante `%s`. También se validaron los identificadores del
  constructor de consultas y se parametrizaron consultas de metadatos.

## 4.6 Plan de Instalación

### 4.6.1 Situación registrada

La Agenda JAD registra una visita el **07/09/2026** para instalar INVILARA
localmente en el servidor de la institución. También registra al equipo de
proyecto y a la tutora Ing. Jhoanly Hernandez como responsables de esa visita.
El tablero no aporta en esas tarjetas un acta técnica, resultado de una prueba
posterior ni fotografías adjuntas; por tanto, la instalación se reporta como
actividad registrada, no como disponibilidad operativa revalidada.

### 4.6.2 Requisitos previos

1. Servidor institucional autorizado, con Python compatible (el `Containerfile`
   declara Python 3.11), MySQL 8 y acceso de red al puerto elegido.
2. Copia de seguridad de la base de datos y autorización para importar o migrar
   el esquema.
3. Variables de configuración y secretos únicos para el servidor. No reutilizar
   contraseñas de ejemplo ni guardar secretos en el repositorio.
4. El archivo de esquema `my-app/BD/invilara.sql` está presente. La receta
   `Containerfile` copia también una carpeta `wheels/`, que no está presente en
   este repositorio; por ello, el build aislado/offline de contenedor requiere
   proporcionar ese wheelhouse o preparar una receta de instalación aprobada.
5. Confirmar con la institución los puertos, DNS o acceso local, usuarios
   administradores y responsable del respaldo.

### 4.6.3 Procedimiento

1. Respaldar la instancia existente y conservar el archivo con fecha y
   responsable.
2. Preparar el servidor y MySQL; crear o validar la base de datos requerida e
   importar el esquema aprobado.
3. Crear el entorno a partir de `my-app/.env.example`, completar los datos
   propios de infraestructura y proteger el archivo. No publicar el contenido
   de `.env`.
4. Instalar las dependencias de `my-app/requirements.txt` en un entorno virtual
   compatible con la plataforma.
5. Iniciar la aplicación con `python run.py` y confirmar el puerto 5600 desde
   el servidor.
6. Verificar la página de acceso, autenticación, permisos por rol, módulo de
   solicitudes, obras, informes, exportación PDF/Excel y bitácora.
7. Ejecutar un respaldo de prueba y restaurarlo en un entorno controlado.
8. Registrar versiones, fecha, responsable, incidencias y capturas; entregar
   credenciales por un canal institucional seguro y cambiarlas al finalizar la
   instalación.

**Criterio de cierre:** rutas principales operativas con la base de datos real,
autorización comprobada por rol, copia y restauración verificadas, y acta de
instalación firmada por el responsable institucional.

## 4.7 Plan de Capacitación

Plan propuesto siguiendo los campos del formato de capacitación adjunto. La
Agenda JAD registra instalación y capacitación el 07/09/2026, pero no detalla
temario completado, lista de asistencia, evaluación ni duración; la tabla
siguiente es una propuesta para formalizar o repetir, no una afirmación de que
todos estos talleres ya ocurrieron.

**Objetivo general:** preparar a las personas usuarias y administradoras de
Invilara para realizar de forma segura los flujos de trabajo asignados y
consultar el manual y las ayudas del sistema.

**Metodología:** demostración breve, práctica guiada con cuentas y datos de
prueba, resolución de dudas y verificación práctica al cierre. Duración total
propuesta: **6 horas y 30 minutos**, distribuibles en dos sesiones.

| Taller | Temas | Duración | Público |
|---|---|---:|---|
| Introducción | Propósito del sistema, responsables, normas de uso y recorrido por la interfaz. | 30 min | Todas las personas usuarias |
| 1. Acceso y perfiles | Inicio/cierre de sesión, recuperación de acceso, roles y permisos. | 30 min | Todas las personas usuarias |
| 2. Solicitudes | Registro, consulta, búsqueda, estado y priorización. | 60 min | Personal que recibe y gestiona solicitudes |
| 3. Gestión de obras | Proyectos, obras, contrataciones y empresas; consulta de hitos y avances. | 60 min | Personal responsable de obras y contratos |
| 4. Inspecciones y evidencias | Registro de inspecciones, carga y consulta de evidencias e informes de avance. | 75 min | Inspectores, responsables de obra y personal autorizado |
| 5. Consultas y reportes | Filtros, reportes estadísticos y exportaciones PDF/Excel. | 45 min | Coordinación y usuarios autorizados |
| 6. Seguridad y respaldos | Bitácora, protección de información y procedimiento de respaldo/restauración. | 30 min | Administradores designados |
| 7. Administración de usuarios | Gestión de cuentas, roles y permisos por módulo. | 30 min | Administradores designados |
| 8. Práctica y evaluación | Completar un flujo asignado, cuestionario breve y encuesta de satisfacción. | 30 min | Todas las personas participantes |

**Recursos:** servidor de capacitación, navegador actualizado, cuentas por rol,
datos ficticios, proyector, manual de usuario y acceso a las ayudas interactivas.
**Facilitadores propuestos:** equipo de proyecto, con acompañamiento de la
tutora y de la persona responsable del sistema en Invilara. **Fecha, lugar,
asistencia y evaluación:** coordinar y dejar constancia con la institución;
no se asignan fechas nuevas sin su confirmación.

**Evaluación propuesta:** observar la ejecución de una tarea correspondiente
al rol y aplicar un cuestionario breve. Registrar asistencia, dudas, tareas
completadas y acciones correctivas; conservar la evidencia con autorización de
las personas participantes.

---

## Ubicación de imágenes y evidencias en el informe

| Imagen o evidencia que se debe insertar | Ubicación recomendada | Pie sugerido / indicación |
|---|---|---|
| `mapa navegacional INVILARA.png` (ya está en el repositorio) | Capítulo III, apartado de diseño o presentación del producto, después de describir la navegación. | **Figura X. Mapa navegacional del Sistema Invilara.** Reducir el tamaño para el documento sin volver ilegibles sus etiquetas. |
| Captura real de la pantalla inicial y del panel principal | Capítulo III, presentación del producto, después de la descripción general. | **Figura X. Pantalla de acceso / panel principal de INVISAP.** Usar capturas del sistema instalado, sin mostrar claves ni datos personales. |
| Captura de un flujo de solicitud, obra o informe | Capítulo III, junto a la descripción del módulo funcional que ilustra. | Indicar nombre del módulo, rol de prueba y resultado visible; anonimizar los datos. |
| Salida de pytest con 29 pruebas aprobadas | Capitulo IV, numeral 4.5.1, despues de la bitacora automatizada. | Figura X. Resultado de pytest de la repetición del 23/10/2026; mostrar comando, total y estado final. |
| Resultado Bandit | Capitulo IV, numeral 4.5.1, junto a la entrada SAST de la bitacora. | Figura X. Analisis Bandit: 113 alertas (56 medias, 57 bajas y 0 altas); no presentarlas como resueltas. |
| Captura Playwright `my-app/test-results/playwright_login.png` | Capitulo IV, numeral 4.5.1, después del registro de prueba UI. | Figura X. Verificación de la pantalla de acceso: HTTP 200, formulario y dos campos. |
| CSV de Locust `my-app/test-results/locust-rnf-final-20261023_*` | Capitulo IV, numeral 4.5.1, después del registro de rendimiento. | Mostrar ejecución RNF con 20 usuarios y el período medido; señalar la diferencia de cinco solicitudes entre CSV y resumen de terminal. |
| Fotografías de la visita e instalación del 07/09/2026 | Capítulo IV, numeral 4.6, después del procedimiento de instalación; copias completas en Capítulo V, Anexos. | Incluir fecha, lugar, actividad y autorización para publicar a las personas fotografiadas. |
| Lista de asistencia y encuesta de capacitación | Capítulo IV, numeral 4.7, después del plan y sus resultados; originales en anexos si corresponde. | No inventar asistencia ni resultados: añadir solo documentos efectivamente firmados o aplicados. |

En la respuesta pública del tablero no se encontraron archivos de imagen adjuntos
a las tarjetas; aparece una tarea que solicita fotos de la visita, pero no las
fotografías. En los archivos del proyecto sí está el mapa navegacional, pero no
se encontraron capturas de pantalla de pruebas ni fotos de la visita. Esas
evidencias deben agregarse desde los originales de la comunidad. No utilizar
capturas de los trabajos de referencia PFC como si fueran pantallas o resultados
de INVISAP.

## Fuentes consultadas

- Agenda JAD de Invilara: https://trello.com/b/3QYNygGb/agenda-jad-invilara
- *Manual Informe de Proyecto III.pdf*: estructura del informe; la ubicación de
  pruebas, instalación y capacitación en este capítulo sigue la corrección
  indicada por la profesora.
- *Pruebas de auditorías del Sistema.pdf* y *Requisitos No funcionales 2026.pdf*:
  categorías de pruebas y criterios de rendimiento.
- *Formato del Plan de Capacitación.pdf*: campos y estructura del plan.
- Código del proyecto: suite en `my-app/tests`, `my-app/locustfile.py`,
  `my-app/verificar_tours.py`, `my-app/run.py` y `compose.yaml`.
