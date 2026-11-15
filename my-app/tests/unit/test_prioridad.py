import pytest
from unittest.mock import MagicMock, patch

from models.model_prioridad import PrioridadModel


def test_prioridad_redondea_rango_valido():
    prioridad = PrioridadModel()

    prioridad.set_rango('0.7564')

    assert prioridad.get_rango() == 0.756


@pytest.mark.parametrize('valor', [-0.1, 1.1, 'invalido'])
def test_prioridad_rechaza_rango_fuera_de_limites(valor):
    with pytest.raises(ValueError):
        PrioridadModel().set_rango(valor)


def test_prioridad_rechaza_origen_no_permitido():
    with pytest.raises(ValueError):
        PrioridadModel().set_origen('desconocido')


def test_prioridad_constructor_getters_y_setters_validos():
    prioridad = PrioridadModel(
        id_prioridad=4,
        solicitud_id=9,
        rango_prioridad=0.25,
        justificacion='Prioridad por riesgo alto',
        responsable='Ana Pérez',
        estado=0,
        tipo_obra='Obra Mayor',
        gravedad_sugerida='Alta',
        origen='ia',
    )
    assert (prioridad.get_id(), prioridad.get_solicitud_id()) == (4, 9)
    assert prioridad.get_rango() == 0.25
    assert prioridad.get_justificacion() == 'Prioridad por riesgo alto'
    assert prioridad.get_responsable() == 'Ana Pérez'
    assert prioridad.get_estado() == 0
    assert prioridad.get_tipo_obra() == 'Obra Mayor'
    assert prioridad.get_gravedad_sugerida() == 'Alta'
    assert prioridad.get_origen() == 'ia'

    prioridad.set_justificacion('Requiere atención inmediata')
    prioridad.set_responsable('Luis Díaz')
    prioridad.set_estado('2')
    prioridad.set_origen('heuristica')
    prioridad.set_tipo_obra('Obra Menor')
    prioridad.set_gravedad_sugerida('Baja')
    assert prioridad.get_justificacion() == 'Requiere atención inmediata'
    assert prioridad.get_responsable() == 'Luis Díaz'
    assert prioridad.get_estado() == 1
    assert prioridad.get_origen() == 'heuristica'
    assert prioridad.get_tipo_obra() == 'Obra Menor'
    assert prioridad.get_gravedad_sugerida() == 'Baja'
    prioridad.set_estado(0)
    assert prioridad.get_estado() == 0


@pytest.mark.parametrize(
    ('setter', 'value'),
    [
        ('set_justificacion', 'x'),
        ('set_justificacion', 'x' * 151),
        ('set_responsable', 'A'),
        ('set_responsable', 'R' * 31),
        ('set_estado', 'no-numérico'),
        ('set_tipo_obra', 'Obra gigante'),
        ('set_gravedad_sugerida', 'Media'),
        ('set_origen', 'humano'),
    ],
)
def test_prioridad_setters_rechazan_entrada_fuera_de_reglas(setter, value):
    with pytest.raises(ValueError):
        getattr(PrioridadModel(), setter)(value)


def test_validar_para_persistencia_requiere_rango_justificacion_y_limite():
    with pytest.raises(ValueError, match='prioridad es obligatoria'):
        PrioridadModel()._validar_para_persistencia()
    with pytest.raises(ValueError, match='justificación es obligatoria'):
        PrioridadModel(rango_prioridad=0.3)._validar_para_persistencia()
    with pytest.raises(ValueError, match='no puede superar'):
        PrioridadModel(rango_prioridad=0.3, justificacion='x' * 151)._validar_para_persistencia()
    PrioridadModel(rango_prioridad=0.3, justificacion='Validada')._validar_para_persistencia()


def _prioridad_db():
    conexion = MagicMock()
    return conexion, conexion.cursor.return_value


