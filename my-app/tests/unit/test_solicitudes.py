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

    # INICIO DE ASERCIÓN: Verificar que tipo y estatus se establecen correctamente
    assert solicitud.get_tipo_solicitud() == 'Comunidad'
    assert solicitud.get_estatus_solicitud() == 'En Proceso'
    # FIN DE ASERCIÓN


def test_rechaza_tipo_de_solicitud_desconocido():
    # INICIO DE MOCK: pytest.raises context manager para prueba de excepción
    with pytest.raises(ValueError):
        SolicitudModel().set_tipo_solicitud('Desconocido')
    # FIN DE MOCK


def test_problematica_incluye_categoria_valida():
    solicitud = SolicitudModel()

    solicitud.set_problematica(
        'La vía requiere reparación urgente',
        'Infraestructura y Vialidad',
    )

    # INICIO DE ASERCIÓN: Verificar que problemática incluye prefijo de categoría
    assert solicitud.get_problematica().startswith('[Infraestructura y Vialidad]')
    # FIN DE ASERCIÓN


def test_SolicitudModel__constructor_getters_y_fecha_por_defecto():
    solicitud = SolicitudModel(42)

    # INICIO DE ASERCIÓN: Verificar que el constructor inicializa todos los campos correctamente
    assert solicitud.get_id() == 42
    assert solicitud.get_tipo_solicitud() is None
    assert solicitud.get_estatus_solicitud() == 'Pendiente'
    assert solicitud.get_problematica() is None
    assert solicitud.get_fecha() is None
    # FIN DE ASERCIÓN


def test_fecha_acepta_formato_iso_y_reemplaza_separador():
    solicitud = SolicitudModel()

    solicitud.set_fecha('2026-11-12T10:30:00')

    # INICIO DE ASERCIÓN: Verificar que formato ISO se convierte a formato SQL
    assert solicitud.get_fecha() == '2026-11-12 10:30:00'
    # FIN DE ASERCIÓN


def test_fecha_vacia_genera_fecha_actual_SolicitudModel__con_formato_sql():
    solicitud = SolicitudModel()

    solicitud.set_fecha('')

    # INICIO DE ASERCIÓN: Verificar que cadena vacía genera fecha actual en formato SQL
    assert datetime.strptime(solicitud.get_fecha(), '%Y-%m-%d %H:%M:%S')
    # FIN DE ASERCIÓN


def test_estatus_desconocido_se_normaliza_a_pendiente():
    solicitud = SolicitudModel()

    solicitud.set_estatus_solicitud('No existe')

    # INICIO DE ASERCIÓN: Verificar que estatus desconocido se normaliza a Pendiente
    assert solicitud.get_estatus_solicitud() == 'Pendiente'
    # FIN DE ASERCIÓN


@pytest.mark.parametrize('tipo', ['Comunidad', 'Institucion', 'Particular'])
def test_datos_de_solicitante_validos_por_tipo(tipo):
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud(tipo)

    solicitud.set_solicitante_data(_datos_solicitante(tipo))

    # INICIO DE ASERCIÓN: Verificar que datos del solicitante se almacenan correctamente por tipo
    assert solicitud._SolicitudModel__solicitante_data['tipo_solicitante'] == tipo
    assert solicitud._SolicitudModel__solicitante_data['cedula_persona'] == '12345678'
    assert solicitud._SolicitudModel__solicitante_data['parroquia'] == 'Concepcion'
    # FIN DE ASERCIÓN


def test_datos_de_solicitante_requieren_tipo_previo():
    # INICIO DE MOCK: pytest.raises para ValueError en tipo faltante
    with pytest.raises(ValueError, match='tipo de solicitud'):
        SolicitudModel().set_solicitante_data({})
    # FIN DE MOCK


def test_datos_de_solicitante_rechazan_cedula_invalida():
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud('Particular')
    datos = _datos_solicitante('Particular')
    datos['part_cedula'] = '12-345'

    # INICIO DE MOCK: pytest.raises para ValueError en cédula inválida
    with pytest.raises(ValueError, match='Cédula inválida'):
        solicitud.set_solicitante_data(datos)
    # FIN DE MOCK


def test_SolicitudModel__conexion_delegada_a_SolicitudModel__conexion_compartida():
    # INICIO DE MOCK: Crear objeto de conexión simulado
    conexion = Mock()

    # INICIO DE MOCK: Parchear obtener_conexion para devolver conexión simulada
    with patch.object(SolicitudModel, 'obtener_conexion', return_value=conexion):
        # INICIO DE ASERCIÓN: Verificar que _SolicitudModel__con devuelve la conexión simulada
        assert SolicitudModel._SolicitudModel__con() is conexion
        # FIN DE ASERCIÓN
    # FIN DE MOCK


