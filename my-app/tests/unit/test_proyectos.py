import json
from unittest.mock import MagicMock, patch

import pytest

from models.model_proyecto import ProyectoModel


def test_computos_metricos_se_serializan_y_se_recuperan():
    entradas = [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]

    serializado = ProyectoModel._serializar_computos_metricos(entradas)

    # INICIO DE ASERCIÓN: Verificar serialización y parseo
    assert json.loads(serializado) == entradas
    assert ProyectoModel._parsear_computos_metricos(serializado) == entradas
    # FIN DE ASERCIÓN


def test_texto_legacy_de_computos_metricos_se_convierte():
    # INICIO DE ASERCIÓN: Verificar conversión de texto legacy
    assert ProyectoModel._parsear_computos_metricos('10 km') == [
        {'metrica': '', 'opcion': '10 km', 'costo': ''}
    ]
    # FIN DE ASERCIÓN


def test_formatea_computos_metricos_para_mostrar():
    # INICIO DE ASERCIÓN: Verificar formateo para mostrar
    assert ProyectoModel._formatear_computos_metricos(
        [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]
    ) == '500 Longitud 10 km'
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('value', 'expected'),
    [
        (None, []),
        ([], []),
        ('', []),
        ('  ', []),
        ('[{"metrica":"Área","opcion":"5 m2","costo":"20"}]',
         [{'metrica': 'Área', 'opcion': '5 m2', 'costo': '20'}]),
        ('{"not":"a list"}', [{'metrica': '', 'opcion': '{"not":"a list"}', 'costo': ''}]),
        ('texto antiguo', [{'metrica': '', 'opcion': 'texto antiguo', 'costo': ''}]),
        (42, []),
    ],
)
def test_parsear_computos_metricos_maneja_json_legacy_y_tipos(value, expected):
    # INICIO DE ASERCIÓN: Verificar parseo de varios tipos
    assert ProyectoModel._parsear_computos_metricos(value) == expected
    # FIN DE ASERCIÓN


def test_serializar_computos_metricos_normaliza_items_y_texto():
    # INICIO DE ASERCIÓN: Verificar serialización y formateo
    assert json.loads(ProyectoModel._serializar_computos_metricos([
        {'metrica': 'Área', 'opcion': '5 m2'},
        ' Longitud ',
        '',
        9,
    ])) == [
        {'metrica': 'Área', 'opcion': '5 m2', 'costo': ''},
        {'metrica': '', 'opcion': 'Longitud', 'costo': ''},
    ]
    assert ProyectoModel._serializar_computos_metricos('  ') == '[]'
    assert ProyectoModel._serializar_computos_metricos('texto') == (
        '[{"metrica": "", "opcion": "texto", "costo": ""}]'
    )
    assert ProyectoModel._serializar_computos_metricos('{"x": 1}') == '{"x": 1}'
    assert ProyectoModel._formatear_computos_metricos([{}, {'costo': '2', 'metrica': 'Área'}]) == '2 Área'
    assert ProyectoModel._formatear_computos_metricos(None) == ''
    # FIN DE ASERCIÓN


def _modelo_proyecto_conexion():
    modelo = ProyectoModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    return modelo, conexion, cursor


