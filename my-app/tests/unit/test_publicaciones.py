from unittest.mock import MagicMock, patch

import pytest

from models.model_publicaciones import PublicacionModel
from models.model_publicacion import PublicacionModel as PublicacionEntityModel


def test_obtener_publicacion_consulta_por_id_con_parametro():
    modelo = PublicacionModel()
    conexion = MagicMock()
    conexion.cursor.return_value.fetchone.return_value = {'id_publicacion': 7}

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        resultado = modelo.obtener_publicacion_por_id(7)

    assert resultado == {'id_publicacion': 7}
    conexion.cursor.return_value.execute.assert_called_once_with(
        'SELECT *, cuerpo_publicacion FROM publicacion WHERE id_publicacion = %s', (7,)
    )


def _mock_publicacion_model():
    modelo = PublicacionModel()
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    return modelo, conexion, cursor


def test_listado_publicaciones_y_listado_informes_devuelven_filas_y_cierran():
    modelo, conexion, cursor = _mock_publicacion_model()
    cursor.fetchall.side_effect = [[{'id_publicacion': 3}], [{'id_informe': 6}]]

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.obtener_todas_las_publicaciones() == [{'id_publicacion': 3}]
        assert modelo.obtener_informes_para_publicaciones() == [{'id_informe': 6}]

    cursor.execute.assert_any_call(
        'SELECT * FROM publicacion ORDER BY fecha_publicacion DESC'
    )
    cursor.execute.assert_any_call(
        'SELECT id_informe, tipo_informe AS nombre_proyecto FROM informe_avance_obra'
    )
    assert cursor.close.call_count == 2
    assert conexion.close.call_count == 2


def test_registrar_publicacion_construye_datos_confirma_y_reintenta_id_duplicado():
    modelo, conexion, cursor = _mock_publicacion_model()
    cursor.fetchone.side_effect = [(4,), (5,)]
    cursor.execute.side_effect = [None, Exception(1062), None, None]
    cursor.rowcount = 1
    datos = {
        'titulo_publicacion': 'Avance de obra',
        'nombre_responsable': 'Ana Pérez',
        'tipo_publicacion': 'Informativa',
        'fecha_publicacion': '2025-03-01',
        'informe_avance_obra_id_informe': 9,
    }

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.registrar_publicacion(datos) == 1

    inserts = [call for call in cursor.execute.call_args_list if 'INSERT INTO publicacion' in call.args[0]]
    assert [call.args[1] for call in inserts] == [
        (4, 'Avance de obra', 'Ana Pérez', 'Informativa', '2025-03-01', 9, 1, 'Contenido pendiente'),
        (5, 'Avance de obra', 'Ana Pérez', 'Informativa', '2025-03-01', 9, 1, 'Contenido pendiente'),
    ]
    conexion.rollback.assert_called_once_with()
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_actualizar_y_eliminar_publicacion_verifican_sql_transaccion_y_rowcount():
    modelo, conexion, cursor = _mock_publicacion_model()
    cursor.rowcount = 1
    datos = {
        'titulo_publicacion': 'Actualización de obra',
        'nombre_responsable': 'Ana Pérez',
        'tipo_publicacion': 'General',
        'informe_avance_obra_id_informe': 2,
    }

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.actualizar_publicacion(7, datos) == 1
        assert modelo.eliminar_publicacion(7) == 1

    assert cursor.execute.call_args_list[0].args[1] == (
        'Actualización de obra', 'Ana Pérez', 'General', 2, 'Contenido pendiente', 7
    )
    cursor.execute.assert_any_call('DELETE FROM publicacion WHERE id_publicacion = %s', (7,))
    assert conexion.commit.call_count == 2
    assert cursor.close.call_count == 2
    assert conexion.close.call_count == 2


def test_validar_informe_activo_distingue_existe_y_ausente():
    modelo, conexion, cursor = _mock_publicacion_model()
    cursor.fetchone.side_effect = [(1,), None]

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.validar_informe_activo(1) is True
        assert modelo.validar_informe_activo(9) is False

    cursor.execute.assert_any_call(
        'SELECT COUNT(*) FROM informe_avance_obra WHERE id_informe = %s', (1,)
    )
    assert cursor.close.call_count == 2
    assert conexion.close.call_count == 2


