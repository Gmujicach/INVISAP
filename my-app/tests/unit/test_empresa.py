from unittest.mock import patch

from models.model_empresas import EmpresaModel, REQUISITOS_EMPRESA


class _CursorRequisitos:
    def __init__(self, resultados):
        self.resultados = resultados
        self.ultima_consulta = ''
        self.parametros = None
        self.consultas = []
        self.rowcount = 1
        self.closed = False

    def execute(self, sql, parametros=None):
        self.ultima_consulta = sql
        self.parametros = parametros
        self.consultas.append((sql, parametros))

    def fetchone(self):
        if 'cumple_requisitos FROM empresa' in self.ultima_consulta:
            return {'cumple_requisitos': self.resultados['cumple']}
        if 'FOR UPDATE' in self.ultima_consulta:
            return {'rif': 'J-123'}
        return None

    def fetchall(self):
        return self.resultados.get('requisitos', [])

    def close(self):
        self.closed = True


class _ConexionRequisitos:
    def __init__(self, resultados):
        self.cursor_falso = _CursorRequisitos(resultados)
        self.confirmada = False
        self.revertida = False

    def cursor(self, **kwargs):
        return self.cursor_falso

    def commit(self):
        self.confirmada = True

    def rollback(self):
        self.revertida = True

    def close(self):
        self.cerrada = True


def test_empresa_existente_activa_no_se_registra_de_nuevo():
    modelo = EmpresaModel()
    datos = {
        'rif': 'J-123',
        'nombre_empresa': 'Empresa Ejemplo',
        'telefono': '0251-1234567',
        'domicilio_fiscal': 'Barquisimeto',
    }

    with patch.object(modelo, '_ejecutar_consulta', return_value={'estado': 1}), \
            patch.object(modelo, '_ejecutar_modificacion') as modificar:
        resultado = modelo.registrar_Empresas(datos)

    assert resultado == 'DUPLICADO'
    modificar.assert_not_called()


def test_empresa_nueva_usa_rif_parametrizado():
    modelo = EmpresaModel()
    datos = {
        'rif': 'J-123',
        'nombre_empresa': 'Empresa Ejemplo',
        'telefono': '0251-1234567',
        'domicilio_fiscal': 'Barquisimeto',
    }

    with patch.object(modelo, '_ejecutar_consulta', return_value=None), \
            patch.object(modelo, '_ejecutar_modificacion', return_value=True) as modificar:
        assert modelo.registrar_Empresas(datos) is True

    assert modificar.call_args.args[1] == ('J-123', 'Empresa Ejemplo', '0251-1234567', 'Barquisimeto')


def test_obtener_requisitos_conserva_estados_individuales():
    conexion = _ConexionRequisitos({
        'cumple': 0,
        'requisitos': [
            {'requisito': 'req_acta_constitutiva', 'verificado': 1},
            {'requisito': 'req_rif', 'verificado': 0},
        ],
    })
    modelo = EmpresaModel()

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        requisitos = modelo.obtener_requisitos('J-123')

    assert requisitos['req_acta_constitutiva'] is True
    assert requisitos['req_rif'] is False
    assert all(
        requisitos[nombre] is False
        for nombre in REQUISITOS_EMPRESA
        if nombre not in ('req_acta_constitutiva', 'req_rif')
    )


def test_actualizar_requisitos_guarda_estado_parcial_y_actualiza_cumplimiento():
    conexion = _ConexionRequisitos({'cumple': 0})
    requisitos = {nombre: False for nombre in REQUISITOS_EMPRESA}
    requisitos['req_rif'] = True
    modelo = EmpresaModel()

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.actualizar_requisitos('J-123', requisitos) is True

    assert conexion.confirmada is True
    assert conexion.revertida is False
    assert any(
        'UPDATE empresa SET cumple_requisitos = %s' in sql
        and parametros == (0, 'J-123')
        for sql, parametros in conexion.cursor_falso.consultas
    )
    guardados = [
        parametros for sql, parametros in conexion.cursor_falso.consultas
        if 'INSERT INTO empresa_requisito' in sql
    ]
    assert len(guardados) == len(REQUISITOS_EMPRESA)
    assert ('J-123', 'req_rif', 1) in guardados


