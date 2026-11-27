from unittest.mock import MagicMock, patch

import pytest

from models.model_obra import ObraModel


def test_valida_texto_y_numero_de_contrato():
    # INICIO DE ASERCIÓN: Verificar validadores de texto y número de contrato
    assert ObraModel._es_texto_valido('Reparación de vía') is True
    assert ObraModel._es_numero_contrato_valido('CTR-001/2025') is True
    # FIN DE ASERCIÓN


def test_rechaza_texto_o_numero_de_contrato_con_caracteres_invalidos():
    # INICIO DE ASERCIÓN: Verificar rechazo de caracteres inválidos
    assert ObraModel._es_texto_valido('<script>') is False
    assert ObraModel._es_numero_contrato_valido('CTR;DROP') is False
    # FIN DE ASERCIÓN


def test_fecha_fin_no_puede_ser_anterior_a_fecha_inicio():
    # INICIO DE ASERCIÓN: Verificar validación de fechas
    assert ObraModel._validar_fechas('2025-02-01', '2025-01-31') is False
    assert ObraModel._validar_fechas('2025-01-01', '2025-02-01') is True
    # FIN DE ASERCIÓN


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
    # INICIO DE ASERCIÓN: Verificar validadores estáticos
    assert ObraModel._es_texto_valido('  Reparación vial  ', 45) is True
    assert ObraModel._es_texto_valido('', 45) is False
    assert ObraModel._es_texto_valido('texto<script>', 100) is False
    assert ObraModel._es_texto_valido('válido' * 20, 6) is True
    assert ObraModel._es_numero_contrato_valido('CTR-20/#A') is True
    assert ObraModel._es_numero_contrato_valido('CONTRATO; DROP') is False
    assert ObraModel._validar_fechas(None, 'fecha invalida') is True
    assert ObraModel._validar_fechas('2025-02-01', '2025-02-01 10:00:00') is True
    assert ObraModel._validar_fechas('2025-03-01', '2025-02-28') is False
    # FIN DE ASERCIÓN

    conexion, cursor = _obra_db()
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    # INICIO DE MOCK: Llamar _eliminar_trigger_semaforo
    ObraModel._eliminar_trigger_semaforo()
    # INICIO DE ASERCIÓN: Verificar ejecución de trigger y commit/close
    cursor.execute.assert_called_once_with('DROP TRIGGER IF EXISTS actualizar_semaforo_obra')
    conexion.commit.assert_called_once_with()
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_lecturas_validaciones_duplicados_y_listas_cierran_recursos(monkeypatch):
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchall.return_value = [{'id_obra': 3}]
    cursor.fetchone.side_effect = [
        {'id_obra': 4}, (1,), None, (1,), None, (1,),
    ]
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    # INICIO DE MOCK: Llamar métodos públicos (fachada)
    assert modelo.obtener_todas() == [{'id_obra': 3}]
    assert modelo.obtener_por_id(4) == {'id_obra': 4}
    assert modelo.validar_estado(2) is True
    assert modelo.validar_contratacion(5) is False
    assert modelo.validar_proyecto('P1') is True
    assert modelo.validar_numero_contrato('CTR-1') is False
    assert modelo.validar_numero_contrato('NA') is False
    assert modelo.listar_estados() == [{'id_obra': 3}]
    assert modelo.listar_contrataciones() == [{'id_obra': 3}]
    assert modelo.listar_proyectos() == [{'id_obra': 3}]
    # INICIO DE ASERCIÓN: Verificar llamadas y cierre de recursos
    assert any(call.args[1] == (4,) for call in cursor.execute.call_args_list if len(call.args) > 1)
    assert any(call.args[1] == (2,) for call in cursor.execute.call_args_list if len(call.args) > 1)
    assert cursor.close.call_count == 9
    assert conexion.close.call_count == 9
    # FIN DE ASERCIÓN


