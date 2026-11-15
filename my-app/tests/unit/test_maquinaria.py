from unittest.mock import MagicMock, patch

import pytest

from models.model_maquinaria import MaquinariaModel


def test_valida_nombre_y_tipo_de_maquinaria():
    modelo = MaquinariaModel()

    assert modelo.validar_nombre('Excavadora')['valido'] is True
    assert modelo.validar_tipo('Pesada')['valido'] is True


def test_rechaza_nombre_corto_y_tipo_ajeno_al_catalogo():
    modelo = MaquinariaModel()

    assert modelo.validar_nombre('AB')['valido'] is False
    assert modelo.validar_tipo('Aeronave')['valido'] is False


def _conexion_maquinaria():
    conexion = MagicMock()
    cursor = conexion.cursor.return_value
    return conexion, cursor


def test_listado_paginado_y_conteo_usan_sql_y_limpian_conexion():
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.fetchall.return_value = [{'id_maquinaria': 4}]
    cursor.fetchone.return_value = (3,)

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.obtener_maquinarias(page=3, per_page=5) == [{'id_maquinaria': 4}]
        assert modelo.contar_maquinarias() == 3

    cursor.execute.assert_any_call(
        'SELECT * FROM maquinaria WHERE estado = 1 ORDER BY id_maquinaria DESC LIMIT %s OFFSET %s',
        (5, 10),
    )
    cursor.execute.assert_any_call('SELECT COUNT(*) FROM maquinaria WHERE estado = 1')
    assert cursor.close.call_count == 2
    assert conexion.close.call_count == 2


def test_consulta_maquinarias_eliminadas_y_por_id():
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.fetchall.return_value = [{'id_maquinaria': 2, 'estado': 0}]
    cursor.fetchone.return_value = {'id_maquinaria': 2}

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.obtener_maquinarias_eliminadas() == [{'id_maquinaria': 2, 'estado': 0}]
        assert modelo.obtener_maquinaria_por_id(2) == {'id_maquinaria': 2}

    cursor.execute.assert_any_call(
        'SELECT * FROM maquinaria WHERE estado = 0 ORDER BY id_maquinaria DESC'
    )
    cursor.execute.assert_any_call('SELECT * FROM maquinaria WHERE id_maquinaria = %s', (2,))
    assert conexion.close.call_count == 2


@pytest.mark.parametrize(
    ('rowcount', 'expected'),
    [
        (1, {'success': True, 'message': 'Maquinaria restaurada correctamente'}),
        (0, {'success': False, 'message': 'Maquinaria no encontrada o ya está activa'}),
    ],
)
def test_restaurar_maquinaria_devuelve_estado_y_confirma(rowcount, expected):
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.rowcount = rowcount

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.restaurar_maquinaria(6) == expected

    cursor.execute.assert_called_once_with(
        'UPDATE maquinaria SET estado = 1 WHERE id_maquinaria = %s AND estado = 0', (6,)
    )
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_registrar_maquinaria_rechaza_datos_antes_de_conectar():
    modelo = MaquinariaModel()
    with patch.object(modelo, 'obtener_conexion_estricta') as conectar:
        assert modelo.registrar_maquinaria('AB', 'Pesada') == {
            'success': False, 'message': 'El nombre debe tener al menos 3 caracteres'
        }
        assert modelo.registrar_maquinaria('Grúa', 'Aeronave') == {
            'success': False, 'message': 'Debe seleccionar un tipo válido'
        }
    conectar.assert_not_called()


