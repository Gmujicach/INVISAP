from unittest.mock import MagicMock, patch

import pytest

from models.model_obra import ObraModel


def test_valida_texto_y_numero_de_contrato():
    assert ObraModel._es_texto_valido('Reparación de vía') is True
    assert ObraModel._es_numero_contrato_valido('CTR-001/2025') is True


def test_rechaza_texto_o_numero_de_contrato_con_caracteres_invalidos():
    assert ObraModel._es_texto_valido('<script>') is False
    assert ObraModel._es_numero_contrato_valido('CTR;DROP') is False


def test_fecha_fin_no_puede_ser_anterior_a_fecha_inicio():
    assert ObraModel._validar_fechas('2025-02-01', '2025-01-31') is False
    assert ObraModel._validar_fechas('2025-01-01', '2025-02-01') is True


def _datos_obra():
    return {
        'titulo_obra': 'Reparación vial',
        'ubicacion_obra': 'Sector Norte',
        'periodo_ejecucion': '2 meses',
        'fecha_inicio': '2025-01-01',
        'fecha_fin': '2025-03-01',
        'mediciones_obra': '100 metros',
        'valuaciones': 'Valuación inicial',
        'modificaciones_contrato': 'Sin cambios',
        'certificaciones_obras_ejecutadas': '2',
        'numero_contrato': 'CTR-001/2025',
        'porcentaje_avance_obra': '75',
        'estado': '2',
        'contratacion_id_contratacion': '4',
        'gestionar_proyectos_codigo_proyecto': 'P-25',
    }


def _obra_db():
    conexion = MagicMock()
    return conexion, conexion.cursor.return_value


def test_validadores_estaticos_fechas_y_conexion_controlada(monkeypatch):
    assert ObraModel._es_texto_valido('  Reparación vial  ', 45) is True
    assert ObraModel._es_texto_valido('', 45) is False
    assert ObraModel._es_texto_valido('texto<script>', 100) is False
    assert ObraModel._es_texto_valido('válido' * 20, 6) is True
    assert ObraModel._es_numero_contrato_valido('CTR-20/#A') is True
    assert ObraModel._es_numero_contrato_valido('CONTRATO; DROP') is False
    assert ObraModel._validar_fechas(None, 'fecha invalida') is True
    assert ObraModel._validar_fechas('2025-02-01', '2025-02-01 10:00:00') is True
    assert ObraModel._validar_fechas('2025-03-01', '2025-02-28') is False

    conexion, cursor = _obra_db()
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    assert ObraModel._con() is conexion
    ObraModel._eliminar_trigger_semaforo()
    cursor.execute.assert_called_once_with('DROP TRIGGER IF EXISTS actualizar_semaforo_obra')
    conexion.commit.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_lecturas_validaciones_duplicados_y_listas_cierran_recursos():
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchall.return_value = [{'id_obra': 3}]
    cursor.fetchone.side_effect = [
        {'id_obra': 4}, (1,), None, (1,), None, (1,),
    ]
    with patch.object(modelo, '_con', return_value=conexion):
        assert modelo._sql_obtener_todas() == [{'id_obra': 3}]
        assert modelo._sql_obtener_por_id(4) == {'id_obra': 4}
        assert modelo._sql_validar_estado(2) is True
        assert modelo._sql_validar_contratacion(5) is False
        assert modelo._sql_validar_proyecto('P1') is True
        assert modelo._sql_validar_numero_contrato_duplicado('CTR-1') is False
        assert modelo._sql_validar_numero_contrato_duplicado('NA') is False
        assert modelo._sql_listar_estados() == [{'id_obra': 3}]
        assert modelo._sql_listar_contrataciones() == [{'id_obra': 3}]
        assert modelo._sql_listar_proyectos() == [{'id_obra': 3}]
    assert any(call.args[1] == (4,) for call in cursor.execute.call_args_list if len(call.args) > 1)
    assert any(call.args[1] == (2,) for call in cursor.execute.call_args_list if len(call.args) > 1)
    assert cursor.close.call_count == 9
    assert conexion.close.call_count == 9


def test_numero_contrato_duplicado_filtra_edicion_y_no_consulta_placeholders():
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = (1,)
    with patch.object(modelo, '_con', return_value=conexion):
        assert modelo._sql_validar_numero_contrato_duplicado('CTR-5', excluir_id_obra=10) is True
        assert modelo._sql_validar_numero_contrato_duplicado('S/N') is False
    cursor.execute.assert_called_once_with(
        'SELECT 1 FROM obra WHERE numero_contrato = %s AND id_obra != %s AND estado = 1 LIMIT 1',
        ('CTR-5', 10),
    )
    assert cursor.close.call_count == 1
    assert conexion.close.call_count == 1


@pytest.mark.parametrize(
    ('field', 'expected'),
    [
        ('titulo_obra', "El campo 'titulo_obra' es obligatorio."),
        ('numero_contrato', "El campo 'numero_contrato' es obligatorio."),
    ],
)
def test_insertar_obra_rechaza_campos_requeridos_antes_de_conectar(field, expected):
    modelo = ObraModel()
    datos = _datos_obra()
    datos.pop(field)
    with patch.object(modelo, '_con') as conectar:
        assert modelo._sql_insertar(datos) == (False, expected)
    conectar.assert_not_called()


