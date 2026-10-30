# Complemento del Capítulo IV: pruebas de rendimiento

> Este archivo complementa el informe del proyecto. El PDF proporcionado,
> **Manual Informe de Proyecto III**, contiene únicamente el esquema del
> documento (tres páginas), no el informe desarrollado; por eso no se modifica
> ni se inventan resultados. Al ejecutar escenarios con
> `run_performance.py`, se actualizará automáticamente la bitácora de este
> complemento con las mediciones reales.

## 4.7 Plan de Pruebas

El objetivo es medir la disponibilidad y el tiempo de respuesta de las rutas
HTTP de lectura de los veinte módulos de INVISAP. Se usa Locust contra una
instancia de pruebas, con datos de prueba y sin generar o modificar registros.
Las consultas de reportes PDF y Excel cargan solamente sus formularios; no
ejecutan exportaciones durante la carga.

Se contemplan cuatro perfiles: verificación rápida (`quick`), carga de
referencia (`baseline`), estrés (`stress`) y pico de concurrencia (`spike`).
Los usuarios virtuales consultan las rutas asignadas a su módulo y esperan
entre una y dos segundos entre solicitudes. Los perfiles de estrés y pico se
reservan para entornos preparados y no deben ejecutarse en producción.

Se registran el número de solicitudes y fallos, solicitudes por segundo,
tiempos promedio, mediano y percentil 95. Los umbrales de aceptación deben ser
acordados con el tutor/comunidad antes de declarar que el sistema cumple el
rendimiento esperado. Una respuesta 401/403 indica que se debe configurar una
sesión de pruebas; no representa una medición funcional autenticada.

## 4.7.1 Bitácora de Pruebas

Cada ejecución individual o global agrega las métricas de Locust a
`tests/performance/results/bitacora_rendimiento.csv` y actualiza la tabla
siguiente. No se han ejecutado pruebas contra el servidor en el momento de
crear este documento.

