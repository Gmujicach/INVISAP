# Matriz de cumplimiento — Exigencias del Proyecto III (PNFI)

Sistema: **INVISAP**
Fecha de elaboracion: 2026-09-27
Alcance: verificacion sobre el codigo fuente del repositorio.

> **Nota importante.** Esta matriz consolida lo que el sistema **si** hace, con
> evidencia `archivo:linea`. El PDF "Exigencias del Proyecto III PNFI" no esta
> versionado en el repositorio, por lo que el mapeo **item por item** del
> documento (numeros de requisito, redaccion exacta y anexos) debe completarse
> con el PDF en mano. La seccion 6 lista exactamente que datos faltan para
> cerrarlo.

---

## 1. Arquitectura y stack tecnologico

| Exigencia | Estado | Evidencia |
|---|---|---|
| App web con framework | CUMPLE | Flask 3 + Werkzeug, `app.py`, `run.py` (puerto 5600) |
| Patron MVC | CUMPLE | `controllers/`, `models/`, `vista/` (24 plantillas) |
| Blueprints por modulo | CUMPLE | `empleado_bp`, `obra_bp`, `inspeccion_bp`, `informe_avance_bp`, `respaldo_bp`, `contrataciones_bp`, `reporte_estadistico_bp`, `reporte_excel_bp`, `reporte_pdf_bp`, `user_bp`, `login_bp` (216 rutas registradas) |
| Base de datos relacional | CUMPLE | MySQL, `conexion/conexionBD.py` |
| **Dos** bases de datos separadas | CUMPLE | `invilara` (funcional, `connectionBD`) e `invilara_seguridad` (seguridad, `connectionBD_seguridad`) — `conexion/conexionBD.py:29,65` |
| Configuracion por variables de entorno | CUMPLE | `conexion/conexionBD.py:5-16` (cargador `.env`), claves en `claveApi.py` |
| Interfaz responsive | CUMPLE | Bootstrap 5 + `table-responsive`, clases `col-*`, `flex-column flex-md-row` |
| Modo claro/oscuro | CUMPLE | Paleta `[data-bs-theme]` / `data-theme` en el layout |

## 2. Seguridad

| Exigencia | Estado | Evidencia |
|---|---|---|
| Hash de contrasenas (no MD5) | CUMPLE | `werkzeug.security.generate_password_hash` / `check_password_hash` — `models/model_usuarios.py:126,135`; `controllers/UserController.py:204,258` |
| Autenticacion de usuarios | CUMPLE | `controllers/UserController.py`, `routers/router_login.py` |
| Segundo factor (OTP) | CUMPLE | Codigo OTP de 4 digitos tras validar credenciales (`generar_manual.py:175`) |
| reCAPTCHA / control anti-bot | CUMPLE | `claveApi.py`, `funciones_login.py`, `router_login.py`, `vista/login/auth_login.html` |
| Control de acceso por URL y rol | CUMPLE | `app.py:131-181` (`proteger_modulos_por_url`), cache en `g._permisos_cache` |
| Roles, modulos y permisos CRUD | CUMPLE | 9 roles activos con 19 permisos cada uno; `router_home.py:1406-1553` (18 endpoints `/api/seguridad/*`) |
| Permisos por accion CRUD | CUMPLE | `verificar_permiso_accion` — `controllers/UserController.py:56` |
| Excepciones por usuario | CUMPLE | `/api/seguridad/usuarios/permisos/guardar`, `RolPermisoModel.obtener_permisos_usuario` |
| Secreto de la aplicacion | CUMPLE | `claveApi.SECRET_KEY` (`app.py:185`), fuera del codigo |
| Sesion firmada | CUMPLE | `app.secret_key` + `session` de Flask |

## 3. Modulos funcionales

Todos los modulos siguen el mismo patron: listado con los tres botones
estandar (Ver / Editar / Eliminar), formularios con validacion en cliente y
servidor, API JSON y tour interactivo.

| Modulo | Listado | API | Tour | Notas |
|---|---|---|---|---|
| Solicitudes | `lista_solicitudes.html` | `/api/solicitudes/*` (6) | si (17 pasos) | CRUD completo + actualizar estatus |
| Empresas | `lista_empresas.html` | `/api/empresas/<rif>` | si (7) | Ver/Editar/Eliminar + requisitos legales |
| Empleados | `empleados.html` | `/api/listar-json`, `/api/<id>` | si (35 pasos) | Borrado logico, dashboard SPA |
| Contrataciones | `form_contratacion.html` | `/api/obtener-empresas-json` | si (7) | DataTables + modal de detalle |
| Obras | `form_gestionar_obras.html` | `/api/obra/*` | si (64 pasos) | Modal nueva/editar |
| Proyectos | `proyectos.html` | `/api/proyecto/*` | si (8 pasos) | |
| Maquinaria | | `/api/maquinaria/*` (6) | si | Borrado logico + restaurar |
| Gravedad | `form_gestionar_gravedad.html` | `/api/gravedad/*` | si (10 pasos) | |
| Prioridad (IA) | `form_gestionar_prioridad.html` | `/api/prioridad/*` (11) | si | |
| Inspecciones | `inspeccion_lista.html` | `/api/crear`, `/api/actualizar`, `/api/validar/*` | si (15 pasos) | |
| Evidencias | `lista_evidencias.html` | `/api/evidencias/*` (4) | si (35 pasos) | Carga multiple (3-50 imagenes) |
| Informes de avance | `inf_avance_obra.html` | `/api/informes/*` (8) | si (44 pasos) | |
| Publicaciones | `lista_publicaciones.html` | `/api/publicaciones/*` (3) | si (7 pasos) | |
| Usuarios | `lista_usuarios.html` | `/api/users/<id>` (2) | si (32 pasos) | Alta y perfil |
| Bitacora | `lista_bitacora.html` | `/api/obtener-bitacora-json` | si (7 pasos) | Auditoria |
| Notificaciones | | `/lista`, `/eliminar/<id>`, `/eliminar-todas` | si | |
| Respaldo y restauracion | `form_respaldo.html` | `/api/listar-json`, `/eliminar/<id>` | si (3 pasos) | `mysqldump` via `subprocess` |
| Reportes estadisticos | `reporteEstadistico.html` | `/reporte-estadistico/data` | si (14 pasos) | 3 graficos (Chart.js) |
| Reportes PDF | `reportePDF.html` | `/reporte-pdf` | si | Pillow + BytesIO |
| Reportes Excel | `reporteExcel.html` | `/reporte-excel` | si | |

