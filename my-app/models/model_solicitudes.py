"""
SolicitudModel — Modelo SOLID/DRY para gestión de solicitudes.

Principios aplicados:
- SRP: Una sola responsabilidad por método.
- OCP: Abierto a extensión, cerrado a modificación (usando _parse helpers).
- DRY: Lógica de conexión centralizada en _con(), validaciones en _validators.
- Inyección SQL: Todas las consultas son parametrizadas.
- Métodos privados (_): contienen SQL directo.
- Métodos públicos: fachada con validación regex antes de delegar.
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara


class SolicitudModel:
    """Repositorio de solicitudes y solicitantes."""

    # -----------------------------------------------------------------
    # Constantes de validación (regex compilados una sola vez - DRY)
    # -----------------------------------------------------------------
    _RE_CEDULA = re.compile(r'^\d{7,10}$')
    _RE_TELEFONO = re.compile(r'^(0414|0424|0412|0416|0426|0251)-?\d{7}$')
    _RE_CORREO = re.compile(r'^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$')
    _RE_RIF_NUM = re.compile(r'^\d{8,9}$')
    _RE_TEXTO = re.compile(r'^[\w\s\.,\-áéíóúÁÉÍÓÚñÑ]{2,100}$', re.UNICODE)
    _RE_PROBLEMATICA = re.compile(r'^[\w\s\.,\!\?\-áéíóúÁÉÍÓÚñÑ]{15,500}$', re.UNICODE)

    TIPOS_SOLICITANTE_VALIDOS = {'Comunidad', 'Institucion', 'Particular'}
    ESTATUS_VALIDOS = {'Pendiente', 'En Proceso', 'Completada', 'Procesada', 'PENDIENTE'}

    # -----------------------------------------------------------------
    # Utilidades internas (DRY)
    # -----------------------------------------------------------------
    @staticmethod
    def _con():
        """Abre y retorna una conexión nueva a la BD."""
        return connectionBD_invilara()

    @staticmethod
    def _cerrar(conn, cursor):
        """Cierra cursor y conexión de forma segura."""
        try:
            if cursor:
                cursor.close()
        except Exception:
            pass
        try:
            if conn:
                conn.close()
        except Exception:
            pass

    @staticmethod
    def _limpiar(valor: str, max_len: int = 255) -> str:
        """Elimina caracteres peligrosos y limita longitud (DRY)."""
        if not isinstance(valor, str):
            valor = str(valor or '')
        return re.sub(r'[<>\'";\\]', '', valor).strip()[:max_len]

    # -----------------------------------------------------------------
    # Validadores de entrada (SRP)
    # -----------------------------------------------------------------
    def _validar_cedula(self, cedula: str) -> bool:
        return bool(self._RE_CEDULA.match(cedula.strip()))

    def _validar_telefono(self, telefono: str) -> bool:
        # Quitar guiones para validar
        tel_limpio = telefono.replace('-', '').strip()
        return bool(re.match(r'^(0414|0424|0412|0416|0426|0251)\d{7}$', tel_limpio))

    def _validar_correo(self, correo: str) -> bool:
        return bool(self._RE_CORREO.match(correo.strip()))

    def _validar_rif_numero(self, rif_num: str) -> bool:
        return bool(self._RE_RIF_NUM.match(rif_num.strip()))

    def _validar_texto(self, texto: str) -> bool:
        return bool(self._RE_TEXTO.match(texto.strip())) if texto.strip() else False

    def _validar_problematica(self, texto: str) -> bool:
        return len(texto.strip()) >= 15

    # -----------------------------------------------------------------
    # Parsers de datos de formulario (SRP)
    # -----------------------------------------------------------------
    def _parse_solicitante_data(self, datos: dict) -> dict:
        """Extrae y normaliza datos del solicitante según su tipo."""
        tipo = datos.get('tipo_solicitud', '').strip()

        if tipo == 'Comunidad':
            letra = self._limpiar(datos.get('com_rif_letra', 'J'), 1)
            num = self._limpiar(datos.get('com_rif_numero', ''), 9)
            return {
                'nombre_solicitante': self._limpiar(datos.get('com_nombre', ''), 80),
                'rif': f"{letra}-{num}",
                'parroquia': self._limpiar(datos.get('com_parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('com_municipio', ''), 45),
                'ambito': self._limpiar(datos.get('com_ambito', ''), 50),
                'cedula': self._limpiar(datos.get('com_cedula', ''), 10),
                'correo': self._limpiar(datos.get('com_correo', ''), 50),
                'tipo_solicitante': tipo,
            }
        elif tipo == 'Institucion':
            letra = self._limpiar(datos.get('inst_rif_letra', 'J'), 1)
            num = self._limpiar(datos.get('inst_rif_numero', ''), 9)
            return {
                'nombre_solicitante': self._limpiar(datos.get('inst_nombre', ''), 80),
                'rif': f"{letra}-{num}",
                'parroquia': 'No aplica',
                'municipio': 'No aplica',
                'ambito': self._limpiar(datos.get('inst_direccion', ''), 100),
                'cedula': self._limpiar(datos.get('inst_director_cedula', ''), 10),
                'correo': self._limpiar(datos.get('inst_correo', ''), 50),
                'tipo_solicitante': tipo,
            }
        elif tipo == 'Particular':
            cedula = self._limpiar(datos.get('part_cedula', ''), 10)
            return {
                'nombre_solicitante': self._limpiar(datos.get('part_nombre', ''), 80),
                'rif': f"V-{cedula}",
                'parroquia': self._limpiar(datos.get('part_parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('part_municipio', ''), 45),
                'ambito': self._limpiar(datos.get('part_direccion', ''), 100),
                'cedula': cedula,
                'correo': self._limpiar(datos.get('part_correo', ''), 50),
                'tipo_solicitante': tipo,
            }
        else:
            return {
                'nombre_solicitante': self._limpiar(datos.get('nombre_solicitante', ''), 80),
                'rif': self._limpiar(datos.get('rif', ''), 15),
                'parroquia': self._limpiar(datos.get('parroquia', ''), 45),
                'municipio': self._limpiar(datos.get('municipio', ''), 45),
                'ambito': self._limpiar(datos.get('ambito', ''), 100),
                'cedula': self._limpiar(datos.get('cedula', ''), 10),
                'correo': self._limpiar(datos.get('correo', ''), 50),
                'tipo_solicitante': tipo,
            }

    def _parse_solicitud_data(self, datos: dict) -> dict:
        """Extrae y normaliza datos de la solicitud."""
        fecha_raw = datos.get('fecha', '').strip()
        fecha = fecha_raw.replace('T', ' ') if fecha_raw else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        telefono = (
            datos.get('com_telefono', '') or
            datos.get('inst_telefono', '') or
            datos.get('part_telefono', '') or ''
        ).strip()

        direccion = (
            datos.get('part_direccion', '') or
            datos.get('inst_direccion', '') or
            datos.get('com_ambito', '') or ''
        ).strip()

        estatus = self._limpiar(
            datos.get('estatus_solicitud', datos.get('estatus', 'Pendiente')), 20
        ) or 'Pendiente'

        # Normalizar tipo de problemática
        tipo_problematica = self._limpiar(datos.get('tipo_problematica', ''), 50)
        problematica_libre = self._limpiar(datos.get('problematica', ''), 500)

        # Construir descripción de problemática combinando tipo + descripción libre
        problematica_final = problematica_libre
        if tipo_problematica and problematica_libre:
            problematica_final = f"[{tipo_problematica}] {problematica_libre}"
        elif tipo_problematica:
            problematica_final = tipo_problematica

        return {
            'fecha': fecha,
            'telefono_solicitante': self._limpiar(telefono, 12),
            'direccion_solicitante': self._limpiar(direccion, 200),
            'tipo_solicitud': self._limpiar(datos.get('tipo_solicitud', ''), 45),
            'estatus_solicitud': estatus,
            'problematica': problematica_final,
            'tipo_solicitante': self._limpiar(datos.get('tipo_solicitud', ''), 45),
        }

    # -----------------------------------------------------------------
    # Métodos privados — SQL (SRP)
    # -----------------------------------------------------------------
    def _sql_buscar_solicitante(self, cursor, rif: str, cedula: str):
        """Busca un solicitante existente por RIF o cédula."""
        sql = "SELECT id_solicitante FROM solicitante WHERE rif = %s OR cedula = %s LIMIT 1"
        cursor.execute(sql, (rif, cedula))
        row = cursor.fetchone()
        if row:
            return row['id_solicitante'] if isinstance(row, dict) else row[0]
        return None

    def _sql_insertar_solicitante(self, cursor, datos: dict) -> int:
        """Inserta un nuevo solicitante y retorna su ID."""
        sql = """
            INSERT INTO solicitante
                (nombre_solicitante, parroquia, municipio, ambito, rif, cedula, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            datos['nombre_solicitante'], datos['parroquia'], datos['municipio'],
            datos['ambito'], datos['rif'], datos['cedula'], datos['correo']
        ))
        return cursor.lastrowid

    def _sql_insertar_solicitud(self, cursor, datos: dict, solicitante_id: int) -> int:
        """Inserta una nueva solicitud y retorna su ID."""
        sql = """
            INSERT INTO solicitudes
                (fecha, telefono_solicitante, direccion_solicitante,
                 tipo_solicitud, estatus_solicitud, problematica,
                 tipo_solicitante, solicitante_id_comunidad)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            datos['fecha'], datos['telefono_solicitante'], datos['direccion_solicitante'],
            datos['tipo_solicitud'], datos['estatus_solicitud'], datos['problematica'],
            datos['tipo_solicitante'], solicitante_id
        ))
        return cursor.lastrowid

    def _sql_todas_solicitudes(self) -> list:
        """Retorna todas las solicitudes con datos del solicitante."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return []
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT gs.id_solicitud, gs.fecha, gs.tipo_solicitud, gs.estatus_solicitud,
                       gs.problematica, gs.telefono_solicitante, gs.direccion_solicitante,
                       gs.tipo_solicitante,
                       s.nombre_solicitante, s.rif, s.cedula, s.correo,
                       s.municipio, s.parroquia, s.ambito
                FROM solicitudes gs
                LEFT JOIN solicitante s ON gs.solicitante_id_comunidad = s.id_solicitante
                ORDER BY gs.fecha DESC
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except Exception as e:
            print(f"[SolicitudModel._sql_todas_solicitudes] Error: {e}")
            return []
        finally:
            self._cerrar(conn, cursor)

    def _sql_solicitud_por_id(self, id_solicitud: int):
        """Retorna una solicitud específica con todos sus datos."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return None
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT gs.*, s.nombre_solicitante, s.rif, s.cedula, s.correo,
                       s.municipio, s.parroquia, s.ambito
                FROM solicitudes gs
                LEFT JOIN solicitante s ON gs.solicitante_id_comunidad = s.id_solicitante
                WHERE gs.id_solicitud = %s
            """
            cursor.execute(sql, (id_solicitud,))
            return cursor.fetchone()
        except Exception as e:
            print(f"[SolicitudModel._sql_solicitud_por_id] Error: {e}")
            return None
        finally:
            self._cerrar(conn, cursor)

    def _sql_actualizar_solicitud(self, id_solicitud: int, estatus: str,
                                   problematica: str) -> bool:
        """Actualiza el estatus y problemática de una solicitud."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = """
                UPDATE solicitudes
                SET estatus_solicitud = %s, problematica = %s
                WHERE id_solicitud = %s
            """
            cursor.execute(sql, (estatus, problematica, id_solicitud))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[SolicitudModel._sql_actualizar_solicitud] Error: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            self._cerrar(conn, cursor)

    def _sql_eliminar_solicitud(self, id_solicitud: int) -> bool:
        """Elimina una solicitud por su ID."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor()
            sql = "DELETE FROM solicitudes WHERE id_solicitud = %s"
            cursor.execute(sql, (id_solicitud,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"[SolicitudModel._sql_eliminar_solicitud] Error: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            self._cerrar(conn, cursor)

    # -----------------------------------------------------------------
    # Métodos públicos — Fachada con validación (SRP + DRY)
    # -----------------------------------------------------------------
    def obtener_todas_las_solicitudes(self) -> list:
        """Retorna todas las solicitudes registradas."""
        return self._sql_todas_solicitudes()

    def obtener_solicitud_por_id(self, id_solicitud) -> dict | None:
        """Retorna una solicitud por su ID."""
        try:
            id_val = int(id_solicitud)
        except (ValueError, TypeError):
            return None
        if id_val <= 0:
            return None
        return self._sql_solicitud_por_id(id_val)

    def crear_nueva_solicitud(self, datos: dict) -> int | bool:
        """
        Valida los datos, crea o recupera el solicitante, e inserta la solicitud.
        Retorna el ID de la nueva solicitud o False si falla.
        """
        tipo = datos.get('tipo_solicitud', '').strip()
        if tipo not in self.TIPOS_SOLICITANTE_VALIDOS:
            print(f"[SolicitudModel] Tipo de solicitante inválido: {tipo}")
            return False

        problematica = datos.get('problematica', '').strip()
        if not self._validar_problematica(problematica):
            print("[SolicitudModel] Problemática demasiado corta o vacía.")
            return False

        solicitante_data = self._parse_solicitante_data(datos)
        solicitud_data = self._parse_solicitud_data(datos)

        if not solicitante_data['nombre_solicitante']:
            print("[SolicitudModel] Nombre del solicitante requerido.")
            return False

        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return False
            cursor = conn.cursor(dictionary=True)

            # Buscar o crear solicitante (DRY — lógica centralizada)
            solicitante_id = self._sql_buscar_solicitante(
                cursor, solicitante_data['rif'], solicitante_data['cedula']
            )
            if not solicitante_id:
                solicitante_id = self._sql_insertar_solicitante(cursor, solicitante_data)

            if not solicitante_id:
                print("[SolicitudModel] No se pudo crear el solicitante.")
                return False

            nueva_id = self._sql_insertar_solicitud(cursor, solicitud_data, solicitante_id)
            conn.commit()
            return nueva_id

        except Exception as e:
            print(f"[SolicitudModel.crear_nueva_solicitud] Error: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            return False
        finally:
            self._cerrar(conn, cursor)

    def actualizar_solicitud(self, id_solicitud, datos: dict) -> bool:
        """Actualiza estatus y problemática de una solicitud con validación."""
        try:
            id_val = int(id_solicitud)
        except (ValueError, TypeError):
            return False

        estatus = self._limpiar(
            datos.get('estatus_solicitud', datos.get('estatus', '')), 20
        )
        if estatus not in self.ESTATUS_VALIDOS:
            estatus = 'Pendiente'

        problematica = self._limpiar(datos.get('problematica', ''), 500)
        if not self._validar_problematica(problematica):
            return False

        return self._sql_actualizar_solicitud(id_val, estatus, problematica)

    def eliminar_solicitud(self, id_solicitud) -> bool:
        """Elimina una solicitud por su ID con validación."""
        try:
            id_val = int(id_solicitud)
        except (ValueError, TypeError):
            return False
        if id_val <= 0:
            return False
        return self._sql_eliminar_solicitud(id_val)

    def obtener_estadisticas(self) -> dict:
        """Retorna conteo de solicitudes por estatus (para dashboard)."""
        conn = cursor = None
        try:
            conn = self._con()
            if conn is None:
                return {}
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT estatus_solicitud, COUNT(*) as total FROM solicitudes GROUP BY estatus_solicitud"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return {r['estatus_solicitud']: r['total'] for r in rows}
        except Exception as e:
            print(f"[SolicitudModel.obtener_estadisticas] Error: {e}")
            return {}
        finally:
            self._cerrar(conn, cursor)