from conexion.conexionBD import connectionBD_invilara

class EmpresaModel:
    def obtener_todas_las_empresas(self):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            # FILTRO: Solo seleccionamos las empresas activas (estado = 1)
            sql = """
                SELECT rif, nombre_empresa, telefono, domicilio_fiscal 
                FROM empresa
                WHERE estado = 1
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
            
            # --- VALIDACIÓN DE NEGOCIO: Verificar si el RIF ya existe y su estado ---
            cursor.execute("SELECT rif, estado FROM empresa WHERE rif = %s", (datos['rif'],))
            empresa_existente = cursor.fetchone()
            
            if empresa_existente:
                if empresa_existente['estado'] == 1:
                    return "DUPLICADO" # El RIF ya está activo en el sistema
                else:
                    # Si existía pero estaba dada de baja (estado 0), la reactivamos con los nuevos datos
                    sql_reactivar = """
                        UPDATE empresa 
                        SET nombre_empresa = %s, telefono = %s, domicilio_fiscal = %s, estado = 1 
                        WHERE rif = %s
                    """
                    valores = (
                        datos['nombre_empresa'], 
                        datos['telefono'], 
                        datos['domicilio_fiscal'],
                        datos['rif']
                    )
                    cursor.execute(sql_reactivar, valores)
                    conexion.commit()
                    return True
            
            # Si no existe en absoluto, procedemos a realizar un INSERT común
            sql = "INSERT INTO empresa (rif, nombre_empresa, telefono, domicilio_fiscal, estado) VALUES (%s, %s, %s, %s, 1)"
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
            # Actualizamos los datos asegurándonos de que la empresa siga activa
            sql = """UPDATE empresa 
                     SET nombre_empresa = %s, 
                         telefono = %s, 
                         domicilio_fiscal = %s 
                     WHERE rif = %s AND estado = 1"""
            cursor.execute(sql, (
                datos['nombre_empresa'], 
                datos['telefono'], 
                datos['domicilio_fiscal'], 
                datos['rif']
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
            
            # BORRADO LÓGICO: Cambiamos el estado a 0. No rompe restricciones de FK.
            sql_empresa = "UPDATE empresa SET estado = 0 WHERE rif = %s"
            cursor.execute(sql_empresa, (rif,))
            
            conexion.commit()
            return cursor.rowcount > 0 # Retorna True si se desactivó la empresa correctamente
        except Exception as e:
            print(f"Error al eliminar empresa de forma lógica: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_relaciones_activas(self):
        conexion = connectionBD_invilara()
        try:
            cursor = conexion.cursor(dictionary=True)
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