def test_insertar_obra_valida_datos_transacciona_y_deriva_semaforo():
    modelo = ObraModel()
    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.lastrowid = 41
    with patch.object(modelo, '_sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_sql_validar_estado', return_value=True) as estado, \
            patch.object(modelo, '_sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_sql_validar_proyecto', return_value=True), \
            patch.object(modelo, '_con', return_value=conexion):
        assert modelo._sql_insertar(datos) == (True, 41)
    estado.assert_called_once_with(1)
    conexion.start_transaction.assert_called_once_with()
    sql, valores = cursor.execute.call_args.args
    assert 'INSERT INTO obra' in sql
    assert valores == (
        'Reparación vial', 'Sector Norte', '2 meses', '2025-01-01', '2025-03-01',
        '100 metros', 'Valuación inicial', 'Sin cambios', 2, 'CTR-001/2025',
        75, 1, 4, 'P-25',
    )
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_insertar_obra_rechaza_validacion_y_revierte_error_sql():
    modelo = ObraModel()
    datos = _datos_obra()
    datos['porcentaje_avance_obra'] = '101'
    assert modelo._sql_insertar(datos) == (
        False, 'Porcentaje de avance debe estar entre 0 y 100.'
    )

    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.execute.side_effect = RuntimeError('fallo de inserción')
    with patch.object(modelo, '_sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_sql_validar_estado', return_value=True), \
            patch.object(modelo, '_sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_sql_validar_proyecto', return_value=True), \
            patch.object(modelo, '_con', return_value=conexion):
        resultado = modelo._sql_insertar(datos)
    assert resultado == (False, 'Error al registrar obra: fallo de inserción')
    conexion.rollback.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_actualizar_obra_verifica_existencia_y_guarda_valores_con_transaccion():
    modelo = ObraModel()
    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.rowcount = 1
    with patch.object(modelo, '_sql_obtener_por_id', return_value={'id_obra': 9}), \
            patch.object(modelo, '_sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_sql_validar_estado', return_value=True), \
            patch.object(modelo, '_sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_sql_validar_proyecto', return_value=True), \
            patch.object(ObraModel, '_eliminar_trigger_semaforo'), \
            patch.object(modelo, '_con', return_value=conexion):
        assert modelo._sql_actualizar(9, datos) == (True, 1)
    conexion.start_transaction.assert_called_once_with()
    assert 'UPDATE obra SET' in cursor.execute.call_args.args[0]
    assert cursor.execute.call_args.args[1][-1] == 9
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_eliminar_obra_solo_actualiza_registro_activo():
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = (9,)
    cursor.rowcount = 1
    with patch.object(ObraModel, '_eliminar_trigger_semaforo'), \
            patch.object(modelo, '_con', return_value=conexion):
        assert modelo._sql_eliminar(9) == (True, 1)
    assert cursor.execute.call_args_list[0].args == (
        'SELECT id_obra FROM obra WHERE id_obra = %s AND estado = 1', (9,)
    )
    assert cursor.execute.call_args_list[1].args == (
        'UPDATE obra SET estado = 0 WHERE id_obra = %s AND estado = 1', (9,)
    )
    conexion.commit.assert_called_once_with()


def test_metodos_publicos_de_obra_encaminan_a_sql_helpers():
    modelo = ObraModel()
    mapping = [
        ('obtener_obra_por_id', '_sql_obtener_por_id', (1,), {'id_obra': 1}),
        ('obtener_todas', '_sql_obtener_todas', (), []),
        ('registrar_obra', '_sql_insertar', ({},), (False, 'inválido')),
        ('actualizar_obra', '_sql_actualizar', (1, {}), (False, 'inválido')),
        ('eliminar_obra', '_sql_eliminar', (1,), (False, 'inválido')),
        ('validar_estado', '_sql_validar_estado', (1,), True),
        ('validar_contratacion', '_sql_validar_contratacion', (1,), True),
        ('validar_proyecto', '_sql_validar_proyecto', ('P1',), True),
        ('listar_estados', '_sql_listar_estados', (), []),
        ('listar_contrataciones', '_sql_listar_contrataciones', (), []),
        ('listar_proyectos', '_sql_listar_proyectos', (), []),
    ]
    for public_name, sql_name, args, expected in mapping:
        with patch.object(modelo, sql_name, return_value=expected) as delegate:
            assert getattr(modelo, public_name)(*args) == expected
        delegate.assert_called_once_with(*args)


def test_asegurar_tabla_obra_agrega_columna_solo_si_falta(monkeypatch):
    from models import model_obra

    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = None
    monkeypatch.setattr(ObraModel, 'obtener_conexion', staticmethod(lambda: conexion))
    model_obra.asegurar_tabla_obra()
    cursor.execute.assert_any_call("SHOW COLUMNS FROM obra LIKE 'activo'")
    assert 'ALTER TABLE obra ADD COLUMN activo' in cursor.execute.call_args_list[1].args[0]
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