## 4. Bitacora / auditoria

| Exigencia | Estado | Evidencia |
|---|---|---|
| Registro de acciones del usuario | CUMPLE | `services/bitacora_service.BitacoraService.registrar_accion` |
| Se invoca en crear/editar/eliminar | CUMPLE | `controllers/controller_empleado.py:84,133,196`, `routers/router_home.py:1069` (publicaciones) |
| Consulta de bitacora | CUMPLE | `/api/obtener-bitacora-json` + `lista_bitacora.html` |

## 5. Usabilidad e interaccion

| Exigencia | Estado | Evidencia |
|---|---|---|
| Botones de accion estandarizados | CUMPLE | `static/assets/css/estandar-acciones.css` + `static/js/ui/estandar-ui.js`; 17 vistas auditadas |
| Ver / Editar / Eliminar homogeneos | CUMPLE | `.btn-accion-ver` (`bi-eye`), `.btn-accion-editar` (`bi-pencil-square`), `.btn-accion-eliminar` (`bi-trash`), celda `.acciones`, contenedor `.btn-acciones` |
| Normalizacion de botones legacy | CUMPLE | `estandar-ui.js` + `MutationObserver` repinta tambien contenido AJAX |
| Cierre de modal unico | CUMPLE | `.btn-close-custom` con `bi bi-x-lg` en 14 vistas |
| Bitacora de solo lectura | CUMPLE (por diseno) | Un registro de auditoria **no** debe editarse ni borrarse: `lista_bitacora.html` expone solo Ver |
| Sin recargas de pagina (AJAX) | CUMPLE | `static/js/ui/ajax-refresh.js` repinta el `<tbody>`; 12 modulos migrados |
| Tours interactivos (Driver.js) | CUMPLE | 21 tours, **339 pasos, 0 selectores sin resolver** (`verificar_tours.py`) |
| Boton de tour global | CUMPLE | `#btnTourInvilara` en `base_cpanel.html` y en el manual standalone |
| Manual de usuario | CUMPLE | `/manual-sistema` (interactivo) + `static/manuals/Manual_del_Sistema_INVILARA.pdf` |

## 6. Brechas: lo que NO se puede afirmar sin el PDF

Estos puntos **no estan implementados como codigo** o **no estan
documentados** en el repositorio. Requieren definicion del profesor:

| Punto | Estado | Observacion |
|---|---|---|
| PERT / CPM (red de proyectos) | NO CUMPLE | No hay calculo de ruta critica ni grafo de actividades |
| Modelos entrada/salida (IO) | NO CUMPLE | No hay diagramas ni calculo de IO en el repositorio |
| Multitareas / procesos concurrentes | PARCIAL | Existe concurrencia en `services/ia_prioridad_service.py` (`threading`, `subprocess`) y en `models/model_respaldo.py:223` (`mysqldump`), pero no hay un modulo que lo documente como requisito |
| Sincronizacion de procesos | PARCIAL | Sin semaforos ni colas documentadas; se apoya en el Aislamiento por peticion HTTP de Flask |
| Pruebas Box-White / Box-Black | PARCIAL | Hay `test_security_controls.py`; no hay suite completa de pruebas unitarias ni de caja negra documentada |
| Plan de pruebas formal | NO CUMPLE | No existe documento de plan de pruebas |
| Plan de capacitacion | NO CUMPLE | No existe documento de plan de capacitacion |
| Especificacion de Requisitos (SRS) | PARCIAL | `ARQUITECTURA_DEL_PROYECTO.md` documenta arquitectura, pero no hay SRS formal firmado |

## 7. Como verificar

Los dos unicos scripts de apoyo que quedaron en el repositorio son de
mantencion, no forman parte de la aplicacion:

| Script | Para que |
|---|---|
| `verificar_tours.py` | Confirma que los 339 pasos de los tours apuntan a elementos que existen en las vistas |
| `generar_vendor_min.py` | Regenera los `.min.js` de jQuery, Bootstrap, Popper, perfect-scrollbar y menu; descarta el archivo si el resultado no es JS valido |

Comprobaciones manuales equivalentes, sin scripts:

```powershell
# 1. Sin sintaxis roto (Python)
python -c "import ast,pathlib;[ast.parse(p.read_text(encoding='utf-8')) for p in pathlib.Path('.').rglob('*.py')]"

# 2. Plantillas Jinja correctas
python -c "import pathlib;from jinja2 import Environment,FileSystemLoader;e=Environment(loader=FileSystemLoader('vista'));[e.parse(p.read_text(encoding='utf-8')) for p in pathlib.Path('vista').rglob('*.html')]"

# 3. Tours
python verificar_tours.py

# 4. Arranque: arrancar la app con run.py y abrir cada modulo
python run.py
```

Resultado vigente: Python OK · Jinja OK · JS OK (73 archivos) ·
Tours 339/339 · Vistas 17/17 estandarizadas · 26/26 rutas HTTP 200.