def test_SolicitudModel__cerrar_cierra_cursor_y_SolicitudModel__conexion():
    # INICIO DE MOCK: Crear cursor y conexión simulados
    cursor = Mock()
    conexion = Mock()

    # INICIO DE MOCK: Llamar _SolicitudModel__cerrar con mocks
    SolicitudModel._SolicitudModel__cerrar(conexion, cursor)

    # INICIO DE ASERCIÓN: Verificar que métodos close se llaman una vez
    cursor.close.assert_called_once()
    conexion.close.assert_called_once()
    # FIN DE ASERCIÓN


def test_limpia_texto_y_respeta_longitud_maxima():
    # INICIO DE ASERCIÓN: Verificar limpieza de texto y manejo de longitud máxima
    assert SolicitudModel._SolicitudModel__limpiar(" O'Neil <ok> ", 20) == 'ONeil ok'
    assert SolicitudModel._SolicitudModel__limpiar('abcdef', 3) == 'abc'
    # FIN DE ASERCIÓN


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
    # INICIO DE ASERCIÓN: Verificar que _SolicitudModel__formatear_fecha maneja varios tipos de entrada
    assert SolicitudModel()._SolicitudModel__formatear_fecha(fecha) == esperada
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('fila', 'esperado'),
    [({'id_persona': 17}, 17), ((18,), 18), (None, None)],
)
def test_busca_persona_admite_filas_diccionario_y_tupla(fila, esperado):
    # INICIO DE MOCK: Crear cursor simulado con valor de retorno fetchone
    cursor = Mock()
    cursor.fetchone.return_value = fila

    # INICIO DE MOCK: Llamar _SolicitudModel__sql_buscar_persona con cursor simulado
    resultado = SolicitudModel()._SolicitudModel__sql_buscar_persona(cursor, '12345678')

    # INICIO DE ASERCIÓN: Verificar que resultado coincide con esperado y execute llamado una vez
    assert resultado == esperado
    cursor.execute.assert_called_once()
    # FIN DE ASERCIÓN


def test_inserta_persona_y_devuelve_id_siguiente():
    # INICIO DE MOCK: Crear cursor simulado con valor de retorno fetchone
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

    # INICIO DE MOCK: Llamar _SolicitudModel__sql_insertar_persona con cursor simulado
    resultado = SolicitudModel()._SolicitudModel__sql_insertar_persona(cursor, datos)

    # INICIO DE ASERCIÓN: Verificar ID devuelto y llamadas execute
    assert resultado == 9
    assert cursor.execute.call_count == 2
    assert cursor.execute.call_args_list[1].args[1][1] == 12345678
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('tipo', 'tabla'),
    [
        ('Particular', 'particular'),
        ('Comunidad', 'comunidad'),
        ('Institucion', 'institucion'),
    ],
)
def test_inserta_subtipo_segun_categoria(tipo, tabla):
    # INICIO DE MOCK: Crear cursor simulado con valor de retorno fetchone
    cursor = Mock()
    cursor.fetchone.return_value = {'siguiente_id': 4}
    datos = _datos_solicitante(tipo)
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud(tipo)
    solicitud.set_solicitante_data(datos)

    # INICIO DE MOCK: Llamar _SolicitudModel__sql_insertar_subtipo con cursor simulado
    solicitud._SolicitudModel__sql_insertar_subtipo(cursor, 12, solicitud._SolicitudModel__solicitante_data)

    # INICIO DE ASERCIÓN: Verificar llamadas execute y nombre de tabla en consulta
    assert cursor.execute.call_count == 2
    assert tabla in cursor.execute.call_args_list[1].args[0]
    assert cursor.execute.call_args_list[1].args[1][-1] == 12
    # FIN DE ASERCIÓN


def test_crea_prioridad_pendiente_y_devuelve_id():
    # INICIO DE MOCK: Crear cursor simulado con lastrowid
    cursor = Mock()
    cursor.lastrowid = 21
    solicitud = SolicitudModel()
    solicitud.set_fecha('2026-11-12 10:30:00')

    # INICIO DE MOCK: Llamar _SolicitudModel__sql_crear_prioridad_pendiente con cursor simulado
    resultado = solicitud._SolicitudModel__sql_crear_prioridad_pendiente(cursor)

    # INICIO DE ASERCIÓN: Verificar ID devuelto y llamada execute con estado pendiente
    assert resultado == 21
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1][1] == 'pendiente'
    # FIN DE ASERCIÓN


