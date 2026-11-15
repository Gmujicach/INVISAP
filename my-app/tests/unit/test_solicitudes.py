import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from models.model_solicitudes import SolicitudModel


def _datos_solicitante(tipo):
    if tipo == 'Comunidad':
        return {
            'com_cedula': '12345678',
            'com_telefono': '04121234567',
            'com_correo': 'comunidad@example.com',
            'com_municipio': 'Iribarren',
            'com_parroquia': 'Concepcion',
            'com_ambito': 'Comunitario',
            'com_nombre': 'Comunidad Norte',
            'com_sector': 'Sector Uno',
        }
    if tipo == 'Institucion':
        return {
            'inst_director_cedula': '12345678',
            'inst_telefono': '04121234567',
            'inst_correo': 'director@example.com',
            'inst_municipio': 'Iribarren',
            'inst_parroquia': 'Concepcion',
            'inst_direccion': 'Avenida Central',
            'inst_director_nombre': 'Ana Perez',
            'inst_nombre': 'Escuela Central',
        }
    return {
        'part_cedula': '12345678',
        'part_telefono': '04121234567',
        'part_correo': 'persona@example.com',
        'part_municipio': 'Iribarren',
        'part_parroquia': 'Concepcion',
        'part_direccion': 'Avenida Central',
        'part_nombre': 'Ana',
        'part_apellido': 'Perez',
    }


def _fecha_formateada_esperada():
    return datetime(2026, 11, 12, 10, 30).strftime('%a %d-%m-%Y %I:%M:%S %p')


def test_tipo_y_estado_de_solicitud_validos():
    solicitud = SolicitudModel()

    solicitud.set_tipo_solicitud('Comunidad')
    solicitud.set_estatus_solicitud('En Proceso')

    assert solicitud.get_tipo_solicitud() == 'Comunidad'
    assert solicitud.get_estatus_solicitud() == 'En Proceso'


def test_rechaza_tipo_de_solicitud_desconocido():
    with pytest.raises(ValueError):
        SolicitudModel().set_tipo_solicitud('Desconocido')


def test_problematica_incluye_categoria_valida():
    solicitud = SolicitudModel()

    solicitud.set_problematica(
        'La vía requiere reparación urgente',
        'Infraestructura y Vialidad',
    )

    assert solicitud.get_problematica().startswith('[Infraestructura y Vialidad]')


def test_constructor_getters_y_fecha_por_defecto():
    solicitud = SolicitudModel(42)

    assert solicitud.get_id() == 42
    assert solicitud.get_tipo_solicitud() is None
    assert solicitud.get_estatus_solicitud() == 'Pendiente'
    assert solicitud.get_problematica() is None
    assert solicitud.get_fecha() is None


def test_fecha_acepta_formato_iso_y_reemplaza_separador():
    solicitud = SolicitudModel()

    solicitud.set_fecha('2026-11-12T10:30:00')

    assert solicitud.get_fecha() == '2026-11-12 10:30:00'


def test_fecha_vacia_genera_fecha_actual_con_formato_sql():
    solicitud = SolicitudModel()

    solicitud.set_fecha('')

    assert datetime.strptime(solicitud.get_fecha(), '%Y-%m-%d %H:%M:%S')


def test_estatus_desconocido_se_normaliza_a_pendiente():
    solicitud = SolicitudModel()

    solicitud.set_estatus_solicitud('No existe')

    assert solicitud.get_estatus_solicitud() == 'Pendiente'


@pytest.mark.parametrize('tipo', ['Comunidad', 'Institucion', 'Particular'])
def test_datos_de_solicitante_validos_por_tipo(tipo):
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud(tipo)

    solicitud.set_solicitante_data(_datos_solicitante(tipo))

    assert solicitud._solicitante_data['tipo_solicitante'] == tipo
    assert solicitud._solicitante_data['cedula_persona'] == '12345678'
    assert solicitud._solicitante_data['parroquia'] == 'Concepcion'


def test_datos_de_solicitante_requieren_tipo_previo():
    with pytest.raises(ValueError, match='tipo de solicitud'):
        SolicitudModel().set_solicitante_data({})


