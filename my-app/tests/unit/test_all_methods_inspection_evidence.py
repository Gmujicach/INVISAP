"""Focused behavior tests for active methods in inspection/evidence/report/publication models."""

import io
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from models.model_inspeccion import InspeccionModel
from models.model_evidencia import EvidenciaModel
from models.model_informe_avance import InformeAvanceModel
from models.model_publicacion import PublicacionModel as PublicationRepository
from models.model_publicaciones import PublicacionModel as LegacyPublicationRepository


class Cursor:
    def __init__(self, one=None, many=None, rowcount=1, lastrowid=23, error=None):
        self.one = one
        self.many = many or []
        self.rowcount = rowcount
        self.lastrowid = lastrowid
        self.error = error
        self.calls = []
        self.closed = False

    def execute(self, sql, params=None):
        self.calls.append((sql, params))
        if self.error:
            error, self.error = self.error, None
            raise error

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.many

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, cursor=None):
        self.cur = cursor or Cursor()
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def cursor(self, **kwargs):
        return self.cur

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True


def raw(cls):
    return cls.__new__(cls)


def test_inspeccion_constructor_initializes_state_and_runs_migration():
    with patch.object(InspeccionModel, "_InspeccionModel__asegurar_tabla_inspeccion") as ensure:
        model = InspeccionModel()
    ensure.assert_called_once_with()
    assert model.get_id_inspeccion() is None
    assert model.get_estado() == 1


def test_inspeccion_connection_fallbacks_and_error_paths():
    model = raw(InspeccionModel)
    with patch.object(model, "obtener_conexion", side_effect=RuntimeError("main")), patch.object(
        model, "obtener_conexion_seguridad_segura", return_value="fallback"
    ):
        assert model._conectar() == "fallback"
    with patch.object(model, "obtener_conexion", return_value=None), patch.object(
        model, "obtener_conexion_seguridad_segura", side_effect=RuntimeError("alternate")
    ):
        assert model._conectar() is None


def test_inspeccion_initial_schema_checks_and_column_variants():
    model = raw(InspeccionModel)
    cur = Cursor(one=None)
    conn = Connection(cur)
    with patch.object(model, "_conectar", return_value=conn):
        model._InspeccionModel__asegurar_tabla_inspeccion()
    assert any("ALTER TABLE inspeccion ADD COLUMN estado" in sql for sql, _ in cur.calls)
    assert conn.closed and cur.closed and conn.commits >= 1

    for semaforo, expected in ((True, "obra_semaforo_id_semaforo"), (False, "obra_estado")):
        cur = Cursor(one=("found",) if semaforo else None)
        assert InspeccionModel._InspeccionModel__get_obra_fk_config(cur)["semaforo_col"] == expected


def test_inspeccion_ensure_columns_selects_old_and_new_fk_names():
    model = raw(InspeccionModel)
    for semaforo in (True, False):
        cur = Cursor()
        cur.fetchone = MagicMock(side_effect=[("present",) if semaforo else None] + [None] * 8)
        model._InspeccionModel__asegurar_columnas_obra_inspeccion(cur)
        added = " ".join(sql for sql, _ in cur.calls if sql.startswith("ALTER TABLE"))
        assert ("obra_semaforo_id_semaforo1" in added) == semaforo
        assert ("obra_estado1" in added) != semaforo
        assert "evidencias_adicionales" in added


def test_inspeccion_cleanup_cedula_removes_only_valid_named_trigger_and_columns():
    model = raw(InspeccionModel)
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[("index",), ("column",)])
    cur.fetchall = MagicMock(return_value=[("trigger_1",), ("bad;trigger",)])
    conn = Connection(cur)
    model._InspeccionModel__limpiar_cedula_inspeccion(cur, conn)
    sqls = [sql for sql, _ in cur.calls]
    assert "DROP TRIGGER IF EXISTS `trigger_1`" in sqls
    assert not any("bad;trigger" in sql for sql in sqls)
    assert any("DROP INDEX cedula_UNIQUE" in sql for sql in sqls)
    assert any("DROP COLUMN cedula" in sql for sql in sqls)
    assert conn.commits == 1


def test_inspeccion_accessors_validators_and_setter_boundaries():
    with patch.object(InspeccionModel, "_InspeccionModel__asegurar_tabla_inspeccion"):
        model = InspeccionModel()
    assert model.get_id_inspeccion() is None
    for setter, getter, val in [
        (model.set_id_inspeccion, model.get_id_inspeccion, 1),
        (model.set_inspector, model.get_inspector, "9"),
        (model.set_fecha_inspeccion, model.get_fecha_inspeccion, "2024-02-29"),
        (model.set_tipo_inspeccion, model.get_tipo_inspeccion, "Final"),
        (model.set_observaciones, model.get_observaciones, "  trabajo correcto  "),
        (model.set_obra_id_obra, model.get_obra_id_obra, 4),
        (model.set_evidencia_id_evidencia, model.get_evidencia_id_evidencia, 5),
        (model.set_evidencias_adicionales, model.get_evidencias_adicionales, 0),
        (model.set_estado, model.get_estado, 0),
    ]:
        setter(val)
        assert getter() is not None
    assert model.get_inspector() == 9
    assert model.get_observaciones() == "trabajo correcto"
    assert model.get_evidencias_adicionales() == ""
    for action, value in [
        (model.set_id_inspeccion, 0), (model.set_obra_id_obra, -1),
        (model.set_evidencia_id_evidencia, "5"), (model.set_inspector, "x"),
        (model.set_fecha_inspeccion, "2024-2-01"), (model.set_tipo_inspeccion, "otro"),
        (model.set_observaciones, "no"), (model.set_estado, 2),
    ]:
        with pytest.raises(ValueError):
            action(value)
    assert model._validar_inspector(None) is False
    assert model._validar_fecha(None) is False
    assert model._validar_observaciones(" " * 8) is False