def test_asegura_columna_problematica_ampliando_esquema_antiguo():
    SolicitudModel._SolicitudModel__columna_problematica_verificada = False
    # INICIO DE MOCK: Crear conexión y cursor simulados
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = {'Type': 'varchar(255)'}

    try:
        # INICIO DE MOCK: Llamar _SolicitudModel__asegurar_columna_problematica con conexión simulada
        SolicitudModel._SolicitudModel__asegurar_columna_problematica(conexion)
    finally:
        SolicitudModel._SolicitudModel__columna_problematica_verificada = False

    # INICIO DE ASERCIÓN: Verificar ALTER TABLE ejecutado y commit/close llamados
    assert any('ALTER TABLE solicitudes' in call.args[0] for call in cursor.execute.call_args_list)
    conexion.commit.assert_called_once()
    cursor.close.assert_called_once()
    # FIN DE ASERCIÓN


def test_guardar_retorna_false_si_faltan_datos_obligatorios():
    # INICIO DE ASERCIÓN: Verificar que guardar devuelve False cuando faltan datos requeridos
    assert SolicitudModel().guardar() is False
    # FIN DE ASERCIÓN


def test_guardar_registra_solicitud_y_SolicitudModel__confirma_transaccion():
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud('Comunidad')
    solicitud.set_problematica('La vía requiere reparación urgente')
    solicitud.set_fecha('2026-11-12 10:30:00')
    solicitud._SolicitudModel__solicitante_data = {'cedula_persona': '12345678'}
    # INICIO DE MOCK: Crear conexión y cursor simulados
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.lastrowid = 73

    # INICIO DE MOCK: Parchear múltiples métodos para prueba de guardar
    with (
        patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion),
        patch.object(SolicitudModel, '_SolicitudModel__asegurar_columna_problematica'),
        patch.object(solicitud, '_SolicitudModel__sql_buscar_persona', return_value=18),
        patch.object(solicitud, '_SolicitudModel__sql_crear_prioridad_pendiente', return_value=24),
    ):
        # INICIO DE MOCK: Llamar guardar con métodos parcheados
        resultado = solicitud.guardar()

    # INICIO DE ASERCIÓN: Verificar ID devuelto, ID de solicitud establecido, commit y execute llamados
    assert resultado == 73
    assert solicitud.get_id() == 73
    conexion.commit.assert_called_once()
    cursor.execute.assert_called_once()
    # FIN DE ASERCIÓN


def test_actualizar_retorna_false_sin_identificador():
    # INICIO DE ASERCIÓN: Verificar que actualizar devuelve False cuando no hay ID
    assert SolicitudModel().actualizar() is False
    # FIN DE ASERCIÓN


def test_actualizar_modifica_campos_y_SolicitudModel__confirma():
    solicitud = SolicitudModel(7)
    solicitud.set_estatus_solicitud('Completada')
    solicitud.set_problematica('La vía requiere reparación urgente')
    # INICIO DE MOCK: Crear conexión simulada con rowcount
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    # INICIO DE MOCK: Parchear _SolicitudModel__con y _SolicitudModel__asegurar_columna_problematica
    with (
        patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion),
        patch.object(SolicitudModel, '_SolicitudModel__asegurar_columna_problematica'),
    ):
        # INICIO DE MOCK: Llamar actualizar con métodos parcheados
        assert solicitud.actualizar() is True

    # INICIO DE ASERCIÓN: Verificar que commit se llama una vez
    conexion.commit.assert_called_once()
    # FIN DE ASERCIÓN


def test_actualizar_estatus_ejecuta_update():
    # INICIO DE MOCK: Crear conexión simulada con rowcount
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    # INICIO DE MOCK: Parchear _SolicitudModel__con para actualizar_estatus
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar actualizar_estatus con conexión parcheada
        resultado = SolicitudModel.actualizar_estatus(5, 'En Proceso')

    # INICIO DE ASERCIÓN: Verificar que resultado es True y commit llamado
    assert resultado is True
    conexion.commit.assert_called_once()
    # FIN DE ASERCIÓN


def test_eliminar_retorna_false_sin_identificador():
    # INICIO DE ASERCIÓN: Verificar que eliminar devuelve False cuando no hay ID
    assert SolicitudModel().eliminar() is False
    # FIN DE ASERCIÓN


def test_eliminar_borra_registro_existente():
    solicitud = SolicitudModel(5)
    # INICIO DE MOCK: Crear conexión simulada con rowcount
    conexion = Mock()
    conexion.cursor.return_value.rowcount = 1

    # INICIO DE MOCK: Parchear _SolicitudModel__con para eliminar
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar eliminar con conexión parcheada
        resultado = solicitud.eliminar()

    # INICIO DE ASERCIÓN: Verificar que resultado es True y commit llamado
    assert resultado is True
    conexion.commit.assert_called_once()
    # FIN DE ASERCIÓN


