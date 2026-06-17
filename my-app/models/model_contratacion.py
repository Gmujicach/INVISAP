from conexion.conexionBD import connectionBD_invilara as connectionBD

class ContratacionModel:
    
    def registrar_contrataciones(self, datos):
        conexion = connectionBD()
        if conexion is None: return False
            
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO contratacion (
                descripcion, empresa_ganadora, numero_contrato, monto, 
                fecha_inicio_procedimiento, fecha_adjudicacion, tipo_contrato, 
                modalidad, objeto, observacion, fecha_registro, empresa_rif
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            
            valores = (
                datos.get('descripcion'), 
                datos.get('empresa_ganadora'), 
                datos.get('numero_contrato'), 
                datos.get('monto'), 
                datos.get('fecha_inicio_procedimiento'), 
                datos.get('fecha_adjudicacion'), 
                datos.get('tipo_contrato'), 
                datos.get('modalidad'), 
                datos.get('objeto'), 
                datos.get('observacion'), 
                datos.get('fecha_registro'), 
                datos.get('empresa_rif')
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
            
            sql = """
            SELECT c.*, e.nombre_empresa 
            FROM contratacion c
            LEFT JOIN empresa e ON c.empresa_rif = e.rif
            """
            
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [ERROR AL CONSULTAR]: {e} ---")
            return []
        finally:
            if conexion: conexion.close()


    def obtener_empresas(self):
        conexion = connectionBD()
        if conexion is None: return []
            
        try:
            cursor = conexion.cursor(dictionary=True)
            # Consultamos el RIF y el Nombre exacto de la tabla empresa
            sql = "SELECT rif, nombre_empresa FROM empresa"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [ERROR AL OBTENER EMPRESAS PARA MODAL]: {e} ---")
            return []
        finally:
            if conexion: conexion.close()

    def obtener_contratacion_por_id(self, id_contratacion):
        conexion = connectionBD()
        if conexion is None: return None
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM contratacion WHERE id_contratacion = %s"
            cursor.execute(sql, (id_contratacion,))
            return cursor.fetchone()
        except Exception as e:
            print(f"--- [ERROR AL BUSCAR UNA CONTRATACION]: {e} ---")
            return None
        finally:
            if conexion: conexion.close()


    def actualizar_contratacion(self, datos):
        conexion = connectionBD()
        if conexion is None: return False
        try:
            cursor = conexion.cursor()
            sql = """UPDATE contratacion SET 
                descripcion = %s, empresa_ganadora = %s, numero_contrato = %s, monto = %s, 
                fecha_inicio_procedimiento = %s, fecha_adjudicacion = %s, tipo_contrato = %s, 
                modalidad = %s, objeto = %s, observacion = %s, fecha_registro = %s, empresa_rif = %s 
                WHERE id_contratacion = %s"""
            valores = (
                datos.get('descripcion'),
                datos.get('empresa_ganadora'),
                datos.get('numero_contrato'),
                datos.get('monto'),
                datos.get('fecha_inicio_procedimiento'),
                datos.get('fecha_adjudicacion'),
                datos.get('tipo_contrato'),
                datos.get('modalidad'),
                datos.get('objeto'),
                datos.get('observacion'),
                datos.get('fecha_registro'),
                datos.get('empresa_rif'),
                datos.get('id_contratacion')
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return True
        except Exception as e:
            print(f"--- [ERROR DETALLADO UPDATE]: {e} ---")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_contratacion(self, id_contratacion):
        conexion = connectionBD()
        if conexion is None: return False
            
        try:
            cursor = conexion.cursor()
            sql = "DELETE FROM contratacion WHERE id_contratacion = %s"
            cursor.execute(sql, (id_contratacion,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"--- [ERROR AL ELIMINAR CONTRATACION]: {e} ---")
            return False
        finally:
            if conexion: conexion.close()