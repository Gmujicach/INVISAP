"""
RespaldoModel — Modelo SOLID para respaldo y restauración de base de datos MySQL.
Genera dumps con mysqldump, importa archivos .sql y registra metadatos en respaldo_bd.
"""
import os
import re
import subprocess
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara

class RespaldoModel:
    CARPETA_RESPALDOS = os.path.join('static', 'respaldos_bd')

    def __init__(self):
        if not os.path.exists(self.CARPETA_RESPALDOS):
            os.makedirs(self.CARPETA_RESPALDOS, exist_ok=True)

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
        password = os.getenv('DB_PASSWORD', '')
        database = os.getenv('DB_NAME', 'invilara')
        charset = 'utf8mb4'

        rutas_mysqldump = [
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysqldump.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysqldump.exe',
            'mysqldump'
        ]
        mysqldump = next((r for r in rutas_mysqldump if os.path.exists(r)), 'mysqldump')

        rutas_mysql = [
            r'C:\laragon\bin\mysql\mysql-8.0.33\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql-8.0.31\bin\mysql.exe',
            r'C:\laragon\bin\mysql\mysql\bin\mysql.exe',
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
            f"--password={cfg['password']}",
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
            f"--password={cfg['password']}",
            f"--default-character-set={cfg['charset']}",
            '--binary-mode',
            '--auto-rehash',
            cfg['database']
        ]
        with open(ruta_archivo, 'r', encoding='utf-8') as entrada:
            resultado = subprocess.run(comando, stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if resultado.returncode != 0:
            raise RuntimeError(resultado.stderr or 'Error al ejecutar importación mysql.')
        return True

    def crear_respaldo(self, descripcion=''):
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
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255]

        conn = connectionBD_invilara()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos para registrar el respaldo.')
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO respaldo_bd (nombre_archivo, tamano, descripcion) VALUES (%s, %s, %s)",
                (nombre_archivo, tamano, descripcion)
            )
            conn.commit()
            id_respaldo = cur.lastrowid
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Error al registrar respaldo: {e}")
        finally:
            cur.close()
            conn.close()

        return {
            'id_respaldo': id_respaldo,
            'nombre_archivo': nombre_archivo,
            'fecha_respaldo': datetime.now(),
            'tamano': tamano,
            'descripcion': descripcion,
            'estado': 1
        }

    def listar_respaldos(self):
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
        except Exception:
            return []
        finally:
            cur.close()
            conn.close()

    def obtener_por_id(self, id_respaldo):
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
            return cur.rowcount > 0
        except Exception:
            return False
        finally:
            cur.close()
            conn.close()

    def importar_respaldo(self, ruta_archivo, descripcion=''):
        try:
            self._importar_sql(ruta_archivo)
        except Exception as e:
            raise RuntimeError(f"Error al importar respaldo: {e}")

        tamano = os.path.getsize(ruta_archivo)
        descripcion = re.sub(r'[<\'";\\]', '', descripcion).strip()[:255] or 'Respaldo importado'
        nombre_archivo = os.path.basename(ruta_archivo)

        conn = connectionBD_invilara()
        if not conn:
            raise RuntimeError('No se pudo conectar a la base de datos para registrar la importación.')
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO respaldo_bd (nombre_archivo, tamano, descripcion) VALUES (%s, %s, %s)",
                (nombre_archivo, tamano, descripcion)
            )
            conn.commit()
            id_respaldo = cur.lastrowid
        except Exception as e:
            conn.rollback()
            raise RuntimeError(f"Error al registrar importación: {e}")
        finally:
            cur.close()
            conn.close()

        return id_respaldo
