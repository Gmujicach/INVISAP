import os
import uuid
from werkzeug.utils import secure_filename
from conexion.conexionBD import connectionBD


class EmpleadoModel:
    def __init__(self):
        self.upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'fotos_empleados')
        if not os.path.exists(self.upload_dir):
            os.makedirs(self.upload_dir, exist_ok=True)

    def _save_file(self, file_storage):
        if not file_storage or file_storage.filename == '':
            return None
        filename = secure_filename(file_storage.filename)
        ext = os.path.splitext(filename)[1]
        name = (uuid.uuid4().hex + uuid.uuid4().hex)[:100] + ext
        path_file = os.path.join(self.upload_dir, name)
        file_storage.save(path_file)
        return name

    def all(self):
        conn = connectionBD()
        cur = conn.cursor(dictionary=True)
        try:
            sql = """SELECT id_empleados, nombre_empleado, cargo, fecha_ingreso, gerencia_asignada
                     FROM empleados ORDER BY id_empleados DESC"""
            cur.execute(sql)
            return cur.fetchall()
        finally:
            cur.close()
            conn.close()

    def get(self, id_empleado):
        conn = connectionBD()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM empleados WHERE id_empleados = %s", (id_empleado,))
            return cur.fetchone()
        finally:
            cur.close()
            conn.close()

    def create(self, form):
        conn = connectionBD()
        cur = conn.cursor()
        try:
            sql = "INSERT INTO empleados (nombre_empleado, cargo, fecha_ingreso, gerencia_asignada) VALUES (%s,%s,%s,%s)"
            params = (
                form.get('nombre_empleado'),
                form.get('cargo'),
                form.get('fecha_ingreso'),
                form.get('gerencia_asignada')
            )
            cur.execute(sql, params)
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
            conn.close()

    def update(self, form, file_storage=None):
        id_empleado = form.get('id_empleado')
        salario = int(''.join([c for c in form.get('salario_empleado','0') if c.isdigit()]) or 0)
        conn = connectionBD()
        cur = conn.cursor()
        try:
            sql = "UPDATE tbl_empleados SET nombre_empleado=%s, apellido_empleado=%s, sexo_empleado=%s, telefono_empleado=%s, email_empleado=%s, profesion_empleado=%s, salario_empleado=%s"
            params = [
                form.get('nombre_empleado'),
                form.get('apellido_empleado'),
                form.get('sexo_empleado'),
                form.get('telefono_empleado'),
                form.get('email_empleado'),
                form.get('profesion_empleado'),
                salario,
            ]
            if file_storage and file_storage.filename != '':
                foto = self._save_file(file_storage)
                sql += ", foto_empleado=%s"
                params.append(foto)
            sql += " WHERE id_empleado=%s"
            params.append(id_empleado)
            cur.execute(sql, tuple(params))
            conn.commit()
            return cur.rowcount
        finally:
            cur.close()
            conn.close()

    def delete(self, id_empleado, foto_nombre=None):
        conn = connectionBD()
        cur = conn.cursor()
        try:
            cur.execute("DELETE FROM tbl_empleados WHERE id_empleado=%s", (id_empleado,))
            conn.commit()
            # borrar foto si existe
            if foto_nombre:
                fpath = os.path.join(self.upload_dir, foto_nombre)
                try:
                    if os.path.exists(fpath):
                        os.remove(fpath)
                except Exception:
                    pass
            return cur.rowcount
        finally:
            cur.close()
            conn.close()
