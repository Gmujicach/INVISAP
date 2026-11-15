from unittest.mock import patch

from models.model_contratacion import ContratacionModel


class _Cursor:
    def __init__(self, one=None, many=None, error=None):
        self.one, self.many, self.error = one, many or [], error
        self.calls = []
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        if self.error:
            raise self.error

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many

    def close(self):
        self.closed = True


class _Connection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.closed = False

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def close(self):
        self.closed = True


def test_registro_rechaza_datos_incompletos_sin_conectar_base_de_datos():
    modelo = ContratacionModel()

    with patch.object(modelo, 'obtener_conexion') as obtener_conexion:
        registrado, mensaje = modelo.registrar_contrataciones({})

    assert registrado is False
    assert 'obligatorio' in mensaje
    obtener_conexion.assert_not_called()


def test_valida_datos_completos_de_contratacion():
    modelo = ContratacionModel()
    datos = {
        'empresa_ganadora': 'Empresa S.A.',
        'empresa_rif': 'J-12345678-9',
        'descripcion': 'Mantenimiento vial',
        'numero_contrato': 'CTR-001',
        'monto': '1000',
        'tipo_contrato': 'Contrato de Obra',
        'modalidad': 'Concurso Abierto',
        'objeto': 'Ejecución de Obras',
        'fecha_inicio_procedimiento': '2024-01-01',
        'fecha_adjudicacion': '2024-01-02',
        'fecha_registro': '2024-01-03',
    }

    assert modelo._ContratacionModel__validar_datos(datos) == (True, 'Validación exitosa')


def _datos_contratacion():
    return {
        'empresa_ganadora': 'Empresa S.A.',
        'empresa_rif': 'J-12345678-9',
        'descripcion': 'Mantenimiento vial',
        'numero_contrato': 'CTR-001',
        'monto': '1000',
        'tipo_contrato': 'Contrato de Obra',
        'modalidad': 'Concurso Abierto',
        'objeto': 'Ejecución de Obras',
        'fecha_inicio_procedimiento': '2024-01-01',
        'fecha_adjudicacion': '2024-01-02',
        'fecha_registro': '2024-01-03',
    }


def test_validacion_rechaza_campo_obligatorio_y_catalogos_y_formatos():
    modelo = ContratacionModel()
    datos = _datos_contratacion()
    datos['monto'] = ''
    assert modelo._ContratacionModel__validar_datos(datos)[0] is False
    datos = _datos_contratacion()
    datos['descripcion'] = 'corto'
    assert modelo._ContratacionModel__validar_datos(datos)[0] is True
    datos['descripcion'] = 'abc'
    assert modelo._ContratacionModel__validar_datos(datos)[0] is False
    datos = _datos_contratacion()
    datos['numero_contrato'] = 'ab'
    assert modelo._ContratacionModel__validar_datos(datos)[0] is False
    for campo, valor in [('tipo_contrato', 'Otro'), ('modalidad', 'Otro'), ('objeto', 'Otro'),
                         ('fecha_registro', '03/01/2024')]:
        datos = _datos_contratacion()
        datos[campo] = valor
        assert modelo._ContratacionModel__validar_datos(datos)[0] is False


def test_registrar_consulta_e_insercion_parametrizada_y_cierra_conexion():
    modelo = ContratacionModel()
    cursor = _Cursor(one=(8,))
    conexion = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.registrar_contrataciones(_datos_contratacion()) == (
            True, 'Contratación registrada correctamente.'
        )
    assert 'MAX(id_contratacion)' in cursor.calls[0][0]
    insert = cursor.calls[1]
    assert insert[1][0:4] == (8, 'Mantenimiento vial', 'Empresa S.A.', 'CTR-001')
    assert conexion.commits == 1 and conexion.closed


