from conexion.conexionBD import connectionBD
import datetime

class ProyectoModel:
    def __init__(self):
        pass

    def registrar_proyecto(self, datos):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            sql = """INSERT INTO gestionar_proyectos 
                (codigo_proyecto, fecha_planificacion, descripcion_tecnica, 
                 computos_metricos, estimacion_costo_proyecto, inspecciones_previas, 
                 maquinaria_id_maquinaria, problematica_solicitud, nombre_solicitante, tipo_solicitud) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            # Manejo seguro de la maquinaria (evita error si el string está vacío)
            id_maquinaria = datos.get('maquinaria_p')
            # Tu BD no permite NULL en maquinaria_id_maquinaria. Si no hay, forzamos un valor o lanzamos error.
            id_maquinaria = int(id_maquinaria) if id_maquinaria and str(id_maquinaria).isdigit() else 1

            # Manejo de fecha: Si viene vacía, enviamos None para que MySQL guarde NULL o falle si es obligatorio
            fecha_plan = datos.get('fecha_p')
            if not fecha_plan:
                # Si la fecha es obligatoria y viene vacía, usamos la fecha actual como fallback
                fecha_plan = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            valores = (
                datos.get('Codigo_p', '')[:15], # Límite varchar(15)
                fecha_plan,
                datos.get('observaciones', '')[:200], # Límite varchar(200)
                datos.get('computos_p', '')[:255],
                datos.get('estimacion_p', '')[:45], # Límite varchar(45)
                datos.get('inspeccion_p', '')[:255],
                id_maquinaria,
                (datos.get('problematica_p') or 'Sin problemática')[:80], 
                (datos.get('solicitante_p') or 'N/A')[:58],  
                (datos.get('tipo_solicitud_p') or 'N/A')[:30]
            )

            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback() # Revertimos si hay error
            print(f"---------- ERROR CRÍTICO EN BD ----------")
            print(f"Mensaje de MySQL: {e}")
            print(f"Valores intentados: {valores}")
            print(f"-----------------------------------------")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_proyectos(self):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM gestionar_proyectos ORDER BY id_proyectos DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en ProyectoModel.obtener_proyectos: {e}")
            return []
        finally:
            if conexion: conexion.close()

    def obtener_proyecto_por_id(self, id_proyecto):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM gestionar_proyectos WHERE id_proyectos = %s", (id_proyecto,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en ProyectoModel.obtener_proyecto_por_id: {e}")
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_proyecto(self, id_proyecto, datos):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            sql = """UPDATE gestionar_proyectos SET 
                codigo_proyecto=%s, fecha_planificacion=%s, descripcion_tecnica=%s, 
                computos_metricos=%s, estimacion_costo_proyecto=%s, inspecciones_previas=%s, 
                maquinaria_id_maquinaria=%s, problematica_solicitud=%s, nombre_solicitante=%s, tipo_solicitud=%s
                WHERE id_proyectos=%s"""
            
            id_maquinaria = datos.get('maquinaria_p')
            id_maquinaria = int(id_maquinaria) if id_maquinaria and str(id_maquinaria).isdigit() else 1
            
            fecha_plan = datos.get('fecha_p')
            if not fecha_plan:
                fecha_plan = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            valores = (
                datos.get('Codigo_p', '')[:15],
                fecha_plan,
                datos.get('observaciones', '')[:200],
                datos.get('computos_p', '')[:255],
                datos.get('estimacion_p', '')[:45],
                datos.get('inspeccion_p', '')[:255],
                id_maquinaria,
                (datos.get('problematica_p') or 'Sin problemática')[:80],
                (datos.get('solicitante_p') or 'N/A')[:58],
                (datos.get('tipo_solicitud_p') or 'N/A')[:30],
                id_proyecto
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback()
            print(f"Error en ProyectoModel.actualizar_proyecto: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_proyecto(self, id_proyecto):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM gestionar_proyectos WHERE id_proyectos = %s", (id_proyecto,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            if conexion: conexion.rollback()
            print(f"Error en ProyectoModel.eliminar_proyecto: {e}")
            return False
        finally:
            if conexion: conexion.close()