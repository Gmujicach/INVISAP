from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from models.model_respaldo import RespaldoModel


def test_limpia_nombre_de_archivo_de_respaldo():
    assert RespaldoModel._limpiar_nombre('copia de bd!.sql') == 'copia_de_bd__sql'


def test_formatea_tamano_de_respaldo():
    assert RespaldoModel._formatear_tamano(1024) == '1.0 KB'
    assert RespaldoModel._formatear_tamano(1048576) == '1.0 MB'


def _db(cursor=None, database='invilara_seguridad'):
    cursor = cursor or MagicMock()
    connection = MagicMock()
    connection.cursor.return_value = cursor
    connection.database = database
    return connection, cursor


def _model_without_constructor():
    return RespaldoModel.__new__(RespaldoModel)


def test_constructor_crea_la_carpeta_si_no_existe():
    with patch.object(RespaldoModel, 'CARPETA_RESPALDOS', 'respaldos-test'), \
            patch('models.model_respaldo.os.path.exists', return_value=False), \
            patch('models.model_respaldo.os.makedirs') as makedirs:
        RespaldoModel()

    makedirs.assert_called_once_with('respaldos-test', exist_ok=True)


def test_asegurar_tabla_agrega_columnas_faltantes_y_ensancha_decimal():
    connection, cursor = _db()
    cursor.fetchone.side_effect = [None, None, (None, 'decimal(4,2)')]
    model = _model_without_constructor()

    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._asegurar_tabla_seguridad() is True

    executed = [item.args[0] for item in cursor.execute.call_args_list]
    assert any('ADD COLUMN `nombre_archivo`' in sql for sql in executed)
    assert any('ADD COLUMN `descripcion`' in sql for sql in executed)
    assert any('MODIFY `tamaño_respaldo` decimal(10,2)' in sql for sql in executed)
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_asegurar_tabla_no_conecta_y_cierra_en_error():
    model = _model_without_constructor()
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=None):
        assert model._asegurar_tabla_seguridad() is False

    connection, cursor = _db()
    cursor.execute.side_effect = RuntimeError('DDL rechazado')
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._asegurar_tabla_seguridad() is False
    connection.commit.assert_not_called()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_asegurar_tabla_no_modifica_columnas_ya_migradas():
    connection, cursor = _db()
    cursor.fetchone.side_effect = [
        ('nombre_archivo', 'varchar(255)'),
        ('descripcion', 'varchar(255)'),
        ('tamaño_respaldo', 'decimal(10,2)'),
    ]
    model = _model_without_constructor()
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._asegurar_tabla_seguridad() is True

    sql_statements = [item.args[0] for item in cursor.execute.call_args_list]
    assert not any(sql.startswith('ALTER TABLE') for sql in sql_statements)
    connection.commit.assert_called_once_with()


def test_siguiente_id_usa_maximo_y_cierra_recursos():
    connection, cursor = _db()
    cursor.fetchone.return_value = (17,)
    model = _model_without_constructor()
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._siguiente_id() == 17

    assert 'MAX(`id_respaldo`)' in cursor.execute.call_args.args[0]
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_siguiente_id_falla_sin_conexion_y_usa_uno_si_no_hay_fila():
    model = _model_without_constructor()
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=None):
        with pytest.raises(RuntimeError, match='No se pudo conectar'):
            model._siguiente_id()

    connection, cursor = _db()
    cursor.fetchone.return_value = None
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._siguiente_id() == 1


def test_guardar_en_seguridad_inserta_datos_normalizados_y_confirma():
    connection, cursor = _db()
    model = _model_without_constructor()
    with patch.object(model, '_asegurar_tabla_seguridad') as asegurar, \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model._guardar_en_seguridad(4, 'bd.sql', 1_572_864, 'diario', None) == 'invilara_seguridad'

    asegurar.assert_called_once_with()
    sql, values = cursor.execute.call_args.args
    assert 'ON DUPLICATE KEY UPDATE' in sql
    assert values[0] == 4
    assert values[2:4] == (Decimal('1.5'), 1)
    assert values[5:] == ('bd.sql', 'diario')
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_guardar_en_seguridad_limita_tamano_y_falla_sin_conexion():
    model = _model_without_constructor()
    with patch.object(model, 'obtener_conexion_seguridad_segura', return_value=None):
        with pytest.raises(RuntimeError, match='No se pudo conectar'):
            model._guardar_en_seguridad(1, 'x.sql', 0, '', 3)