def test_registrar_actualizar_y_eliminar_prioridad_confirman_y_limpian():
    conexion, cursor = _prioridad_db()
    cursor.lastrowid = 15
    cursor.rowcount = 1
    prioridad = PrioridadModel(
        id_prioridad=15,
        rango_prioridad=0.3,
        justificacion='Atención prioritaria',
        tipo_obra='Obra Mayor',
    )
    with patch.object(prioridad, 'obtener_conexion_estricta', return_value=conexion):
        assert prioridad.registrar() == 15
        assert prioridad.actualizar() is True
        assert prioridad.eliminar_logico() is True

    assert 'INSERT INTO prioridad' in cursor.execute.call_args_list[0].args[0]
    assert cursor.execute.call_args_list[0].args[1][:4] == (0.3, 'Obra Mayor', None, 'manual')
    assert 'WHERE id_gestion_prioridad=%s' in cursor.execute.call_args_list[1].args[0]
    assert cursor.execute.call_args_list[1].args[1][-1] == 15
    cursor.execute.assert_any_call(
        'UPDATE prioridad SET estado=0 WHERE id_gestion_prioridad=%s', (15,)
    )
    assert conexion.commit.call_count == 3
    assert cursor.close.call_count == 3
    assert conexion.close.call_count == 3


def test_persistencia_prioridad_rechaza_datos_invalidos_sin_conectar():
    prioridad = PrioridadModel(rango_prioridad=0.2)
    with patch.object(prioridad, 'obtener_conexion_estricta') as conectar:
        with pytest.raises(ValueError):
            prioridad.registrar()
        with pytest.raises(ValueError):
            prioridad.actualizar()
    conectar.assert_not_called()


@pytest.mark.parametrize(
    ('method_name', 'args', 'fila'),
    [
        ('obtener_detalle_completo', (4,), {'id_gestion_prioridad': 4}),
        ('obtener_por_id', (4,), {'id_gestion_prioridad': 4}),
        ('obtener_datos_solicitud', (9,), {'descripcion': 'Reparación'}),
        ('obtener_gravedad_obra', (2,), {'id_gravedad': 2}),
    ],
)
def test_consultas_individuales_de_prioridad_devuelven_filas_y_parametrizan(
    method_name, args, fila
):
    conexion, cursor = _prioridad_db()
    cursor.fetchone.return_value = fila
    with patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        assert getattr(PrioridadModel, method_name)(*args) == fila
    assert cursor.execute.call_args.args[1] == args
    assert cursor.close.call_count == 1
    assert conexion.close.call_count == 1


@pytest.mark.parametrize(
    ('method_name', 'fetched', 'expected_where'),
    [
        ('obtener_solicitudes_sin_priorizar', [{'id': 1}], 's.prioridad_id_gestion_prioridad IS NULL'),
        ('obtener_todas_solicitudes', [{'id': 1}], 'WHERE s.estado = 1'),
    ],
)
def test_listas_de_solicitudes_prioridad_consultan_estado_y_devuelven_filas(
    method_name, fetched, expected_where
):
    conexion, cursor = _prioridad_db()
    cursor.fetchall.return_value = fetched
    with patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        assert getattr(PrioridadModel, method_name)() == fetched
    assert expected_where in cursor.execute.call_args.args[0]
    assert cursor.execute.call_args.args[1] == ()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_listar_priorizadas_filtra_ordena_pagina_y_normaliza_rango():
    conexion, cursor = _prioridad_db()
    cursor.fetchone.return_value = {'total': 3}
    cursor.fetchall.return_value = [
        {'id_gestion_prioridad': 1, 'rango_prioridad': '0.125'},
        {'id_gestion_prioridad': 2, 'rango_prioridad': None},
    ]
    with patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        filas, total = PrioridadModel.listar_priorizadas(
            page=2, per_page=5, q='bache', riesgo='ALTA', orden='fecha_desc'
        )
    assert total == 3
    assert filas == [
        {'id_gestion_prioridad': 1, 'rango_prioridad': 0.125},
        {'id_gestion_prioridad': 2, 'rango_prioridad': 0.0},
    ]
    count_sql, count_params = cursor.execute.call_args_list[0].args
    page_sql, page_params = cursor.execute.call_args_list[1].args
    assert 'p.rango_prioridad <= 0.30' in count_sql
    assert 'p.fecha_asignacion DESC' in page_sql
    assert count_params == ['%bache%'] * 12
    assert page_params == ('%bache%',) * 12 + (5, 5)
    assert cursor.close.call_count == 1
    assert conexion.close.call_count == 1