def test_metodos_publicacion_capturan_error_de_bd_y_cierran_recursos():
    modelo, conexion, cursor = _mock_publicacion_model()
    cursor.execute.side_effect = RuntimeError('fallo simulado')

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        assert modelo.obtener_todas_las_publicaciones() == []
        assert modelo.registrar_publicacion({
            'titulo_publicacion': 'Avance de obra',
            'nombre_responsable': 'Ana Pérez',
            'tipo_publicacion': 'General',
            'fecha_publicacion': '2025-03-01',
            'informe_avance_obra_id_informe': 1,
        }) == 0
        assert modelo.obtener_publicacion_por_id(1) is None
        assert modelo.actualizar_publicacion(1, {
            'titulo_publicacion': 'Avance de obra',
            'nombre_responsable': 'Ana Pérez',
            'tipo_publicacion': 'General',
            'informe_avance_obra_id_informe': 1,
        }) == 0
        assert modelo.eliminar_publicacion(1) == 0
        assert modelo.obtener_informes_para_publicaciones() == []
        assert modelo.validar_informe_activo(1) is False

    assert cursor.close.call_count == 7
    assert conexion.close.call_count == 7


def _crear_entidad_publicacion(monkeypatch, respuesta_columna=None):
    conexion = MagicMock()
    conexion.cursor.return_value.fetchone.return_value = respuesta_columna
    monkeypatch.setattr(PublicacionEntityModel, 'obtener_conexion', lambda self: conexion)
    return PublicacionEntityModel(), conexion, conexion.cursor.return_value


