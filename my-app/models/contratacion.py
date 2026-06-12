from conexion.conexionBD import connectionBD_invilara as connectionBD

class ContratacionModel:
    
    def registrar_contrataciones(self, datos):
        conexion = connectionBD()
        if conexion is None:
            print("Error: No se pudo establecer conexión.")
            return False
            
        try:
            cursor = conexion.cursor()
            
            sql = """INSERT INTO contrataciones (
                descripcion, empresa_ganadora, numero_contrato, monto, tipo_contrato, 
                fecha_inicio_procedimiento, fecha_adjudicacion, fecha_registro, 
                modalidad, objeto, observacion, 
                gestionar_proyectos_id_proyectos, gestionar_proyectos_maquinaria_id_maquinaria, 
                empresa_rif, empresa_gestionar_proyectos_id_proyectos, 
                empresa_gestionar_proyectos_maquinaria_id_maquinaria
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            valores = (
                datos['descripcion'], datos['empresa_ganadora'], datos['numero_contrato'], 
                datos['monto'], datos['tipo_contrato'], datos['fecha_inicio'], 
                datos['fecha_adjudicacion'], datos['fecha_registro'], datos['modalidad'], 
                datos['objeto'], datos['observacion'], datos['id_proyecto'], 
                datos['id_maquinaria'], datos['empresa_rif'], 
                datos['empresa_proyecto_id'], datos['empresa_maquinaria_id']
            )
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True
            
        except Exception as e:
            print(f"--- [ERROR AL REGISTRAR]: {e} ---")
            return False
            
        finally:
            if conexion:
                conexion.close()

    def obtener_todas_las_contrataciones(self):
        conexion = connectionBD()
        if conexion is None:
            return []
            
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM contrataciones")
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [ERROR AL CONSULTAR]: {e} ---")
            return []
        finally:
            if conexion:
                conexion.close()