def test_actualizar_requisitos_rechaza_estado_incompleto():
    modelo = EmpresaModel()

    assert modelo.actualizar_requisitos('J-123', {'req_rif': True}) is False


def test_helpers_de_consulta_y_modificacion_devuelven_y_cierran_conexion():
    modelo = EmpresaModel()
    conexion = _ConexionRequisitos({'cumple': 1})
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        resultado = modelo._ejecutar_consulta(
            'SELECT cumple_requisitos FROM empresa WHERE rif = %s', (1,), un_solo_registro=True
        )
    assert resultado == {'cumple_requisitos': 1}
    assert conexion.cursor_falso.parametros == (1,)
    assert not conexion.cursor_falso.closed and conexion.cerrada

    conexion = _ConexionRequisitos({'cumple': 1})
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo._ejecutar_modificacion('UPDATE x', (2,), retornar_rowcount=True) is True
    assert conexion.confirmada and conexion.cerrada
    assert conexion.cursor_falso.parametros == (2,)


def test_empresa_reactiva_actualiza_lista_y_usa_consulta_parametrizada():
    modelo = EmpresaModel()
    datos = {'rif': 'J-2', 'nombre_empresa': 'Empresa B', 'telefono': '0251',
             'domicilio_fiscal': 'Centro'}
    with patch.object(modelo, '_ejecutar_consulta', return_value={'estado': 0}) as consultar, \
            patch.object(modelo, '_ejecutar_modificacion', return_value=True) as modificar:
        assert modelo.registrar_Empresas(datos) is True
    consultar.assert_called_once()
    assert consultar.call_args.args[1] == ('J-2',)
    assert modificar.call_args.args[1] == ('Empresa B', '0251', 'Centro', 'J-2')
    with patch.object(modelo, '_ejecutar_consulta', return_value=[{'rif': 'J-2'}]) as consultar:
        assert modelo.obtener_todas_las_empresas() == [{'rif': 'J-2'}]
        assert 'WHERE estado = 1' in consultar.call_args.args[0]
    with patch.object(modelo, '_ejecutar_consulta', return_value=[{'rel': 1}]) as consultar:
        assert modelo.obtener_relaciones_activas() == [{'rel': 1}]
        assert 'JOIN proyecto_has_maquinaria' in consultar.call_args.args[0]


def test_empresa_update_delete_y_requisitos_sin_empresa_hacen_respuestas_correctas():
    modelo = EmpresaModel()
    datos = {'rif': 'J-4', 'nombre_empresa': 'X', 'telefono': '1', 'domicilio_fiscal': 'Y'}
    with patch.object(modelo, '_ejecutar_modificacion', return_value=True) as modificar:
        assert modelo.update_empresa(datos) is True
        assert modificar.call_args.args[1] == ('X', '1', 'Y', 'J-4')
        assert modelo.eliminar_empresa('J-4') is True
        assert modificar.call_args.kwargs == {'retornar_rowcount': True}
        assert modelo.actualizar_cumple_requisitos('J-4', 1) is True
        assert modificar.call_args.args[1] == (1, 'J-4')
    conexion = _ConexionRequisitos({'cumple': None})
    conexion.cursor_falso.fetchone = lambda: None
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.obtener_requisitos('sin-empresa') is None
    assert conexion.cursor_falso.closed and conexion.cerrada


def test_requisitos_rechazan_empresa_inactiva_y_revierten():
    conexion = _ConexionRequisitos({'cumple': 0})
    conexion.cursor_falso.fetchone = lambda: None
    modelo = EmpresaModel()
    requisitos = {nombre: False for nombre in REQUISITOS_EMPRESA}
    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.actualizar_requisitos('J-123', requisitos) is False
    assert conexion.revertida and not conexion.confirmada