def test_puntaje_ponderado_usa_pesos_catalogados_y_fallbacks():
    assert PrioridadModel._calcular_puntaje_ponderado(
        'Comunidad', 3, 'Obra Mayor', 3
    ) == {
        'puntaje_ponderado': 3.0,
        'rango_prioridad': 0.0,
        'peso_solicitante': 3,
        'peso_gravedad': 3,
        'peso_tipo_obra': 3,
        'peso_zona_agricola': 3,
    }
    resultado = PrioridadModel._calcular_puntaje_ponderado(
        None, 'alta', 'Tipo desconocido', None
    )
    assert resultado == {
        'puntaje_ponderado': 1.0,
        'rango_prioridad': 1.0,
        'peso_solicitante': 1,
        'peso_gravedad': 1,
        'peso_tipo_obra': 1,
        'peso_zona_agricola': 1,
    }


def test_clasificar_nueva_solicitud_sin_datos_no_invoca_servicio_ia():
    with patch.object(PrioridadModel, 'obtener_datos_solicitud', return_value=None), \
            patch('services.ia_prioridad_service.clasificar_solicitud_ia') as clasificar:
        assert PrioridadModel.clasificar_nueva_solicitud(6) == {
            'success': False, 'message': 'Solicitud no encontrada.'
        }
    clasificar.assert_not_called()


def test_clasificar_nueva_solicitud_actualiza_prioridad_existente():
    conexion, cursor = _prioridad_db()
    cursor.fetchone.side_effect = [{'pid': 12}, {'id_gestion_prioridad': 12}]
    datos = {
        'descripcion': 'Reparar vía',
        'tipo_solicitante': 'comunidad',
        'municipio': 'Coro',
        'parroquia': 'Centro',
        'sector': 'Norte',
        'ambito': 'Rural',
        'nivel_gravedad': 'Alta',
        'color_semaforo': 'Rojo',
    }
    ia = {
        'gravedad_valor': 3, 'tipo_obra': 'Obra Mayor', 'es_zona_agricola': 3,
        'gravedad_sugerida': 'Alta', 'justificacion': 'Riesgo alto', 'origen': 'ia',
    }
    with patch.object(PrioridadModel, 'obtener_datos_solicitud', return_value=datos), \
            patch('services.ia_prioridad_service.clasificar_solicitud_ia', return_value=ia), \
            patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        resultado = PrioridadModel.clasificar_nueva_solicitud(6, 'analista')
    assert resultado['success'] is True
    assert resultado['data']['id_prioridad'] == 12
    assert resultado['data']['rango'] == 0.0
    assert resultado['data']['calculo']['puntaje_ponderado'] == 3.0
    update = cursor.execute.call_args_list[-1]
    assert 'UPDATE prioridad' in update.args[0]
    assert update.args[1] == (
        0.0, 'Riesgo alto', 'Obra Mayor', 'Alta', 'ia', 'analista', 12
    )
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_clasificar_nueva_solicitud_inserta_prioridad_y_vincula_solicitud():
    conexion, cursor = _prioridad_db()
    cursor.fetchone.side_effect = [{'pid': None}]
    cursor.lastrowid = 22
    datos = {'descripcion': 'Vía rural', 'tipo_solicitante': 'particular'}
    ia = {'gravedad_valor': 1, 'tipo_obra': 'Obra Menor', 'es_zona_agricola': 1}
    with patch.object(PrioridadModel, 'obtener_datos_solicitud', return_value=datos), \
            patch('services.ia_prioridad_service.clasificar_solicitud_ia', return_value=ia), \
            patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        resultado = PrioridadModel.clasificar_nueva_solicitud(7)
    assert resultado['success'] is True
    assert resultado['data']['id_prioridad'] == 22
    assert any('INSERT INTO prioridad' in call.args[0] for call in cursor.execute.call_args_list)
    assert cursor.execute.call_args_list[-1].args == (
        'UPDATE solicitudes SET prioridad_id_gestion_prioridad=%s WHERE id_solicitudes=%s',
        (22, 7),
    )
    conexion.commit.assert_called_once_with()


