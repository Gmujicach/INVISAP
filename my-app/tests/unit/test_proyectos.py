import json
from unittest.mock import MagicMock, patch

import pytest

from models.model_proyecto import ProyectoModel


def test_computos_metricos_se_serializan_y_se_recuperan():
    entradas = [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]

    serializado = ProyectoModel._serializar_computos_metricos(entradas)

    assert json.loads(serializado) == entradas
    assert ProyectoModel._parsear_computos_metricos(serializado) == entradas


def test_texto_legacy_de_computos_metricos_se_convierte():
    assert ProyectoModel._parsear_computos_metricos('10 km') == [
        {'metrica': '', 'opcion': '10 km', 'costo': ''}
    ]


def test_formatea_computos_metricos_para_mostrar():
    assert ProyectoModel._formatear_computos_metricos(
        [{'metrica': 'Longitud', 'opcion': '10 km', 'costo': '500'}]
    ) == '500 Longitud 10 km'


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
    assert ProyectoModel._parsear_computos_metricos(value) == expected


def test_serializar_computos_metricos_normaliza_items_y_texto():
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


def _modelo_proyecto_conexion():
    modelo = ProyectoModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    return modelo, conexion, cursor


def test_asegurar_descripcion_tecnica_solo_modifica_tipo_no_text():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.return_value = ('descripcion_tecnica', 'varchar')
    modelo._asegurar_descripcion_tecnica(conexion)
    cursor.execute.assert_any_call("SHOW COLUMNS FROM proyecto LIKE 'descripcion_tecnica'")
    cursor.execute.assert_any_call(
        'ALTER TABLE proyecto MODIFY COLUMN descripcion_tecnica TEXT NOT NULL'
    )
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()

    cursor.reset_mock()
    cursor.fetchone.return_value = ('descripcion_tecnica', 'text')
    modelo._asegurar_descripcion_tecnica(conexion)
    assert cursor.execute.call_count == 1
    conexion.commit.assert_called_once_with()


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
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.validar_codigo_proyecto('PR-8') == esperado
    cursor.execute.assert_called_once_with(
        'SELECT estado FROM proyecto WHERE codigo_proyecto = %s', ('PR-8',)
    )
    conexion.close.assert_called_once_with()


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
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'disponible': True}), \
            patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.registrar_proyecto(datos) == 1

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


def test_registrar_proyecto_rechaza_codigo_usado_y_revierte_error_de_enlace():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'existe_activo': True}):
        assert modelo.registrar_proyecto({'Codigo_p': 'A'}) is False
    conexion.rollback.assert_not_called()
    conexion.close.assert_not_called()

    conexion.reset_mock()
    cursor.fetchone.return_value = None
    cursor.fetchone.return_value = None
    with patch.object(modelo, 'validar_codigo_proyecto', return_value={'disponible': True}), \
            patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.registrar_proyecto({'Codigo_p': 'A', 'solicitud_id_p': 99}) is False
    conexion.rollback.assert_called_once_with()
    assert 'SELECT persona_id_persona' in cursor.execute.call_args_list[-1].args[0]
    conexion.close.assert_called_once_with()


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
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        lista = modelo.obtener_proyectos()
        detalle = modelo.obtener_proyecto_por_id('P1')
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


def test_detalle_proyecto_agrupa_relaciones_y_devuelve_none_si_no_existe():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.fetchone.side_effect = [
        {'codigo_proyecto': 'P1', 'computos_metricos': '10 km'},
        None,
    ]
    cursor.fetchall.side_effect = [[{'id_solicitudes': 2}], [{'id_maquinaria': 3}]]
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        detalle = modelo.obtener_detalle_proyecto_por_codigo('P1')
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

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.obtener_detalle_proyecto_por_codigo('missing') is None


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
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.actualizar_proyecto('P1', datos) is True
    update = next(
        call for call in cursor.execute.call_args_list if 'UPDATE proyecto SET' in call.args[0]
    )
    assert update.args[1] == ('P2', '2024-01-02', 'Actualización', '', '900', None, 'P1')
    assert ('P2', 7, 4, 8) in [call.args[1] for call in cursor.execute.call_args_list if len(call.args) > 1 and isinstance(call.args[1], tuple)]
    assert ('P2', 5) in [call.args[1] for call in cursor.execute.call_args_list if len(call.args) > 1 and isinstance(call.args[1], tuple)]
    conexion.commit.assert_called_once_with()


def test_eliminar_y_contar_proyectos_retorna_metricas_de_estado():
    modelo, conexion, cursor = _modelo_proyecto_conexion()
    cursor.rowcount = 1
    cursor.fetchall.return_value = [
        {'tipo_solicitud': 'En Proceso'},
        {'tipo_solicitud': 'Completada'},
        {'tipo_solicitud': 'Finalizado'},
        {'tipo_solicitud': 'Nueva'},
    ]
    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.eliminar_proyecto('P1') is True
        assert modelo.obtener_contadores_proyectos() == {
            'total_registrados': 4, 'en_proceso': 1, 'completadas': 2, 'total': 4
        }
    assert cursor.execute.call_args_list[0].args == (
        'UPDATE proyecto SET estado = 0 WHERE codigo_proyecto = %s', ('P1',)
    )
    conexion.commit.assert_called_once_with()