def test_datos_de_solicitante_rechazan_cedula_invalida():
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud('Particular')
    datos = _datos_solicitante('Particular')
    datos['part_cedula'] = '12-345'

    with pytest.raises(ValueError, match='Cédula inválida'):
        solicitud.set_solicitante_data(datos)


def test_conexion_delegada_a_conexion_compartida():
    conexion = Mock()

    with patch.object(SolicitudModel, 'obtener_conexion', return_value=conexion):
        assert SolicitudModel._con() is conexion


def test_cerrar_cierra_cursor_y_conexion():
    cursor = Mock()
    conexion = Mock()

    SolicitudModel._cerrar(conexion, cursor)

    cursor.close.assert_called_once()
    conexion.close.assert_called_once()


def test_limpia_texto_y_respeta_longitud_maxima():
    assert SolicitudModel._limpiar(" O'Neil <ok> ", 20) == 'ONeil ok'
    assert SolicitudModel._limpiar('abcdef', 3) == 'abc'


@pytest.mark.parametrize(
    ('fecha', 'esperada'),
    [
        (None, ''),
        (datetime(2026, 11, 12, 10, 30), _fecha_formateada_esperada()),
        ('2026-11-12 10:30:00', _fecha_formateada_esperada()),
        ('fecha no normalizada', 'fecha no normalizada'),
        (123, '123'),
    ],
)
def test_formatea_fecha_segun_tipo_de_entrada(fecha, esperada):
    assert SolicitudModel()._formatear_fecha(fecha) == esperada


@pytest.mark.parametrize(
    ('fila', 'esperado'),
    [({'id_persona': 17}, 17), ((18,), 18), (None, None)],
)
def test_busca_persona_admite_filas_diccionario_y_tupla(fila, esperado):
    cursor = Mock()
    cursor.fetchone.return_value = fila

    resultado = SolicitudModel()._sql_buscar_persona(cursor, '12345678')

    assert resultado == esperado
    cursor.execute.assert_called_once()


def test_inserta_persona_y_devuelve_id_siguiente():
    cursor = Mock()
    cursor.fetchone.return_value = {'siguiente_id': 9}
    datos = {
        'cedula_persona': '12.345.678',
        'direccion': 'Calle Uno',
        'parroquia': 'Concepcion',
        'municipio': 'Iribarren',
        'telefono': '04121234567',
        'correo': 'persona@example.com',
    }

    resultado = SolicitudModel()._sql_insertar_persona(cursor, datos)

    assert resultado == 9
    assert cursor.execute.call_count == 2
    assert cursor.execute.call_args_list[1].args[1][1] == 12345678


@pytest.mark.parametrize(
    ('tipo', 'tabla'),
    [
        ('Particular', 'particular'),
        ('Comunidad', 'comunidad'),
        ('Institucion', 'institucion'),
    ],
)
def test_inserta_subtipo_segun_categoria(tipo, tabla):
    cursor = Mock()
    cursor.fetchone.return_value = {'siguiente_id': 4}
    datos = _datos_solicitante(tipo)
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud(tipo)
    solicitud.set_solicitante_data(datos)

    solicitud._sql_insertar_subtipo(cursor, 12, solicitud._solicitante_data)

    assert cursor.execute.call_count == 2
    assert tabla in cursor.execute.call_args_list[1].args[0]
    assert cursor.execute.call_args_list[1].args[1][-1] == 12


def test_crea_prioridad_pendiente_y_devuelve_id():
    cursor = Mock()
    cursor.lastrowid = 21
    solicitud = SolicitudModel()
    solicitud.set_fecha('2026-11-12 10:30:00')

    resultado = solicitud._sql_crear_prioridad_pendiente(cursor)

    assert resultado == 21
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1][1] == 'pendiente'


def test_asegura_columna_problematica_ampliando_esquema_antiguo():
    SolicitudModel._columna_problematica_verificada = False
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = {'Type': 'varchar(255)'}

    try:
        SolicitudModel._asegurar_columna_problematica(conexion)
    finally:
        SolicitudModel._columna_problematica_verificada = False

    assert any('ALTER TABLE solicitudes' in call.args[0] for call in cursor.execute.call_args_list)
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()


