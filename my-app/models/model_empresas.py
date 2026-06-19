from conexion.conexionBD import connectionBD_invilara

class EmpresaModel:
    def obtener_todas_las_empresas(self):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            # Seleccionamos los campos correspondientes a la tabla empresas
            sql = """
                SELECT rif, nombre_empresa, telefono, domicilio_fiscal 
                FROM empresa
                ORDER BY nombre_empresa ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener empresas: {e}")
            return []
        finally:
            if conexion: conexion.close()

    def registrar_Empresas(self, datos):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            
            # --- VALIDACIÓN DE NEGOCIO: Evitar duplicados ---
            cursor.execute("SELECT rif FROM empresa WHERE rif = %s", (datos['rif'],))
            if cursor.fetchone():
                return "DUPLICADO" # Avisamos al controlador que el RIF ya existe
            
            # Si no existe, procedemos a insertar
            sql = "INSERT INTO empresa (rif, nombre_empresa, telefono, domicilio_fiscal) VALUES (%s, %s, %s, %s)"
            valores = (
                datos['rif'], 
                datos['nombre_empresa'], 
                datos['telefono'], 
                datos['domicilio_fiscal']
            )
            cursor.execute(sql, valores)
            conexion.commit()
            return True
            
        except Exception as e:
            print(f"Error fatal en el modelo al insertar empresa: {e}")
            return False
            
        finally:
            if conexion: conexion.close()

    def update_empresa(self, datos):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            # Se actualizan los datos buscando por el RIF
            sql = """UPDATE empresa 
                     SET nombre_empresa = %s, 
                         telefono = %s, 
                         domicilio_fiscal = %s 
                     WHERE rif = %s"""
            cursor.execute(sql, (
                datos['nombre_empresa'], 
                datos['telefono'], 
                datos['domicilio_fiscal'], 
                datos['rif']  # El RIF va de último para el WHERE
            ))
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al actualizar empresa: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_empresa(self, rif):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            
            # PASO 1: Eliminar las relaciones de esta empresa en los proyectos primero
            # Esto evita el error de bloqueo de MySQL
            #sql_proyectos = "DELETE FROM proyecto WHERE empresa_rif = %s"
            #cursor.execute(sql_proyectos, (rif,))
            
            # PASO 2: Ahora sí, eliminar la empresa tranquilamente
            sql_empresa = "DELETE FROM empresa WHERE rif = %s"
            cursor.execute(sql_empresa, (rif,))
            
            conexion.commit()
            return True
        except Exception as e:
            print(f"Error al eliminar empresa: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_relaciones_activas(self):
        conexion = connectionBD_invilara()
        try:
            cursor = conexion.cursor(dictionary=True)
            # Unimos las tablas para que el usuario vea: "Proyecto - Maquinaria"
            # Se actualizó el nombre de la tabla a 'proyecto' y se usa la tabla intermedia proyecto_has_maquinaria
            sql = """
            SELECT 
                p.codigo_proyecto, 
                m.id_maquinaria,
                CONCAT(p.codigo_proyecto, ' | ', p.descripcion_tecnica, ' | ', m.nombre_maquinaria) as info_completa
            FROM proyecto p
            JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
            JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al obtener relaciones activas: {e}")
            return []
        finally:
            if conexion: conexion.close()