def test_inspeccion_next_id_and_fk_mapping():
    cur = Cursor(one={"siguiente": "17"})
    conn = Connection(cur)
    with patch.object(conn, "cursor", return_value=cur):
        assert InspeccionModel._InspeccionModel__obtener_siguiente_id_inspeccion(conn) == 17
    assert cur.closed
    assert InspeccionModel._InspeccionModel__mapear_tipo_a_etapa("Final") == "despues"
    assert InspeccionModel._InspeccionModel__mapear_tipo_a_etapa("Extraordinaria") == "durante"
    assert InspeccionModel._InspeccionModel__mapear_tipo_a_etapa("other") == "antes"


def test_inspeccion_column_validation_and_private_lookups_use_parameters_and_cleanup():
    model = raw(InspeccionModel)
    with pytest.raises(ValueError):
        model._InspeccionModel__columna_existe("users", "x")
    cur = Cursor(one=("x",))
    conn = Connection(cur)
    with patch.object(model, "_conectar", return_value=conn):
        assert model._InspeccionModel__columna_existe("obra", "estado")
    assert cur.calls[-1] == ("SHOW COLUMNS FROM obra LIKE %s", ("estado",))
    assert conn.closed and cur.closed

    for method, params, response in [
        ("_InspeccionModel__validar_obra_existe_db", (12,), (12,)),
        ("_InspeccionModel__validar_evidencia_existe_db", (13,), (13,)),
        ("_InspeccionModel__buscar_evidencia_por_id_db", (13,), {"id_evidencia": 13}),
    ]:
        cur = Cursor(one=response)
        conn = Connection(cur)
        with patch.object(model, "_conectar", return_value=conn):
            assert getattr(model, method)(*params) == (response is not None if "validar_" in method else response)
        assert cur.calls[-1][1] == params
        assert cur.closed and conn.closed


def test_inspeccion_listing_and_lookup_paths_include_fk_schema_and_extra_evidences():
    model = raw(InspeccionModel)
    model.set_id_inspeccion(3)
    cur = Cursor(many=[{"id_inspeccion": 3, "evidencias_adicionales": "1, 2,bad"}])
    conn = Connection(cur)
    with patch.object(model, "_conectar", return_value=conn), patch.object(
        model, "_InspeccionModel__columna_existe", return_value=True
    ):
        assert model._InspeccionModel__obtener_todas_inspecciones_db() == cur.many
    assert "i.estado = 1" in cur.calls[0][0]
    assert conn.closed and cur.closed

    row_cur = Cursor(one={"id_inspeccion": 3, "evidencias_adicionales": "1, 2,bad"}, many=[{"id_evidencia": 1}])
    row_conn = Connection(row_cur)
    with patch.object(model, "_conectar", return_value=row_conn), patch.object(
        model, "_InspeccionModel__columna_existe", return_value=True
    ):
        result = model._InspeccionModel__obtener_inspeccion_por_id_db()
    assert result["evidencias_adicionales_list"] == [{"id_evidencia": 1}]
    assert row_cur.calls[-1][1] == [1, 2]
    assert row_conn.closed and row_cur.closed

    for ids, expected in [("", []), ("bad,,", []), ("2,4", None)]:
        target = {"evidencias_adicionales": ids}
        cur = Cursor(many=[{"id_evidencia": 2}])
        InspeccionModel._InspeccionModel__cargar_evidencias_adicionales(target, cur)
        if expected is not None:
            assert target["evidencias_adicionales_list"] == expected
        else:
            assert target["evidencias_adicionales_list"] == cur.many


def test_inspeccion_active_delete_catalog_and_public_delegations():
    model = raw(InspeccionModel)
    model.set_id_inspeccion(8)
    cur = Cursor(one=(8,), rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "_conectar", return_value=conn), patch.object(
        model, "_InspeccionModel__columna_existe", return_value=True
    ):
        assert model._InspeccionModel__validar_inspeccion_activa_db() is True
        assert model._InspeccionModel__eliminar_logico_db() is True
    assert cur.calls[-1] == ("UPDATE inspeccion SET estado = 0 WHERE id_inspeccion = %s", (8,))

    with patch.object(model, "_InspeccionModel__validar_inspeccion_activa_db", return_value=True), patch.object(
        model, "_InspeccionModel__eliminar_logico_db", return_value=True
    ):
        assert model.eliminar_inspeccion(8) is True
    with patch.object(model, "_InspeccionModel__validar_inspeccion_activa_db", return_value=False):
        with pytest.raises(ValueError):
            model.eliminar_inspeccion(8)
    assert model.obtener_catalogo_tipos_inspeccion() == sorted(model._TIPOS_INSPECCION_VALIDOS)
    with patch.object(model, "_InspeccionModel__obtener_inspeccion_por_id_db", return_value={"id": 8}):
        assert model.obtener_inspeccion_por_id(8) == {"id": 8}
        assert model.obtener_inspeccion_por_id("bad") is None
    with patch.object(model, "_InspeccionModel__validar_inspeccion_activa_db", return_value=True):
        assert model.validar_inspeccion_activa(8)
        assert model.validar_inspeccion_activa("bad") is False
    for public, private, response in [
        ("obtener_todas_inspecciones", "_InspeccionModel__obtener_todas_inspecciones_db", [1]),
        ("obtener_obras", "_InspeccionModel__obtener_obras_db", [2]),
        ("obtener_evidencias", "_InspeccionModel__obtener_evidencias_db", [3]),
        ("obtener_inspectores", "_InspeccionModel__obtener_inspectores_db", [4]),
    ]:
        with patch.object(model, private, return_value=response):
            assert getattr(model, public)() == response
    for public, private in [("obra_existe", "_InspeccionModel__validar_obra_existe_db"),
                            ("evidencia_existe", "_InspeccionModel__validar_evidencia_existe_db")]:
        with patch.object(model, private, return_value=True):
            assert getattr(model, public)(2)


