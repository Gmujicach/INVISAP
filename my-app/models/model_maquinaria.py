from conexion.conexionBD import connectionBD

class MaquinariaModel:
    def registrar_maquinaria(self, nombre):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            sql = "INSERT INTO maquinaria (nombre_maquinaria) VALUES (%s)"
            cursor.execute(sql, (nombre,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en MaquinariaModel.registrar_maquinaria: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_maquinarias(self):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria ORDER BY id_maquinaria DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en MaquinariaModel.obtener_maquinarias: {e}")
            return []
        finally:
            if conexion: conexion.close()

    def obtener_maquinaria_por_id(self, id_maquinaria):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM maquinaria WHERE id_maquinaria = %s"
            cursor.execute(sql, (id_maquinaria,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error en MaquinariaModel.obtener_maquinaria_por_id: {e}")
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_maquinaria(self, id_maquinaria, nombre):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor()
            sql = "UPDATE maquinaria SET nombre_maquinaria = %s WHERE id_maquinaria = %s"
            cursor.execute(sql, (nombre, id_maquinaria))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en MaquinariaModel.actualizar_maquinaria: {e}")
            return False
        finally:
            if conexion: conexion.close()

    def eliminar_maquinaria(self, id_maquinaria):
        conexion = None
        try:
            conexion = connectionBD()
            cursor = conexion.cursor(dictionary=True)
            
            # Verificar si la maquinaria está siendo usada en algún proyecto
            cursor.execute("SELECT COUNT(*) as total FROM gestionar_proyectos WHERE maquinaria_id_maquinaria = %s", (id_maquinaria,))
            if cursor.fetchone()['total'] > 0:
                return "utilizada"

            cursor.execute("DELETE FROM maquinaria WHERE id_maquinaria = %s", (id_maquinaria,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error en MaquinariaModel.eliminar_maquinaria: {e}")
            return False
        finally:
            if conexion: conexion.close()