<!-- PERFORMANCE_RESULTS_START -->
| Fecha y hora | Módulo | Perfil | Solicitudes | Fallos | Fallos % | Req/s | Promedio ms | Mediana ms | P95 ms |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2026-10-29T22:36:12-04:00 | Solicitudes | quick | 3 | 3 | 100.00% | 0.9257400196611693 | 15.300266665993453 | 7 | 34 |
| 2026-10-29T22:36:19-04:00 | Gravedad de Obra | quick | 3 | 3 | 100.00% | 1.0450211862647227 | 6.7109999993893625 | 6 | 9 |
| 2026-10-29T22:36:25-04:00 | Prioridad | quick | 3 | 3 | 100.00% | 0.8682509199915293 | 5.995233333427071 | 6 | 7 |
| 2026-10-29T22:36:30-04:00 | Proyectos | quick | 3 | 3 | 100.00% | 0.995303381792916 | 6.651500000468029 | 6.00269999995362 | 8 |
| 2026-10-29T22:36:36-04:00 | Maquinaria | quick | 3 | 3 | 100.00% | 0.7880477441404079 | 6.850533332908526 | 6 | 9 |
| 2026-10-29T22:36:42-04:00 | Contratación | quick | 4 | 4 | 100.00% | 1.1598368271553594 | 5.6903999998212385 | 7 | 7 |
| 2026-10-29T22:36:47-04:00 | Empresa | quick | 3 | 3 | 100.00% | 1.1473306708899575 | 7.1952999993906515 | 7 | 8 |
| 2026-10-29T22:36:53-04:00 | Obras | quick | 3 | 3 | 100.00% | 0.9960625056351979 | 6.0012333324266365 | 6 | 8 |
| 2026-10-29T22:36:59-04:00 | Empleados | quick | 3 | 3 | 100.00% | 0.9078348870335409 | 9.762933334059198 | 6 | 18 |
| 2026-10-29T22:37:04-04:00 | Inspecciones | quick | 4 | 4 | 100.00% | 1.0970320424437456 | 7.334524999805581 | 8 | 10 |
| 2026-10-29T22:37:10-04:00 | Evidencias | quick | 3 | 0 | 0.00% | 0.9382611914322725 | 30.288266666805914 | 28 | 37 |
| 2026-10-29T22:37:16-04:00 | Informe de Avance de Obra | quick | 4 | 4 | 100.00% | 1.0447600140486872 | 5.658150000272144 | 6 | 8 |
| 2026-10-29T22:37:21-04:00 | Publicaciones | quick | 3 | 0 | 0.00% | 0.8788646690509725 | 20.048600000033428 | 24 | 26 |
| 2026-10-29T22:37:27-04:00 | Reportes PDF | quick | 3 | 3 | 100.00% | 1.0744203763375166 | 8.684933333521863 | 8 | 14 |
| 2026-10-29T22:37:33-04:00 | Reportes Excel | quick | 3 | 3 | 100.00% | 0.900452791448222 | 8.382133333725506 | 8 | 11 |
| 2026-10-29T22:37:38-04:00 | Reportes Estadísticos | quick | 3 | 3 | 100.00% | 1.2764942634963101 | 6.140066666678952 | 7 | 9 |
| 2026-10-29T22:37:44-04:00 | Usuarios | quick | 3 | 3 | 100.00% | 0.8472523259370105 | 6.082766666925939 | 6 | 7 |
| 2026-10-29T22:37:50-04:00 | Permisos por Rol | quick | 3 | 3 | 100.00% | 1.0117480343020602 | 6.981733333911204 | 7 | 8 |
| 2026-10-29T22:37:55-04:00 | Administración de Respaldos | quick | 3 | 3 | 100.00% | 0.7806920107839616 | 7.396666665954399 | 7 | 9 |
| 2026-10-29T22:38:01-04:00 | Bitácora | quick | 3 | 3 | 100.00% | 1.0579107398911143 | 7.081700000223161 | 7 | 8 |
| 2026-10-29T22:44:23-04:00 | Solicitudes | quick | 3 | 3 | 100.00% | 0.9439230897220062 | 11.442600000009406 | 10 | 14 |
| 2026-10-29T22:44:29-04:00 | Gravedad de Obra | quick | 3 | 3 | 100.00% | 1.0042159327557687 | 8.71973333354011 | 8 | 10 |
| 2026-10-29T22:44:35-04:00 | Prioridad | quick | 4 | 4 | 100.00% | 1.0337752459705807 | 8.402350000324077 | 8.253700001660036 | 9 |
| 2026-10-29T22:44:41-04:00 | Proyectos | quick | 3 | 3 | 100.00% | 0.8656777062730804 | 8.757099999153676 | 9 | 12 |
| 2026-10-29T22:44:47-04:00 | Maquinaria | quick | 3 | 3 | 100.00% | 1.045580846533368 | 8.341966666800241 | 8.657799999127747 | 9 |
| 2026-10-29T22:44:52-04:00 | Contratación | quick | 3 | 3 | 100.00% | 0.791274650314591 | 11.051400000117914 | 13 | 14 |
| 2026-10-29T22:44:58-04:00 | Empresa | quick | 3 | 3 | 100.00% | 1.0003032809111814 | 9.358066666512363 | 9 | 11 |
| 2026-10-29T22:45:04-04:00 | Obras | quick | 3 | 3 | 100.00% | 1.0307300262201924 | 9.142433333181543 | 8 | 12 |
| 2026-10-29T22:45:10-04:00 | Empleados | quick | 3 | 3 | 100.00% | 0.8597326440301389 | 8.57953333312859 | 9 | 12 |
| 2026-10-29T22:45:16-04:00 | Inspecciones | quick | 3 | 3 | 100.00% | 1.0393927055978665 | 7.458066666610345 | 9 | 10 |
| 2026-10-29T22:45:21-04:00 | Evidencias | quick | 3 | 0 | 0.00% | 0.9593140646809243 | 28.623500000321656 | 31 | 37 |
| 2026-10-29T22:45:27-04:00 | Informe de Avance de Obra | quick | 3 | 3 | 100.00% | 0.9775947210292794 | 11.206266667916983 | 9 | 16 |
| 2026-10-29T22:45:33-04:00 | Publicaciones | quick | 3 | 0 | 0.00% | 0.8507979489831395 | 25.098133333206835 | 28 | 33 |
| 2026-10-29T22:45:39-04:00 | Reportes PDF | quick | 3 | 3 | 100.00% | 1.2294032960510406 | 10.440400000031028 | 10.229199999230332 | 11 |
| 2026-10-29T22:45:45-04:00 | Reportes Excel | quick | 3 | 3 | 100.00% | 1.0636145345383827 | 9.674000000207647 | 9 | 11 |
| 2026-10-29T22:45:51-04:00 | Reportes Estadísticos | quick | 3 | 3 | 100.00% | 0.9887957180751833 | 9.612033333420792 | 8 | 13 |
| 2026-10-29T22:45:56-04:00 | Usuarios | quick | 4 | 4 | 100.00% | 1.0187611897121807 | 10.163650000322377 | 11 | 12 |
| 2026-10-29T22:46:02-04:00 | Permisos por Rol | quick | 4 | 4 | 100.00% | 1.0630789886603622 | 10.047074999874894 | 10 | 14 |
| 2026-10-29T22:46:08-04:00 | Administración de Respaldos | quick | 3 | 3 | 100.00% | 0.8913596868693788 | 9.735099999791904 | 9 | 12 |
| 2026-10-29T22:46:14-04:00 | Bitácora | quick | 3 | 3 | 100.00% | 0.9623759095808507 | 11.270833333886307 | 9 | 17 |
| 2026-10-29T22:50:15-04:00 | Solicitudes | baseline | 91 | 91 | 100.00% | 3.1745535127806037 | 6.154869230678222 | 6 | 10 |
<!-- PERFORMANCE_RESULTS_END -->

