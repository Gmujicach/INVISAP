import io
from unittest.mock import patch

import pytest
from PIL import Image

from models.model_evidencia import EvidenciaModel


def test_validadores_de_archivo_y_url():
    evidencia = EvidenciaModel.__new__(EvidenciaModel)

    assert evidencia._validar_nombre_archivo('obra_01.jpg') is True
    assert evidencia._validar_url('uploads/obra_01.jpg') is True


def test_url_no_permite_traversal_de_directorios():
    evidencia = EvidenciaModel.__new__(EvidenciaModel)

    assert evidencia._validar_url('../secreto.jpg') is False


def _evidencia():
    e = EvidenciaModel.__new__(EvidenciaModel)
    e._EvidenciaModel__id_evidencia = None
    e._EvidenciaModel__archivos = []
    e._EvidenciaModel__etapas = []
    e._EvidenciaModel__estado = 1
    e._EvidenciaModel__upload_folder = '.'
    return e


class _Cursor:
    def __init__(self, rows=None, rowcount=1):
        self.rows = iter(rows or [])
        self.calls = []
        self.rowcount = rowcount
        self.lastrowid = 6
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def fetchone(self):
        return next(self.rows, None)

    def fetchall(self):
        return list(self.rows)

    def close(self):
        self.closed = True


class _Connection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = self.rollbacks = 0
        self.closed = False

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def test_accesores_etapas_y_estado_validan_completamente():
    e = _evidencia()
    e.set_id_evidencia(3)
    e.set_estado(0)
    assert e.get_id_evidencia() == 3
    with pytest.raises(ValueError):
        e.set_id_evidencia(0)
    with pytest.raises(ValueError):
        e.set_estado(2)
    assert e._EvidenciaModel__validar_etapas_regex([' ANTES ', 'durante'])
    for bad in ([], 'antes', ['inicio'], [None]):
        with pytest.raises(ValueError):
            e._EvidenciaModel__validar_etapas_regex(bad)
    assert not e._validar_nombre_archivo('../bad?.jpg')
    assert not e._validar_url('123456789\x00')


def test_constructor_inicializa_repositorio_sin_conectar_bd():
    with patch.object(EvidenciaModel, '_EvidenciaModel__asegurar_tabla_evidencia') as asegurar, \
            patch('models.model_evidencia.os.path.exists', return_value=True):
        evidencia = EvidenciaModel()
    asegurar.assert_called_once_with()
    assert evidencia.get_id_evidencia() is None
    assert evidencia._EvidenciaModel__archivos == []
    assert evidencia._EvidenciaModel__etapas == []


def test_extrae_etapas_por_campo_lista_y_fallback():
    class Form:
        def __init__(self, data=None, stages=None):
            self.data, self.stages = data or {}, stages or []

        def get(self, key):
            return self.data.get(key)

        def getlist(self, key):
            return self.stages

    e = _evidencia()
    assert e._EvidenciaModel__extraer_etapas(
        Form({'etapa-foto-0': ' DURANTE '}), 2
    ) == ['durante', 'antes']
    assert e._EvidenciaModel__extraer_etapas(Form(stages=['despues', 'invalid']), 2) == ['despues', 'antes']
    with pytest.raises(ValueError):
        e._EvidenciaModel__extraer_etapas(Form({'etapa-foto-0': 'inicio'}), 1)


def test_compresion_de_imagen_convierte_a_jpeg_y_rechaza_archivo_vacio(tmp_path):
    class Upload:
        filename = 'Árbol verde.png'

        def read(self):
            stream = io.BytesIO()
            Image.new('RGBA', (8, 6), (255, 0, 0, 100)).save(stream, format='PNG')
            return stream.getvalue()

    e = _evidencia()
    e._EvidenciaModel__upload_folder = str(tmp_path)
    url = e._EvidenciaModel__comprimir_y_guardar_imagen(Upload())
    assert url.startswith('uploads/evidencias/') and url.endswith('_Arbol_verde.jpg')
    assert len(list(tmp_path.iterdir())) == 1

    class Empty(Upload):
        filename = 'vacio.png'

        def read(self):
            return b''

    with pytest.raises(ValueError, match='está vacío'):
        e._EvidenciaModel__comprimir_y_guardar_imagen(Empty())


def test_registrar_evidencias_valida_limites_y_delega_con_etapas():
    e = _evidencia()
    files = [object(), object(), object()]
    with patch.object(e, '_EvidenciaModel__guardar_evidencias_db', return_value=[1, 2, 3]) as guardar:
        assert e.registrar_evidencias(files, ['antes', 'durante', 'despues']) == [1, 2, 3]
    assert e._EvidenciaModel__archivos == files
    assert guardar.call_count == 1
    for files_arg, etapas, message in [
        ([], ['antes'], 'archivos'),
        (files, [], 'etapas'),
        (files[:2], ['antes'], 'Inconsistencia'),
        (files[:2], ['antes', 'durante'], 'entre 3 y 50'),
        (files, ['mal', 'antes', 'despues'], 'Etapa'),
    ]:
        with pytest.raises(ValueError, match=message):
            e.registrar_evidencias(files_arg, etapas)


def test_metodos_db_basicos_evidencia_parametrizan_y_cierra_recursos():
    e = _evidencia()
    cursor = _Cursor([{'id_evidencia': 4}, (2,), (4,)], rowcount=1)
    cursor.fetchall = lambda: [{'id_evidencia': 5}]
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn):
        assert e._EvidenciaModel__eliminar_logico_db(4)
        assert e._EvidenciaModel__obtener_evidencia_por_id_db(4) == {'id_evidencia': 4}
        assert e._EvidenciaModel__obtener_todas_evidencias_db(2, 10) == [{'id_evidencia': 5}]
        assert e._EvidenciaModel__contar_evidencias_db() == 2
        assert e._EvidenciaModel__validar_evidencia_activa_db(4)
    assert cursor.calls[0][1] == (4,)
    assert cursor.calls[1][1] == (4,)
    assert cursor.calls[2][1] == [10, 10]
    assert conn.closed and cursor.closed


