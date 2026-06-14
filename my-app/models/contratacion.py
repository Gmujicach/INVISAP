from conexion.conexionBD import connectionBD_invilara as connectionBD

class ContratacionModel:
    
    def registrar_contrataciones(self, datos):
        conexion = connectionBD()
        if conexion is None: return False
            
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO gestionar_contrataciones (
                descripcion, empresa_ganadora, numero_contrato, monto, tipo_contrato, 
                fecha_inicio_procedimiento, fecha_adjudicacion, fecha_registro, 
                modalidad, objeto, observacion, 
                gestionar_proyectos_id_proyectos, gestionar_proyectos_maquinaria_id_maquinaria, 
                empresa_rif, empresa_gestionar_proyectos_id_proyectos, 
                empresa_gestionar_proyectos_maquinaria_id_maquinaria
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            valores = (
                datos.get('descripcion'), 
                datos.get('empresa_ganadora'), 
                datos.get('numero_contrato'), 
                datos.get('monto'), 
                datos.get('tipo_contrato'), 
                datos.get('fecha_inicio'), 
                datos.get('fecha_adjudicacion'), 
                datos.get('fecha_registro'), 
                datos.get('modalidad'), 
                datos.get('objeto'), 
                datos.get('observacion'), 
                
                # Relaciones principales
                datos.get('id_proyecto'), 
                datos.get('id_maquinaria'), 
                datos.get('empresa_rif'), 
                
                # AQUÍ ESTÁ EL TRUCO: Reutilizamos los IDs para cumplir con la DB
                datos.get('id_proyecto'), 
                datos.get('id_maquinaria')
            )
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True
            
        except Exception as e:
            print(f"--- [ERROR DETALLADO INSERT]: {e} ---") 
            return False
        finally:
            if conexion: conexion.close()

    def obtener_todas_las_contrataciones(self):
        conexion = connectionBD()
        if conexion is None: return []
            
        try:
            cursor = conexion.cursor(dictionary=True)
            # Hacemos JOINs para traer los nombres reales
            sql = """
            SELECT c.*, 
                   p.codigo_proyecto as nombre_proyecto, 
                   m.nombre_maquinaria as nombre_maquinaria
            FROM gestionar_contrataciones c
            LEFT JOIN gestionar_proyectos p ON c.gestionar_proyectos_id_proyectos = p.id_proyectos
            LEFT JOIN maquinaria m ON c.gestionar_proyectos_maquinaria_id_maquinaria = m.id_maquinaria
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [ERROR AL CONSULTAR]: {e} ---")
            return []
        finally:
            if conexion: conexion.close()