## 4.8 Plan de Instalación

1. Instalar las dependencias del sistema indicadas en `requirements.txt` y
   Locust con `pip install -r tests\performance\requirements.txt`.
2. Desplegar INVISAP y su base de datos en un entorno de pruebas aislado.
3. Configurar `INVISAP_TEST_URL` y, si se medirán rutas protegidas,
   `INVISAP_PERF_SESSION_COOKIE` con una cuenta de pruebas.
4. Ejecutar primero el perfil `quick` para comprobar conectividad y después
   `baseline`. Aplicar `stress` o `spike` solo con autorización y recursos
   supervisados.
5. Revisar la bitácora, los CSV de Locust, errores del servidor y métricas de
   CPU/memoria; conservar la versión del código, fecha, entorno y parámetros.
6. Finalizar la prueba y verificar que no queden procesos Locust activos. No
   ejecutar cargas contra producción.

## 4.9 Plan de Capacitación

Capacitar al personal técnico para instalar Locust, iniciar el servidor de
pruebas, seleccionar el perfil, interpretar fallos HTTP y percentiles, y
consultar la bitácora. Antes de utilizar usuarios o cookies, se debe explicar
su manejo seguro. El personal no técnico debe conocer que los resultados
dependen del equipo, red, base de datos, volumen de información y concurrencia
seleccionada, y que una ejecución rápida no reemplaza una prueba de carga.

## 6. Capítulo IV: Recomendaciones y Evolución Previsible del Sistema

- Definir con los responsables tiempos máximos de respuesta y disponibilidad
  aceptables para cada operación antes de usar las métricas como criterio de
  aprobación.
- Ejecutar primero pruebas de referencia y comparar cambios del sistema con
  el mismo entorno y volumen de datos.
- Investigar las rutas con fallos HTTP o percentiles altos antes de aumentar la
  concurrencia; revisar aplicación, consultas SQL, índices, pool de conexiones,
  red y recursos del servidor.
- Incorporar pruebas periódicas en un entorno controlado y conservar la
  bitácora como evidencia de evolución, sin incluir cookies ni secretos.
- Ampliar gradualmente los escenarios de lectura y, con aprobación expresa,
  diseñar pruebas separadas para operaciones de escritura y generación de
  reportes.
