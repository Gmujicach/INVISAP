from conexion.conexionBD import connectionBD

class MaquinariaModel:
    def obtener_maquinarias(self):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria ORDER BY id_maquinaria DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_maquinarias: {e}")
            return []
        finally:
            if cursor: cursor.close()
            conexion.close()

    def registrar_maquinaria(self, nombre, tipo):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "INSERT INTO maquinaria (nombre_maquinaria, tipo_maquinaria) VALUES (%s, %s)"
            cursor.execute(sql, (nombre, tipo))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error al registrar: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            conexion.close()

    def obtener_maquinaria_por_id(self, id_maquinaria):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria WHERE id_maquinaria = %s", (id_maquinaria,))
            return cursor.fetchone()
        except Exception as e:
            print(f"Error al obtener por ID: {e}")
            return None
        finally:
            if cursor: cursor.close()
            conexion.close()

    def actualizar_maquinaria(self, id_maquinaria, nombre, tipo):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "UPDATE maquinaria SET nombre_maquinaria = %s, tipo_maquinaria = %s WHERE id_maquinaria = %s"
            cursor.execute(sql, (nombre, tipo, id_maquinaria))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error al actualizar: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            conexion.close()

    def eliminar_maquinaria(self, id_maquinaria):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM maquinaria WHERE id_maquinaria = %s", (id_maquinaria,))
            conexion.commit()
            return cursor.rowcount
        except Exception as e:
            print(f"Error al eliminar: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            conexion.close()