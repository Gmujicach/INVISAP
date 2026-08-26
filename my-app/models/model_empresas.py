from conexion.conexionBD import connectionBD_invilara
from models.base_model import BaseModel


class EmpresaModel(BaseModel):
    
    # MÉTODOS PRIVADOS
    
    def _ejecutar_consulta(self, sql, valores=None, un_solo_registro=False):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor(dictionary=True)
            
            if valores:
                cursor.execute(sql, valores)
            else:
                cursor.execute(sql)
                
            return cursor.fetchone() if un_solo_registro else cursor.fetchall()
        except Exception as e:
            print(f"[EmpresaModel] Error interno en consulta: {e}")
            return None if un_solo_registro else []
        finally:
            if conexion: 
                conexion.close()

    def _ejecutar_modificacion(self, sql, valores, retornar_rowcount=False):
        conexion = None
        try:
            conexion = connectionBD_invilara()
            cursor = conexion.cursor()
            cursor.execute(sql, valores)
            conexion.commit()
            
            if retornar_rowcount:
                return cursor.rowcount > 0
            return True
        except Exception as e:
            print(f"[EmpresaModel] Error interno en modificación: {e}")
            return 0 if retornar_rowcount else False
        finally:
            if conexion: 
                conexion.close()


    # MÉTODOS PÚBLICOS
    def obtener_todas_las_empresas(self):
        #Lista de todas las empresas activas.
        sql = """
            SELECT rif, nombre_empresa, telefono, domicilio_fiscal, cumple_requisitos 
            FROM empresa 
            WHERE estado = 1 
            ORDER BY nombre_empresa ASC
        """
        return self._ejecutar_consulta(sql)

    def registrar_Empresas(self, datos):
        sql_buscar = "SELECT rif, estado FROM empresa WHERE rif = %s"
        empresa_existente = self._ejecutar_consulta(sql_buscar, (datos['rif'],), un_solo_registro=True)
        
        if empresa_existente:
            if empresa_existente['estado'] == 1:
                return "DUPLICADO"  # El RIF ya está activo
            else:
                # Si existía pero estaba inactiva, Se reactiva
                sql_reactivar = """
                    UPDATE empresa 
                    SET nombre_empresa = %s, telefono = %s, domicilio_fiscal = %s, estado = 1 
                    WHERE rif = %s
                """
                valores_reactivar = (
                    datos['nombre_empresa'], 
                    datos['telefono'], 
                    datos['domicilio_fiscal'],
                    datos['rif']
                )
                return self._ejecutar_modificacion(sql_reactivar, valores_reactivar)
        
        sql_insert = """
            INSERT INTO empresa (rif, nombre_empresa, telefono, domicilio_fiscal, estado) 
            VALUES (%s, %s, %s, %s, 1)
        """
        valores_insert = (
            datos['rif'], 
            datos['nombre_empresa'], 
            datos['telefono'], 
            datos['domicilio_fiscal']
        )
        return self._ejecutar_modificacion(sql_insert, valores_insert)

    def update_empresa(self, datos):
        sql = """
            UPDATE empresa 
            SET nombre_empresa = %s, 
                telefono = %s, 
                domicilio_fiscal = %s 
            WHERE rif = %s AND estado = 1
        """
        valores = (
            datos['nombre_empresa'], 
            datos['telefono'], 
            datos['domicilio_fiscal'], 
            datos['rif']
        )
        return self._ejecutar_modificacion(sql, valores)

    def eliminar_empresa(self, rif):
        sql = "UPDATE empresa SET estado = 0 WHERE rif = %s"
        return self._ejecutar_modificacion(sql, (rif,), retornar_rowcount=True)

    def actualizar_cumple_requisitos(self, rif, valor):
        sql = "UPDATE empresa SET cumple_requisitos = %s WHERE rif = %s AND estado = 1"
        return self._ejecutar_modificacion(sql, (valor, rif), retornar_rowcount=True)

    def obtener_relaciones_activas(self):
        sql = """
            SELECT 
                p.codigo_proyecto, 
                m.id_maquinaria,
                CONCAT(p.codigo_proyecto, ' | ', p.descripcion_tecnica, ' | ', m.nombre_maquinaria) as info_completa
            FROM proyecto p
            JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
            JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria
        """
        return self._ejecutar_consulta(sql)