def test_asegurar_descripcion_tecnica_solo_modifica_tipo_no_text():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.return_value = ('descripcion_tecnica', 'varchar')
    # INICIO DE MOCK: Llamar _asegurar_descripcion_tecnica
    modelo._asegurar_descripcion_tecnica(conexion)
    # INICIO DE ASERCIÓN: Verificar ALTER TABLE y commit/close
    cursor.execute.assert_any_call("SHOW COLUMNS FROM proyecto LIKE 'descripcion_tecnica'")
    cursor.execute.assert_any_call(
        'ALTER TABLE proyecto MODIFY COLUMN descripcion_tecnica TEXT NOT NULL'
    )
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    # FIN DE ASERCIÓN

    cursor.reset_mock()
    cursor.fetchone.return_value = ('descripcion_tecnica', 'text')
    # INICIO DE MOCK: Llamar _asegurar_descripcion_tecnica con tipo text
    modelo._asegurar_descripcion_tecnica(conexion)
    # INICIO DE ASERCIÓN: Verificar que no se ejecuta ALTER
    assert cursor.execute.call_count == 1
    conexion.commit.assert_called_once_with()
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('fila', 'esperado'),
    [
        ({'estado': 0}, {'existe_eliminado': True}),
        ({'estado': 1}, {'existe_activo': True}),
        (None, {'disponible': True}),
    ],
)
def test_validar_codigo_proyecto_distingue_activo_eliminado_y_disponible(fila, esperado):
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.return_value = fila
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar validar_codigo_proyecto
        assert modelo.validar_codigo_proyecto('PR-8') == esperado
    # INICIO DE ASERCIÓN: Verificar consulta y cierre
    cursor.execute.assert_called_once_with(
        'SELECT estado FROM proyecto WHERE codigo_proyecto = %s', ('PR-8',)
    )
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_registrar_proyecto_serializa_y_registra_maquinaria_con_transaccion():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.rowcount = 1
    cursor.fetchone.return_value = ('descripcion_tecnica', 'text')
    datos = {
        'Codigo_p': 'PROY-01',
        'fecha_p': '2025-03-04 10:11:12',
        'observaciones': 'Rehabilitación',
        'computos_p': [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}],
        'estimacion_p': '1000',
        'proyectista_p': '7',
        'maquinaria_0': '3',
        'maquinaria_1': 'no-numero',
    }
    # INICIO DE MOCK: Parchear validar_codigo_proyecto y obtener_conexion_estricta
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'disponible': True}), \
            patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar registrar_proyecto
        assert modelo.registrar_proyecto(datos) == 1

    # INICIO DE ASERCIÓN: Verificar INSERT proyecto, maquinaria, commit y close
    insert = next(call for call in cursor.execute.call_args_list if 'INSERT INTO proyecto' in call.args[0])
    assert insert.args[1] == (
        'PROY-01', '2025-03-04 10:11:12', 'Rehabilitación',
        '[{"metrica": "Longitud", "opcion": "10 km", "costo": "500"}]',
        '1000', 7,
    )
    assert cursor.execute.call_args_list[-1].args == (
        'INSERT INTO proyecto_has_maquinaria (proyecto_codigo_proyecto, maquinaria_id_maquinaria) VALUES (%s, %s)',
        ('PROY-01', 3),
    )
    conexion.commit.assert_called_once_with()
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_registrar_proyecto_rechaza_codigo_usado_y_revierte_error_de_enlace():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    # INICIO DE MOCK: Parchear validar_codigo_proyecto con código en uso
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'existe_activo': True}):
        # INICIO DE MOCK: Llamar registrar_proyecto
        assert modelo.registrar_proyecto({'Codigo_p': 'A'}) is False
    # INICIO DE ASERCIÓN: Verificar que no hay rollback ni close
    conexion.rollback.assert_not_called()
    conexion.close.assert_not_called()
    # FIN DE ASERCIÓN

    conexion.reset_mock()
    cursor.fetchone.return_value = None
    cursor.fetchone.return_value = None
    # INICIO DE MOCK: Parchear validar_codigo_proyecto y obtener_conexion_estricta
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'disponible': True}), \
            patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar registrar_proyecto con error de enlace
        assert modelo.registrar_proyecto({'Codigo_p': 'A', 'solicitud_id_p': 99}) is False
    # INICIO DE ASERCIÓN: Verificar rollback y consulta de persona
    conexion.rollback.assert_called_once_with()
    assert 'SELECT persona_id_persona' in cursor.execute.call_args_list[-1].args[0]
    conexion.close.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_listado_y_busqueda_de_proyectos_parsean_computos_metricos():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchall.return_value = [{
        'codigo_proyecto': 'P1',
        'computos_metricos': '[{"metrica":"Longitud","opcion":"10 km","costo":"500"}]',
    }]
    cursor.fetchone.return_value = {
        'codigo_proyecto': 'P1',
        'computos_metricos': '10 km',
    }
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_proyectos y obtener_proyecto_por_id
        lista = modelo.obtener_proyectos()
        detalle = modelo.obtener_proyecto_por_id('P1')
    # INICIO DE ASERCIÓN: Verificar parseo y consultas
    assert lista[0]['computos_metricos_texto'] == '500 Longitud 10 km'
    assert detalle['computos_metricos'] == [{'metrica': '', 'opcion': '10 km', 'costo': ''}]
    assert detalle['computos_metricos_texto'] == '10 km'
    list_query = cursor.execute.call_args_list[0].args[0]
    id_query, id_params = cursor.execute.call_args_list[1].args
    assert 'WHERE p.estado = 1' in list_query
    assert 'ORDER BY p.codigo_proyecto DESC' in list_query
    assert 'WHERE p.codigo_proyecto = %s' in id_query
    assert id_params == ('P1',)
    assert conexion.close.call_count == 2
    # FIN DE ASERCIÓN


def test_detalle_proyecto_agrupa_relaciones_y_devuelve_none_si_no_existe():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.side_effect = [
        {'codigo_proyecto': 'P1', 'computos_metricos': '10 km'},
        None,
    ]
    cursor.fetchall.side_effect = [[{'id_solicitudes': 2}], [{'id_maquinaria': 3}]]
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_detalle_proyecto_por_codigo
        detalle = modelo.obtener_detalle_proyecto_por_codigo('P1')
    # INICIO DE ASERCIÓN: Verificar estructura del detalle
    assert detalle == {
        'proyecto': {
            'codigo_proyecto': 'P1',
            'computos_metricos': [{'metrica': '', 'opcion': '10 km', 'costo': ''}],
            'computos_metricos_texto': '10 km',
        },
        'solicitudes': [{'id_solicitudes': 2}],
        'maquinaria': [{'id_maquinaria': 3}],
    }
    assert cursor.execute.call_count == 3
    # FIN DE ASERCIÓN

    # INICIO DE MOCK: Parchear obtener_conexion_estricta para proyecto inexistente
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_detalle_proyecto_por_codigo
        assert modelo.obtener_detalle_proyecto_por_codigo('missing') is None
        # FIN DE ASERCIÓN: Verificar None implícito


def test_actualizar_proyecto_usa_fecha_existente_actualiza_vinculos_y_confirma():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.side_effect = [
        ('descripcion_tecnica', 'text'),
        {'fecha_planificacion': '2024-01-02'},
        {'persona_id_persona': 4, 'prioridad_id_gestion_prioridad': 8},
    ]
    datos = {
        'Codigo_p': 'P2',
        'observaciones_p': 'Actualización',
        'computos_p': [],
        'estimacion_p': '900',
        'proyectista_p': 'bad',
        'solicitud_id_p': 7,
        'maquinaria_0': '5',
    }
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar actualizar_proyecto
        assert modelo.actualizar_proyecto('P1', datos) is True
    # INICIO DE ASERCIÓN: Verificar UPDATE, vínculos, commit
    update = next(
        call for call in cursor.execute.call_args_list if 'UPDATE proyecto SET' in call.args[0]
    )
    assert update.args[1] == ('P2', '2024-01-02', 'Actualización', '', '900', None, 'P1')
    assert ('P2', 7, 4, 8) in [call.args[1] for call in cursor.execute.call_args_list if len(call.args) > 1 and isinstance(call.args[1], tuple)]
    assert ('P2', 5) in [call.args[1] for call in cursor.execute.call_args_list if len(call.args) > 1 and isinstance(call.args[1], tuple)]
    conexion.commit.assert_called_once_with()
    # FIN DE ASERCIÓN


def test_eliminar_y_contar_proyectos_retorna_metricas_de_estado():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.rowcount = 1
    cursor.fetchall.return_value = [
        {'tipo_solicitud': 'En Proceso'},
        {'tipo_solicitud': 'Completada'},
        {'tipo_solicitud': 'Finalizado'},
        {'tipo_solicitud': 'Nueva'},
    ]
    # INICIO DE MOCK: Parchear obtener_conexion_estricta
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        # INICIO DE MOCK: Llamar eliminar_proyecto y obtener_contadores_proyectos
        assert modelo.eliminar_proyecto('P1') is True
        assert modelo.obtener_contadores_proyectos() == {
            'total_registrados': 4, 'en_proceso': 1, 'completadas': 2, 'total': 4
        }
    # INICIO DE ASERCIÓN: Verificar UPDATE y contadores
    assert cursor.execute.call_args_list[0].args == (
        'UPDATE proyecto SET estado = 0 WHERE codigo_proyecto = %s', ('P1',)
    )
    conexion.commit.assert_called_once_with()
    # FIN DE ASERCIÓN