def test_guardar_en_seguridad_satura_tamano_y_preserva_usuario():
    connection, cursor = _db()
    model = _model_without_constructor()
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        model._guardar_en_seguridad(2, 'grande.sql', 10**18, 'larga', 15)

    values = cursor.execute.call_args.args[1]
    assert values[2] == Decimal('99999999.99')
    assert values[3] == 15
    connection.commit.assert_called_once_with()


def test_limpia_nombre_y_formatea_limites_y_tamanos_muy_grandes():
    assert RespaldoModel._limpiar_nombre('! / db..sql') == '____db__sql'
    assert RespaldoModel._formatear_tamano(0) == '0.0 B'
    assert RespaldoModel._formatear_tamano(1023) == '1023.0 B'
    assert RespaldoModel._formatear_tamano(1024 ** 3) == '1.0 GB'
    assert RespaldoModel._formatear_tamano(1024 ** 4) == '1.0 GB'


def test_obtener_config_bd_devuelve_config_y_comandos_por_defecto():
    config = {'host': 'db.local', 'user': 'tester', 'password': '', 'database': 'app', 'charset': 'utf8mb4'}
    with patch.object(RespaldoModel, 'configuracion_db', return_value=config), \
            patch('models.model_respaldo.os.path.exists', return_value=False):
        result = RespaldoModel._obtener_config_bd()

    assert result == {**config, 'mysqldump': 'mysqldump', 'mysql': 'mysql'}


def test_exportar_dump_y_importar_sql_invocan_clientes_y_reportan_fallos():
    model = _model_without_constructor()
    config = {'mysqldump': 'dump', 'mysql': 'mysql', 'host': 'h', 'user': 'u',
              'password': '', 'charset': 'utf8mb4', 'database': 'db'}
    output = MagicMock()
    output.__enter__.return_value = output
    output.__exit__.return_value = False
    result = SimpleNamespace(returncode=0, stderr='')
    with patch.object(model, '_obtener_config_bd', return_value=config), \
            patch('builtins.open', return_value=output), \
            patch('models.model_respaldo.subprocess.run', return_value=result) as run, \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch('models.model_respaldo.os.path.getsize', return_value=5):
        assert model._exportar_dump('out.sql') is True
        assert model._importar_sql('in.sql') is True

    export_command = run.call_args_list[0].args[0]
    import_command = run.call_args_list[1].args[0]
    assert export_command[0] == 'dump' and '--single-transaction' in export_command
    assert import_command[0] == 'mysql' and '--binary-mode' in import_command
    assert run.call_args_list[0].kwargs['stdout'] is output
    assert run.call_args_list[1].kwargs['stdin'] is output

    failed = SimpleNamespace(returncode=2, stderr='client failed')
    with patch.object(model, '_obtener_config_bd', return_value=config), \
            patch('builtins.open', return_value=output), \
            patch('models.model_respaldo.subprocess.run', return_value=failed), \
            patch('models.model_respaldo.os.path.exists', return_value=False), \
            patch('models.model_respaldo.os.path.getsize', return_value=0):
        with pytest.raises(RuntimeError, match='client failed'):
            model._exportar_dump('out.sql')
        with pytest.raises(RuntimeError, match='client failed'):
            model._importar_sql('in.sql')


def test_clientes_mysql_incluyen_password_y_exportacion_parcial_es_valida():
    model = _model_without_constructor()
    config = {'mysqldump': 'dump', 'mysql': 'mysql', 'host': 'h', 'user': 'u',
              'password': 'secret-test', 'charset': 'utf8mb4', 'database': 'db'}
    output = MagicMock()
    output.__enter__.return_value = output
    output.__exit__.return_value = False
    partial_result = SimpleNamespace(returncode=1, stderr='warning')
    with patch.object(model, '_obtener_config_bd', return_value=config), \
            patch('builtins.open', return_value=output), \
            patch('models.model_respaldo.subprocess.run', return_value=partial_result) as run, \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch('models.model_respaldo.os.path.getsize', return_value=1):
        assert model._exportar_dump('out.sql') is True
    assert '--password=secret-test' in run.call_args.args[0]

    with patch.object(model, '_obtener_config_bd', return_value=config), \
            patch('builtins.open', return_value=output), \
            patch('models.model_respaldo.subprocess.run', return_value=SimpleNamespace(returncode=0, stderr='')) as run:
        assert model._importar_sql('in.sql') is True
    assert '--password=secret-test' in run.call_args.args[0]


