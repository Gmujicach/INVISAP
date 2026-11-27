"""
EmpresaModel — Modelo SOLID/POO para gestión de empresas.
Implementa encapsulamiento, validaciones Regex, borrado lógico y requisitos legales.
"""

import re
from models.base_model import BaseModel


REQUISITOS_EMPRESA = (
    'req_acta_constitutiva',
    'req_acta_asamblea',
    'req_rif',
    'req_cedula_representante',
    'req_poder_representante',
    'req_estados_financieros',
    'req_declaracion_islr',
    'req_solvencia_seniat',
    'req_solvencia_ivss',
    'req_relacion_experiencia',
    'req_nomina_personal',
    'req_relacion_equipos',
    'req_clasificacion',
)


class EmpresaModel(BaseModel):
    """Repositorio de empresas con validación y encapsulamiento."""

    _RE_RIF = re.compile(r'^[A-Za-z0-9\-]{1,12}$')
    _RE_NOMBRE = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:áéíóúÁÉÍÓÚñÑ]{3,100}$', re.UNICODE)
    _RE_TELEFONO = re.compile(r'^[\d\s\-\(\)]{7,20}$')
    _RE_DIRECCION = re.compile(r'^[\w\s\.\,\-\#\/\(\)\:áéíóúÁÉÍÓÚñÑ]{5,200}$', re.UNICODE)

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__rif = None
        self.__nombre_empresa = None
        self.__telefono = None
        self.__domicilio_fiscal = None
        self.__cumple_requisitos = 0
        self.__estado = 1
        self.__asegurar_tabla_empresa()
        self.__asegurar_tabla_requisitos()

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========

    def get_rif(self):
        return self.__rif

    def set_rif(self, valor):
        if not self._RE_RIF.match(str(valor or '').strip()):
            raise ValueError("RIF inválido. Formato: J-12345678-9 o similar (máx 12 chars).")
        self.__rif = valor.strip().upper()[:12]

    def get_nombre_empresa(self):
        return self.__nombre_empresa

    def set_nombre_empresa(self, valor):
        if not self._RE_NOMBRE.match(str(valor or '').strip()):
            raise ValueError("Nombre de empresa inválido. Mínimo 3, máximo 100 caracteres.")
        self.__nombre_empresa = self._limpiar_texto(valor, 100)

    def get_telefono(self):
        return self.__telefono

    def set_telefono(self, valor):
        if valor and not self._RE_TELEFONO.match(str(valor).strip()):
            raise ValueError("Teléfono inválido. Formato: 0414-1234567 o similar.")
        self.__telefono = self._limpiar_texto(valor or '', 20)

    def get_domicilio_fiscal(self):
        return self.__domicilio_fiscal

    def set_domicilio_fiscal(self, valor):
        if not self._RE_DIRECCION.match(str(valor or '').strip()):
            raise ValueError("Domicilio fiscal inválido. Mínimo 5, máximo 200 caracteres.")
        self.__domicilio_fiscal = self._limpiar_texto(valor, 200)

    def get_cumple_requisitos(self):
        return self.__cumple_requisitos

    def set_cumple_requisitos(self, valor):
        self.__cumple_requisitos = 1 if int(valor) else 0

    def get_estado(self):
        return self.__estado

    def set_estado(self, valor):
        self.__estado = 1 if int(valor) else 0

    # ========== MÉTODOS PRIVADOS DE BASE DE DATOS ==========

    def __asegurar_tabla_empresa(self):
        try:
            conexion = self.obtener_conexion_estricta()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("SHOW COLUMNS FROM empresa LIKE 'estado'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE empresa ADD COLUMN estado TINYINT NOT NULL DEFAULT 1")
                    conexion.commit()
                cursor.execute("SHOW COLUMNS FROM empresa LIKE 'cumple_requisitos'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE empresa ADD COLUMN cumple_requisitos TINYINT NOT NULL DEFAULT 0")
                    conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla empresa: {e}")

    def __asegurar_tabla_requisitos(self):
        try:
            conexion = self.obtener_conexion_estricta()
            if conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS empresa_requisito (
                        rif VARCHAR(12) NOT NULL,
                        requisito VARCHAR(50) NOT NULL,
                        verificado TINYINT(1) NOT NULL DEFAULT 0,
                        PRIMARY KEY (rif, requisito),
                        CONSTRAINT fk_empresa_requisito_empresa
                            FOREIGN KEY (rif) REFERENCES empresa (rif)
                            ON DELETE CASCADE ON UPDATE CASCADE
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
                """)
                conexion.commit()
                cursor.close()
                conexion.close()
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla empresa_requisito: {e}")

    def __ejecutar_consulta(self, sql, valores=None, un_solo_registro=False):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)
            if valores:
                cursor.execute(sql, valores)
            else:
                cursor.execute(sql)
            return cursor.fetchone() if un_solo_registro else cursor.fetchall()
        except Exception as e:
            print(f"[EmpresaModel] Error en consulta: {e}")
            return None if un_solo_registro else []
        finally:
            if conexion:
                conexion.close()

    def __ejecutar_modificacion(self, sql, valores, retornar_rowcount=False):
        conexion = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor()
            cursor.execute(sql, valores)
            conexion.commit()
            if retornar_rowcount:
                return cursor.rowcount > 0
            return True
        except Exception as e:
            print(f"[EmpresaModel] Error en modificación: {e}")
            return 0 if retornar_rowcount else False
        finally:
            if conexion:
                conexion.close()

    def __obtener_todas_empresas_db(self):
        sql = """
            SELECT rif, nombre_empresa, telefono, domicilio_fiscal, cumple_requisitos
            FROM empresa
            WHERE estado = 1
            ORDER BY nombre_empresa ASC
        """
        return self.__ejecutar_consulta(sql)

    def __registrar_empresa_db(self):
        sql_buscar = "SELECT rif, estado FROM empresa WHERE rif = %s"
        empresa_existente = self.__ejecutar_consulta(sql_buscar, (self.__rif,), un_solo_registro=True)

        if empresa_existente:
            if empresa_existente['estado'] == 1:
                return "DUPLICADO"
            else:
                sql_reactivar = """
                    UPDATE empresa
                    SET nombre_empresa = %s, telefono = %s, domicilio_fiscal = %s, estado = 1
                    WHERE rif = %s
                """
                valores_reactivar = (self.__nombre_empresa, self.__telefono, self.__domicilio_fiscal, self.__rif)
                return self.__ejecutar_modificacion(sql_reactivar, valores_reactivar)

        sql_insert = """
            INSERT INTO empresa (rif, nombre_empresa, telefono, domicilio_fiscal, estado)
            VALUES (%s, %s, %s, %s, 1)
        """
        valores_insert = (self.__rif, self.__nombre_empresa, self.__telefono, self.__domicilio_fiscal)
        return self.__ejecutar_modificacion(sql_insert, valores_insert)

    def __actualizar_empresa_db(self):
        sql = """
            UPDATE empresa
            SET nombre_empresa = %s,
                telefono = %s,
                domicilio_fiscal = %s
            WHERE rif = %s AND estado = 1
        """
        valores = (self.__nombre_empresa, self.__telefono, self.__domicilio_fiscal, self.__rif)
        return self.__ejecutar_modificacion(sql, valores)

    def __eliminar_empresa_db(self, rif):
        sql = "UPDATE empresa SET estado = 0 WHERE rif = %s"
        return self.__ejecutar_modificacion(sql, (rif,), retornar_rowcount=True)

    def __actualizar_cumple_requisitos_db(self, rif, valor):
        sql = "UPDATE empresa SET cumple_requisitos = %s WHERE rif = %s AND estado = 1"
        return self.__ejecutar_modificacion(sql, (valor, rif), retornar_rowcount=True)

    def __obtener_requisitos_db(self, rif):
        conexion = None
        cursor = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor(dictionary=True)
            self.__asegurar_tabla_requisitos()
            cursor.execute("SELECT cumple_requisitos FROM empresa WHERE rif = %s AND estado = 1", (rif,))
            empresa = cursor.fetchone()
            if not empresa:
                return None
            cursor.execute("SELECT requisito, verificado FROM empresa_requisito WHERE rif = %s", (rif,))
            requisitos_guardados = cursor.fetchall()
            valor_legacy = bool(empresa['cumple_requisitos'])
            requisitos = {nombre: valor_legacy for nombre in REQUISITOS_EMPRESA}
            requisitos.update({
                fila['requisito']: bool(fila['verificado'])
                for fila in requisitos_guardados
                if fila['requisito'] in REQUISITOS_EMPRESA
            })
            return requisitos
        except Exception as e:
            print(f"[EmpresaModel] Error consultando requisitos: {e}")
            raise RuntimeError('No se pudieron consultar los requisitos legales.') from e
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __actualizar_requisitos_db(self, rif, requisitos):
        if (not isinstance(requisitos, dict)
                or set(requisitos) != set(REQUISITOS_EMPRESA)
                or any(type(valor) is not bool for valor in requisitos.values())):
            return False

        conexion = None
        cursor = None
        try:
            conexion = self.obtener_conexion_estricta()
            cursor = conexion.cursor()
            self.__asegurar_tabla_requisitos()
            cursor.execute("SELECT rif FROM empresa WHERE rif = %s AND estado = 1 FOR UPDATE", (rif,))
            if not cursor.fetchone():
                conexion.rollback()
                return False

            for requisito, verificado in requisitos.items():
                cursor.execute("""
                    INSERT INTO empresa_requisito (rif, requisito, verificado)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE verificado = VALUES(verificado)
                """, (rif, requisito, int(verificado)))

            cumple = int(all(requisitos.values()))
            cursor.execute("UPDATE empresa SET cumple_requisitos = %s WHERE rif = %s AND estado = 1", (cumple, rif))
            conexion.commit()
            return True
        except Exception as e:
            if conexion:
                conexion.rollback()
            print(f"[EmpresaModel] Error guardando requisitos: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()

    def __obtener_relaciones_activas_db(self):
        sql = """
            SELECT
                p.codigo_proyecto,
                m.id_maquinaria,
                CONCAT(p.codigo_proyecto, ' | ', p.descripcion_tecnica, ' | ', m.nombre_maquinaria) as info_completa
            FROM proyecto p
            JOIN proyecto_has_maquinaria phm ON p.codigo_proyecto = phm.proyecto_codigo_proyecto
            JOIN maquinaria m ON phm.maquinaria_id_maquinaria = m.id_maquinaria
        """
        return self.__ejecutar_consulta(sql)

    # ========== MÉTODOS PÚBLICOS (Fachada) ==========

    def obtener_todas(self):
        """Método público para obtener todas las empresas activas."""
        return self.__obtener_todas_empresas_db()

    def registrar(self, datos):
        """Método público para registrar empresa."""
        try:
            self.set_rif(datos['rif'])
            self.set_nombre_empresa(datos['nombre_empresa'])
            self.set_telefono(datos.get('telefono', ''))
            self.set_domicilio_fiscal(datos['domicilio_fiscal'])
            return self.__registrar_empresa_db()
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            print(f"Error registrando empresa: {e}")
            return False, "Error interno al registrar."

    def actualizar(self, datos):
        """Método público para actualizar empresa."""
        try:
            self.set_rif(datos['rif'])
            self.set_nombre_empresa(datos['nombre_empresa'])
            self.set_telefono(datos.get('telefono', ''))
            self.set_domicilio_fiscal(datos['domicilio_fiscal'])
            return self.__actualizar_empresa_db()
        except ValueError as ve:
            return False, str(ve)
        except Exception as e:
            print(f"Error actualizando empresa: {e}")
            return False, "Error interno al actualizar."

    def eliminar(self, rif):
        """Método público para borrado lógico de empresa."""
        return self.__eliminar_empresa_db(rif)

    def actualizar_cumple_requisitos(self, rif, valor):
        """Método público para actualizar cumplimiento de requisitos."""
        return self.__actualizar_cumple_requisitos_db(rif, valor)

    def obtener_requisitos(self, rif):
        """Método público para obtener requisitos de una empresa."""
        return self.__obtener_requisitos_db(rif)

    def actualizar_requisitos(self, rif, requisitos):
        """Método público para actualizar requisitos de una empresa."""
        return self.__actualizar_requisitos_db(rif, requisitos)

    def obtener_relaciones_activas(self):
        """Método público para obtener relaciones proyecto-maquinaria."""
        return self.__obtener_relaciones_activas_db()

    def validar_rif_existente(self, rif, excluir_rif=None):
        """Método público para validar RIF duplicado."""
        conexion = self.obtener_conexion_estricta()
        if not conexion:
            return False
        try:
            cursor = conexion.cursor()
            if excluir_rif:
                cursor.execute("SELECT 1 FROM empresa WHERE rif = %s AND rif != %s AND estado = 1 LIMIT 1", (rif.strip(), excluir_rif))
            else:
                cursor.execute("SELECT 1 FROM empresa WHERE rif = %s AND estado = 1 LIMIT 1", (rif.strip(),))
            return cursor.fetchone() is not None
        except Exception as e:
            print(f"Error validando RIF: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            conexion.close()