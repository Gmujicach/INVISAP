"""
RespaldoModel — Modelo SOLID para respaldo y restauración de base de datos MySQL.
Genera dumps con mysqldump, importa archivos .sql y registra metadatos en respaldo_bd.
"""
import os
import re
import subprocess
import logging
import traceback
from datetime import datetime
from decimal import Decimal
from conexion.conexionBD import connectionBD_invilara, connectionBD_invilara_seguridad, _get_env

logger = logging.getLogger(__name__)

class RespaldoModel:
    CARPETA_RESPALDOS = os.path.join('static', 'respaldos_bd')

    def __init__(self):
        if not os.path.exists(self.CARPETA_RESPALDOS):
            os.makedirs(self.CARPETA_RESPALDOS, exist_ok=True)

    def _asegurar_tabla_respaldo(self):
        """Crea la tabla respaldo_bd si no existe (auto-reparacion)."""
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            cur = conn.cursor()
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS respaldo_bd (
                        id_respaldo INT NOT NULL AUTO_INCREMENT,
                        nombre_archivo VARCHAR(255) NOT NULL,
                        tamano BIGINT NOT NULL DEFAULT 0,
                        descripcion VARCHAR(255) DEFAULT '',
                        fecha_respaldo TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        estado TINYINT NOT NULL DEFAULT 1,
                        PRIMARY KEY (id_respaldo)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
                """)
                conn.commit()
            finally:
                cur.close()
                conn.close()
            return True
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla respaldo_bd: {e}")
            return False

    def _asegurar_tabla_seguridad(self):
        """Crea la tabla administracion_respaldos en la BD de seguridad si no existe,
        con el esquema real (incluye columna estado y PK compuesta)."""
        conn = connectionBD_invilara_seguridad()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `administracion_respaldos` (
                    `id_respaldo` int(11) NOT NULL,
                    `fecha_respaldo` datetime NOT NULL,
                    `tamaño_respaldo` decimal(4,2) NOT NULL,
                    `usuarios_id_usuarios` int(11) NOT NULL,
                    `estado` tinyint(4) NOT NULL,
                    PRIMARY KEY (`id_respaldo`, `usuarios_id_usuarios`),
                    KEY `fk_administracion_respaldos_usuarios_idx` (`usuarios_id_usuarios`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
                COMMENT='Tabla de administracion de respaldos.'
            """)
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def _registrar_en_bd_seguridad(self, id_respaldo, tamano_bytes, id_usuario):
        tamano_mb = Decimal(str(round(tamano_bytes / (1024 * 1024), 2)))
        tamano_mb = min(tamano_mb, Decimal('99.99'))
        id_usuario = id_usuario or 1

        conn = connectionBD_invilara_seguridad()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos de seguridad.')
        db_actual = conn.database
        cur = conn.cursor()
        try:
            self._asegurar_tabla_seguridad()
            # Detectar si la tabla tiene una PK propia (id) o la PK compuesta original.
            cur.execute("SHOW COLUMNS FROM `administracion_respaldos` LIKE 'id'")
            tiene_id = cur.fetchone() is not None

            columnas = ("`id_respaldo`, `fecha_respaldo`, `tamaño_respaldo`, "
                        "`usuarios_id_usuarios`, `estado`")
            valores = (id_respaldo, datetime.now(), tamano_mb, id_usuario, 1)
            if tiene_id:
                cur.execute(
                    f"INSERT INTO `administracion_respaldos` ({columnas}) VALUES (%s, %s, %s, %s, %s)",
                    valores
                )
            else:
                # PK compuesta (id_respaldo, usuarios_id_usuarios): evita el choque por id reusado.
                cur.execute(
                    f"INSERT INTO `administracion_respaldos` ({columnas}) VALUES (%s, %s, %s, %s, %s) "
                    "ON DUPLICATE KEY UPDATE "
                    "`fecha_respaldo` = VALUES(`fecha_respaldo`), "
                    "`tamaño_respaldo` = VALUES(`tamaño_respaldo`), "
                    "`estado` = VALUES(`estado`)",
                    valores
                )
            conn.commit()
            logger.info("[Respaldo] Registro en seguridad OK (BD=%s, tabla=%s).", db_actual,
                        'id' if tiene_id else 'compuesta')
        finally:
            cur.close()
            conn.close()

        return db_actual

    @staticmethod
    def _limpiar_nombre(nombre):
        return re.sub(r'[^A-Za-z0-9_\-]', '_', nombre.strip())[:100]

    @staticmethod
    def _formatear_tamano(bytes_size):
        for unit in ['B','KB','MB','GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} GB"

    @staticmethod
    def _obtener_config_bd():
        host = os.getenv('DB_HOST', 'localhost')
        user = os.getenv('DB_USER', 'root')
        password = _get_env('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'invilara')
        charset = 'utf8mb4'

        rutas_mysqldump = [
            r'C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-9.4.0-winx64\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysqldump.exe',
            r'C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysqldump.exe',
            'mysqldump'
        ]
        mysqldump = next((r for r in rutas_mysqldump if os.path.exists(r)), 'mysqldump')

        rutas_mysql = [
            r'C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-9.4.0-winx64\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysql.exe',
            r'C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysql.exe',
            'mysql'
        ]
        mysql = next((r for r in rutas_mysql if os.path.exists(r)), 'mysql')

        return {
            'host': host,
            'user': user,
            'password': password,
            'database': database,
            'charset': charset,
            'mysqldump': mysqldump,
            'mysql': mysql
        }

    def _exportar_dump(self, ruta_salida):
        cfg = self._obtener_config_bd()
        env = os.environ.copy()
        env['MYSQL_PWD'] = cfg['password']
        comando = [
            cfg['mysqldump'],
            f"--host={cfg['host']}",
            f"--user={cfg['user']}",
            f"--default-character-set={cfg['charset']}",
            '--routines',
            '--triggers',
            '--events',
            '--single-transaction',
            '--add-drop-table',
            '--skip-lock-tables',
            cfg['database']
        ]
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            resultado = subprocess.run(comando, stdout=archivo, stderr=subprocess.PIPE, text=True, env=env)

        if resultado.returncode != 0:
            if not (os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 0):
                error = resultado.stderr or 'Error desconocido mysqldump.'
                raise RuntimeError(error)
        return os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 0

    def _importar_sql(self, ruta_archivo):
        cfg = self._obtener_config_bd()
        env = os.environ.copy()
        env['MYSQL_PWD'] = cfg['password']
        comando = [
            cfg['mysql'],
            f"--host={cfg['host']}",
            f"--user={cfg['user']}",
            f"--default-character-set={cfg['charset']}",
            '--binary-mode',
            '--auto-rehash',
            cfg['database']
        ]
        with open(ruta_archivo, 'r', encoding='utf-8') as entrada:
            resultado = subprocess.run(comando, stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)
        if resultado.returncode != 0:
            raise RuntimeError(resultado.stderr or 'Error al ejecutar importación mysql.')
        return True

    def crear_respaldo(self, descripcion='', id_usuario=None):
        if not os.path.exists(self.CARPETA_RESPALDOS):
            os.makedirs(self.CARPETA_RESPALDOS, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"respaldo_{timestamp}.sql"
        ruta_salida = os.path.join(self.CARPETA_RESPALDOS, nombre_archivo)

        try:
            exito = self._exportar_dump(ruta_salida)
            if not exito:
                raise RuntimeError('No se pudo generar el archivo SQL de respaldo.')
        except FileNotFoundError:
            raise RuntimeError('mysqldump no está disponible en el sistema.')
        except Exception as e:
            raise RuntimeError(f"Error al generar respaldo: {e}")

        tamano = os.path.getsize(ruta_salida)
        self._asegurar_tabla_respaldo()
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255]

        conn = connectionBD_invilara()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos para registrar el respaldo.')
        cur = conn.cursor()
        try:
            cur.execute("SELECT COALESCE(MAX(id_respaldo), 0) + 1 AS siguiente_id FROM respaldo_bd")
            fila = cur.fetchone()
            siguiente_id = fila[0] if fila else 1

            cur.execute(
                "INSERT INTO respaldo_bd (id_respaldo, nombre_archivo, tamano, descripcion) VALUES (%s, %s, %s, %s)",
                (siguiente_id, nombre_archivo, tamano, descripcion)
            )
            conn.commit()
            id_respaldo = siguiente_id
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Error al registrar respaldo: {e}")
        finally:
            cur.close()
            conn.close()

        try:
            self._registrar_en_bd_seguridad(id_respaldo, tamano, id_usuario)
        except Exception as e:
            logger.error("[Respaldo] Error al registrar en BD seguridad:\n%s", traceback.format_exc())
            print(f"[Respaldo] Error al registrar en BD seguridad: {e}")

        return {
            'id_respaldo': id_respaldo,
            'nombre_archivo': nombre_archivo,
            'fecha_respaldo': datetime.now(),
            'tamano': tamano,
            'descripcion': descripcion,
            'estado': 1
        }

    def listar_respaldos(self):
        self._asegurar_tabla_respaldo()
        conn = connectionBD_invilara()
        if not conn:
            return []
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM respaldo_bd WHERE estado=1 ORDER BY fecha_respaldo DESC")
            respaldos = cur.fetchall() or []
            for r in respaldos:
                r['tamano_formateado'] = self._formatear_tamano(r.get('tamano', 0) or 0)
            return respaldos
        except Exception as e:
            print(f"[Respaldo] Error al listar respaldos: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def obtener_por_id(self, id_respaldo):
        self._asegurar_tabla_respaldo()
        conn = connectionBD_invilara()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM respaldo_bd WHERE id_respaldo=%s AND estado=1", (id_respaldo,))
            return cur.fetchone()
        except Exception:
            return None
        finally:
            cur.close()
            conn.close()

    def eliminar_respaldo(self, id_respaldo):
        self._asegurar_tabla_respaldo()
        respaldo = self.obtener_por_id(id_respaldo)
        if not respaldo:
            return False
        ruta = os.path.join(self.CARPETA_RESPALDOS, respaldo['nombre_archivo'])
        try:
            if os.path.exists(ruta):
                os.remove(ruta)
        except Exception:
            pass
        conn = connectionBD_invilara()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute("UPDATE respaldo_bd SET estado=0 WHERE id_respaldo=%s AND estado=1", (id_respaldo,))
            conn.commit()
            afectados = cur.rowcount
        except Exception:
            return False
        finally:
            cur.close()
            conn.close()

        # Borrado lógico en la BD de seguridad (estado=0 = eliminado).
        try:
            self._marcar_borrado_seguridad(id_respaldo)
        except Exception as e:
            print(f"[Respaldo] No se pudo marcar borrado lógico en seguridad: {e}")

        return afectados > 0

    def _marcar_borrado_seguridad(self, id_respaldo):
        """Borrado lógico del registro en administracion_respaldos (estado=0)."""
        conn = connectionBD_invilara_seguridad()
        if not conn:
            return
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE `administracion_respaldos` SET `estado`=0 WHERE `id_respaldo`=%s AND `estado`=1",
                (id_respaldo,)
            )
            conn.commit()
        finally:
            cur.close()
            conn.close()

    def importar_respaldo(self, ruta_archivo, descripcion='', id_usuario=None):
        try:
            self._importar_sql(ruta_archivo)
        except Exception as e:
            raise RuntimeError(f"Error al importar respaldo: {e}")

        tamano = os.path.getsize(ruta_archivo)
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255] or 'Respaldo importado'
        nombre_archivo = os.path.basename(ruta_archivo)
        self._asegurar_tabla_respaldo()

        conn = connectionBD_invilara()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos para registrar la importación.')
        cur = conn.cursor()
        try:
            cur.execute("SELECT COALESCE(MAX(id_respaldo), 0) + 1 AS siguiente_id FROM respaldo_bd")
            fila = cur.fetchone()
            siguiente_id = fila[0] if fila else 1

            cur.execute(
                "INSERT INTO respaldo_bd (id_respaldo, nombre_archivo, tamano, descripcion) VALUES (%s, %s, %s, %s)",
                (siguiente_id, nombre_archivo, tamano, descripcion)
            )
            conn.commit()
            id_respaldo = siguiente_id
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Error al registrar importación: {e}")
        finally:
            cur.close()
            conn.close()

        advertencia = None
        db_seguridad = None
        try:
            db_seguridad = self._registrar_en_bd_seguridad(id_respaldo, tamano, id_usuario)
        except Exception as e:
            advertencia = f"No se pudo registrar el respaldo en la base de datos de seguridad: {e}"
            logger.error("[Respaldo] Error al registrar importación en BD seguridad:\n%s", traceback.format_exc())
            print(f"[Respaldo] Error al registrar importación en BD seguridad: {e}")

        return {'id_respaldo': id_respaldo, 'advertencia': advertencia, 'db_seguridad': db_seguridad}