def test_batch_de_solicitudes_pendientes_retorna_no_hay_trabajo_y_agrega_resultados():
    with patch.object(PrioridadModel, 'obtener_solicitudes_sin_priorizar', return_value=[]):
        assert PrioridadModel.procesar_solicitudes_pendientes_batch() == {
            'success': True, 'message': 'No hay solicitudes pendientes.', 'procesadas': 0
        }
    solicitudes = [{'id': 1}, {'id': 2}, {'id': 3}]
    salidas = [
        {'success': True, 'data': {
            'id_prioridad': 4, 'rango': 0.2, 'tipo_obra': 'Obra Mayor', 'gravedad_sugerida': 'Alta'
        }},
        {'success': False, 'message': 'No clasificada'},
        RuntimeError('simulada'),
    ]
    def clasificar(_id, _responsable):
        resultado = salidas.pop(0)
        if isinstance(resultado, Exception):
            raise resultado
        return resultado
    with patch.object(PrioridadModel, 'obtener_solicitudes_sin_priorizar', return_value=solicitudes), \
            patch.object(PrioridadModel, 'clasificar_nueva_solicitud', side_effect=clasificar):
        resumen = PrioridadModel.procesar_solicitudes_pendientes_batch('operador')
    assert resumen['success'] is False
    assert (resumen['procesadas'], resumen['errores']) == (1, 2)
    assert resumen['detalle'][0] == {
        'solicitud_id': 1, 'id_prioridad': 4, 'rango': 0.2,
        'tipo_obra': 'Obra Mayor', 'gravedad_sugerida': 'Alta',
    }
    assert resumen['detalle'][1] == {'solicitud_id': 2, 'error': 'No clasificada'}
    assert resumen['detalle'][2]['error'] == 'simulada'
    assert 'traceback' in resumen['detalle'][2]


def test_batch_todas_solicitudes_reclasifica_y_devuelve_contadores():
    with patch.object(PrioridadModel, 'obtener_todas_solicitudes', return_value=[]):
        assert PrioridadModel.procesar_todas_solicitudes_batch() == {
            'success': True, 'message': 'No hay solicitudes para procesar.', 'procesadas': 0
        }
    with patch.object(PrioridadModel, 'obtener_todas_solicitudes', return_value=[{'id': 1}]), \
            patch.object(PrioridadModel, 'clasificar_nueva_solicitud', return_value={
                'success': True, 'data': {
                    'id_prioridad': 3, 'rango': 0.4,
                    'tipo_obra': 'Obra Menor', 'gravedad_sugerida': 'Baja',
                }
            }):
        resumen = PrioridadModel.procesar_todas_solicitudes_batch('admin')
    assert resumen['success'] is True
    assert resumen['procesadas'] == 1
    assert resumen['errores'] == 0


def test_clasificar_solicitud_con_ia_actualiza_o_inserta_en_funcion_de_vinculo():
    conexion, cursor = _prioridad_db()
    cursor.fetchone.side_effect = [{'pid': 5}]
    with patch('services.ia_prioridad_service.calcular_prioridad_con_ia', return_value={
        'prioridad': 0.25, 'justificacion': 'IA', 'tipo_obra': 'Obra Mayor',
        'gravedad_sugerida': 'Alta', 'origen': 'ia',
    }), patch.object(PrioridadModel, 'obtener_conexion_estricta', return_value=conexion):
        assert PrioridadModel.clasificar_solicitud_con_ia(9, 'descripcion', responsable='admin') == {
            'id_prioridad': 5, 'rango': 0.25, 'justificacion': 'IA'
        }
    assert 'UPDATE prioridad' in cursor.execute.call_args_list[-1].args[0]
    assert cursor.execute.call_args_list[-1].args[1] == (
        0.25, 'IA', 'Obra Mayor', 'Alta', 'ia', 'admin', 5
    )
    conexion.commit.assert_called_once_with()