def test_crear_respaldo_limpia_datos_y_devuelve_metadatos():
    model = _model_without_constructor()
    with patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch('models.model_respaldo.os.path.getsize', return_value=20), \
            patch.object(model, '_exportar_dump', return_value=True) as export, \
            patch.object(model, '_asegurar_tabla_seguridad') as asegurar, \
            patch.object(model, '_siguiente_id', return_value=9), \
            patch.object(model, '_guardar_en_seguridad') as guardar:
        result = model.crear_respaldo('  <diario>; "ok"  ', 6, 'respaldo final')

    assert result['id_respaldo'] == 9
    assert result['nombre_archivo'] == 'respaldo_final.sql'
    assert result['descripcion'] == 'diario> ok'
    assert result['tamano'] == 20
    export.assert_called_once_with('respaldos\\respaldo_final.sql')
    asegurar.assert_called_once_with()
    guardar.assert_called_once_with(9, 'respaldo_final.sql', 20, 'diario> ok', 6)


def test_crear_respaldo_envuelve_errores_de_exportacion_y_registro():
    model = _model_without_constructor()
    with patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch.object(model, '_exportar_dump', side_effect=FileNotFoundError()):
        with pytest.raises(RuntimeError, match='mysqldump no está disponible'):
            model.crear_respaldo()

    with patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch('models.model_respaldo.os.path.getsize', return_value=10), \
            patch.object(model, '_exportar_dump', return_value=True), \
            patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, '_siguiente_id', return_value=2), \
            patch.object(model, '_guardar_en_seguridad', side_effect=ValueError('write')):
        with pytest.raises(RuntimeError, match='Error al registrar respaldo'):
            model.crear_respaldo()


def test_crear_respaldo_genera_nombre_automatico_e_interpreta_errores_de_id():
    model = _model_without_constructor()
    with patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch('models.model_respaldo.os.path.getsize', return_value=3), \
            patch.object(model, '_exportar_dump', return_value=True) as export, \
            patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, '_siguiente_id', side_effect=ValueError('id error')):
        with pytest.raises(RuntimeError, match='Error al obtener el siguiente ID'):
            model.crear_respaldo()

    assert export.call_args.args[0].startswith('respaldos\\respaldo_')
    assert export.call_args.args[0].endswith('.sql')

    with patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=True), \
            patch.object(model, '_exportar_dump', return_value=False):
        with pytest.raises(RuntimeError, match='No se pudo generar'):
            model.crear_respaldo()


@pytest.mark.parametrize(
    ('row', 'expected_size', 'formatted'),
    [({'tamaño_respaldo': '2.5'}, 2_621_440, '2.5 MB'),
     ({'tamaño_respaldo': 'invalid'}, 0, '0.0 B'),
     ({'tamaño_respaldo': None}, 0, '0.0 B')],
)
def test_normalizar_fila_convierte_tamano_y_completa_campos(row, expected_size, formatted):
    normalized = RespaldoModel._normalizar_fila(row)
    assert normalized['tamano'] == expected_size
    assert normalized['tamano_formateado'] == formatted
    assert normalized['nombre_archivo'] == ''
    assert normalized['descripcion'] == ''


