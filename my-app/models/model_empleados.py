"""
EmpleadoModel — Modelo SOLID/POO para gestión de empleados.
Implementa encapsulamiento, validaciones Regex, borrado lógico y relación con Persona.
"""
import re
from datetime import datetime
from conexion.conexionBD import connectionBD_invilara
from models.base_model import BaseModel


class EmpleadoModel(BaseModel):
    """Repositorio de empleados con validación y encapsulamiento."""

    # Expresiones regulares para validación (Principio de Responsabilidad Única)
    _RE_NOMBRE = re.compile(r'^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{3,45}$')
    _RE_GERENCIA = re.compile(r'^[A-ZñÑa-záéíóúÁÉÍÓÚ\s]{5,45}$')
    _RE_FECHA = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    _RE_CEDULA = re.compile(r'^\d{7,8}$')
    _RE_TELEFONO = re.compile(r'^\d{10,11}$')
    _RE_CORREO = re.compile(r'^[\w._%+\-]+@[\w.\-]+\.[a-zA-Z]{2,}$')
    
    # Cargos válidos (catálogo)
    CARGOS_VALIDOS = {
        'Gerente', 'Inspector', 'Asistente', 'Proyectista', 
        'Recepcionista', 'Ingeniero', 'Coordinador', 'Operador'
    }

    def __init__(self):
        # --- Atributos PRIVADOS para encapsulamiento (POO) ---
        self.__id_empleados = None
        self.__nombre_empleado = None
        self.__cargo = None
        self.__fecha_ingreso = None
        self.__gerencia_asignada = None
        self.__estado = 1  # 1 = Activo, 0 = Inactivo
        
        # Atributos de la tabla Persona (relación FK)
        self.__persona_id_persona = None
        self.__cedula_persona = None
        self.__direccion = None
        self.__parroquia = None
        self.__municipio = None
        self.__telefono = None
        self.__correo = None

    # ========== GETTERS Y SETTERS (Encapsulamiento) ==========
    
    def get_id_empleado(self):
        return self.__id_empleados
    
    def set_id_empleado(self, valor):
        if not isinstance(valor, int) or valor <= 0:
            raise ValueError("ID de empleado debe ser un entero positivo.")
        self.__id_empleados = valor
    
    def get_nombre_empleado(self):
        return self.__nombre_empleado
    
    def set_nombre_empleado(self, valor):
        """Valida y establece el nombre del empleado."""
        if not self._validar_nombre(valor):
            raise ValueError(
                "Nombre inválido. Solo letras, mínimo 3, máximo 45 caracteres."
            )
        self.__nombre_empleado = self._limpiar_texto(valor, 45)
    
    def get_cargo(self):
        return self.__cargo
    
    def set_cargo(self, valor):
        """Valida y establece el cargo desde el catálogo."""
        valor_limpio = self._limpiar_texto(valor, 45)
        if valor_limpio not in self.CARGOS_VALIDOS:
            raise ValueError(
                f"Cargo '{valor}' no válido. Use: {', '.join(self.CARGOS_VALIDOS)}"
            )
        self.__cargo = valor_limpio
    
    def get_fecha_ingreso(self):
        return self.__fecha_ingreso
    
    def set_fecha_ingreso(self, valor):
        """Valida y establece la fecha de ingreso."""
        if not self._validar_fecha(valor):
            raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD.")
        self.__fecha_ingreso = valor
    
    def get_gerencia_asignada(self):
        return self.__gerencia_asignada
    
    def set_gerencia_asignada(self, valor):
        """Valida y establece la gerencia asignada."""
        if not self._validar_gerencia(valor):
            raise ValueError(
                "Gerencia inválida. Mínimo 5, máximo 45 caracteres."
            )
        self.__gerencia_asignada = self._limpiar_texto(valor, 45)
    
    def get_cedula_persona(self):
        return self.__cedula_persona
    
    def set_cedula_persona(self, valor):
        """Valida y establece la cédula."""
        if not self._validar_cedula(valor):
            raise ValueError("Cédula inválida. Debe tener 7-8 dígitos.")
        self.__cedula_persona = int(''.join(filter(str.isdigit, str(valor))))
    
    def get_estado(self):
        return self.__estado
    
    def set_estado(self, valor):
        if valor not in (0, 1):
            raise ValueError("Estado debe ser 0 (inactivo) o 1 (activo).")
        self.__estado = valor

    # ========== VALIDACIONES (Método Aparte - Responsabilidad Única) ==========
    
    def _validar_nombre(self, nombre: str) -> bool:
        """Valida el nombre del empleado con Regex."""
        return bool(self._RE_NOMBRE.match(str(nombre)))
    
    def _validar_gerencia(self, gerencia: str) -> bool:
        """Valida la gerencia con Regex."""
        return bool(self._RE_GERENCIA.match(str(gerencia)))
    
    def _validar_fecha(self, fecha: str) -> bool:
        """Valida el formato de fecha con Regex."""
        return bool(self._RE_FECHA.match(str(fecha)))
    
    def _validar_cedula(self, cedula: str) -> bool:
        """Valida la cédula con Regex."""
        return bool(self._RE_CEDULA.match(str(cedula).strip()))
    
    def _validar_telefono(self, telefono: str) -> bool:
        """Valida el teléfono con Regex."""
        return bool(self._RE_TELEFONO.match(str(telefono)))
    
    def _validar_correo(self, correo: str) -> bool:
        """Valida el correo con Regex."""
        return bool(self._RE_CORREO.match(str(correo)))
    
    # ========== MÉTODOS PRIVADOS DE LÓGICA DE NEGOCIO ==========
    
    def __buscar_o_crear_persona(self, cursor):
        """
        Método PRIVADO que busca o crea un registro en la tabla persona.
        Retorna el id_persona.
        """
        # Buscar si ya existe la persona por cédula
        sql_buscar = "SELECT id_persona FROM persona WHERE cedula_persona = %s LIMIT 1"
        cursor.execute(sql_buscar, (self.__cedula_persona,))
        row = cursor.fetchone()
        
        if row:
            # Si existe, retornar el ID
            return row['id_persona'] if isinstance(row, dict) else row[0]
        
        # Si no existe, crear nuevo registro en persona
        cursor.execute("SELECT COALESCE(MAX(id_persona), 0) + 1 AS siguiente_id FROM persona")
        fila = cursor.fetchone()
        siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)

        sql_insertar = """
            INSERT INTO persona (id_persona, cedula_persona, direccion, parroquia, municipio, telefono, correo)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insertar, (
            siguiente_id,
            self.__cedula_persona,
            self.__direccion or 'No especificado',
            self.__parroquia or 'No especificado',
            self.__municipio or 'No especificado',
                self.__telefono or '0000000000',
            self.__correo or 'sin_correo@invilara.gob.ve'
        ))
        
        return cursor.lastrowid
    
    def __guardar_empleado_db(self):
        """
        Método PRIVADO que guarda el empleado en la base de datos.
        Usa consultas parametrizadas (marcadores) para evitar inyecciones.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor(dictionary=True)
            
            # Paso 1: Buscar o crear persona
            persona_id = self.__buscar_o_crear_persona(cur)
            
            if not persona_id:
                return None
            
            # Paso 2: Insertar empleado con FK a persona
            cur.execute("SELECT COALESCE(MAX(id_empleados), 0) + 1 AS siguiente_id FROM empleados")
            fila = cur.fetchone()
            siguiente_id = fila['siguiente_id'] if isinstance(fila, dict) else (fila[0] if fila else 1)

            sql = """
                INSERT INTO empleados 
                (id_empleados, nombre_empleado, cargo, fecha_ingreso, gerencia_asignada, persona_id_persona, estado) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cur.execute(sql, (
                siguiente_id,
                self.__nombre_empleado,
                self.__cargo,
                self.__fecha_ingreso,
                self.__gerencia_asignada,
                persona_id,
                1
            ))
            
            conn.commit()
            return cur.lastrowid
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error al guardar empleado en BD: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __actualizar_empleado_db(self):
        """
        Método PRIVADO que actualiza un empleado existente.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Actualizar solo datos de empleado (no persona por ahora)
            sql = """
                UPDATE empleados 
                SET nombre_empleado = %s, cargo = %s, fecha_ingreso = %s, gerencia_asignada = %s
                WHERE id_empleados = %s AND estado = 1
            """
            cur.execute(sql, (
                self.__nombre_empleado,
                self.__cargo,
                self.__fecha_ingreso,
                self.__gerencia_asignada,
                self.__id_empleados
            ))
            
            conn.commit()
            return cur.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error al actualizar empleado: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __eliminar_logico_db(self):
        """
        Método PRIVADO que realiza el borrado LÓGICO.
        No elimina físicamente, solo cambia el estado a 0.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            # Borrado lógico: cambiar estado a 0
            sql = "UPDATE empleados SET estado = 0 WHERE id_empleados = %s"
            cur.execute(sql, (self.__id_empleados,))
            conn.commit()
            
            return cur.rowcount > 0
            
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error en borrado lógico: {e}")
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_todos_empleados_db(self, limite=None, offset=None):
        """Método PRIVADO que obtiene empleados activos con paginación opcional."""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            
            cur = conn.cursor(dictionary=True)
            
            # Consulta solo empleados activos (estado = 1)
            sql = """
                SELECT e.id_empleados, e.nombre_empleado, e.cargo, e.fecha_ingreso, 
                       e.gerencia_asignada, e.estado, e.persona_id_persona,
                       p.cedula_persona, p.telefono, p.correo
                FROM empleados e
                LEFT JOIN persona p ON e.persona_id_persona = p.id_persona
                WHERE e.estado = 1 
                ORDER BY e.id_empleados DESC
            """
            parametros = []
            if limite is not None and offset is not None:
                sql += " LIMIT %s OFFSET %s"
                parametros.extend([limite, offset])
            
            cur.execute(sql, parametros)
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error al obtener empleados: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def contar_empleados(self):
        """Retorna el total de empleados activos."""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return 0
            
            cur = conn.cursor()
            sql = "SELECT COUNT(*) FROM empleados WHERE estado = 1"
            cur.execute(sql)
            resultado = cur.fetchone()
            return resultado[0] if resultado else 0
            
        except Exception as e:
            print(f"Error al contar empleados: {e}")
            return 0
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_empleado_por_id_db(self, id_empleado: int):
        """Método PRIVADO que obtiene un empleado por su ID."""
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return None
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT e.*, p.cedula_persona, p.telefono, p.correo, p.direccion, p.parroquia, p.municipio
                FROM empleados e
                LEFT JOIN persona p ON e.persona_id_persona = p.id_persona
                WHERE e.id_empleados = %s AND e.estado = 1
            """
            cur.execute(sql, (id_empleado,))
            return cur.fetchone()
            
        except Exception as e:
            print(f"Error al obtener empleado: {e}")
            return None
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __obtener_empleados_por_cargo_db(self, cargo: str):
        """
        Método PRIVADO que filtra empleados por cargo.
        Usado por otros módulos (inspecciones, proyectos, etc.)
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return []
            
            cur = conn.cursor(dictionary=True)
            
            sql = """
                SELECT e.id_empleados, e.nombre_empleado, e.cargo, e.gerencia_asignada
                FROM empleados e
                WHERE e.cargo = %s AND e.estado = 1
                ORDER BY e.nombre_empleado ASC
            """
            cur.execute(sql, (cargo,))
            return cur.fetchall()
            
        except Exception as e:
            print(f"Error al filtrar empleados por cargo: {e}")
            return []
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()
    
    def __validar_empleado_activo_db(self, id_empleado: int) -> bool:
        """
        Método PRIVADO que valida si un empleado existe y está activo.
        Validación en tiempo real según instrucciones del profesor.
        """
        conn = None
        cur = None
        
        try:
            conn = connectionBD_invilara()
            if not conn:
                return False
            
            cur = conn.cursor()
            
            sql = "SELECT id_empleados FROM empleados WHERE id_empleados = %s AND estado = 1"
            cur.execute(sql, (id_empleado,))
            return cur.fetchone() is not None
            
        except Exception:
            return False
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    # ========== MÉTODOS PÚBLICOS (Interfaz Pública - Capa de Seguridad) ==========
    
    def registrar_empleado(self, data):
        """
        Método PÚBLICO que actúa como interfaz para registrar empleados.
        Valida datos y llama al método privado.
        """
        try:
            self.set_nombre_empleado(data.get('nombre_empleado'))
            self.set_cargo(data.get('cargo'))
            self.set_fecha_ingreso(data.get('fecha_ingreso'))
            self.set_gerencia_asignada(data.get('gerencia_asignada'))
            self.set_cedula_persona(data.get('cedula_empleado'))
            
            # Datos opcionales de persona
            self.__direccion = data.get('direccion', 'No especificado')
            self.__parroquia = data.get('parroquia', 'No especificado')
            self.__municipio = data.get('municipio', 'No especificado')
            
            telefono = data.get('telefono', '').strip()
            if telefono and not self._validar_telefono(telefono):
                raise ValueError("El teléfono debe contener solo números (10 u 11 dígitos). Ej: 04141234567")
            self.__telefono = telefono if telefono else '0000000000'
            self.__correo = data.get('correo', 'sin_correo@invilara.gob.ve')
            
            return self.__guardar_empleado_db()
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al registrar: {e}")
            return None
    
    def actualizar_empleado(self, data):
        """
        Método PÚBLICO que actúa como interfaz para actualizar empleados.
        """
        try:
            id_empleado = int(data.get('id_empleado'))
            
            # Validar que el empleado existe y está activo
            if not self.__validar_empleado_activo_db(id_empleado):
                raise ValueError("El empleado no existe o fue eliminado.")
            
            self.set_id_empleado(id_empleado)
            self.set_nombre_empleado(data.get('nombre_empleado'))
            self.set_cargo(data.get('cargo'))
            self.set_fecha_ingreso(data.get('fecha_ingreso'))
            self.set_gerencia_asignada(data.get('gerencia_asignada'))
            
            return self.__actualizar_empleado_db()
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al actualizar: {e}")
            return False
    
    def eliminar_empleado_logico(self, id_empleado):
        """
        Método PÚBLICO que actúa como interfaz para el borrado lógico.
        """
        try:
            id_val = int(id_empleado)
            if id_val <= 0:
                raise ValueError("ID inválido.")
            
            # Validar existencia antes de eliminar
            if not self.__validar_empleado_activo_db(id_val):
                raise ValueError("El empleado no existe o ya fue eliminado.")
            
            self.set_id_empleado(id_val)
            return self.__eliminar_logico_db()
        except ValueError as ve:
            print(f"Error de validación: {ve}")
            raise ve
        except Exception as e:
            print(f"Error inesperado al eliminar: {e}")
            return False
    
    def obtener_todos_empleados(self):
        """Método PÚBLICO para obtener todos los empleados activos."""
        return self.__obtener_todos_empleados_db()
    
    def obtener_empleados_paginados(self, page=1, per_page=10):
        """Método PÚBLICO para obtener empleados activos paginados."""
        if page < 1:
            page = 1
        offset = (page - 1) * per_page
        return self.__obtener_todos_empleados_db(limite=per_page, offset=offset)
    
    def obtener_empleado_por_id(self, id_empleado):
        """Método PÚBLICO para obtener un empleado específico."""
        try:
            id_val = int(id_empleado)
            if id_val <= 0:
                return None
            return self.__obtener_empleado_por_id_db(id_val)
        except (ValueError, TypeError):
            return None
    
    def obtener_empleados_por_cargo(self, cargo):
        """
        Método PÚBLICO para filtrar empleados por cargo.
        Usado por otros módulos (inspecciones, proyectos, etc.)
        """
        if cargo not in self.CARGOS_VALIDOS:
            return []
        return self.__obtener_empleados_por_cargo_db(cargo)
    
    def validar_empleado_activo(self, id_empleado):
        """
        Método PÚBLICO para validar existencia en tiempo real.
        Usado por Ajax/Fetch desde el frontend.
        """
        try:
            id_val = int(id_empleado)
            return self.__validar_empleado_activo_db(id_val)
        except (ValueError, TypeError):
            return False
    
    def obtener_catalogo_cargos(self):
        """Método PÚBLICO para obtener el catálogo de cargos."""
        return list(self.CARGOS_VALIDOS)