def test_numero_contrato_duplicado_filtra_edicion_y_no_consulta_placeholders(monkeypatch):
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = (1,)
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    # INICIO DE MOCK: Llamar validar_numero_contrato (fachada)
    assert modelo.validar_numero_contrato('CTR-5', excluir_id=10) is True
    assert modelo.validar_numero_contrato('S/N') is False
    # INICIO DE ASERCIÓN: Verificar consulta y cierre de recursos
    cursor.execute.assert_called_once_with(
        'SELECT 1 FROM obra WHERE numero_contrato = %s AND id_obra != %s AND estado = 1 LIMIT 1',
        ('CTR-5', 10),
    )
    assert cursor.close.call_count == 1
    assert conexion.close.call_count == 1
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('field', 'expected'),
    [
        ('titulo_obra', "El campo 'titulo_obra' es obligatorio."),
        ('numero_contrato', "El campo 'numero_contrato' es obligatorio."),
    ],
)
def test_insertar_obra_rechaza_campos_requeridos_antes_de_conectar(field, expected, monkeypatch):
    modelo = ObraModel()
    datos = _datos_obra()
    datos.pop(field)
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    conectar = MagicMock(return_value=MagicMock())
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(conectar))
    # INICIO DE MOCK: Llamar registrar (fachada)
    assert modelo.registrar(datos) == (False, expected)
    # INICIO DE ASERCIÓN: Verificar que no se llama a la BD
    conectar.assert_not_called()
    # FIN DE ASERCIÓN


def test_insertar_obra_valida_datos_transacciona_y_deriva_semaforo(monkeypatch):
    modelo = ObraModel()
    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.lastrowid = 41
    # INICIO DE MOCK: Parchear métodos privados de validación y conexión
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    with patch.object(modelo, '_ObraModel__sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_ObraModel__sql_validar_estado', return_value=True) as estado, \
            patch.object(modelo, '_ObraModel__sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_ObraModel__sql_validar_proyecto', return_value=True):
        # INICIO DE MOCK: Llamar registrar (fachada)
        assert modelo.registrar(datos) == (True, 41)
    # INICIO DE ASERCIÓN: Verificar validaciones, transacción, SQL y commit/close
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
    # FIN DE ASERCIÓN