def test_inspeccion_data_writes_validate_relations_and_cleanup():
    model = raw(InspeccionModel)
    conn = Connection(Cursor(lastrowid=7))
    model._InspeccionModel__id_inspeccion = 9
    model._InspeccionModel__inspector = 2
    model._InspeccionModel__fecha_inspeccion = "2024-01-02"
    model._InspeccionModel__tipo_inspeccion = "Final"
    model._InspeccionModel__observaciones = "valid observation"
    model._InspeccionModel__obra_id_obra = 3
    model._InspeccionModel__evidencia_id_evidencia = 4
    model._InspeccionModel__evidencias_adicionales = "5"
    model._InspeccionModel__obtener_siguiente_id_inspeccion = MagicMock(return_value=6)
    with patch.object(model, "_conectar", return_value=conn), patch.object(
        model, "_InspeccionModel__limpiar_cedula_inspeccion"
    ), patch.object(model, "_InspeccionModel__columna_existe", return_value=False), patch.object(
        model, "_InspeccionModel__buscar_obra_por_id_db", return_value={"estado": 8, "contratacion_id_contratacion": 9, "gestionar_proyectos_codigo_proyecto": "P1"}
    ), patch.object(model, "_InspeccionModel__buscar_evidencia_por_id_db", return_value={"id_evidencia": 4}), patch.object(
        model, "_InspeccionModel__get_obra_fk_config", return_value={"semaforo_col": "obra_estado", "semaforo1_col": "obra_estado1"}
    ):
        assert model._InspeccionModel__guardar_inspeccion_db() == 7
    assert conn.cur.calls[-1][1][-1] == "5"
    assert conn.commits == 1 and conn.closed and conn.cur.closed

    for no_obra, no_evid in ((True, False), (False, True)):
        conn = Connection(Cursor())
        with patch.object(model, "_conectar", return_value=conn), patch.object(
            model, "_InspeccionModel__limpiar_cedula_inspeccion"
        ), patch.object(model, "_InspeccionModel__columna_existe", return_value=False), patch.object(
            model, "_InspeccionModel__buscar_obra_por_id_db", return_value=None if no_obra else {"estado": 1}
        ), patch.object(model, "_InspeccionModel__buscar_evidencia_por_id_db", return_value=None if no_evid else {"id": 4}):
            with pytest.raises(ValueError):
                model._InspeccionModel__guardar_inspeccion_db()
        assert conn.rollbacks == 1 and conn.closed

    with patch.object(model, "_InspeccionModel__validar_inspeccion_activa_db", return_value=True), patch.object(
        model, "_InspeccionModel__actualizar_inspeccion_db", return_value=True
    ):
        payload = {"id_inspeccion": 9, "inspector": "2", "fecha_inspeccion": "2024-01-02",
                   "tipo_inspeccion": "Final", "observaciones": "valid observation",
                   "obra_id_obra": "3", "evidencia_id_evidencia": "4", "evidencias_adicionales": "5"}
        assert model.actualizar_inspeccion(payload) is True
    with patch.object(model, "_InspeccionModel__guardar_inspeccion_db", return_value=7):
        assert model.registrar_inspeccion(payload) == 7
    with pytest.raises(ValueError):
        model.registrar_inspeccion({**payload, "inspector": "bad"})


def test_inspeccion_update_database_binds_parameters_and_synchronizes_evidence():
    model = raw(InspeccionModel)
    model._InspeccionModel__id_inspeccion = 9
    model._InspeccionModel__inspector = 2
    model._InspeccionModel__fecha_inspeccion = "2024-01-02"
    model._InspeccionModel__tipo_inspeccion = "Final"
    model._InspeccionModel__observaciones = "valid observation"
    model._InspeccionModel__obra_id_obra = 3
    model._InspeccionModel__evidencia_id_evidencia = 4
    model._InspeccionModel__evidencias_adicionales = "5"
    cur = Cursor(rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "_conectar", return_value=conn), patch.object(
        model, "_InspeccionModel__limpiar_cedula_inspeccion"
    ), patch.object(
        model, "_InspeccionModel__buscar_obra_por_id_db",
        return_value={"estado": 8, "contratacion_id_contratacion": 9, "gestionar_proyectos_codigo_proyecto": "P-1"},
    ), patch.object(model, "_InspeccionModel__buscar_evidencia_por_id_db", return_value={"id_evidencia": 4}), patch.object(
        model, "_InspeccionModel__get_obra_fk_config",
        return_value={"semaforo_col": "obra_estado", "semaforo1_col": "obra_estado1"},
    ), patch.object(model, "_InspeccionModel__columna_existe", side_effect=[True, True]):
        assert model._InspeccionModel__actualizar_inspeccion_db() is True
    assert cur.calls[0][1][-3:] == (4, "5", 9)
    assert cur.calls[1] == (
        "UPDATE evidencia SET etapa = %s, fecha_registro = NOW() WHERE id_evidencia = %s AND estado = 1",
        ("despues", 4),
    )
    assert conn.commits == 1 and conn.closed and cur.closed


def test_inspeccion_related_select_methods_return_data_and_bind_ids():
    model = raw(InspeccionModel)
    for private, args, expected, first_sql in [
        ("_InspeccionModel__obtener_obras_db", (), [{"id_obra": 2}], "SHOW COLUMNS FROM obra"),
        ("_InspeccionModel__obtener_evidencias_db", (), [{"id_evidencia": 3}], "SELECT id_evidencia"),
        ("_InspeccionModel__obtener_inspectores_db", (), [{"id_empleados": 4}], "SELECT id_empleados"),
        ("_InspeccionModel__buscar_obra_por_id_db", (2,), {"id_obra": 2}, "SHOW COLUMNS FROM obra"),
    ]:
        cur = Cursor(many=expected if isinstance(expected, list) else [], one=None)
        if isinstance(expected, dict):
            cur.fetchone = MagicMock(side_effect=[None, expected])
        conn = Connection(cur)
        with patch.object(model, "_conectar", return_value=conn):
            result = getattr(model, private)(*args)
        assert result == expected
        assert first_sql in cur.calls[0][0]
        if args:
            assert cur.calls[-1][1] == args
        assert cur.closed and conn.closed

    conn = Connection(Cursor(one={"id_evidencia": 4}))
    with patch.object(model, "_conectar", return_value=conn):
        assert model._InspeccionModel__buscar_evidencia_por_id_db(4) == {"id_evidencia": 4}
    assert conn.cur.calls[0][1] == (4,)


def test_inspeccion_connectionless_query_and_schema_error_fallbacks():
    model = raw(InspeccionModel)
    with patch.object(model, "_conectar", return_value=None):
        assert model._InspeccionModel__obtener_todas_inspecciones_db() == []
        assert model._InspeccionModel__obtener_inspeccion_por_id_db() is None
        assert model._InspeccionModel__validar_inspeccion_activa_db() is False
        assert model._InspeccionModel__obtener_obras_db() == []
        assert model._InspeccionModel__obtener_evidencias_db() == []
        assert model._InspeccionModel__obtener_inspectores_db() == []
        assert model._InspeccionModel__buscar_obra_por_id_db(1) is None
        assert model._InspeccionModel__buscar_evidencia_por_id_db(1) is None


def test_evidencia_constructor_validation_and_form_stage_extraction():
    with patch.object(EvidenciaModel, "_EvidenciaModel__asegurar_tabla_evidencia"), patch(
        "models.model_evidencia.os.path.exists", return_value=True
    ):
        model = EvidenciaModel()
    assert model.get_id_evidencia() is None
    model.set_id_evidencia(2)
    assert model.get_id_evidencia() == 2
    for setter, value in ((model.set_id_evidencia, 0), (model.set_estado, 2)):
        with pytest.raises(ValueError):
            setter(value)
    model.set_estado(0)
    assert model._validar_nombre_archivo("a b.jpg")
    assert not model._validar_nombre_archivo("../bad.jpg")
    assert model._validar_url("uploads/a.jpg")
    for invalid in (None, "../secret.jpg", "uploads/\x00x.jpg"):
        assert not model._validar_url(invalid)
    assert EvidenciaModel._EvidenciaModel__validar_etapas_regex(model, [" ANTES ", "despues"])
    for stages in ([], "antes", ["bad"], [3]):
        with pytest.raises(ValueError):
            model._EvidenciaModel__validar_etapas_regex(stages)

    class Form(dict):
        def getlist(self, key):
            return self.get(key, [])

    assert model._EvidenciaModel__extraer_etapas(Form({"etapa-foto-0": " DURANTE "}), 2) == ["durante", "antes"]
    assert model._EvidenciaModel__extraer_etapas(Form({"etapas": ["despues", "bad"]}), 2) == ["despues", "antes"]
    with pytest.raises(ValueError):
        model._EvidenciaModel__extraer_etapas(Form({"etapa-foto-0": "bad"}), 1)


def test_evidencia_schema_migration_adds_missing_columns_and_closes_resources():
    model = raw(EvidenciaModel)
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[None, None])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        model._EvidenciaModel__asegurar_tabla_evidencia()
    added = [sql for sql, _ in cur.calls if sql.startswith("ALTER TABLE")]
    assert len(added) == 2 and "estado" in added[0] and "etapa" in added[1]
    assert conn.commits == 2 and conn.closed and cur.closed


def test_evidencia_compression_converts_modes_resizes_and_rejects_bad_input(tmp_path):
    model = raw(EvidenciaModel)
    model._EvidenciaModel__upload_folder = str(tmp_path)
    image = Image.new("RGBA", (2100, 1000), (255, 0, 0, 100))
    stream = io.BytesIO()
    image.save(stream, format="PNG")

    class Upload:
        filename = "  Árbol foto.png"
        def __init__(self, data):
            self.data = data
        def read(self):
            return self.data

    relative = model._EvidenciaModel__comprimir_y_guardar_imagen(Upload(stream.getvalue()))
    assert relative.startswith("uploads/evidencias/") and relative.endswith(".jpg")
    saved = next(tmp_path.glob("*.jpg"))
    with Image.open(saved) as result:
        assert result.mode == "RGB" and max(result.size) == 1920
    with pytest.raises(ValueError, match="vacío"):
        model._EvidenciaModel__comprimir_y_guardar_imagen(Upload(b""))
    with pytest.raises(ValueError, match="procesar"):
        model._EvidenciaModel__comprimir_y_guardar_imagen(Upload(b"not an image"))


def test_evidencia_db_reads_delete_and_validation_use_expected_sql_and_cleanup():
    model = raw(EvidenciaModel)
    for private, args, one, many, expected in [
        ("_EvidenciaModel__obtener_evidencia_por_id_db", (3,), {"id_evidencia": 3}, [], {"id_evidencia": 3}),
        ("_EvidenciaModel__obtener_todas_evidencias_db", (), None, [{"id": 1}], [{"id": 1}]),
    ]:
        cur = Cursor(one=one, many=many)
        conn = Connection(cur)
        with patch.object(model, "obtener_conexion", return_value=conn):
            actual = getattr(model, private)(*args)
        assert actual == expected and conn.closed and cur.closed
    cur = Cursor(one=(3,), rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._EvidenciaModel__validar_evidencia_activa_db(3)
        assert model._EvidenciaModel__contar_evidencias_db() == 3
        assert model._EvidenciaModel__eliminar_logico_db(3)
    assert cur.calls[0][1] == (3,)
    assert cur.calls[-1] == ("UPDATE evidencia SET estado = 0 WHERE id_evidencia = %s", (3,))
    assert conn.commits == 1 and conn.closed and cur.closed

    cur = Cursor(many=[1])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._EvidenciaModel__obtener_todas_evidencias_db(page=3, per_page=10) == [1]
    assert cur.calls[0][1] == [10, 20]


def test_evidencia_write_retry_update_validation_and_public_delegations():
    model = raw(EvidenciaModel)
    model._EvidenciaModel__archivos = []
    model._EvidenciaModel__etapas = []
    file = MagicMock(filename="photo.jpg")
    model._EvidenciaModel__archivos = [file] * 3
    model._EvidenciaModel__etapas = ["antes", "durante", "despues"]
    cursor = Cursor(lastrowid=12)
    cursor.fetchone = MagicMock(side_effect=[(1,), (1,), (2,), (3,)])
    conn = Connection(cursor)
    duplicate = Exception(1062)
    did_duplicate = [False]
    def execute_with_one_duplicate(sql, params=None):
        cursor.calls.append((sql, params))
        if sql.startswith("INSERT") and not did_duplicate[0]:
            did_duplicate[0] = True
            raise duplicate
    cursor.execute = execute_with_one_duplicate
    with patch.object(model, "obtener_conexion", return_value=conn), patch.object(
        model, "_EvidenciaModel__comprimir_y_guardar_imagen", return_value="uploads/evidencias/p.jpg"
    ), patch.object(model, "_validar_url", return_value=True), patch.object(
        model, "_limpiar_texto", side_effect=lambda text, size: text
    ):
        assert model._EvidenciaModel__guardar_evidencias_db() == [12, 12, 12]
    assert conn.rollbacks == 1 and conn.commits == 1 and conn.closed

    model._EvidenciaModel__archivos = [file]
    model._EvidenciaModel__etapas = ["antes"]
    cursor = Cursor(one={"url_archivos": "uploads/old.jpg"}, rowcount=1)
    conn = Connection(cursor)
    with patch.object(model, "obtener_conexion", return_value=conn), patch(
        "models.model_evidencia.os.path.exists", return_value=False
    ), patch.object(model, "_EvidenciaModel__comprimir_y_guardar_imagen", return_value="uploads/new.jpg"), patch.object(
        model, "_limpiar_texto", return_value="photo"
    ):
        assert model._EvidenciaModel__actualizar_evidencias_db(4)
    assert cursor.calls[-1][1] == ("photo", "uploads/new.jpg", "antes", 4)
    assert conn.commits == 1 and conn.closed

    with patch.object(model, "_EvidenciaModel__validar_evidencia_activa_db", return_value=False):
        with pytest.raises(ValueError, match="no existe"):
            model.actualizar_evidencia(1, [file], ["antes"])
    with patch.object(model, "_EvidenciaModel__validar_evidencia_activa_db", return_value=True), patch.object(
        model, "_EvidenciaModel__actualizar_evidencias_db", return_value=True
    ) as update:
        assert model.actualizar_evidencia(1, [file], ["durante"]) is True
        update.assert_called_once_with(1)
    with patch.object(model, "_EvidenciaModel__guardar_evidencias_db", return_value=[2]) as save:
        assert model.registrar_evidencias([file] * 3, ["antes"] * 3) == [2]
        save.assert_called_once()
    for files, stages in (([], ["antes"]), ([file] * 3, ["antes"]), ([file], ["antes"])):
        with pytest.raises(ValueError):
            model.registrar_evidencias(files, stages)
    with pytest.raises(ValueError, match="Error en base de datos"):
        with patch.object(model, "obtener_conexion", return_value=None):
            model._EvidenciaModel__guardar_evidencias_db()
    empty_cur = Cursor(one=None)
    empty_conn = Connection(empty_cur)
    with patch.object(model, "obtener_conexion", return_value=empty_conn):
        with pytest.raises(ValueError, match="No existe el registro activo"):
            model._EvidenciaModel__actualizar_evidencias_db(99)
    assert empty_conn.rollbacks == 1 and empty_conn.closed and empty_cur.closed
    for public, private, args, answer in [
        ("eliminar_evidencia", "_EvidenciaModel__eliminar_logico_db", (1,), True),
        ("obtener_evidencia_por_id", "_EvidenciaModel__obtener_evidencia_por_id_db", (1,), {"id": 1}),
        ("obtener_todas_evidencias", "_EvidenciaModel__obtener_todas_evidencias_db", (), []),
        ("contar_evidencias", "_EvidenciaModel__contar_evidencias_db", (), 0),
        ("validar_evidencia_activa", "_EvidenciaModel__validar_evidencia_activa_db", (1,), True),
    ]:
        with patch.object(model, private, return_value=answer):
            assert getattr(model, public)(*args) == answer


def test_informe_constructor_accessors_and_value_boundaries():
    with patch.object(InformeAvanceModel, "_InformeAvanceModel__asegurar_tabla_informe"), patch.object(
        InformeAvanceModel, "_InformeAvanceModel__asegurar_tabla_avance"
    ):
        model = InformeAvanceModel()
    pairs = [
        ("id_informe", 4, "get_id_informe"), ("fecha", "2024-01-02 03:04:05", "get_fecha"),
        ("estado", "En Ejecución", "get_estado"), ("poblacion_beneficiada", " Villa ", "get_poblacion_beneficiada"),
        ("tipo_informe", "Menor", "get_tipo_informe"), ("observaciones", None, "get_observaciones"),
        ("avance_id", 5, "get_avance_id"), ("gerente", 6, "get_gerente"),
    ]
    for key, value, getter in pairs:
        getattr(model, "set_" + key)(value)
        assert getattr(model, getter)() is not None
    assert model.get_estado() == "En Ejecucion"
    assert model.get_observaciones() == "Sin observaciones"
    assert model.get_id_informe() == 4 and model.get_avance_id() == "5"
    model.set_fecha("invalid")
    assert isinstance(model.get_fecha(), datetime)
    model.set_porcentaje_avance("oops")
    assert model.get_porcentaje_avance() == 0
    model.set_porcentaje_avance(130)
    assert model.get_porcentaje_avance() == 100
    model.set_gerente("")
    assert model.get_gerente() == "6"
    model.set_evidencias_antes([1, 2])
    model.set_evidencias_durante([3])
    model.set_evidencias_despues([4])
    for setter in (model.set_evidencias_antes, model.set_evidencias_durante, model.set_evidencias_despues):
        with pytest.raises(ValueError):
            setter(list(range(6)))
        with pytest.raises(ValueError):
            setter(["x" * 256])
    for setter, value in ((model.set_estado, "bad"), (model.set_tipo_informe, "bad"), (model.set_poblacion_beneficiada, "x")):
        with pytest.raises(ValueError):
            setter(value)


def test_informe_schema_migrations_cover_population_and_evidence_columns():
    model = raw(InformeAvanceModel)
    for correct, typo, expected in [
        (True, True, "DROP COLUMN poblacion_benefiada"),
        (False, True, "CHANGE COLUMN poblacion_benefiada"),
        (False, False, "ADD COLUMN poblacion_beneficiada"),
        (True, False, "MODIFY COLUMN poblacion_beneficiada"),
    ]:
        cur = Cursor()
        cur.fetchone = MagicMock(side_effect=[("yes",) if correct else None, ("yes",) if typo else None])
        model._InformeAvanceModel__asegurar_columna_poblacion(cur)
        assert any(expected in sql for sql, _ in cur.calls)
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[("x", "varchar(45)"), None, ("x", "varchar(255)")])
    model._InformeAvanceModel__asegurar_columnas_evidencia(cur)
    assert any("MODIFY COLUMN evidencia_antes VARCHAR(255)" in sql for sql, _ in cur.calls)


def test_informe_schema_constructor_paths_are_mocked_and_closed():
    model = raw(InformeAvanceModel)
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[("x",), None, None, None, None, ("x", "varchar(45)"), None, None, None])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        model._InformeAvanceModel__asegurar_tabla_informe()
    assert conn.closed and cur.closed
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[("x", "varchar(45)"), None, None, None, None])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        model._InformeAvanceModel__asegurar_tabla_avance()
    assert conn.closed and cur.closed


def test_informe_create_advance_and_report_database_operations():
    model = raw(InformeAvanceModel)
    # Existing real-work row path and fallback semaforo path for the advance writer.
    for row, expected_column in [((3, 5, 6, "P-1"), "semaforo_id_semaforo"), (None, "estado")]:
        cur = Cursor()
        cur.fetchone = MagicMock(side_effect=[None, row, (8,), None])
        conn = Connection(cur)
        with patch.object(model, "obtener_conexion", return_value=conn):
            advance = model._InformeAvanceModel__crear_avance_db(7, 140, "Some description")
        assert advance and expected_column in cur.calls[-1][0]
        assert cur.calls[-1][1][2] == 100
        assert conn.commits == 1 and conn.closed and cur.closed

    model._InformeAvanceModel__fecha = None
    model._InformeAvanceModel__estado = "Aprobado"
    model._InformeAvanceModel__poblacion_beneficiada = "Villa"
    model._InformeAvanceModel__tipo_informe = "Menor"
    model._InformeAvanceModel__avance_id = None
    model._InformeAvanceModel__evidencias_antes = [1, 2]
    model._InformeAvanceModel__evidencias_durante = []
    model._InformeAvanceModel__evidencias_despues = [3]
    cur = Cursor(rowcount=1)
    cur.fetchone = MagicMock(return_value=(10,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn), patch.object(
        model, "_InformeAvanceModel__asegurar_columna_poblacion"
    ):
        assert model._InformeAvanceModel__registrar_informe_db() == 10
    insert = [call for call in cur.calls if call[0].startswith("INSERT")][0]
    assert insert[1][5:8] == ("1,2", "", "3")
    assert conn.commits == 2 and conn.closed

    model._InformeAvanceModel__id_informe = 10
    model._InformeAvanceModel__observaciones = "Progress"
    model._InformeAvanceModel__porcentaje_avance = 50
    cur = Cursor()
    cur.fetchone = MagicMock(side_effect=[("advance-1",)])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__actualizar_informe_db() is True
    assert any("UPDATE avance SET" in sql for sql, _ in cur.calls)
    assert conn.commits == 1 and conn.closed

    cur = Cursor(rowcount=1)
    conn = Connection(cur)
    model._InformeAvanceModel__id_informe = 10
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__eliminar_logico_db() is True
    assert cur.calls[0][0].startswith("UPDATE") and conn.commits == 1


def test_informe_query_helpers_join_related_evidence_and_handle_errors():
    model = raw(InformeAvanceModel)
    rows = [{"id_informe": 1, "evidencia_antes": "2", "evidencia_durante": "", "evidencia_despues": ""}]
    ev = [{"id_evidencia": 2, "etapa": "antes"}]
    cur = Cursor(many=rows)
    cur.fetchall = MagicMock(side_effect=[rows, ev])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        result = model.obtener_informes_por_ids([1])
    assert result[0]["evidencias"] == ev
    assert cur.calls[0][1] == (1,)
    assert cur.calls[1][1] == ("2",)
    assert conn.closed and cur.closed
    assert model.obtener_informes_por_ids([]) == []
    with patch.object(model, "obtener_conexion", return_value=None):
        assert model.obtener_informes_por_ids([1]) == []

    cur = Cursor(many=[{"id": 1}])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__obtener_todos_informes_db() == [{"id": 1}]
    assert conn.closed

    cur = Cursor(one={"id_informe": 1})
    cur.fetchall = MagicMock(return_value=ev)
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        row = model._InformeAvanceModel__obtener_informe_por_id_db(1)
    assert row["evidencias"] == ev
    assert conn.closed
    assert model._InformeAvanceModel__obtener_evidencias_por_informe(Cursor(error=RuntimeError("query")), 1) == []

    cur = Cursor(many=[{"id_empleados": 4}])
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__obtener_gerentes_activos_db() == [{"id_empleados": 4}]
    assert conn.closed


def test_informe_validators_and_public_workflows():
    model = raw(InformeAvanceModel)
    cur = Cursor(one=(4,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__validar_informe_activo_db(4)
    assert cur.calls[0][1] == (4,) and conn.closed
    cur = Cursor(one=(4,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._InformeAvanceModel__validar_gerente_activo_db("4")
    assert cur.calls[0][1] == (4, "Gerente", "Inspector")
    assert not model._InformeAvanceModel__validar_gerente_activo_db("bad")

    model = raw(InformeAvanceModel)
    with patch.object(model, "_InformeAvanceModel__validar_gerente_activo_db", return_value=True), patch.object(
        model, "_InformeAvanceModel__crear_avance_db", return_value="adv"
    ), patch.object(model, "_InformeAvanceModel__registrar_informe_db", return_value=11):
        payload = {"gerente_responsable_id": "4", "estado": "Aprobado", "poblacion_beneficiada": "Villa",
                   "tipo_informe": "Menor", "observaciones": "Progress", "avance_id_avance": "adv",
                   "evidencias_antes": "1,2"}
        assert model.registrar_informe(payload) == 11
        assert model.get_gerente() == "4"
        assert model._InformeAvanceModel__evidencias_antes == ["1", "2"]
    with pytest.raises(ValueError):
        model.registrar_informe([])
    with patch.object(model, "_InformeAvanceModel__validar_gerente_activo_db", return_value=True), patch.object(
        model, "_InformeAvanceModel__actualizar_informe_db", return_value=True
    ), patch.object(model, "_InformeAvanceModel__validar_informe_activo_db", return_value=True):
        payload["id_informe"] = 1
        assert model.actualizar_informe(payload)
        assert model._InformeAvanceModel__evidencias_antes == ["1", "2"]
    with patch.object(model, "_InformeAvanceModel__validar_informe_activo_db", return_value=False):
        with pytest.raises(ValueError):
            model.eliminar_informe_logico(1)
    with patch.object(model, "_InformeAvanceModel__validar_informe_activo_db", return_value=True), patch.object(
        model, "_InformeAvanceModel__eliminar_logico_db", return_value=True
    ):
        assert model.eliminar_informe_logico("1")
    for public, private, args, expected in [
        ("obtener_todos_informes", "_InformeAvanceModel__obtener_todos_informes_db", (), [1]),
        ("obtener_gerentes_activos", "_InformeAvanceModel__obtener_gerentes_activos_db", (), [2]),
        ("validar_informe_activo", "_InformeAvanceModel__validar_informe_activo_db", (1,), True),
        ("validar_gerente_activo", "_InformeAvanceModel__validar_gerente_activo_db", (2,), True),
    ]:
        with patch.object(model, private, return_value=expected):
            assert getattr(model, public)(*args) == expected
    with patch.object(model, "_InformeAvanceModel__obtener_informe_por_id_db", return_value={"id": 1}):
        assert model.obtener_informe_por_id("1") == {"id": 1}
        assert model.obtener_informe_por_id("bad") is None


def test_informe_image_compression_success_and_invalid_file(tmp_path):
    path = tmp_path / "wide.png"
    Image.new("RGBA", (2200, 800), (1, 2, 3, 100)).save(path)
    assert InformeAvanceModel.comprimir_imagen(str(path), calidad=70)
    with Image.open(path) as image:
        assert image.mode == "RGB" and image.width == 1920
    assert InformeAvanceModel.comprimir_imagen(str(tmp_path / "missing.jpg")) is False


def test_publication_repository_constructor_properties_and_public_dispatch():
    with patch.object(PublicationRepository, "_PublicacionModel__asegurar_tabla_publicacion"):
        model = PublicationRepository()
    model.titulo = "A valid title"
    model.responsable = "Ana Maria"
    model.tipo = "News"
    model.id_informe = 3
    model.cuerpo = ""
    assert (model.titulo, model.responsable, model.tipo, model.id_informe, model.cuerpo) == (
        "A valid title", "Ana Maria", "News", 3, "Contenido pendiente"
    )
    for prop, value in (("titulo", "bad"), ("responsable", "x")):
        with pytest.raises(ValueError):
            setattr(model, prop, value)
    with patch.object(model, "_PublicacionModel__registrar_db", return_value=True) as save:
        assert model.registrar_publicacion({
            "titulo_publicacion": "Another title", "autor_publicacion": "Ana Maria",
            "tipo_publicacion": "News", "id_informe": "8", "cuerpo_publicacion": "Body",
        }) == 1
        save.assert_called_once_with()
        assert model.id_informe == "8" and model.cuerpo == "Body"
    with patch.object(model, "_PublicacionModel__actualizar_db", return_value=True) as update:
        assert model.actualizar_publicacion(7, {
            "titulo_publicacion": "Another title", "nombre_responsable": "Ana Maria",
            "tipo_publicacion": "News", "id_informe": 8,
        }) is True
        update.assert_called_once_with()
    with patch.object(model, "_PublicacionModel__registrar_db", return_value=False):
        assert model.registrar_publicacion({"titulo_publicacion": "bad"}) == 0
    for method, private, args, expected in [
        ("obtener_todas_las_publicaciones", "_PublicacionModel__obtener_publicaciones_db", (), [1]),
        ("obtener_todas", "_PublicacionModel__obtener_publicaciones_db", (), [1]),
        ("obtener_publicacion_por_id", "_PublicacionModel__obtener_por_id_db", (2,), {"id": 2}),
        ("obtener_por_id", "_PublicacionModel__obtener_por_id_db", (2,), {"id": 2}),
        ("obtener_informes_para_publicaciones", "_PublicacionModel__obtener_informes_db", (), [3]),
        ("guardar", "_PublicacionModel__registrar_db", (), True),
        ("actualizar", "_PublicacionModel__actualizar_db", (), True),
        ("eliminar", "_PublicacionModel__borrado_logico_db", (), True),
        ("validar_informe_activo", "_PublicacionModel__verificar_existencia_informe", (3,), True),
    ]:
        with patch.object(model, private, return_value=expected):
            assert getattr(model, method)(*args) == expected


def test_publication_repository_sql_writes_and_failures():
    with patch.object(PublicationRepository, "_PublicacionModel__asegurar_tabla_publicacion"):
        model = PublicationRepository("A title", "Ana Maria", "News", "12", 8)
    cur = Cursor(rowcount=1)
    cur.fetchone = MagicMock(return_value=(9,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._PublicacionModel__registrar_db()
    insert = cur.calls[-1]
    assert insert[1][0:4] == (9, "A title", "Ana Maria", "News")
    assert insert[1][5:] == (12, 1, "Contenido pendiente")
    assert conn.commits == 1 and conn.closed

    for private, response, args in [
        ("_PublicacionModel__actualizar_db", True, ()),
        ("_PublicacionModel__borrado_logico_db", True, ()),
    ]:
        cur = Cursor(rowcount=1)
        conn = Connection(cur)
        with patch.object(model, "obtener_conexion", return_value=conn):
            assert getattr(model, private)(*args) is response
        assert conn.commits == 1 and conn.closed and cur.closed
        if private.endswith("actualizar_db"):
            assert cur.calls[0][1] == ("A title", "Ana Maria", "News", 12, "Contenido pendiente", 8)
        else:
            assert cur.calls[0][1] == (8,)
    for private, expected, rows in [
        ("_PublicacionModel__obtener_publicaciones_db", [1], [1]),
        ("_PublicacionModel__obtener_informes_db", [2], [2]),
        ("_PublicacionModel__obtener_por_id_db", {"id": 8}, None),
    ]:
        cur = Cursor(one=expected, many=rows or [])
        conn = Connection(cur)
        with patch.object(model, "obtener_conexion", return_value=conn):
            result = getattr(model, private)(8) if private.endswith("por_id_db") else getattr(model, private)()
        assert result == expected
        assert conn.closed and cur.closed

    with patch.object(model, "obtener_conexion", return_value=None):
        assert model._PublicacionModel__obtener_publicaciones_db() == []
        assert model._PublicacionModel__verificar_existencia_informe(2) is False

    cur = Cursor(one=(12,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model._PublicacionModel__verificar_existencia_informe(" 12 ")
    assert cur.calls[0][1] == ("12",) and conn.closed and cur.closed


def test_publication_repository_schema_migration_is_mocked_and_closed():
    cur = Cursor(one=None)
    conn = Connection(cur)
    with patch.object(PublicationRepository, "obtener_conexion", return_value=conn):
        PublicationRepository()
    assert cur.calls == [
        ("SHOW COLUMNS FROM publicacion LIKE 'cuerpo_publicacion'", None),
        ("ALTER TABLE publicacion ADD COLUMN cuerpo_publicacion TEXT", None),
    ]
    assert conn.commits == 1 and conn.closed and cur.closed


def test_legacy_publication_layer_sql_and_error_contracts():
    model = raw(LegacyPublicationRepository)
    cur = Cursor(many=[{"id": 1}], rowcount=1)
    cur.fetchone = MagicMock(return_value=(1,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model.obtener_todas_las_publicaciones() == [{"id": 1}]
        assert model.obtener_informes_para_publicaciones() == [{"id": 1}]
        assert model.validar_informe_activo(1)
    assert conn.closed and cur.closed

    data = {"titulo_publicacion": "title", "nombre_responsable": "person", "tipo_publicacion": "News",
            "fecha_publicacion": "2024-01-01", "informe_avance_obra_id_informe": 3}
    cur = Cursor(rowcount=1)
    cur.fetchone = MagicMock(return_value=(5,))
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model.registrar_publicacion(data) == 1
    assert cur.calls[-1][1] == (5, "title", "person", "News", "2024-01-01", 3, 1, "Contenido pendiente")

    cur = Cursor(one={"id_publicacion": 4}, rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model.obtener_publicacion_por_id(4) == {"id_publicacion": 4}
    assert cur.calls[0][1] == (4,)

    cur = Cursor(rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model.actualizar_publicacion(4, data) == 1
    assert cur.calls[0][1] == ("title", "person", "News", 3, "Contenido pendiente", 4)
    cur = Cursor(rowcount=1)
    conn = Connection(cur)
    with patch.object(model, "obtener_conexion", return_value=conn):
        assert model.eliminar_publicacion(4) == 1
    assert cur.calls[0] == ("DELETE FROM publicacion WHERE id_publicacion = %s", (4,))

    for method, args, expected in [
        ("obtener_todas_las_publicaciones", (), []),
        ("registrar_publicacion", (data,), 0),
        ("actualizar_publicacion", (1, data), 0),
        ("eliminar_publicacion", (1,), 0),
        ("obtener_informes_para_publicaciones", (), []),
        ("validar_informe_activo", (1,), False),
    ]:
        failed_cur = Cursor(error=RuntimeError("query failed"))
        failed_conn = Connection(failed_cur)
        with patch.object(model, "obtener_conexion", return_value=failed_conn):
            assert getattr(model, method)(*args) == expected
        assert failed_conn.closed and failed_cur.closed
    failed_conn = Connection()
    with patch.object(model, "obtener_conexion", return_value=failed_conn):
        assert model.obtener_publicacion_por_id(1) is None
    assert failed_conn.closed

