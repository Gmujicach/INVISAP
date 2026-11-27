"""
ProyectoModel — Modelo SOLID/POO para gestión de proyectos.
Implementa encapsulamiento, validaciones Regex, borrado lógico y relaciones.
"""

import re
import json
import datetime
from models.base_model import BaseModel


class ProyectoModel(BaseModel):
    """Repositorio de proyectos con validación y encapsulamiento."""

    _RE_CODIGO = re.compile(r'^[A-Za-z0-9\-_]{1,15}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:°º²ºáéíóúÁÉÍÓÚñÑ]{1,2500}$')
    _RE_ESTIMACION = re.compile(r'^[\d\.,\s]{1,45}$')

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__codigo_proyecto = None
        self.__fecha_planificacion = None
        self.__descripcion_tecnica = None
        self.__computos_metricos = []
        self.__estimacion_costo = None
        self.__proyecto_has_empleado = None
        self.__estado = 1
        self.__asegurar_descripcion_tecnica()

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_codigo_proyecto(self):
        return self.__codigo_proyecto

    def set_codigo_proyecto(self, valor):
        if not self._RE_CODIGO.match(str(valor or '').strip()):
            raise ValueError("Código de proyecto inválido (máx 15 chars, alfanumérico, guiones).")
        self.__codigo_proyecto = valor.strip()[:15]

    def get_fecha_planificacion(self):
        return self.__fecha_planificacion

    def set_fecha_planificacion(self, valor):
        fecha_raw = str(valor or '').strip()
        if not fecha_raw:
            self.__fecha_planificacion = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif len(fecha_raw) == 10:
            ahora = datetime.datetime.now()
            self.__fecha_planificacion = f"{fecha_raw} {ahora.strftime('%H:%M:%S')}"
        else:
            self.__fecha_planificacion = fecha_raw.replace('T', ' ')

    def get_descripcion_tecnica(self):
        return self.__descripcion_tecnica

    def set_descripcion_tecnica(self, valor):
        if not self._RE_TEXTO.match(str(valor or '')):
            raise ValueError("Descripción técnica inválida.")
        self.__descripcion_tecnica = self._limpiar_texto(valor, 2500)

    def get_computos_metricos(self):
        return self.__computos_metricos

    def set_computos_metricos(self, valor):
        self.__computos_metricos = self._parsear_computos_metricos(valor)

    def get_estimacion_costo(self):
        return self.__estimacion_costo

    def set_estimacion_costo(self, valor):
        if valor and not self._RE_ESTIMACION.match(str(valor)):
            raise ValueError("Estimación de costo inválida.")
        self.__estimacion_costo = str(valor or '')[:45]

    def get_proyecto_has_empleado(self):
        return self.__proyecto_has_empleado

    def set_proyecto_has_empleado(self, valor):
        if valor is not None:
            try:
                self.__proyecto_has_empleado = int(valor)
            except (TypeError, ValueError):
                self.__proyecto_has_empleado = None
        else:
            self.__proyecto_has_empleado = None

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        self.__estado = 1 if int(valor) else 0

    # ========== MÉTODOS PRIVADOS DE UTILIDAD ==========

    @staticmethod
    def _parsear_computos_metricos(valor):
        if valor is None:
            return []
        if isinstance(valor, list):
            return valor
        if isinstance(valor, str):
            valor = valor.strip()
            if not valor:
                return []
            try:
                datos = json.loads(valor)
                if isinstance(datos, list):
                    return datos
            except (json.JSONDecodeError, TypeError):
                pass
            return [{'metrica': '', 'opcion': valor, 'costo': ''}]
        return []

    @staticmethod
    def _serializar_computos_metricos(items):
        if not items:
            return json.dumps([])
        if isinstance(items, str):
            valor = items.strip()
            if not valor:
                return json.dumps([])
            try:
                json.loads(valor)
                return valor
            except (json.JSONDecodeError, TypeError):
                return json.dumps([{'metrica': '', 'opcion': valor, 'costo': ''}])
        limpios = []
        for item in items:
            if isinstance(item, dict):
                limpios.append({
                    'metrica': item.get('metrica', ''),
                    'opcion': item.get('opcion', ''),
                    'costo': item.get('costo', '')
                })
            elif isinstance(item, str) and item.strip():
                limpios.append({'metrica': '', 'opcion': item.strip(), 'costo': ''})
        return json.dumps(limpios)

    @staticmethod
    def _formatear_computos_metricos(items):
        datos = ProyectoModel._parsear_computos_metricos(items)
        if not datos:
            return ''
        partes = []
        for item in datos:
            costo = item.get('costo', '')
            metrica = item.get('metrica', '')
            opcion = item.get('opcion', '')
            texto = ' '.join(filter(None, [str(costo), metrica, opcion]))
            if texto.strip():
                partes.append(texto.strip())
        return ', '.join(partes) if partes else ''

    def __asegurar_descripcion_tecnica(self, conexion=None):
        if conexion is None:
            conexion = self.obtener_conexion_estricta()
            if not conexion:
                return
            cursor = conexion.cursor()
            try:
                cursor.execute("SHOW COLUMNS FROM proyecto LIKE 'descripcion_tecnica'")
                columna = cursor.fetchone()
                if columna and str(columna[1]).lower() != 'text':
                    cursor.execute("ALTER TABLE proyecto MODIFY COLUMN descripcion_tecnica TEXT NOT NULL")
                    conexion.commit()
            finally:
                cursor.close()
        else:
            cursor = conexion.cursor()
            try:
                cursor.execute("SHOW COLUMNS FROM proyecto LIKE 'descripcion_tecnica'")
                columna = cursor.fetchone()
                if columna and str(columna[1]).lower() != 'text':
                    cursor.execute("ALTER TABLE proyecto MODIFY COLUMN descripcion_tecnica TEXT NOT NULL")
                    conexion.commit()
            finally:
                cursor.close()

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __validar_codigo_proyecto_db(self, codigo_proyecto, excluir_id=None):
        conexion = self.obtener_conexion_estricta()
        try:
            cursor = conexion.cursor(dictionary=True)
            if excluir_id:
                cursor.execute(
                    "SELECT estado FROM proyecto WHERE codigo_proyecto = %s AND codigo_proyecto != %s",
                    (codigo_proyecto, excluir_id)
                )
            else:
                cursor.execute("SELECT estado FROM proyecto WHERE codigo_proyecto = %s", (codigo_proyecto,))
            fila = cursor.fetchone()
            if fila:
                if fila['estado'] == 0:
                    return {'existe_eliminado': True}
                return {'existe_activo': True}
            return {'disponible': True}
        except Exception as e:
            print(f"Error validando código proyecto: {e}")
            return {'error': True}
        finally:
            cursor.close()
            conexion.close()

    def __registrar_proyecto_db(self, datos):
        conexion = None
        try:
            self.set_codigo_proyecto(datos.get('Codigo_p', ''))
            self.set_fecha_planificacion(datos.get('fecha_p'))
            self.set_descripcion_tecnica(datos.get('observaciones', ''))
            self.set_computos_metricos(datos.get('computos_p', []))
            self.set_estimacion_costo(datos.get('estimacion_p', ''))
            self.set_proyecto_has_empleado(datos.get('proyectista_p'))

            val_result = self.__validar_codigo_proyecto_db(self.__codigo_proyecto)
            if val_result.get('existe_activo'):
                raise Exception(f"El código {self.__codigo_proyecto} ya existe en otro proyecto activo.")
            if val_result.get('existe_eliminado'):
                raise Exception(f"El código {self.__codigo_proyecto} fue usado en un proyecto eliminado. No se pueden reutilizar códigos.")

            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)
            self.__asegurar_descripcion_tecnica(conexion)

            sql = """INSERT INTO proyecto 
              (codigo_proyecto, fecha_planificacion, descripcion_tecnica, 
               computos_metricos, estimacion_costo, proyecto_has_empleado, estado) 
              VALUES (%s, %s, %s, %s, %s, %s, 1)"""

            id_proyectista = self.__proyecto_has_empleado

            valores = (
                self.__codigo_proyecto,
                self.__fecha_planificacion,
                self.__descripcion_tecnica,
                self._serializar_computos_metricos(self.__computos_metricos),
                self.__estimacion_costo,
                id_proyectista
            )

            cursor.execute(sql, valores)

            id_solicitud = datos.get('solicitud_id_p')
            if id_solicitud:
                cursor.execute("""
                    SELECT persona_id_persona, prioridad_id_gestion_prioridad 
                    FROM solicitudes 
                    WHERE id_solicitudes = %s
                """, (id_solicitud,))
                resultado_solicitud = cursor.fetchone()

                if resultado_solicitud:
                    id_persona = resultado_solicitud['persona_id_persona']
                    id_prioridad = resultado_solicitud['prioridad_id_gestion_prioridad']

                    sql_solicitud = """INSERT INTO proyecto_has_solicitudes 
                        (proyecto_codigo_proyecto, solicitudes_id_solicitudes, 
                         solicitudes_persona_id_persona, solicitudes_prioridad_id_gestion_prioridad) 
                        VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql_solicitud, (self.__codigo_proyecto, id_solicitud, id_persona, id_prioridad))

                    cursor.execute("UPDATE solicitudes SET estatus_solicitud = %s WHERE id_solicitudes = %s", ('En Proceso', id_solicitud))
                else:
                    raise Exception(f"No se encontraron datos compuestos para solicitud ID: {id_solicitud}")

            sql_maquinaria = "INSERT INTO proyecto_has_maquinaria (proyecto_codigo_proyecto, maquinaria_id_maquinaria) VALUES (%s, %s)"
            for key, value in datos.items():
                if key.startswith('maquinaria_') and value and str(value).isdigit():
                    cursor.execute(sql_maquinaria, (self.__codigo_proyecto, int(value)))

            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"ERROR CRÍTICO EN BD: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    def __actualizar_proyecto_db(self, codigo_proyecto_actual, datos):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)
            self.__asegurar_descripcion_tecnica(conexion)

            cursor.execute("SELECT fecha_planificacion FROM proyecto WHERE codigo_proyecto = %s", (codigo_proyecto_actual,))
            fila = cursor.fetchone()
            fecha_existente = fila['fecha_planificacion'] if fila else None

            self.set_codigo_proyecto(datos.get('Codigo_p', ''))
            self.set_fecha_planificacion(datos.get('fecha_p') or fecha_existente)
            self.set_descripcion_tecnica(datos.get('observaciones_p') or datos.get('observaciones') or '')
            self.set_computos_metricos(datos.get('computos_p', []))
            self.set_estimacion_costo(datos.get('estimacion_p', ''))
            self.set_proyecto_has_empleado(datos.get('proyectista_p'))

            if self.__codigo_proyecto != codigo_proyecto_actual:
                val_result = self.__validar_codigo_proyecto_db(self.__codigo_proyecto, excluir_id=codigo_proyecto_actual)
                if val_result.get('existe_activo'):
                    raise Exception(f"El código {self.__codigo_proyecto} ya existe en otro proyecto activo.")
                if val_result.get('existe_eliminado'):
                    raise Exception(f"El código {self.__codigo_proyecto} fue usado en un proyecto eliminado. No se pueden reutilizar códigos.")

            sql = """UPDATE proyecto SET 
                codigo_proyecto=%s, fecha_planificacion=%s, descripcion_tecnica=%s,
                computos_metricos=%s, estimacion_costo=%s, proyecto_has_empleado=%s
                WHERE codigo_proyecto=%s"""

            valores = (
                self.__codigo_proyecto,
                self.__fecha_planificacion,
                self.__descripcion_tecnica,
                self._serializar_computos_metricos(self.__computos_metricos) if self.__computos_metricos else '',
                self.__estimacion_costo,
                self.__proyecto_has_empleado,
                codigo_proyecto_actual
            )
            cursor.execute(sql, valores)

            id_solicitud = datos.get('solicitud_id_p')
            if id_solicitud:
                cursor.execute("DELETE FROM proyecto_has_solicitudes WHERE proyecto_codigo_proyecto = %s", (codigo_proyecto_actual,))
                cursor.execute("""
                    SELECT persona_id_persona, prioridad_id_gestion_prioridad 
                    FROM solicitudes 
                    WHERE id_solicitudes = %s
                """, (id_solicitud,))
                res_sol = cursor.fetchone()
                if res_sol:
                    cursor.execute("""INSERT INTO proyecto_has_solicitudes 
                        (proyecto_codigo_proyecto, solicitudes_id_solicitudes, 
                         solicitudes_persona_id_persona, solicitudes_prioridad_id_gestion_prioridad) 
                        VALUES (%s, %s, %s, %s)""",
                        (self.__codigo_proyecto, id_solicitud, res_sol['persona_id_persona'], res_sol['prioridad_id_gestion_prioridad']))
            else:
                if self.__codigo_proyecto != codigo_proyecto_actual:
                    cursor.execute("""
                        UPDATE proyecto_has_solicitudes 
                        SET proyecto_codigo_proyecto = %s 
                        WHERE proyecto_codigo_proyecto = %s
                    """, (self.__codigo_proyecto, codigo_proyecto_actual))

            cursor.execute("DELETE FROM proyecto_has_maquinaria WHERE proyecto_codigo_proyecto = %s", (codigo_proyecto_actual,))
            sql_maquinaria = "INSERT INTO proyecto_has_maquinaria (proyecto_codigo_proyecto, maquinaria_id_maquinaria) VALUES (%s, %s)"
            for key, value in datos.items():
                if key.startswith('maquinaria_') and value and str(value).isdigit():
                    cursor.execute(sql_maquinaria, (self.__codigo_proyecto, int(value)))

            conexion.commit()
            return True
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error actualizando proyecto: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    def __eliminar_proyecto_db(self, codigo_proyecto):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor()
            sql = "UPDATE proyecto SET estado = 0 WHERE codigo_proyecto = %s"
            cursor.execute(sql, (codigo_proyecto,))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"Error eliminando proyecto: {e}")
            return False
        finally:
            if conexion:
                conexion.close()

    def __obtener_proyectos_db(self):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)

            sql = """SELECT 
                        p.codigo_proyecto, p.fecha_planificacion, p.descripcion_tecnica, 
                        p.computos_metricos, p.estimacion_costo, p.proyecto_has_empleado,
                        GROUP_CONCAT(DISTINCT m.nombre_maquinaria SEPARATOR ', ') as nombre_maquinaria,
                        GROUP_CONCAT(DISTINCT m.id_maquinaria SEPARATOR ',') as ids_maquinaria,
                        GROUP_CONCAT(DISTINCT s.id_solicitudes SEPARATOR ',') as ids_solicitudes,
                        GROUP_CONCAT(DISTINCT s.tipo_solicitud SEPARATOR ', ') as tipo_solicitud,
                        GROUP_CONCAT(DISTINCT s.problematica SEPARATOR '; ') as problematica,
                        GROUP_CONCAT(DISTINCT COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) SEPARATOR ', ') as nombre_solicitante,
                        COALESCE(e.nombre_empleado, 'Sin asignar') as nombre_proyectista
                     FROM proyecto p
                     LEFT JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     LEFT JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                     LEFT JOIN persona pers ON phs.solicitudes_persona_id_persona = pers.id_persona
                     LEFT JOIN particular part ON pers.id_persona = part.persona_id_persona
                     LEFT JOIN institucion inst ON pers.id_persona = inst.persona_id_persona
                     LEFT JOIN comunidad com ON pers.id_persona = com.persona_id_persona
                     LEFT JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
                     LEFT JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria 
                     LEFT JOIN empleados e ON p.proyecto_has_empleado = e.id_empleados
                     WHERE p.estado = 1
                     GROUP BY p.codigo_proyecto
                     ORDER BY p.codigo_proyecto DESC"""
            cursor.execute(sql)
            proyectos = cursor.fetchall()
            for p in proyectos:
                p['computos_metricos'] = self._parsear_computos_metricos(p.get('computos_metricos'))
                p['computos_metricos_texto'] = self._formatear_computos_metricos(p['computos_metricos'])
            return proyectos
        except Exception as e:
            print(f"Error obteniendo proyectos: {e}")
            return []
        finally:
            if conexion:
                conexion.close()

    def __obtener_proyecto_por_id_db(self, codigo_proyecto):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)

            sql = """SELECT 
                        p.codigo_proyecto, p.fecha_planificacion, p.descripcion_tecnica, 
                        p.computos_metricos, p.estimacion_costo, p.proyecto_has_empleado,
                        GROUP_CONCAT(DISTINCT m.nombre_maquinaria SEPARATOR ', ') as nombre_maquinaria,
                        GROUP_CONCAT(DISTINCT m.id_maquinaria SEPARATOR ',') as ids_maquinaria,
                        GROUP_CONCAT(DISTINCT s.id_solicitudes SEPARATOR ',') as ids_solicitudes,
                        GROUP_CONCAT(DISTINCT s.tipo_solicitud SEPARATOR ', ') as tipo_solicitud,
                        GROUP_CONCAT(DISTINCT s.problematica SEPARATOR '; ') as problematica,
                        GROUP_CONCAT(DISTINCT COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) SEPARATOR ', ') as nombre_solicitante,
                        COALESCE(e.nombre_empleado, 'Sin asignar') as nombre_proyectista
                     FROM proyecto p
                     LEFT JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     LEFT JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                     LEFT JOIN persona pers ON phs.solicitudes_persona_id_persona = pers.id_persona
                     LEFT JOIN particular part ON pers.id_persona = part.persona_id_persona
                     LEFT JOIN institucion inst ON pers.id_persona = inst.persona_id_persona
                     LEFT JOIN comunidad com ON pers.id_persona = com.persona_id_persona
                     LEFT JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
                     LEFT JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria 
                     LEFT JOIN empleados e ON p.proyecto_has_empleado = e.id_empleados
                     WHERE p.codigo_proyecto = %s
                     GROUP BY p.codigo_proyecto"""
            cursor.execute(sql, (codigo_proyecto,))
            proyecto = cursor.fetchone()
            if proyecto:
                proyecto['computos_metricos'] = self._parsear_computos_metricos(proyecto.get('computos_metricos'))
                proyecto['computos_metricos_texto'] = self._formatear_computos_metricos(proyecto['computos_metricos'])
            return proyecto
        except Exception as e:
            print(f"Error obteniendo proyecto por ID: {e}")
            return None
        finally:
            if conexion:
                conexion.close()

    def __obtener_detalle_proyecto_db(self, codigo_proyecto):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT p.codigo_proyecto, p.fecha_planificacion, p.descripcion_tecnica,
                       p.computos_metricos, p.estimacion_costo, p.proyecto_has_empleado,
                       COALESCE(e.nombre_empleado, 'Sin asignar') as nombre_proyectista
                FROM proyecto p
                LEFT JOIN empleados e ON p.proyecto_has_empleado = e.id_empleados
                WHERE p.codigo_proyecto = %s
            """, (codigo_proyecto,))
            proyecto = cursor.fetchone()
            if not proyecto:
                return None
            proyecto['computos_metricos'] = self._parsear_computos_metricos(proyecto.get('computos_metricos'))
            proyecto['computos_metricos_texto'] = self._formatear_computos_metricos(proyecto['computos_metricos'])
            cursor.execute("""
                SELECT s.id_solicitudes, s.tipo_solicitud, s.estatus_solicitud, s.problematica,
                       COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) as nombre_solicitante
                FROM proyecto_has_solicitudes phs
                JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                LEFT JOIN persona pers ON phs.solicitudes_persona_id_persona = pers.id_persona
                LEFT JOIN particular part ON pers.id_persona = part.persona_id_persona
                LEFT JOIN institucion inst ON pers.id_persona = inst.persona_id_persona
                LEFT JOIN comunidad com ON pers.id_persona = com.persona_id_persona
                WHERE phs.proyecto_codigo_proyecto = %s
            """, (codigo_proyecto,))
            solicitudes = cursor.fetchall()
            cursor.execute("""
                SELECT m.id_maquinaria, m.nombre_maquinaria
                FROM proyecto_has_maquinaria phm
                JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria
                WHERE phm.proyecto_codigo_proyecto = %s
            """, (codigo_proyecto,))
            maquinaria = cursor.fetchall()
            return {
                'proyecto': proyecto,
                'solicitudes': solicitudes,
                'maquinaria': maquinaria
            }
        except Exception as e:
            print(f"Error obteniendo detalle proyecto: {e}")
            return None
        finally:
            if conexion:
                conexion.close()

    def __obtener_contadores_db(self):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)

            sql = """SELECT s.tipo_solicitud 
                     FROM proyecto p
                     INNER JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     INNER JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                     WHERE p.estado = 1"""

            cursor.execute(sql)
            proyectos_vinculados = cursor.fetchall()

            total_registrados = len(proyectos_vinculados)
            en_proceso = 0
            completadas = 0

            for item in proyectos_vinculados:
                estado = str(item.get('tipo_solicitud', '')).lower()
                if 'proceso' in estado:
                    en_proceso += 1
                elif 'completa' in estado or 'finalizado' in estado:
                    completadas += 1

            return {
                'total_registrados': total_registrados,
                'en_proceso': en_proceso,
                'completadas': completadas,
                'total': total_registrados
            }
        except Exception as e:
            print(f"Error obteniendo contadores: {e}")
            return {'total_registrados': 0, 'en_proceso': 0, 'completadas': 0, 'total': 0}
        finally:
            if conexion:
                conexion.close()

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def registrar(self, datos):
        """Método público para registrar proyecto."""
        return self.__registrar_proyecto_db(datos)

    def actualizar(self, codigo_proyecto_actual, datos):
        """Método público para actualizar proyecto."""
        return self.__actualizar_proyecto_db(codigo_proyecto_actual, datos)

    def eliminar(self, codigo_proyecto):
        """Método público para borrado lógico de proyecto."""
        return self.__eliminar_proyecto_db(codigo_proyecto)

    def obtener_todos(self):
        """Método público para obtener todos los proyectos."""
        return self.__obtener_proyectos_db()

    def obtener_por_id(self, codigo_proyecto):
        """Método público para obtener proyecto por código."""
        return self.__obtener_proyecto_por_id_db(codigo_proyecto)

    def obtener_detalle(self, codigo_proyecto):
        """Método público para obtener detalle completo de proyecto."""
        return self.__obtener_detalle_proyecto_db(codigo_proyecto)

    def obtener_contadores(self):
        """Método público para obtener contadores de proyectos."""
        return self.__obtener_contadores_db()

    def validar_codigo(self, codigo_proyecto):
        """Método público para validar código de proyecto."""
        return self.__validar_codigo_proyecto_db(codigo_proyecto)