def test_publicas_evidencia_delegan_y_actualizacion_valida_antes_de_escribir():
    e = _evidencia()
    with patch.object(e, '_EvidenciaModel__validar_evidencia_activa_db', return_value=False):
        with pytest.raises(ValueError, match='no existe'):
            e.actualizar_evidencia(4, [object()], ['antes'])
    with patch.object(e, '_EvidenciaModel__validar_evidencia_activa_db', return_value=True), \
            patch.object(e, '_EvidenciaModel__actualizar_evidencias_db', return_value=True) as update:
        assert e.actualizar_evidencia(4, [object()], ['DURANTE']) is True
        update.assert_called_once_with(4)
    with patch.object(e, '_EvidenciaModel__eliminar_logico_db', return_value=True), \
            patch.object(e, '_EvidenciaModel__obtener_evidencia_por_id_db', return_value={'id': 4}), \
            patch.object(e, '_EvidenciaModel__obtener_todas_evidencias_db', return_value=[4]), \
            patch.object(e, '_EvidenciaModel__contar_evidencias_db', return_value=8), \
            patch.object(e, '_EvidenciaModel__validar_evidencia_activa_db', return_value=True):
        assert e.eliminar_evidencia(4)
        assert e.obtener_evidencia_por_id(4) == {'id': 4}
        assert e.obtener_todas_evidencias(1, 5) == [4]
        assert e.contar_evidencias() == 8
        assert e.validar_evidencia_activa(4)


def test_guardar_evidencias_db_inserta_todas_las_fotos_y_confirma():
    class Upload:
        filename = 'obra.jpg'

    e = _evidencia()
    e._EvidenciaModel__archivos = [Upload(), Upload(), Upload()]
    e._EvidenciaModel__etapas = ['antes', 'durante', 'despues']
    cursor = _Cursor([(1,), (2,), (3,)])
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn), \
            patch.object(e, '_EvidenciaModel__comprimir_y_guardar_imagen',
                         return_value='uploads/evidencias/obra.jpg'):
        assert e._EvidenciaModel__guardar_evidencias_db() == [6, 6, 6]
    inserts = [p for sql, p in cursor.calls if sql.lstrip().startswith('INSERT')]
    assert [p[0] for p in inserts] == [1, 2, 3]
    assert [p[-1] for p in inserts] == ['antes', 'durante', 'despues']
    assert conn.commits == 1 and conn.closed and cursor.closed


def test_actualizar_evidencias_db_consulta_e_actualiza_la_foto():
    class Upload:
        filename = 'nueva.jpg'

    e = _evidencia()
    e._EvidenciaModel__archivos = [Upload()]
    e._EvidenciaModel__etapas = ['durante']
    cursor = _Cursor([{'url_archivos': 'uploads/evidencias/anterior.jpg'}])
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn), \
            patch('models.model_evidencia.os.path.exists', return_value=False), \
            patch.object(e, '_EvidenciaModel__comprimir_y_guardar_imagen',
                         return_value='uploads/evidencias/nueva.jpg'):
        assert e._EvidenciaModel__actualizar_evidencias_db(8) is True
    assert cursor.calls[0][1] == (8,)
    assert cursor.calls[1][1] == ('nueva.jpg', 'uploads/evidencias/nueva.jpg', 'durante', 8)
    assert conn.commits == 1 and conn.closed and cursor.closed


def test_asegurar_tabla_agrega_columnas_sin_usar_db_real():
    e = _evidencia()
    cursor = _Cursor()
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn):
        e._EvidenciaModel__asegurar_tabla_evidencia()
    alters = [sql for sql, _ in cursor.calls if sql.startswith('ALTER TABLE')]
    assert any('ADD COLUMN estado' in sql for sql in alters)
    assert any('ADD COLUMN etapa' in sql for sql in alters)
    assert conn.commits == 2 and conn.closed and cursor.closed


def test_guardar_evidencias_db_reintenta_id_duplicado_y_confirma_luego():
    class Duplicate(Exception):
        errno = 1062

    class RetryCursor(_Cursor):
        def __init__(self):
            super().__init__([(1,), (2,), (3,), (4,)])
            self.insert_count = 0

        def execute(self, sql, params=None):
            super().execute(sql, params)
            if sql.lstrip().startswith('INSERT'):
                self.insert_count += 1
                if self.insert_count == 1:
                    raise Duplicate()

    class Upload:
        filename = 'obra.jpg'

    e = _evidencia()
    e._EvidenciaModel__archivos = [Upload(), Upload(), Upload()]
    e._EvidenciaModel__etapas = ['antes', 'durante', 'despues']
    cursor = RetryCursor()
    conn = _Connection(cursor)
    with patch.object(e, 'obtener_conexion', return_value=conn), \
            patch.object(e, '_EvidenciaModel__comprimir_y_guardar_imagen',
                         return_value='uploads/evidencias/obra.jpg'):
        assert e._EvidenciaModel__guardar_evidencias_db() == [6, 6, 6]
    assert conn.rollbacks == 1 and conn.commits == 1
    assert [params[0] for sql, params in cursor.calls if sql.lstrip().startswith('INSERT')] == [1, 2, 3, 4]
    assert conn.closed and cursor.closed