def test_obtener_todas_formatea_fechas():
    # INICIO DE MOCK: Crear conexión y cursor simulados con valor de retorno fetchall
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': datetime(2026, 11, 12, 10, 30)}]

    # INICIO DE MOCK: Parchear _SolicitudModel__con para obtener_todas
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_todas con conexión parcheada
        resultado = SolicitudModel.obtener_todas()

    # INICIO DE ASERCIÓN: Verificar que fecha_formateada coincide con formato esperado
    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()
    # FIN DE ASERCIÓN


def test_buscar_por_id_SolicitudModel__consulta_y_formatea_fecha():
    # INICIO DE MOCK: Crear conexión y cursor simulados con valor de retorno fetchone
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchone.return_value = {
        'id_solicitudes': 8,
        'fecha': '2026-11-12 10:30:00',
    }

    # INICIO DE MOCK: Parchear _SolicitudModel__con para buscar_por_id
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar buscar_por_id con conexión parcheada
        resultado = SolicitudModel.buscar_por_id(8)

    # INICIO DE ASERCIÓN: Verificar que ID y fecha formateada coinciden con esperado
    assert resultado['id_solicitudes'] == 8
    assert resultado['fecha_formateada'] == _fecha_formateada_esperada()
    cursor.execute.assert_called_once()
    # FIN DE ASERCIÓN


@pytest.mark.parametrize(
    ('metodo', 'fila', 'esperado'),
    [
        ('obtener_estadisticas', {'estatus_solicitud': 'Pendiente', 'total': 3}, {'Pendiente': 3}),
        ('obtener_estadisticas_por_tipo', {'tipo_solicitud': 'Comunidad', 'total': 2}, {'Comunidad': 2}),
    ],
)
def test_obtiene_estadisticas_agrupadas(metodo, fila, esperado):
    # INICIO DE MOCK: Crear conexión simulada con valor de retorno fetchall
    conexion = Mock()
    conexion.cursor.return_value.fetchall.return_value = [fila]

    # INICIO DE MOCK: Parchear _SolicitudModel__con para métodos de estadísticas
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar método de estadísticas con conexión parcheada
        resultado = getattr(SolicitudModel, metodo)()

    # INICIO DE ASERCIÓN: Verificar que resultado coincide con diccionario esperado
    assert resultado == esperado
    # FIN DE ASERCIÓN


def test_obtener_estadisticas_por_parroquia_devuelve_filas():
    # INICIO DE MOCK: Crear conexión simulada con valor de retorno fetchall
    conexion = Mock()
    filas = [{'parroquia': 'Concepcion', 'total': 4}]
    conexion.cursor.return_value.fetchall.return_value = filas

    # INICIO DE MOCK: Parchear _SolicitudModel__con para obtener_estadisticas_por_parroquia
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_estadisticas_por_parroquia con conexión parcheada
        assert SolicitudModel.obtener_estadisticas_por_parroquia() == filas
        # FIN DE ASERCIÓN: Resultado verificado en assert anterior


def test_obtener_solicitudes_priorizadas_aplica_limite_y_formatea_fecha():
    # INICIO DE MOCK: Crear conexión y cursor simulados con valor de retorno fetchall
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': '2026-11-12 10:30:00'}]

    # INICIO DE MOCK: Parchear _SolicitudModel__con para obtener_solicitudes_priorizadas
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_solicitudes_priorizadas con conexión parcheada
        resultado = SolicitudModel.obtener_solicitudes_priorizadas(5)

    # INICIO DE ASERCIÓN: Verificar fecha formateada y parámetro límite pasado correctamente
    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()
    assert cursor.execute.call_args.args[1] == (5,)
    # FIN DE ASERCIÓN


def test_obtener_solicitudes_pendientes_filtra_y_formatea_fecha():
    # INICIO DE MOCK: Crear conexión y cursor simulados con valor de retorno fetchall
    conexion = Mock()
    cursor = conexion.cursor.return_value
    cursor.fetchall.return_value = [{'fecha': '2026-11-12 10:30:00'}]

    # INICIO DE MOCK: Parchear _SolicitudModel__con para obtener_solicitudes_pendientes
    with patch.object(SolicitudModel, '_SolicitudModel__con', return_value=conexion):
        # INICIO DE MOCK: Llamar obtener_solicitudes_pendientes con conexión parcheada
        resultado = SolicitudModel.obtener_solicitudes_pendientes()

    # INICIO DE ASERCIÓN: Verificar fecha formateada y filtro Pendiente en consulta
    assert resultado[0]['fecha_formateada'] == _fecha_formateada_esperada()
    assert 'estatus_solicitud = \'Pendiente\'' in cursor.execute.call_args.args[0]
    # FIN DE ASERCIÓN
