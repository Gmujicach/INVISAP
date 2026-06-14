from conexion.conexionBD import connectionBD

class EmpresaModel:
    def obtener_empresas(self):
        conexion = connectionBD()
        if conexion is None: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            # Seleccionamos el RIF (value) y el nombre (lo que ve el usuario)
            cursor.execute("SELECT rif, nombre_empresa FROM empresa") 
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en EmpresaModel.obtener_empresas: {e}")
            return []
        finally:
            if conexion: conexion.close()

def obtener_relaciones_activas(self):
    conexion = connectionBD()
    try:
        cursor = conexion.cursor(dictionary=True)
        # Unimos las tablas para que el usuario vea: "Empresa X - Proyecto Y - Maquinaria Z"
        sql = """
        SELECT 
            e.rif, 
            p.id_proyectos, 
            m.id_maquinaria,
            CONCAT(e.nombre_empresa, ' | ', p.codigo_proyecto, ' | ', m.nombre_maquinaria) as info_completa
        FROM gestionar_proyectos p
        JOIN empresa e ON p.empresa_rif = e.rif 
        JOIN maquinaria m ON p.maquinaria_id_maquinaria = m.id_maquinaria
        """
        cursor.execute(sql)
        return cursor.fetchall()
    finally:
        conexion.close()