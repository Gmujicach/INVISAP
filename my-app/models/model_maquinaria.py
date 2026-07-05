from conexion.conexionBD import connectionBD
import re

class MaquinariaModel:
    _RE_NOMBRE = re.compile(r'^[\w\s\.\-áéíóúÁÉÍÓÚñÑ]{3,50}$', re.UNICODE)
    
    def obtener_maquinarias(self, page=1, per_page=10):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            offset = (page - 1) * per_page
            cursor.execute("SELECT * FROM maquinaria WHERE estado = 1 ORDER BY id_maquinaria DESC LIMIT %s OFFSET %s", (per_page, offset))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_maquinarias: {e}")
            return []
        finally:
            if cursor: cursor.close()
            conexion.close()

    def contar_maquinarias(self):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM maquinaria WHERE estado = 1")
            return cursor.fetchone()[0]
        except Exception as e:
            print(f"Error en contar_maquinarias: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            conexion.close()

    def obtener_maquinarias_eliminadas(self):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM maquinaria WHERE estado = 0 ORDER BY id_maquinaria DESC")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error en obtener_maquinarias_eliminadas: {e}")
            return []
        finally:
            if cursor: cursor.close()
            conexion.close()

    def restaurar_maquinaria(self, id_maquinaria):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("UPDATE maquinaria SET estado = 1 WHERE id_maquinaria = %s AND estado = 0", (id_maquinaria,))
            conexion.commit()
            if cursor.rowcount > 0:
                return {'success': True, 'message': 'Maquinaria restaurada correctamente'}
            return {'success': False, 'message': 'Maquinaria no encontrada o ya está activa'}
        except Exception as e:
            print(f"Error al restaurar: {e}")
            return {'success': False, 'message': 'Error al restaurar en la base de datos'}
        finally:
            if cursor: cursor.close()
            conexion.close()

    def validar_nombre(self, nombre):
        if not nombre or not nombre.strip():
            return {'valido': False, 'mensaje': 'El nombre es requerido'}
        if len(nombre.strip()) < 3:
            return {'valido': False, 'mensaje': 'El nombre debe tener al menos 3 caracteres'}
        if not self._RE_NOMBRE.match(nombre.strip()):
            return {'valido': False, 'mensaje': 'El nombre contiene caracteres inválidos'}
        return {'valido': True}

    def validar_tipo(self, tipo):
        tipos_validos = ['Pesada', 'Liviana', 'Herramienta', 'Vehículo']
        if not tipo or tipo not in tipos_validos:
            return {'valido': False, 'mensaje': 'Debe seleccionar un tipo válido'}
        return {'valido': True}

    def registrar_maquinaria(self, nombre, tipo):
        val_nombre = self.validar_nombre(nombre)
        if not val_nombre['valido']:
            return {'success': False, 'message': val_nombre['mensaje']}
        
        val_tipo = self.validar_tipo(tipo)
        if not val_tipo['valido']:
            return {'success': False, 'message': val_tipo['mensaje']}

        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id_maquinaria, estado FROM maquinaria WHERE nombre_maquinaria = %s", (nombre.strip(),))
            existe = cursor.fetchone()
            
            if existe:
                if existe['estado'] == 1:
                    return {'success': False, 'message': 'Esta maquinaria ya está registrada.'}
                else:
                    # Restaurar maquinaria desactivada
                    cursor.execute("UPDATE maquinaria SET estado = 1 WHERE id_maquinaria = %s", (existe['id_maquinaria'],))
                    conexion.commit()
                    return {'success': True, 'id': existe['id_maquinaria'], 'restaurada': True, 'message': 'Maquinaria restaurada correctamente'}
            
            sql = "INSERT INTO maquinaria (nombre_maquinaria, tipo_maquinaria, estado) VALUES (%s, %s, 1)"
            cursor.execute(sql, (nombre.strip(), tipo))
            conexion.commit()
            return {'success': True, 'id': cursor.lastrowid, 'message': 'Maquinaria registrada correctamente'}
        except Exception as e:
            print(f"Error al registrar: {e}")
            return {'success': False, 'message': f'Error al registrar en la base de datos: {str(e)}'}
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
        val_nombre = self.validar_nombre(nombre)
        if not val_nombre['valido']:
            return {'success': False, 'message': val_nombre['mensaje']}
        
        val_tipo = self.validar_tipo(tipo)
        if not val_tipo['valido']:
            return {'success': False, 'message': val_tipo['mensaje']}

        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            sql = "UPDATE maquinaria SET nombre_maquinaria = %s, tipo_maquinaria = %s WHERE id_maquinaria = %s"
            cursor.execute(sql, (nombre.strip(), tipo, id_maquinaria))
            conexion.commit()
            return {'success': True, 'message': 'Maquinaria actualizada correctamente'}
        except Exception as e:
            print(f"Error al actualizar: {e}")
            return {'success': False, 'message': 'Error al actualizar en la base de datos'}
        finally:
            if cursor: cursor.close()
            conexion.close()

    def eliminar_maquinaria(self, id_maquinaria):
        conexion = connectionBD()
        cursor = None
        try:
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM proyecto_has_maquinaria WHERE maquinaria_id_maquinaria = %s", (id_maquinaria,))
            result = cursor.fetchone()
            count = result['count'] if isinstance(result, dict) else result[0]
            if count > 0:
                return "utilizada"
            cursor.execute("UPDATE maquinaria SET estado = 0 WHERE id_maquinaria = %s", (id_maquinaria,))
            conexion.commit()
            return "eliminada"
        except Exception as e:
            print(f"Error al eliminar: {e}")
            return 0
        finally:
            if cursor: cursor.close()
            conexion.close()