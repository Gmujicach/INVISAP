"""
RespaldoModel — Modelo SOLID para respaldo y restauración de base de datos MySQL.
Genera dumps con mysqldump, importa archivos .sql y registra metadatos en
`administracion_respaldos` de la base de datos de seguridad (invilara_seguridad).
"""
import os
import re
import subprocess
import logging
import traceback
from datetime import datetime
from decimal import Decimal
from conexion.conexionBD import connectionBD_invilara_seguridad, get_db_config
from models.base_model import BaseModel

logger = logging.getLogger(__name__)


class RespaldoModel(BaseModel):
    CARPETA_RESPALDOS = os.path.join('static', 'respaldos_bd')

    def __init__(self):
        if not os.path.exists(self.CARPETA_RESPALDOS):
            os.makedirs(self.CARPETA_RESPALDOS, exist_ok=True)

    def _asegurar_tabla_seguridad(self):
        """Crea (o migra) la tabla administracion_respaldos en invilara_seguridad.

        La tabla real de producción vive en la BD de seguridad; aquí nos aseguramos
        de que exista y de que tenga las columnas que usa la interfaz
        (nombre_archivo, descripcion) y un tamaño adecuado para tamaño_respaldo.
        """
        conn = connectionBD_invilara_seguridad()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS `administracion_respaldos` (
                    `id_respaldo` int(11) NOT NULL,
                    `fecha_respaldo` datetime NOT NULL,
                    `tamaño_respaldo` decimal(10,2) NOT NULL,
                    `usuarios_id_usuarios` int(11) NOT NULL,
                    `estado` tinyint(4) NOT NULL,
                    PRIMARY KEY (`id_respaldo`, `usuarios_id_usuarios`),
                    KEY `fk_administracion_respaldos_usuarios_idx` (`usuarios_id_usuarios`)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci
                COMMENT='Tabla de administracion de respaldos.'
            """)

            # Migración: añadir columnas que la interfaz necesita y que la
            # tabla original de seguridad no tenía.
            cur.execute("SHOW COLUMNS FROM `administracion_respaldos` LIKE 'nombre_archivo'")
            if cur.fetchone() is None:
                cur.execute(
                    "ALTER TABLE `administracion_respaldos` "
                    "ADD COLUMN `nombre_archivo` varchar(255) NOT NULL DEFAULT ''"
                )

            cur.execute("SHOW COLUMNS FROM `administracion_respaldos` LIKE 'descripcion'")
            if cur.fetchone() is None:
                cur.execute(
                    "ALTER TABLE `administracion_respaldos` "
                    "ADD COLUMN `descripcion` varchar(255) DEFAULT ''"
                )

            # Ensanchar tamaño_respaldo si todavía es muy pequeño (decimal(4,2)).
            cur.execute("SHOW COLUMNS FROM `administracion_respaldos` WHERE Field='tamaño_respaldo'")
            col = cur.fetchone()
            if col and 'decimal(4' in str(col[1]).lower():
                cur.execute(
                    "ALTER TABLE `administracion_respaldos` "
                    "MODIFY `tamaño_respaldo` decimal(10,2) NOT NULL"
                )

            conn.commit()
            return True
        except Exception as e:
            print(f"[DB] No se pudo asegurar tabla administracion_respaldos (seguridad): {e}")
            return False
        finally:
            cur.close()
            conn.close()

    def _siguiente_id(self):
        """Calcula el siguiente id_respaldo disponible en la BD de seguridad."""
        conn = connectionBD_invilara_seguridad()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos de seguridad.')
        cur = conn.cursor()
        try:
            cur.execute(
                "SELECT COALESCE(MAX(`id_respaldo`), 0) + 1 AS siguiente_id "
                "FROM `administracion_respaldos`"
            )
            fila = cur.fetchone()
            return fila[0] if fila else 1
        finally:
            cur.close()
            conn.close()

    def _guardar_en_seguridad(self, id_respaldo, nombre_archivo, tamano_bytes, descripcion, id_usuario):
        """Inserta/actualiza el registro del respaldo en invilara_seguridad."""
        tamano_mb = Decimal(str(round(tamano_bytes / (1024 * 1024), 2)))
        tamano_mb = min(tamano_mb, Decimal('99999999.99'))
        id_usuario = id_usuario or 1

        conn = connectionBD_invilara_seguridad()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos de seguridad.')
        db_actual = conn.database
        cur = conn.cursor()
        try:
            self._asegurar_tabla_seguridad()
            columnas = (
                "`id_respaldo`, `fecha_respaldo`, `tamaño_respaldo`, "
                "`usuarios_id_usuarios`, `estado`, `nombre_archivo`, `descripcion`"
            )
            valores = (id_respaldo, datetime.now(), tamano_mb, id_usuario, 1,
                       nombre_archivo, descripcion)
            cur.execute(
                f"INSERT INTO `administracion_respaldos` ({columnas}) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "`fecha_respaldo` = VALUES(`fecha_respaldo`), "
                "`tamaño_respaldo` = VALUES(`tamaño_respaldo`), "
                "`estado` = VALUES(`estado`), "
                "`nombre_archivo` = VALUES(`nombre_archivo`), "
                "`descripcion` = VALUES(`descripcion`)",
                valores
            )
            conn.commit()
            logger.info("[Respaldo] Registro en seguridad OK (BD=%s, id=%s).", db_actual, id_respaldo)
        finally:
            cur.close()
            conn.close()

        return db_actual

    @staticmethod
    def _limpiar_nombre(nombre):
        return re.sub(r'[^A-Za-z0-9_\-]', '_', nombre.strip())[:100]

    @staticmethod
    def _formatear_tamano(bytes_size):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} GB"

    @staticmethod
    def _obtener_config_bd():
        cfg = get_db_config()
        host = cfg['host']
        user = cfg['user']
        password = cfg['password']
        database = cfg['database']
        charset = cfg['charset']

        rutas_mysqldump = [
            r'C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-9.4.0-winx64\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-9.7.1-winx64\bin\mysqldump.exe',
            r'D:\laragon\bin\mysql\mysql-9.7.1-winx64\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysqldump.exe',
            r'C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysqldump.exe',
            '/usr/bin/mysqldump',
            '/usr/local/mysql/bin/mysqldump',
            '/usr/local/bin/mysqldump',
            '/opt/mysql/bin/mysqldump',
            'mysqldump'
        ]
        mysqldump = next((r for r in rutas_mysqldump if os.path.exists(r)), 'mysqldump')

        rutas_mysql = [
            r'C:\laragon\bin\mysql\mysql-8.4.3-winx64\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-9.4.0-winx64\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-9.7.1-winx64\bin\mysql.exe',
            r'D:\laragon\bin\mysql\mysql-9.7.1-winx64\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysql.exe',
            r'C:\Program Files\MySQL\MySQL Workbench 8.0 CE\mysql.exe',
            '/usr/bin/mysql',
            '/usr/local/mysql/bin/mysql',
            '/usr/local/bin/mysql',
            '/opt/mysql/bin/mysql',
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
        if cfg['password']:
            comando.insert(3, f"--password={cfg['password']}")
        with open(ruta_salida, 'w', encoding='utf-8') as archivo:
            resultado = subprocess.run(comando, stdout=archivo, stderr=subprocess.PIPE, text=True)

        if resultado.returncode != 0:
            if not (os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 0):
                error = resultado.stderr or 'Error desconocido mysqldump.'
                raise RuntimeError(error)
        return os.path.exists(ruta_salida) and os.path.getsize(ruta_salida) > 0

    def _importar_sql(self, ruta_archivo):
        cfg = self._obtener_config_bd()
        comando = [
            cfg['mysql'],
            f"--host={cfg['host']}",
            f"--user={cfg['user']}",
            f"--default-character-set={cfg['charset']}",
            '--binary-mode',
            '--auto-rehash',
            cfg['database']
        ]
        if cfg['password']:
            comando.insert(3, f"--password={cfg['password']}")
        with open(ruta_archivo, 'r', encoding='utf-8') as entrada:
            resultado = subprocess.run(comando, stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if resultado.returncode != 0:
            raise RuntimeError(resultado.stderr or 'Error al ejecutar importación mysql.')
        return True

    def crear_respaldo(self, descripcion='', id_usuario=None, nombre_archivo=''):
        if not os.path.exists(self.CARPETA_RESPALDOS):
            os.makedirs(self.CARPETA_RESPALDOS, exist_ok=True)

        if nombre_archivo:
            nombre_archivo = self._limpiar_nombre(nombre_archivo)
            if not nombre_archivo.lower().endswith('.sql'):
                nombre_archivo += '.sql'
        else:
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
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255]

        self._asegurar_tabla_seguridad()
        try:
            siguiente_id = self._siguiente_id()
        except Exception as e:
            raise RuntimeError(f"Error al obtener el siguiente ID de respaldo: {e}")

        try:
            self._guardar_en_seguridad(siguiente_id, nombre_archivo, tamano, descripcion, id_usuario)
        except Exception as e:
            logger.error("[Respaldo] Error al registrar en BD seguridad:\n%s", traceback.format_exc())
            raise RuntimeError(f"Error al registrar respaldo en la base de datos de seguridad: {e}")

        return {
            'id_respaldo': siguiente_id,
            'nombre_archivo': nombre_archivo,
            'fecha_respaldo': datetime.now(),
            'tamano': tamano,
            'descripcion': descripcion,
            'estado': 1
        }

    @staticmethod
    def _normalizar_fila(r):
        """Convierte una fila de la BD de seguridad a lo que espera la interfaz."""
        tamano_mb = r.get('tamaño_respaldo') or 0
        try:
            tamano_bytes = int(round(float(tamano_mb) * 1024 * 1024))
        except (TypeError, ValueError):
            tamano_bytes = 0
        r['tamano'] = tamano_bytes
        r['tamano_formateado'] = RespaldoModel._formatear_tamano(tamano_bytes)
        r['nombre_archivo'] = r.get('nombre_archivo') or ''
        r['descripcion'] = r.get('descripcion') or ''
        return r

    def listar_respaldos(self):
        self._asegurar_tabla_seguridad()
        conn = connectionBD_invilara_seguridad()
        if not conn:
            return []
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT * FROM `administracion_respaldos` "
                "WHERE `estado`=1 ORDER BY `fecha_respaldo` DESC"
            )
            respaldos = cur.fetchall() or []
            return [self._normalizar_fila(dict(r)) for r in respaldos]
        except Exception as e:
            print(f"[Respaldo] Error al listar respaldos: {e}")
            return []
        finally:
            cur.close()
            conn.close()

    def obtener_por_id(self, id_respaldo):
        self._asegurar_tabla_seguridad()
        conn = connectionBD_invilara_seguridad()
        if not conn:
            return None
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute(
                "SELECT * FROM `administracion_respaldos` "
                "WHERE `id_respaldo`=%s AND `estado`=1",
                (id_respaldo,)
            )
            fila = cur.fetchone()
            return self._normalizar_fila(dict(fila)) if fila else None
        except Exception:
            return None
        finally:
            cur.close()
            conn.close()

    def eliminar_respaldo(self, id_respaldo):
        self._asegurar_tabla_seguridad()
        respaldo = self.obtener_por_id(id_respaldo)
        if not respaldo:
            return False
        ruta = os.path.join(self.CARPETA_RESPALDOS, respaldo['nombre_archivo'])
        try:
            if respaldo['nombre_archivo'] and os.path.exists(ruta):
                os.remove(ruta)
        except Exception:
            pass

        conn = connectionBD_invilara_seguridad()
        if not conn:
            return False
        cur = conn.cursor()
        try:
            cur.execute(
                "UPDATE `administracion_respaldos` SET `estado`=0 "
                "WHERE `id_respaldo`=%s AND `estado`=1",
                (id_respaldo,)
            )
            conn.commit()
            afectados = cur.rowcount
        except Exception:
            return False
        finally:
            cur.close()
            conn.close()

        return afectados > 0

    def importar_respaldo(self, ruta_archivo, descripcion='', id_usuario=None):
        try:
            self._importar_sql(ruta_archivo)
        except Exception as e:
            raise RuntimeError(f"Error al importar respaldo: {e}")

        tamano = os.path.getsize(ruta_archivo)
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255] or 'Respaldo importado'
        nombre_archivo = os.path.basename(ruta_archivo)
        self._asegurar_tabla_seguridad()

        try:
            siguiente_id = self._siguiente_id()
        except Exception as e:
            raise RuntimeError(f"Error al obtener el siguiente ID de respaldo: {e}")

        advertencia = None
        db_seguridad = None
        try:
            db_seguridad = self._guardar_en_seguridad(
                siguiente_id, nombre_archivo, tamano, descripcion, id_usuario
            )
        except Exception as e:
            advertencia = f"No se pudo registrar el respaldo en la base de datos de seguridad: {e}"
            logger.error("[Respaldo] Error al registrar importación en BD seguridad:\n%s", traceback.format_exc())
            print(f"[Respaldo] Error al registrar importación en BD seguridad: {e}")

        return {'id_respaldo': siguiente_id, 'advertencia': advertencia, 'db_seguridad': db_seguridad}
