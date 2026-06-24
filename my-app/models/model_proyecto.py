from conexion.conexionBD import connectionBD
import datetime

class ProyectoModel:
    def __init__(self):
        pass

    def registrar_proyecto(self, datos):
        conexion = None
        valores = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            # 1. Insertar en la tabla principal 'proyecto'
            sql = """INSERT INTO proyecto 
                (codigo_proyecto, fecha_planificacion, descripcion_tecnica,
                 computos_metricos, estimacion_costo) 
                VALUES (%s, %s, %s, %s, %s)"""
            
            codigo_proy = datos.get('Codigo_p', '')[:15]
            fecha_plan = datos.get('fecha_p')
            if not fecha_plan:
                fecha_plan = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            valores = (
                codigo_proy, 
                fecha_plan,
                datos.get('observaciones', '')[:200], 
                datos.get('computos_p', '')[:255],
                datos.get('estimacion_p', '')[:45]
            )

            cursor.execute(sql, valores)

            # 2. Buscar datos obligatorios de la clave compuesta de la tabla 'solicitudes'
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
                    
                    # Insertamos usando el mapeo completo de claves foráneas de tu tabla puente
                    sql_solicitud = """INSERT INTO proyecto_has_solicitudes 
                        (proyecto_codigo_proyecto, solicitudes_id_solicitudes, 
                         solicitudes_persona_id_persona, solicitudes_prioridad_id_gestion_prioridad) 
                        VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql_solicitud, (codigo_proy, id_solicitud, id_persona, id_prioridad))
                else:
                    raise Exception(f"No se encontraron los datos compuestos para la solicitud ID: {id_solicitud}")

            # 3. Relación con maquinaria
            id_maquinaria = datos.get('maquinaria_p')
            if id_maquinaria and str(id_maquinaria).isdigit():
                sql_maquinaria = "INSERT INTO proyecto_has_maquinaria (proyecto_codigo_proyecto, maquinaria_id_maquinaria) VALUES (%s, %s)"
                cursor.execute(sql_maquinaria, (codigo_proy, int(id_maquinaria)))

            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback() 
            print(f"---------- ERROR CRÍTICO EN BD ----------")
            print(f"Mensaje de MySQL: {e}")
            print(f"-----------------------------------------")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_proyectos(self):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            # Cruce de JOINS adaptado al uso de las columnas compuestas guardadas en el puente
            sql = """SELECT 
                        p.codigo_proyecto, p.fecha_planificacion, p.descripcion_tecnica, 
                        p.computos_metricos, p.estimacion_costo,
                        m.nombre_maquinaria, m.id_maquinaria,
                        s.id_solicitudes, s.tipo_solicitud, s.problematica,
                        COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) as nombre_solicitante
                     FROM proyecto p
                     LEFT JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     LEFT JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                     LEFT JOIN persona pers ON phs.solicitudes_persona_id_persona = pers.id_persona
                     LEFT JOIN particular part ON pers.id_persona = part.persona_id_persona
                     LEFT JOIN institucion inst ON pers.id_persona = inst.persona_id_persona
                     LEFT JOIN comunidad com ON pers.id_persona = com.persona_id_persona
                     LEFT JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
                     LEFT JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria 
                     ORDER BY p.codigo_proyecto DESC"""
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en ProyectoModel.obtener_proyectos: {e}")
            return []
        finally:
            if conexion: conexion.close()

    def obtener_proyecto_por_id(self, codigo_proyecto):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            sql = """SELECT 
                        p.codigo_proyecto, p.fecha_planificacion, p.descripcion_tecnica, 
                        p.computos_metricos, p.estimacion_costo, 
                        m.nombre_maquinaria, m.id_maquinaria,
                        s.id_solicitudes, s.tipo_solicitud, s.problematica,
                        COALESCE(CONCAT(part.nombre, ' ', part.apellido), inst.razon_social, com.nombre_comunidad) as nombre_solicitante
                     FROM proyecto p
                     LEFT JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     LEFT JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes
                     LEFT JOIN persona pers ON phs.solicitudes_persona_id_persona = pers.id_persona
                     LEFT JOIN particular part ON pers.id_persona = part.persona_id_persona
                     LEFT JOIN institucion inst ON pers.id_persona = inst.persona_id_persona
                     LEFT JOIN comunidad com ON pers.id_persona = com.persona_id_persona
                     LEFT JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
                     LEFT JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria 
                     WHERE p.codigo_proyecto = %s"""
            cursor.execute(sql, (codigo_proyecto,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en ProyectoModel.obtener_proyecto_por_id: {e}")
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_proyecto(self, codigo_proyecto_actual, datos):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            sql = """UPDATE proyecto SET 
                codigo_proyecto=%s, fecha_planificacion=%s, descripcion_tecnica=%s,
                computos_metricos=%s, estimacion_costo=%s
                WHERE codigo_proyecto=%s"""
            
            codigo_nuevo = datos.get('Codigo_p', '')[:15]
            fecha_plan = datos.get('fecha_p')
            if not fecha_plan:
                fecha_plan = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            valores = (
                codigo_nuevo,
                fecha_plan,
                datos.get('observaciones', '')[:200],
                datos.get('computos_p', '')[:255],
                datos.get('estimacion_p', '')[:45],
                codigo_proyecto_actual
            )
            cursor.execute(sql, valores)

            # MANEJO SEGURO DE LA TABLA PUENTE DE SOLICITUDES
            id_solicitud = datos.get('solicitud_id_p')
            if id_solicitud:
                # Si se especifica una nueva relación, limpiamos la anterior e insertamos con sus claves correspondientes
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
                        (codigo_nuevo, id_solicitud, res_sol['persona_id_persona'], res_sol['prioridad_id_gestion_prioridad']))
            else:
                # Si no se altera la solicitud pero el código del proyecto cambió, actualizamos la referencia en el puente
                if codigo_nuevo != codigo_proyecto_actual:
                    cursor.execute("""
                        UPDATE proyecto_has_solicitudes 
                        SET proyecto_codigo_proyecto = %s 
                        WHERE proyecto_codigo_proyecto = %s
                    """, (codigo_nuevo, codigo_proyecto_actual))

            # MANEJO SEGURO DE LA TABLA PUENTE DE MAQUINARIAS
            id_maquinaria = datos.get('maquinaria_p')
            if id_maquinaria and str(id_maquinaria).isdigit():
                cursor.execute("DELETE FROM proyecto_has_maquinaria WHERE proyecto_codigo_proyecto = %s", (codigo_proyecto_actual,))
                cursor.execute("INSERT INTO proyecto_has_maquinaria (proyecto_codigo_proyecto, maquinaria_id_maquinaria) VALUES (%s, %s)", 
                               (codigo_nuevo, int(id_maquinaria)))
            else:
                if codigo_nuevo != codigo_proyecto_actual:
                    cursor.execute("""
                        UPDATE proyecto_has_maquinaria 
                        SET proyecto_codigo_proyecto = %s 
                        WHERE proyecto_codigo_proyecto = %s
                    """, (codigo_nuevo, codigo_proyecto_actual))

            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback()
            print(f"Error en ProyectoModel.actualizar_proyecto: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_proyecto(self, codigo_proyecto):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            
            # Eliminación preventiva de las referencias en las tablas hijas por integridad referencial
            cursor.execute("DELETE FROM proyecto_has_solicitudes WHERE proyecto_codigo_proyecto = %s", (codigo_proyecto,))
            cursor.execute("DELETE FROM proyecto_has_maquinaria WHERE proyecto_codigo_proyecto = %s", (codigo_proyecto,))
            cursor.execute("DELETE FROM proyecto WHERE codigo_proyecto = %s", (codigo_proyecto,))
            
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback()
            print(f"Error en ProyectoModel.eliminar_proyecto: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_contadores_proyectos(self):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            sql = """SELECT s.tipo_solicitud 
                     FROM proyecto p
                     INNER JOIN proyecto_has_solicitudes phs ON p.codigo_proyecto = phs.proyecto_codigo_proyecto
                     INNER JOIN solicitudes s ON phs.solicitudes_id_solicitudes = s.id_solicitudes"""
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
            print(f"Error en ProyectoModel.obtener_contadores_proyectos: {e}")
            return {'total_registrados': 0, 'en_proceso': 0, 'completadas': 0, 'total': 0}
        finally:
            if conexion: conexion.close()