def test_listar_respaldos_normaliza_resultados_y_cierra_conexion():
    connection, cursor = _db()
    cursor.fetchall.return_value = [{'tamaño_respaldo': 1, 'nombre_archivo': 'a.sql'}]
    model = _model_without_constructor()
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        result = model.listar_respaldos()

    assert result[0]['tamano'] == 1_048_576
    assert result[0]['nombre_archivo'] == 'a.sql'
    assert cursor.execute.call_args.args[1:] == ()
    assert 'WHERE `estado`=1' in cursor.execute.call_args.args[0]
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_listar_respaldos_conexion_ausente_o_error_devuelve_lista_vacia():
    model = _model_without_constructor()
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=None):
        assert model.listar_respaldos() == []

    connection, cursor = _db()
    cursor.execute.side_effect = RuntimeError('select failed')
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model.listar_respaldos() == []
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()


def test_obtener_por_id_normaliza_no_encontrado_y_error():
    model = _model_without_constructor()
    connection, cursor = _db()
    cursor.fetchone.return_value = {'tamaño_respaldo': 1, 'nombre_archivo': 'a.sql'}
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        result = model.obtener_por_id(3)
    assert result['tamano'] == 1_048_576
    assert cursor.execute.call_args.args[1] == (3,)
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()

    cursor.fetchone.return_value = None
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model.obtener_por_id(3) is None


def test_eliminar_respaldo_actualiza_estado_y_cubre_sin_registro_o_db():
    model = _model_without_constructor()
    connection, cursor = _db()
    cursor.rowcount = 1
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_por_id', return_value={'nombre_archivo': 'a.sql'}), \
            patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=False), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=connection):
        assert model.eliminar_respaldo(4) is True

    assert cursor.execute.call_args.args[1] == (4,)
    connection.commit.assert_called_once_with()
    cursor.close.assert_called_once_with()
    connection.close.assert_called_once_with()

    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_por_id', return_value=None):
        assert model.eliminar_respaldo(4) is False
    with patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, 'obtener_por_id', return_value={'nombre_archivo': 'a.sql'}), \
            patch.object(model, 'CARPETA_RESPALDOS', 'respaldos'), \
            patch('models.model_respaldo.os.path.exists', return_value=False), \
            patch.object(model, 'obtener_conexion_seguridad_segura', return_value=None):
        assert model.eliminar_respaldo(4) is False


def test_importar_respaldo_registra_con_metadatos_y_devuelve_advertencia_si_falla():
    model = _model_without_constructor()
    with patch.object(model, '_importar_sql') as importar, \
            patch('models.model_respaldo.os.path.getsize', return_value=12), \
            patch('models.model_respaldo.os.path.basename', return_value='copia.sql'), \
            patch.object(model, '_asegurar_tabla_seguridad') as asegurar, \
            patch.object(model, '_siguiente_id', return_value=7), \
            patch.object(model, '_guardar_en_seguridad', return_value='seguridad') as guardar:
        result = model.importar_respaldo('copia.sql', ' <inicial>; ', 2)

    importar.assert_called_once_with('copia.sql')
    asegurar.assert_called_once_with()
    guardar.assert_called_once_with(7, 'copia.sql', 12, 'inicial>', 2)
    assert result == {'id_respaldo': 7, 'advertencia': None, 'db_seguridad': 'seguridad'}

    with patch.object(model, '_importar_sql', side_effect=ValueError('invalid SQL')):
        with pytest.raises(RuntimeError, match='Error al importar respaldo'):
            model.importar_respaldo('copia.sql')

    with patch.object(model, '_importar_sql'), \
            patch('models.model_respaldo.os.path.getsize', return_value=1), \
            patch('models.model_respaldo.os.path.basename', return_value='copia.sql'), \
            patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, '_siguiente_id', return_value=8), \
            patch.object(model, '_guardar_en_seguridad', side_effect=RuntimeError('offline')):
        warning = model.importar_respaldo('copia.sql', '', 2)
    assert warning['id_respaldo'] == 8
    assert warning['db_seguridad'] is None
    assert 'No se pudo registrar' in warning['advertencia']

    with patch.object(model, '_importar_sql'), \
            patch('models.model_respaldo.os.path.getsize', return_value=1), \
            patch('models.model_respaldo.os.path.basename', return_value='copia.sql'), \
            patch.object(model, '_asegurar_tabla_seguridad'), \
            patch.object(model, '_siguiente_id', side_effect=ValueError('id error')):
        with pytest.raises(RuntimeError, match='Error al obtener el siguiente ID'):
            model.importar_respaldo('copia.sql')
