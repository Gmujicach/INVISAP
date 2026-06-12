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
            
            # Los nombres dentro de datos[] DEBEN ser iguales a los 'name' del input HTML
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
                datos.get('id_proyecto'), 
                datos.get('id_maquinaria'), 
                datos.get('empresa_rif'), 
                datos.get('empresa_proyecto_id'), 
                datos.get('empresa_maquinaria_id')
            )
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True
            
        except Exception as e:
            print(f"--- [ERROR DETALLADO]: {e} ---") 
            return False

    def obtener_todas_las_contrataciones(self):
        conexion = connectionBD()
        if conexion is None:
            return []
            
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM gestionar_contrataciones")
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [ERROR AL CONSULTAR]: {e} ---")
            return []
        finally:
            if conexion:
                conexion.close()