def test_registro_y_actualizacion_manejan_validacion_conexion_y_duplicado():
    modelo = ContratacionModel()
    with patch.object(modelo, 'obtener_conexion', return_value=None):
        assert modelo.registrar_contrataciones(_datos_contratacion())[0] is False
        datos = _datos_contratacion()
        datos['id_contratacion'] = 1
        assert modelo.actualizar_contratacion(datos)[0] is False
    with patch.object(modelo, 'obtener_conexion') as obtener:
        assert modelo.actualizar_contratacion(_datos_contratacion()) == (
            False, 'Falta el ID de la contratación para actualizar.'
        )
        obtener.assert_not_called()
    datos = _datos_contratacion()
    datos['id_contratacion'] = 4
    cursor = _Cursor(error=RuntimeError('db'))
    conexion = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.actualizar_contratacion(datos)[0] is False
    assert conexion.closed


def test_listado_detalle_empresas_y_borrado_logico():
    modelo = ContratacionModel()
    rows = [{'id_contratacion': 2}]
    cursor = _Cursor(one=rows[0], many=rows)
    conexion = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.obtener_todas_las_contrataciones() == rows
        assert 'WHERE c.estado = 1' in cursor.calls[-1][0]
        assert modelo.obtener_contratacion_por_id(2) == rows[0]
        assert cursor.calls[-1][1] == (2,)
        assert modelo.obtener_empresas() == rows
        assert 'cumple_requisitos = 1' in cursor.calls[-1][0]
        assert modelo.eliminar_contratacion(2) is True
    assert cursor.calls[-1][1] == (2,)
    assert 'SET estado = 0' in cursor.calls[-1][0]
    assert conexion.commits == 1 and conexion.closed


def test_consultas_fallan_con_resultado_vacio_y_recurso_cerrado():
    modelo = ContratacionModel()
    cursor = _Cursor(error=RuntimeError('db'))
    conexion = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.obtener_todas_las_contrataciones() == []
        assert modelo.obtener_contratacion_por_id(1) is None
        assert modelo.obtener_empresas() == []
        assert modelo.eliminar_contratacion(1) is False
    assert conexion.closed


def test_actualizacion_exitosa_incluye_id_y_estado_en_condicion():
    modelo = ContratacionModel()
    datos = _datos_contratacion()
    datos['id_contratacion'] = 17
    cursor = _Cursor()
    conexion = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.actualizar_contratacion(datos) == (
            True, 'Contratación modificada correctamente.'
        )
    sql, params = cursor.calls[0]
    assert 'WHERE id_contratacion = %s AND estado = 1' in sql
    assert params == ('Mantenimiento vial', 'Empresa S.A.', 'CTR-001', '1000',
                      '2024-01-01', '2024-01-02', 'Contrato de Obra',
                      'Concurso Abierto', 'Ejecución de Obras', None,
                      '2024-01-03', 'J-12345678-9', 17)
    assert conexion.commits == 1 and conexion.closed


def test_registro_reintenta_colision_de_id_y_rechaza_numero_duplicado():
    class RetryCursor(_Cursor):
        def __init__(self):
            super().__init__()
            self.ids = iter([(1,), (2,)])
            self.insert_count = 0

        def fetchone(self):
            return next(self.ids, None)

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT'):
                self.insert_count += 1
                if self.insert_count == 1:
                    raise RuntimeError('1062 Duplicate PRIMARY id_contratacion')

    modelo = ContratacionModel()
    cursor = RetryCursor()
    conn = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conn):
        assert modelo.registrar_contrataciones(_datos_contratacion())[0] is True
    inserts = [p for sql, p in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert [params[0] for params in inserts] == [1, 2]
    assert conn.commits == 1 and conn.closed

    class ContractDuplicateCursor(_Cursor):
        def fetchone(self):
            return (1,)

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT'):
                raise RuntimeError('1062 Duplicate entry for numero_contrato')

    cursor = ContractDuplicateCursor()
    conn = _Connection(cursor)
    with patch.object(modelo, 'obtener_conexion', return_value=conn):
        result = modelo.registrar_contrataciones(_datos_contratacion())
    assert result == (False, 'El Número de Contrato ya se Encuentra Registrado.')
    assert conn.commits == 0 and conn.closed