@pytest.mark.parametrize(
    ('existing', 'expected'),
    [
        ({'id_maquinaria': 8, 'estado': 1},
         {'success': False, 'message': 'Esta maquinaria ya está registrada.'}),
        ({'id_maquinaria': 8, 'estado': 0},
         {'success': True, 'id': 8, 'restaurada': True, 'message': 'Maquinaria restaurada correctamente'}),
    ],
)
def test_registrar_maquinaria_maneja_registro_existente(existing, expected):
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.fetchone.return_value = existing

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.registrar_maquinaria('  Excavadora  ', 'Pesada') == expected

    cursor.execute.assert_any_call(
        'SELECT id_maquinaria, estado FROM maquinaria WHERE nombre_maquinaria = %s',
        ('Excavadora',),
    )
    assert cursor.execute.call_count == (2 if existing['estado'] == 0 else 1)
    assert conexion.commit.call_count == (1 if existing['estado'] == 0 else 0)
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_registrar_maquinaria_inserta_y_reintenta_colision_de_id():
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.fetchone.side_effect = [None, {'siguiente_id': 11}, {'siguiente_id': 12}]
    cursor.execute.side_effect = [
        None, None, Exception(1062), None, None,
    ]
    cursor.lastrowid = 12

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        resultado = modelo.registrar_maquinaria('Excavadora', 'Pesada')

    assert resultado == {
        'success': True, 'id': 12, 'message': 'Maquinaria registrada correctamente'
    }
    inserts = [call for call in cursor.execute.call_args_list if 'INSERT INTO maquinaria' in call.args[0]]
    assert [call.args[1] for call in inserts] == [
        (11, 'Excavadora', 'Pesada'), (12, 'Excavadora', 'Pesada')
    ]
    conexion.rollback.assert_called_once_with()
    conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


def test_actualizar_maquinaria_valida_antes_de_sql_y_actualiza_los_valores():
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.actualizar_maquinaria(5, 'x', 'Pesada')['success'] is False
        assert modelo.actualizar_maquinaria(5, ' Excavadora ', 'Pesada') == {
            'success': True, 'message': 'Maquinaria actualizada correctamente'
        }

    cursor.execute.assert_called_once_with(
        'UPDATE maquinaria SET nombre_maquinaria = %s, tipo_maquinaria = %s WHERE id_maquinaria = %s',
        ('Excavadora', 'Pesada', 5),
    )
    conexion.commit.assert_called_once_with()
    assert conexion.close.call_count == 1


@pytest.mark.parametrize(
    ('used_count', 'expected'),
    [(2, 'utilizada'), (0, 'eliminada')],
)
def test_eliminar_maquinaria_respeta_uso_en_proyectos(used_count, expected):
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.fetchone.return_value = {'count': used_count}

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        assert modelo.eliminar_maquinaria(9) == expected

    cursor.execute.assert_any_call(
        'SELECT COUNT(*) as count FROM proyecto_has_maquinaria WHERE maquinaria_id_maquinaria = %s',
        (9,),
    )
    if used_count:
        assert cursor.execute.call_count == 1
        conexion.commit.assert_not_called()
    else:
        cursor.execute.assert_called_with(
            'UPDATE maquinaria SET estado = 0 WHERE id_maquinaria = %s', (9,)
        )
        conexion.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    conexion.close.assert_called_once_with()


@pytest.mark.parametrize(
    ('method', 'expected'),
    [
        ('obtener_maquinarias', []),
        ('contar_maquinarias', 0),
        ('obtener_maquinarias_eliminadas', []),
        ('obtener_maquinaria_por_id', None),
        ('restaurar_maquinaria', {'success': False, 'message': 'Error al restaurar en la base de datos'}),
        ('actualizar_maquinaria', {'success': False, 'message': 'Error al actualizar en la base de datos'}),
        ('eliminar_maquinaria', 0),
    ],
)
def test_metodos_de_consulta_y_mutacion_capturan_fallos_y_cierran(method, expected):
    modelo = MaquinariaModel()
    conexion, cursor = _conexion_maquinaria()
    cursor.execute.side_effect = RuntimeError('fallo simulado')
    cursor.fetchone.side_effect = RuntimeError('fallo simulado')

    with patch.object(modelo, 'obtener_conexion_estricta', return_value=conexion):
        if method == 'obtener_maquinarias':
            actual = modelo.obtener_maquinarias()
        elif method == 'contar_maquinarias':
            actual = modelo.contar_maquinarias()
        elif method == 'obtener_maquinarias_eliminadas':
            actual = modelo.obtener_maquinarias_eliminadas()
        elif method == 'obtener_maquinaria_por_id':
            actual = modelo.obtener_maquinaria_por_id(1)
        elif method == 'restaurar_maquinaria':
            actual = modelo.restaurar_maquinaria(1)
        elif method == 'actualizar_maquinaria':
            actual = modelo.actualizar_maquinaria(1, 'Excavadora', 'Pesada')
        else:
            actual = modelo.eliminar_maquinaria(1)
    assert actual == expected
    conexion.close.assert_called_once_with()