def test_guardar_retorna_false_si_faltan_datos_obligatorios():
    assert SolicitudModel().guardar() is False


def test_guardar_registra_solicitud_y_confirma_transaccion():
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud('Comunidad')
    solicitud.set_problematica('La vía requiere reparación urgente')
    solicitud.set_fecha('2026-11-12 10:30:00')
    solicitud._solicitante_data = {'cedula_persona': '12345678'}
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.lastrowid = 73

    with (
        patch.object(SolicitudModel, '_con', return_value=conexion),
        patch.object(SolicitudModel, '_asegurar_columna_problematica'),
        patch.object(solicitud, '_sql_buscar_persona', return_value=18),
        patch.object(solicitud, '_sql_crear_prioridad_pendiente', return_value=24),
    ):
        resultado = solicitud.guardar()

    assert resultado == 73
    assert solicitud.get_id() == 73
    conexion.commit.assert_called_once()
    cursor.execute.assert_called_once()


def test_actualizar_retorna_false_sin_identificador():
    assert SolicitudModel().actualizar() is False


def test_actualizar_modifica_campos_y_confirma():
    solicitud = SolicitudModel(7)
    solicitud.set_estatus_solicitud('Completada')
    solicitud.set_problematica('La vía requiere reparación urgente')
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    with (
        patch.object(SolicitudModel, '_con', return_value=conexion),
        patch.object(SolicitudModel, '_asegurar_columna_problematica'),
    ):
        assert solicitud.actualizar() is True

    conexion.commit.assert_called_once()


def test_actualizar_estatus_ejecuta_update():
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = SolicitudModel.actualizar_estatus(5, 'En Proceso')

    assert resultado is True
    conexion.commit.assert_called_once()


def test_eliminar_retorna_false_sin_identificador():
    assert SolicitudModel().eliminar() is False


def test_eliminar_borra_registro_existente():
    solicitud = SolicitudModel(5)
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = solicitud.eliminar()

    assert resultado is True
    conexion.commit.assert_called_once()


def test_obtener_todas_formatea_fechas():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': datetime(2026, 11, 12, 10, 30)}]

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = SolicitudModel.obtener_todas()

    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()


def test_buscar_por_id_consulta_y_formatea_fecha():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = {
        'id_solicitudes': 8,
        'fecha': '2026-11-12 10:30:00',
    }

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = SolicitudModel.buscar_por_id(8)

    assert resultado['id_solicitudes'] == 8
    assert resultado['fecha_formateada'] == _fecha_formateada_esperada()
    cursor.execute.assert_called_once()


@pytest.mark.parametrize(
    ('metodo', 'fila', 'esperado'),
    [
        ('obtener_estadisticas', {'estatus_solicitud': 'Pendiente', 'total': 3}, {'Pendiente': 3}),
        ('obtener_estadisticas_por_tipo', {'tipo_solicitud': 'Comunidad', 'total': 2}, {'Comunidad': 2}),
    ],
)
def test_obtiene_estadisticas_agrupadas(metodo, fila, esperado):
    conexion = Mock()
    conexion.cursor.return_value.fetchall.return_value = [fila]

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = getattr(SolicitudModel, metodo)()

    assert resultado == esperado


def test_obtener_estadisticas_por_parroquia_devuelve_filas():
    conexion = Mock()
    filas = [{'parroquia': 'Concepcion', 'total': 4}]
    conexion.cursor.return_value.fetchall.return_value = filas

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        assert SolicitudModel.obtener_estadisticas_por_parroquia() == filas


def test_obtener_solicitudes_priorizadas_aplica_limite_y_formatea_fecha():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': '2026-11-12 10:30:00'}]

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = SolicitudModel.obtener_solicitudes_priorizadas(5)

    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()
    assert cursor.execute.call_args.args[1] == (5,)


def test_obtener_solicitudes_pendientes_filtra_y_formatea_fecha():
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': '2026-11-12 10:30:00'}]

    with patch.object(SolicitudModel, '_con', return_value=conexion):
        resultado = SolicitudModel.obtener_solicitudes_pendientes()

    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()
    assert 'estatus_solicitud = \'Pendiente\'' in cursor.execute.call_args.args[0]