def test_insertar_obra_rechaza_validacion_y_revierte_error_sql(monkeypatch):
    modelo = ObraModel()
    datos = _datos_obra()
    datos['porcentaje_avance_obra'] = '101'
    # INICIO DE ASERCIÓN: Verificar rechazo por porcentaje inválido
    assert modelo.registrar(datos) == (
        False, 'Porcentaje de avance debe estar entre 0 y 100.'
    )
    # FIN DE ASERCIÓN

    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.execute.side_effect = RuntimeError('fallo de inserción')
    # INICIO DE MOCK: Parchear métodos de validación y conexión con error
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    with patch.object(modelo, '_ObraModel__sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_ObraModel__sql_validar_estado', return_value=True), \
            patch.object(modelo, '_ObraModel__sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_ObraModel__sql_validar_proyecto', return_value=True):
        # INICIO DE MOCK: Llamar registrar (fachada) con error SQL
        resultado = modelo.registrar(datos)
    # INICIO DE ASERCIÓN: Verificar rollback y cierre
    assert resultado == (False, 'Error al registrar obra: fallo de inserción')
    conexion.rollback.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_actualizar_obra_verifica_existencia_y_guarda_valores_con_transaccion(monkeypatch):
    modelo = ObraModel()
    datos = _datos_obra()
    conexion, cursor = _obra_db()
    cursor.rowcount = 1
    # INICIO DE MOCK: Parchear métodos de validación, trigger y conexión
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    with patch.object(modelo, '_ObraModel__sql_obtener_por_id', return_value={'id_obra': 9}), \
            patch.object(modelo, '_ObraModel__sql_validar_numero_contrato_duplicado', return_value=False), \
            patch.object(modelo, '_ObraModel__sql_validar_estado', return_value=True), \
            patch.object(modelo, '_ObraModel__sql_validar_contratacion', return_value=True), \
            patch.object(modelo, '_ObraModel__sql_validar_proyecto', return_value=True), \
            patch.object(ObraModel, '_eliminar_trigger_semaforo'):
        # INICIO DE MOCK: Llamar actualizar (fachada)
        assert modelo.actualizar(9, datos) == (True, 1)
    # INICIO DE ASERCIÓN: Verificar transacción, SQL, commit y cierre
    conexion.start_transaction.assert_called_once_with()
    assert 'UPDATE obra SET' in cursor.execute.call_args.args[0]
    assert cursor.execute.call_args.args[1][-1] == 9
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_eliminar_obra_solo_actualiza_registro_activo(monkeypatch):
    modelo = ObraModel()
    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = (9,)
    cursor.rowcount = 1
    # INICIO DE MOCK: Parchear trigger y conexión
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    with patch.object(ObraModel, '_eliminar_trigger_semaforo'):
        # INICIO DE MOCK: Llamar eliminar (fachada)
        assert modelo.eliminar(9) == (True, 1)
    # INICIO DE ASERCIÓN: Verificar SELECT y UPDATE, commit
    assert cursor.execute.call_args_list[0].args == (
        'SELECT id_obra FROM obra WHERE id_obra = %s AND estado = 1', (9,)
    )
    assert cursor.execute.call_args_list[1].args == (
        'UPDATE obra SET estado = 0 WHERE id_obra = %s AND estado = 1', (9,)
    )
    conexion.commit.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_metodos_publicos_de_obra_encaminan_a_sql_helpers():
    modelo = ObraModel()
    mapping = [
        ('obtener_por_id', '_ObraModel__sql_obtener_por_id', (1,), {'id_obra': 1}),
        ('obtener_todas', '_ObraModel__sql_obtener_todas', (), []),
        ('registrar', '_ObraModel__sql_insertar', ({},), (False, 'inválido')),
        ('actualizar', '_ObraModel__sql_actualizar', (1, {}), (False, 'inválido')),
        ('eliminar', '_ObraModel__sql_eliminar', (1,), (False, 'inválido')),
        ('validar_estado', '_ObraModel__sql_validar_estado', (1,), True),
        ('validar_contratacion', '_ObraModel__sql_validar_contratacion', (1,), True),
        ('validar_proyecto', '_ObraModel__sql_validar_proyecto', ('P1',), True),
        ('listar_estados', '_ObraModel__sql_listar_estados', (), []),
        ('listar_contrataciones', '_ObraModel__sql_listar_contrataciones', (), []),
        ('listar_proyectos', '_ObraModel__sql_listar_proyectos', (), []),
    ]
    for public_name, sql_name, args, expected in mapping:
        # INICIO DE MOCK: Parchear método SQL
        with patch.object(modelo, sql_name, return_value=expected) as delegate:
            # INICIO DE MOCK: Llamar método público
            assert getattr(modelo, public_name)(*args) == expected
        # INICIO DE ASERCIÓN: Verificar delegación
        delegate.assert_called_once_with(*args)
        # FIN DE ASERCIÓN


def test_construccion_asegura_columna_activo_solo_si_falta(monkeypatch):
    conexion, cursor = _obra_db()
    cursor.fetchone.return_value = None
    monkeypatch.setattr(ObraModel, 'obtener_conexion_estricta', staticmethod(lambda: conexion))
    # INICIO DE MOCK: Construir ObraModel (ejecuta __asegurar_tabla_obra en __init__)
    ObraModel()
    # INICIO DE ASERCIÓN: Verificar SHOW COLUMNS y ALTER TABLE, commit/close
    cursor.execute.assert_any_call("SHOW COLUMNS FROM obra LIKE 'activo'")
    assert 'ALTER TABLE obra ADD COLUMN activo' in cursor.execute.call_args_list[1].args[0]
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN