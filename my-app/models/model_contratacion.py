from conexion.conexionBD import connectionBD_invilara as connectionBD
import re

class ContratacionModel:
    
    # MÉTODO PRIVADO:
    def __validar_datos(self, datos):
        try:
            campos_requeridos = [
                'empresa_ganadora', 'empresa_rif', 'descripcion', 'numero_contrato',
                'monto', 'tipo_contrato', 'modalidad', 'objeto', 
                'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'
            ]
            
            for campo in campos_requeridos:
                valor = str(datos.get(campo, '')).strip()
                if not valor or valor == 'None':
                    nombre_legible = campo.replace('_', ' ').capitalize()
                    return False, f"El campo '{nombre_legible}' es obligatorio o inválido."

            if len(str(datos.get('descripcion')).strip()) < 5:
                return False, "La descripción debe tener al menos 5 caracteres."
                
            if len(str(datos.get('numero_contrato')).strip()) < 3:
                return False, "El número de contrato debe tener al menos 3 caracteres."

            if datos.get('tipo_contrato') not in ['Contrato de Obra', 'Contrato de Servicio', 'Contrato de Bienes']:
                return False, "Tipo de contrato no permitido."

            if datos.get('modalidad') not in ['Concurso Abierto', 'Concurso Cerrado', 'Consulta de Precios', 'Contratación Directa']:
                return False, "Modalidad no permitida."

            if datos.get('objeto') not in ['Ejecución de Obras', 'Prestación de Servicios', 'Suministro de Bienes']:
                return False, "Objeto de contratación no permitido."

            patron_fecha = r'^\d{4}-\d{2}-\d{2}$'
            for campo_fecha in ['fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro']:
                if not re.match(patron_fecha, str(datos.get(campo_fecha))):
                    return False, f"Formato de fecha inválido en {campo_fecha}."

            return True, "Validación exitosa"
            
        except Exception as e:
            return False, f"Error crítico validando datos: {e}"



    # MÉTODOS PÚBLICOS    
    def registrar_contrataciones(self, datos):
        es_valido, mensaje = self.__validar_datos(datos)
        if not es_valido:
            return False, mensaje

        conexion = connectionBD()
        if conexion is None: 
            return False, "Error de conexión a la base de datos."
            
        try:
            cursor = conexion.cursor()
            sql = """INSERT INTO contratacion (
                descripcion, empresa_ganadora, numero_contrato, monto, 
                fecha_inicio_procedimiento, fecha_adjudicacion, tipo_contrato, 
                modalidad, objeto, observacion, fecha_registro, empresa_rif, estado
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1)"""
            
            valores = (
                datos.get('descripcion'), datos.get('empresa_ganadora'), 
                datos.get('numero_contrato'), datos.get('monto'), 
                datos.get('fecha_inicio_procedimiento'), datos.get('fecha_adjudicacion'), 
                datos.get('tipo_contrato'), datos.get('modalidad'), 
                datos.get('objeto'), datos.get('observacion'), 
                datos.get('fecha_registro'), datos.get('empresa_rif')
            )
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True, "Contratación registrada correctamente."
            
        except Exception as e:
            print(f"--- [MODELO] ERROR SQL INSERT: {e} ---") 
            return False, "Número de Contrato ya se Encuentra Registrado."
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
            WHERE c.estado = 1
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [MODELO] ERROR AL CONSULTAR: {e} ---")
            return []
        finally:
            if conexion: conexion.close()

    def obtener_contratacion_por_id(self, id_contratacion):
        conexion = connectionBD()
        if conexion is None: return None
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM contratacion WHERE id_contratacion = %s AND estado = 1"
            cursor.execute(sql, (id_contratacion,))
            return cursor.fetchone()
        except Exception as e:
            print(f"--- [MODELO] ERROR BUSCAR POR ID: {e} ---")
            return None
        finally:
            if conexion: conexion.close()

    def actualizar_contratacion(self, datos):
        es_valido, mensaje = self.__validar_datos(datos)
        if not es_valido:
            return False, mensaje

        if not datos.get('id_contratacion'):
            return False, "Falta el ID de la contratación para actualizar."

        conexion = connectionBD()
        if conexion is None: 
            return False, "Error de conexión a la base de datos."
        
        try:
            cursor = conexion.cursor()
            sql = """UPDATE contratacion SET 
                descripcion = %s, empresa_ganadora = %s, numero_contrato = %s, monto = %s, 
                fecha_inicio_procedimiento = %s, fecha_adjudicacion = %s, tipo_contrato = %s, 
                modalidad = %s, objeto = %s, observacion = %s, fecha_registro = %s, empresa_rif = %s 
                WHERE id_contratacion = %s AND estado = 1"""
            
            valores = (
                datos.get('descripcion'), datos.get('empresa_ganadora'), 
                datos.get('numero_contrato'), datos.get('monto'), 
                datos.get('fecha_inicio_procedimiento'), datos.get('fecha_adjudicacion'), 
                datos.get('tipo_contrato'), datos.get('modalidad'), 
                datos.get('objeto'), datos.get('observacion'), 
                datos.get('fecha_registro'), datos.get('empresa_rif'), 
                datos.get('id_contratacion')
            )
            
            cursor.execute(sql, valores)
            conexion.commit()
            return True, "Contratación modificada correctamente."
            
        except Exception as e:
            print(f"--- [MODELO] ERROR SQL UPDATE: {e} ---")
            return False, "Error interno al actualizar en la base de datos."
        finally:
            if conexion: conexion.close()

    def eliminar_contratacion(self, id_contratacion):
        conexion = connectionBD()
        if conexion is None: return False
        try:
            cursor = conexion.cursor()
            # Borrado Lógico
            sql = "UPDATE contratacion SET estado = 0 WHERE id_contratacion = %s"
            cursor.execute(sql, (id_contratacion,))
            conexion.commit()
            return True
        except Exception as e:
            print(f"--- [MODELO] ERROR AL BORRAR LÓGICAMENTE: {e} ---")
            return False
        finally:
            if conexion: conexion.close()

    def obtener_empresas(self):
        conexion = connectionBD()
        if conexion is None: return []
        try:
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT rif, nombre_empresa FROM empresa WHERE estado = 1"
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"--- [MODELO] ERROR EMPRESAS: {e} ---")
            return []
        finally:
            if conexion: conexion.close()