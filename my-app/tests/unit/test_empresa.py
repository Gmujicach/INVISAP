from unittest.mock import patch

from models.model_empresas import EmpresaModel, REQUISITOS_EMPRESA


class _CursorRequisitos:
    def __init__(self, resultados):
        self.resultados = resultados
        self.ultima_consulta = ''
        self.parametros = None
        self.consultas = []

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
        pass


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
        pass


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