def test_modelo_entidad_publicacion_constructor_y_propiedades_validan_valores(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    assert entidad.titulo is None
    assert entidad.responsable is None
    assert entidad.tipo is None
    assert entidad.id_informe is None
    assert entidad.cuerpo == 'Contenido pendiente'
    assert entidad._PublicacionModel__estado == 1
    cursor.execute.assert_called_once_with(
        "SHOW COLUMNS FROM publicacion LIKE 'cuerpo_publicacion'"
    )

    entidad.titulo = 'Avance de obra'
    entidad.responsable = 'Ana Pérez'
    entidad.tipo = 'Informativa'
    entidad.id_informe = 7
    entidad.cuerpo = ''
    assert (entidad.titulo, entidad.responsable, entidad.tipo, entidad.id_informe) == (
        'Avance de obra', 'Ana Pérez', 'Informativa', 7
    )
    assert entidad.cuerpo == 'Contenido pendiente'
    with pytest.raises(ValueError):
        entidad.titulo = 'x'
    with pytest.raises(ValueError):
        entidad.responsable = 'A1'
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_modelo_entidad_asegura_columna_ausente_y_captura_error(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    cursor.reset_mock()
    conexion.commit.reset_mock()
    conexion.close.reset_mock()
    cursor.fetchone.return_value = None
    entidad._PublicacionModel__asegurar_tabla_publicacion()
    cursor.execute.assert_any_call("ALTER TABLE publicacion ADD COLUMN cuerpo_publicacion TEXT")
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_modelo_entidad_encamina_metodos_delegados_y_validacion(monkeypatch):
    entidad, _, _ = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    entidad._PublicacionModel__obtener_publicaciones_db = MagicMock(return_value=[{'id_publicacion': 1}])
    entidad._PublicacionModel__obtener_por_id_db = MagicMock(return_value={'id_publicacion': 2})
    entidad._PublicacionModel__obtener_informes_db = MagicMock(return_value=[{'id_informe': 3}])
    entidad._PublicacionModel__registrar_db = MagicMock(return_value=True)
    entidad._PublicacionModel__actualizar_db = MagicMock(return_value=True)
    entidad._PublicacionModel__borrado_logico_db = MagicMock(return_value=True)
    entidad._PublicacionModel__verificar_existencia_informe = MagicMock(return_value=True)

    assert entidad.obtener_todas_las_publicaciones() == [{'id_publicacion': 1}]
    assert entidad.obtener_todas() == [{'id_publicacion': 1}]
    assert entidad.obtener_publicacion_por_id(2) == {'id_publicacion': 2}
    assert entidad.obtener_por_id(2) == {'id_publicacion': 2}
    assert entidad.obtener_informes_para_publicaciones() == [{'id_informe': 3}]
    assert entidad.guardar() is True
    assert entidad.actualizar() is True
    assert entidad.eliminar() is True
    assert entidad.validar_informe_activo(3) is True


def test_modelo_entidad_guarda_y_actualiza_datos_normalizados(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    entidad._PublicacionModel__registrar_db = MagicMock(return_value=True)
    entidad._PublicacionModel__actualizar_db = MagicMock(return_value=True)
    data = {
        'titulo_publicacion': 'Avance de obra',
        'nombre_responsable': 'Ana Pérez',
        'tipo_publicacion': 'Informativa',
        'id_informe': '12',
        'cuerpo_publicacion': 'Resumen',
    }

    assert entidad.registrar_publicacion(data) == 1
    assert entidad.titulo == 'Avance de obra'
    assert entidad.responsable == 'Ana Pérez'
    assert entidad.id_informe == '12'
    assert entidad.cuerpo == 'Resumen'
    assert entidad.actualizar_publicacion(8, data) is True
    assert entidad._PublicacionModel__id_publicacion == 8
    assert entidad._PublicacionModel__actualizar_db.call_count == 1


def test_metodos_privados_de_modelo_entidad_forman_sql_y_convierten_id(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    entidad.titulo = 'Avance de obra'
    entidad.responsable = 'Ana Pérez'
    entidad.tipo = 'General'
    entidad.id_informe = '22'
    entidad._PublicacionModel__id_publicacion = 5
    cursor.rowcount = 1

    assert entidad._PublicacionModel__actualizar_db() is True
    sql_actualizar, valores_actualizar = cursor.execute.call_args.args
    assert 'UPDATE publicacion SET' in sql_actualizar
    assert 'WHERE id_publicacion = %s' in sql_actualizar
    assert valores_actualizar == (
        'Avance de obra', 'Ana Pérez', 'General', 22, 'Contenido pendiente', 5
    )
    assert conexion.commit.call_count == 1

    entidad._PublicacionModel__id_publicacion = 5
    assert entidad._PublicacionModel__borrado_logico_db() is True
    cursor.execute.assert_called_with(
        'UPDATE publicacion SET estado = 0 WHERE id_publicacion = %s', (5,)
    )
    assert conexion.commit.call_count == 2


def test_metodos_de_consulta_privados_de_modelo_entidad_devuelven_filas(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    cursor.reset_mock()
    conexion.close.reset_mock()
    publicaciones = [{'id_publicacion': 1}]
    informes = [{'id_informe': 2}]
    publicacion = {'id_publicacion': 3}
    cursor.fetchall.side_effect = [publicaciones, informes]
    cursor.fetchone.return_value = publicacion

    assert entidad._PublicacionModel__obtener_publicaciones_db() == publicaciones
    assert entidad._PublicacionModel__obtener_informes_db() == informes
    assert entidad._PublicacionModel__obtener_por_id_db(3) == publicacion
    assert 'WHERE estado = 1 ORDER BY fecha_publicacion DESC' in cursor.execute.call_args_list[0].args[0]
    assert cursor.execute.call_args_list[1].args[0] == (
        'SELECT id_informe, tipo_informe AS nombre_proyecto FROM informe_avance_obra WHERE estado_registro = 1'
    )
    assert cursor.execute.call_args_list[2].args[1] == (3,)
    assert cursor.close.call_count == 3
    assert conexion.close.call_count == 3


def test_registrar_db_de_entidad_prioriza_id_y_confirma_insercion(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    cursor.reset_mock()
    conexion.close.reset_mock()
    cursor.fetchone.return_value = (10,)
    cursor.rowcount = 1
    entidad.titulo = 'Avance de obra'
    entidad.responsable = 'Ana Pérez'
    entidad.tipo = 'General'
    entidad.id_informe = '7'
    entidad.cuerpo = 'Resumen'

    assert entidad._PublicacionModel__registrar_db() is True
    assert cursor.execute.call_args_list[0].args == (
        'SELECT COALESCE(MAX(id_publicacion), 0) + 1 AS siguiente_id FROM publicacion'
    ,)
    insert = cursor.execute.call_args_list[1]
    assert 'INSERT INTO publicacion' in insert.args[0]
    valores = insert.args[1]
    assert valores[:4] == (10, 'Avance de obra', 'Ana Pérez', 'General')
    assert valores[5:] == (7, 1, 'Resumen')
    assert len(valores[4]) == 19
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_modelo_entidad_verifica_existencia_de_informe_sin_consultar_ids_invalidos(monkeypatch):
    entidad, conexion, cursor = _crear_entidad_publicacion(monkeypatch, ('cuerpo_publicacion', 'text'))
    cursor.reset_mock()
    conexion.close.reset_mock()
    cursor.fetchone.return_value = ('4',)

    assert entidad.validar_informe_activo(None) is False
    cursor.execute.assert_not_called()
    assert entidad.validar_informe_activo(' 4 ') is True
    cursor.execute.assert_called_with(
        'SELECT id_informe FROM informe_avance_obra WHERE id_informe = %s LIMIT 1', ('4',)
    )
    assert conexion.close.call_count == 1
