from conexion.conexionBD import connectionBD

class MaquinariaModel:
    def __init__(self):
        pass

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
            if conexion: conexion.rollback()
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