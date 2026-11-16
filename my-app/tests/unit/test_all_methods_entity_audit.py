"""Behavioral coverage for active methods in the four entity models."""
from datetime import datetime

import pytest

from models.model_bitacora import BitacoraModel
from models.model_empleados import EmpleadoModel
from models.model_empresas import EmpresaModel, REQUISITOS_EMPRESA
from models.model_obra import ObraModel, asegurar_tabla_obra


class Cursor:
    def __init__(self, one=None, many=None, ones=None, manys=None,
                 rowcount=1, lastrowid=23, execute_error=None):
        self.one = one
        self.many = many if many is not None else []
        self.ones = list(ones or [])
        self.manys = list(manys or [])
        self.rowcount = rowcount
        self.lastrowid = lastrowid
        self.execute_error = execute_error
        self.executions = []
        self.closed = False

    def execute(self, sql, params=None):
        self.executions.append((sql, params))
        if self.execute_error:
            error = self.execute_error(sql, params) if callable(self.execute_error) else self.execute_error
            if error:
                raise error

    def fetchone(self):
        return self.ones.pop(0) if self.ones else self.one

    def fetchall(self):
        return self.manys.pop(0) if self.manys else self.many

    def close(self):
        self.closed = True


class Connection:
    def __init__(self, cursor=None):
        self.fake_cursor = cursor or Cursor()
        self.commits = 0
        self.rollbacks = 0
        self.closed = False
        self.started = 0

    def cursor(self, **kwargs):
        self.cursor_options = kwargs
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed = True

    def start_transaction(self):
        self.started += 1


def patch_connection(monkeypatch, obj, connection, method="obtener_conexion"):
    monkeypatch.setattr(obj, method, lambda: connection)


def _employee_private(model, method):
    return getattr(model, f"_EmpleadoModel{method}")


def _valid_obra_data():
    return {
        "titulo_obra": "Reparar avenida",
        "ubicacion_obra": "Barquisimeto",
        "periodo_ejecucion": "2 meses",
        "fecha_inicio": "2025-01-01",
        "fecha_fin": "2025-02-01",
        "mediciones_obra": "metros",
        "valuaciones": "Mensuales",
        "modificaciones_contrato": "Ninguna",
        "certificaciones_obras_ejecutadas": 2,
        "numero_contrato": "CTR-001/2025",
        "porcentaje_avance_obra": 40,
        "estado": 2,
        "contratacion_id_contratacion": 5,
        "gestionar_proyectos_codigo_proyecto": "PR-1",
    }


def _set_employee(model):
    model.set_nombre_empleado("Ana Pérez")
    model.set_cargo("Inspector")
    model.set_fecha_ingreso("2024-01-20")
    model.set_gerencia_asignada("Obras Públicas")
    model.set_cedula_persona("12345678")


# EmpresaModel

def test_empresa_ejecutar_consulta_cubre_parametros_resultados_y_fallos(monkeypatch):
    rows = [{"rif": "J-1"}]
    cursor = Cursor(one=rows[0], many=rows)
    conn = Connection(cursor)
    model = EmpresaModel()
    patch_connection(monkeypatch, model, conn)

    assert model._ejecutar_consulta("SELECT x") == rows
    assert cursor.executions[-1] == ("SELECT x", None)
    assert model._ejecutar_consulta("SELECT x WHERE x=%s", (1,), True) == rows[0]
    assert cursor.executions[-1] == ("SELECT x WHERE x=%s", (1,))
    assert conn.closed

    failed = Connection(Cursor(execute_error=RuntimeError("db down")))
    patch_connection(monkeypatch, model, failed)
    assert model._ejecutar_consulta("SELECT x", un_solo_registro=True) is None
    assert failed.closed


@pytest.mark.parametrize(
    ("rowcount", "return_count", "expected"),
    [(1, False, True), (0, True, False), (2, True, True)],
)
def test_empresa_ejecutar_modificacion_transacciona_y_devuelve_rowcount(
    monkeypatch, rowcount, return_count, expected
):
    cursor = Cursor(rowcount=rowcount)
    conn = Connection(cursor)
    model = EmpresaModel()
    patch_connection(monkeypatch, model, conn)

    assert model._ejecutar_modificacion("UPDATE t SET x=%s", (7,), return_count) is expected
    assert cursor.executions == [("UPDATE t SET x=%s", (7,))]
    assert conn.commits == 1
    assert conn.closed


def test_empresa_ejecutar_modificacion_maneja_error_con_y_sin_rowcount(monkeypatch):
    model = EmpresaModel()
    conn = Connection(Cursor(execute_error=RuntimeError("write failed")))
    patch_connection(monkeypatch, model, conn)
    assert model._ejecutar_modificacion("UPDATE t", ()) is False
    assert model._ejecutar_modificacion("UPDATE t", (), True) == 0
    assert conn.closed


def test_empresa_listados_delegan_consultas_con_filtros_esperados(monkeypatch):
    model = EmpresaModel()
    rows = [{"rif": "J-1"}]
    calls = []
    monkeypatch.setattr(model, "_ejecutar_consulta",
                        lambda sql: calls.append(sql) or rows)

    assert model.obtener_todas_las_empresas() == rows
    assert "WHERE estado = 1" in calls[0] and "ORDER BY nombre_empresa ASC" in calls[0]
    assert model.obtener_relaciones_activas() == rows
    assert "JOIN proyecto_has_maquinaria" in calls[1]
    assert "CONCAT(" in calls[1]


def test_empresa_registrar_nueva_existente_activa_e_inactiva(monkeypatch):
    model = EmpresaModel()
    data = {"rif": "J-123", "nombre_empresa": "Ejemplo", "telefono": "0251",
            "domicilio_fiscal": "Lara"}
    lookups = []
    writes = []
    monkeypatch.setattr(
        model, "_ejecutar_consulta",
        lambda sql, values=None, un_solo_registro=False:
            lookups.append((sql, values, un_solo_registro)) or None,
    )
    monkeypatch.setattr(
        model, "_ejecutar_modificacion",
        lambda sql, values, **kwargs: writes.append((sql, values, kwargs)) or True,
    )
    assert model.registrar_Empresas(data) is True
    assert lookups[-1][1:] == (("J-123",), True)
    assert writes[-1][1] == ("J-123", "Ejemplo", "0251", "Lara")
    assert "INSERT INTO empresa" in writes[-1][0]

    monkeypatch.setattr(
        model, "_ejecutar_consulta",
        lambda *args, **kwargs: {"estado": 1},
    )
    assert model.registrar_Empresas(data) == "DUPLICADO"
    assert "INSERT INTO empresa" in writes[-1][0]

    monkeypatch.setattr(
        model, "_ejecutar_consulta",
        lambda *args, **kwargs: {"estado": 0},
    )
    assert model.registrar_Empresas(data) is True
    assert "UPDATE empresa" in writes[-1][0]


def test_empresa_actualizaciones_usan_valores_parametrizados(monkeypatch):
    model = EmpresaModel()
    writes = []
    monkeypatch.setattr(
        model, "_ejecutar_modificacion",
        lambda sql, values, **kwargs: writes.append((sql, values, kwargs)) or True,
    )
    data = {"rif": "J-9", "nombre_empresa": "Nueva", "telefono": "0412",
            "domicilio_fiscal": "Lara"}
    assert model.update_empresa(data) is True
    assert writes[-1][1] == ("Nueva", "0412", "Lara", "J-9")
    assert model.eliminar_empresa("J-9") is True
    assert writes[-1][1:] == (("J-9",), {"retornar_rowcount": True})
    assert model.actualizar_cumple_requisitos("J-9", 1) is True
    assert writes[-1][1:] == ((1, "J-9"), {"retornar_rowcount": True})


def test_empresa_crea_tabla_requisitos_mediante_cursor():
    cursor = Cursor()
    EmpresaModel._crear_tabla_requisitos(cursor)
    assert len(cursor.executions) == 1
    assert "CREATE TABLE IF NOT EXISTS empresa_requisito" in cursor.executions[0][0]
    assert "ON DELETE CASCADE" in cursor.executions[0][0]


def test_empresa_obtener_requisitos_fusiona_legacy_y_estados_individuales(monkeypatch):
    cursor = Cursor(
        ones=[{"cumple_requisitos": 1}],
        manys=[[{"requisito": "req_rif", "verificado": 0},
                {"requisito": "desconocido", "verificado": 1}]],
    )
    conn = Connection(cursor)
    model = EmpresaModel()
    patch_connection(monkeypatch, model, conn)
    result = model.obtener_requisitos("J-1")

    assert len(result) == len(REQUISITOS_EMPRESA)
    assert result["req_acta_constitutiva"] is True
    assert result["req_rif"] is False
    assert cursor.closed and conn.closed
    assert cursor.executions[1][1] == ("J-1",)


def test_empresa_obtener_requisitos_inexistente_y_error(monkeypatch):
    model = EmpresaModel()
    conn = Connection(Cursor(one=None))
    patch_connection(monkeypatch, model, conn)
    assert model.obtener_requisitos("J-x") is None
    assert len(conn.fake_cursor.executions) == 2
    assert conn.closed

    failed = Connection(Cursor(execute_error=RuntimeError("read failed")))
    patch_connection(monkeypatch, model, failed)
    with pytest.raises(RuntimeError, match="No se pudieron consultar"):
        model.obtener_requisitos("J-x")
    assert failed.closed and failed.fake_cursor.closed


def test_empresa_actualizar_requisitos_valida_completa_y_realiza_commit(monkeypatch):
    model = EmpresaModel()
    requirements = {key: False for key in REQUISITOS_EMPRESA}
    requirements["req_rif"] = True
    assert model.actualizar_requisitos("J-1", []) is False
    assert model.actualizar_requisitos("J-1", {"req_rif": 1}) is False
    assert model.actualizar_requisitos("J-1", {**requirements, "extra": False}) is False

    cursor = Cursor(one={"rif": "J-1"})
    conn = Connection(cursor)
    patch_connection(monkeypatch, model, conn)
    assert model.actualizar_requisitos("J-1", requirements) is True
    inserts = [entry for entry in cursor.executions if "INSERT INTO empresa_requisito" in entry[0]]
    assert len(inserts) == len(REQUISITOS_EMPRESA)
    assert ("J-1", "req_rif", 1) in [entry[1] for entry in inserts]
    assert cursor.executions[-1][1] == (0, "J-1")
    assert conn.commits == 1 and conn.rollbacks == 0
    assert cursor.closed and conn.closed


def test_empresa_actualizar_requisitos_revierte_si_empresa_no_existe_o_hay_error(monkeypatch):
    model = EmpresaModel()
    reqs = {key: False for key in REQUISITOS_EMPRESA}
    missing = Connection(Cursor(one=None))
    patch_connection(monkeypatch, model, missing)
    assert model.actualizar_requisitos("J-x", reqs) is False
    assert missing.rollbacks == 1 and missing.commits == 0
    assert missing.closed and missing.fake_cursor.closed

    failed = Connection(Cursor(execute_error=RuntimeError("write failed")))
    patch_connection(monkeypatch, model, failed)
    assert model.actualizar_requisitos("J-1", reqs) is False
    assert failed.rollbacks == 1 and failed.commits == 0


# ObraModel

def test_obra_connection_and_input_validators_cover_boundaries(monkeypatch):
    connection = Connection()
    monkeypatch.setattr(ObraModel, "obtener_conexion_estricta", staticmethod(lambda: connection))
    assert ObraModel._con() is connection
    assert ObraModel._es_texto_valido("Vía 1") is True
    assert ObraModel._es_texto_valido(" " * 101) is False
    assert ObraModel._es_texto_valido("<script>") is False
    assert ObraModel._es_numero_contrato_valido("CTR-001/2025") is True
    assert ObraModel._es_numero_contrato_valido("CTR;DROP") is False
    assert ObraModel._es_numero_contrato_valido("") is False
    assert ObraModel._validar_fechas("2025-01-01", "2025-01-01") is True
    assert ObraModel._validar_fechas("2025-02-01", "2025-01-31") is False
    assert ObraModel._validar_fechas("bad", "2025-01-01") is True
    assert ObraModel._validar_fechas(datetime(2025, 1, 1), datetime(2025, 1, 2)) is True


def test_obra_eliminar_trigger_confirma_cierra_y_tolera_error(monkeypatch):
    conn = Connection()
    monkeypatch.setattr(ObraModel, "obtener_conexion_estricta", staticmethod(lambda: conn))
    ObraModel._eliminar_trigger_semaforo()
    assert conn.fake_cursor.executions[0][0] == "DROP TRIGGER IF EXISTS actualizar_semaforo_obra"
    assert conn.commits == 1 and conn.closed

    failed = Connection(Cursor(execute_error=RuntimeError("permission denied")))
    monkeypatch.setattr(ObraModel, "obtener_conexion_estricta", staticmethod(lambda: failed))
    ObraModel._eliminar_trigger_semaforo()
    assert failed.closed


@pytest.mark.parametrize(
    ("method", "sql_fragment", "param", "result"),
    [
        ("_sql_obtener_todas", "FROM obra o", None, [{"id_obra": 4}]),
        ("_sql_obtener_por_id", "o.id_obra = %s", (4,), {"id_obra": 4}),
        ("_sql_validar_estado", "FROM semaforo", (3,), True),
        ("_sql_validar_contratacion", "FROM contratacion", (5,), True),
        ("_sql_validar_proyecto", "FROM proyecto", ("PR-1",), True),
        ("_sql_listar_estados", "FROM semaforo", None, [{"id_semaforo": 1}]),
        ("_sql_listar_contrataciones", "FROM contratacion", None, [{"id_contratacion": 5}]),
        ("_sql_listar_proyectos", "FROM proyecto", None, [{"codigo_proyecto": "PR-1"}]),
    ],
)
def test_obra_sql_consultas_resultados_parametros_y_cierre(
    monkeypatch, method, sql_fragment, param, result
):
    model = ObraModel()
    cursor = Cursor(one=(1 if method.startswith("_sql_validar") else result),
                    many=result if isinstance(result, list) else [])
    conn = Connection(cursor)
    monkeypatch.setattr(model, "_con", lambda: conn)
    if method == "_sql_obtener_por_id":
        actual = getattr(model, method)(4)
    elif method == "_sql_validar_estado":
        actual = getattr(model, method)(3)
    elif method == "_sql_validar_contratacion":
        actual = getattr(model, method)(5)
    elif method == "_sql_validar_proyecto":
        actual = getattr(model, method)("PR-1")
    else:
        actual = getattr(model, method)()
    assert actual == result
    sql, params = cursor.executions[0]
    assert sql_fragment in sql
    if param is not None:
        assert params == param
    assert cursor.closed and conn.closed


@pytest.mark.parametrize(
    ("method", "value", "expected"),
    [("_sql_validar_estado", 8, False),
     ("_sql_validar_contratacion", 8, False),
     ("_sql_validar_proyecto", "X", False)],
)
def test_obra_validadores_sql_retorna_false_si_no_hay_fila(monkeypatch, method, value, expected):
    model = ObraModel()
    conn = Connection(Cursor(one=None))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert getattr(model, method)(value) is expected
    assert conn.closed


def test_obra_validar_contrato_omite_placeholders_y_excluye_id(monkeypatch):
    model = ObraModel()
    assert model._sql_validar_numero_contrato_duplicado("N/A") is False
    conn = Connection(Cursor(one={"1": 1}))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_validar_numero_contrato_duplicado("CTR-2", 7) is True
    assert conn.fake_cursor.executions == [
        ("SELECT 1 FROM obra WHERE numero_contrato = %s AND id_obra != %s AND estado = 1 LIMIT 1",
         ("CTR-2", 7))
    ]
    assert conn.fake_cursor.closed and conn.closed


def test_obra_validar_contrato_sin_exclusion_y_error(monkeypatch):
    model = ObraModel()
    conn = Connection(Cursor(one=None))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_validar_numero_contrato_duplicado("CTR-2") is False
    assert conn.fake_cursor.executions[0][1] == ("CTR-2",)
    failed = Connection(Cursor(execute_error=RuntimeError("db error")))
    monkeypatch.setattr(model, "_con", lambda: failed)
    assert model._sql_validar_numero_contrato_duplicado("CTR-3") is False
    assert failed.closed


def test_obra_consultas_sql_regresan_valores_vacios_sin_conexion(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_con", lambda: None)
    assert model._sql_obtener_todas() == []
    assert model._sql_obtener_por_id(1) is None
    assert model._sql_validar_estado(1) is False
    assert model._sql_validar_contratacion(1) is False
    assert model._sql_validar_proyecto("P") is False
    assert model._sql_validar_numero_contrato_duplicado("CTR") is False
    assert model._sql_listar_estados() == []
    assert model._sql_listar_contrataciones() == []
    assert model._sql_listar_proyectos() == []


def test_obra_insertar_rechaza_datos_antes_de_abrir_conexion(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_con", lambda: pytest.fail("no debe abrir conexión"))
    assert model._sql_insertar({}) == (False, "El campo 'titulo_obra' es obligatorio.")
    invalid = _valid_obra_data()
    invalid["porcentaje_avance_obra"] = 101
    assert model._sql_insertar(invalid) == (False, "Porcentaje de avance debe estar entre 0 y 100.")
    invalid = _valid_obra_data()
    invalid["fecha_fin"] = "2024-12-31"
    assert model._sql_insertar(invalid) == (
        False, "La fecha de fin no puede ser anterior a la fecha de inicio."
    )


def test_obra_insertar_parametriza_datos_y_confirma_transaccion(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_sql_validar_numero_contrato_duplicado", lambda *a, **k: False)
    monkeypatch.setattr(model, "_sql_validar_estado", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_contratacion", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_proyecto", lambda *_: True)
    conn = Connection(Cursor(lastrowid=81))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_insertar(_valid_obra_data()) == (True, 81)
    sql, params = conn.fake_cursor.executions[0]
    assert "INSERT INTO obra" in sql and "%s" in sql
    assert params[0:3] == ("Reparar avenida", "Barquisimeto", "2 meses")
    assert params[10:14] == (40, 2, 5, "PR-1")
    assert conn.started == 1 and conn.commits == 1 and conn.rollbacks == 0
    assert conn.fake_cursor.closed and conn.closed


def test_obra_insertar_interpreta_validacion_de_contrato_y_error_de_db(monkeypatch):
    model = ObraModel()
    data = _valid_obra_data()
    monkeypatch.setattr(model, "_sql_validar_numero_contrato_duplicado", lambda *a, **k: True)
    assert model._sql_insertar(data) == (
        False, "El número de contrato ya está registrado en otra obra."
    )

    monkeypatch.setattr(model, "_sql_validar_numero_contrato_duplicado", lambda *a, **k: False)
    monkeypatch.setattr(model, "_sql_validar_estado", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_contratacion", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_proyecto", lambda *_: True)
    conn = Connection(Cursor(execute_error=RuntimeError("insert failed")))
    monkeypatch.setattr(model, "_con", lambda: conn)
    result = model._sql_insertar(data)
    assert result[0] is False and "insert failed" in result[1]
    assert conn.rollbacks == 1 and conn.closed


def test_obra_actualizar_rechaza_no_existente_datos_invalidos_y_exceso_avance(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_sql_obtener_por_id", lambda _id: None)
    assert model._sql_actualizar(1, {}) == (False, "La obra no existe o fue eliminada.")
    monkeypatch.setattr(model, "_sql_obtener_por_id", lambda _id: {"id_obra": _id})
    invalid = _valid_obra_data()
    invalid["porcentaje_avance_obra"] = 101
    assert model._sql_actualizar(1, invalid) == (
        False, "Porcentaje de avance debe estar entre 0 y 100."
    )


def test_obra_actualizar_guarda_valores_y_revierte_error(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_sql_obtener_por_id", lambda _id: {"id_obra": _id})
    monkeypatch.setattr(model, "_sql_validar_numero_contrato_duplicado", lambda *a, **k: False)
    monkeypatch.setattr(model, "_sql_validar_estado", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_contratacion", lambda *_: True)
    monkeypatch.setattr(model, "_sql_validar_proyecto", lambda *_: True)
    monkeypatch.setattr(model, "_eliminar_trigger_semaforo", lambda: None)
    conn = Connection(Cursor(rowcount=2))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_actualizar(9, _valid_obra_data()) == (True, 2)
    assert "UPDATE obra SET" in conn.fake_cursor.executions[0][0]
    assert conn.fake_cursor.executions[0][1][-1] == 9
    assert conn.commits == 1 and conn.started == 1

    broken = Connection(Cursor(execute_error=RuntimeError("update error")))
    monkeypatch.setattr(model, "_con", lambda: broken)
    result = model._sql_actualizar(9, _valid_obra_data())
    assert result[0] is False and "update error" in result[1]
    assert broken.rollbacks == 1 and broken.closed


def test_obra_eliminar_cubre_no_existente_borrado_logico_y_error(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_eliminar_trigger_semaforo", lambda: None)
    missing = Connection(Cursor(one=None))
    monkeypatch.setattr(model, "_con", lambda: missing)
    assert model._sql_eliminar(3) == (False, "La obra no existe o ya fue eliminada.")
    assert missing.commits == 0 and missing.started == 1

    cursor = Cursor(ones=[{"id_obra": 3}], rowcount=1)
    conn = Connection(cursor)
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_eliminar(3) == (True, 1)
    assert cursor.executions[0] == (
        "SELECT id_obra FROM obra WHERE id_obra = %s AND estado = 1", (3,)
    )
    assert "UPDATE obra SET estado = 0" in cursor.executions[1][0]
    assert conn.commits == 1 and cursor.closed and conn.closed


def test_obra_eliminar_error_revierte_y_tolera_sin_conexion(monkeypatch):
    model = ObraModel()
    monkeypatch.setattr(model, "_eliminar_trigger_semaforo", lambda: None)
    monkeypatch.setattr(model, "_con", lambda: None)
    assert model._sql_eliminar(1) == (False, "Error de conexión a la base de datos.")
    broken = Connection(Cursor(execute_error=RuntimeError("select error")))
    monkeypatch.setattr(model, "_con", lambda: broken)
    assert model._sql_eliminar(1)[0] is False
    assert broken.rollbacks == 1 and broken.closed


@pytest.mark.parametrize(
    ("public_name", "private_name", "args"),
    [
        ("obtener_obra_por_id", "_sql_obtener_por_id", (5,)),
        ("obtener_todas", "_sql_obtener_todas", ()),
        ("registrar_obra", "_sql_insertar", (_valid_obra_data(),)),
        ("actualizar_obra", "_sql_actualizar", (5, _valid_obra_data())),
        ("eliminar_obra", "_sql_eliminar", (5,)),
        ("validar_estado", "_sql_validar_estado", (3,)),
        ("validar_contratacion", "_sql_validar_contratacion", (4,)),
        ("validar_proyecto", "_sql_validar_proyecto", ("PR-1",)),
        ("listar_estados", "_sql_listar_estados", ()),
        ("listar_contrataciones", "_sql_listar_contrataciones", ()),
        ("listar_proyectos", "_sql_listar_proyectos", ()),
    ],
)
def test_obra_metodos_publicos_delegan_con_argumentos_y_resultado(
    monkeypatch, public_name, private_name, args
):
    model = ObraModel()
    sentinel = object()
    called = []
    monkeypatch.setattr(
        model, private_name,
        lambda *received: called.append(received) or sentinel,
    )
    assert getattr(model, public_name)(*args) is sentinel
    assert called == [args]


@pytest.mark.parametrize(
    'existing_column,expected_statements,expected_commits',
    [(True, 1, 0), (False, 2, 1)],
)
def test_asegurar_tabla_obra_agrega_columna_solo_si_falta(
    monkeypatch, existing_column, expected_statements, expected_commits
):
    cursor = Cursor(one={'Field': 'activo'} if existing_column else None)
    connection = Connection(cursor)
    monkeypatch.setattr(
        ObraModel,
        'obtener_conexion',
        staticmethod(lambda: connection),
    )

    asegurar_tabla_obra()

    assert len(cursor.executions) == expected_statements
    assert "SHOW COLUMNS FROM obra LIKE 'activo'" in cursor.executions[0][0]
    if not existing_column:
        assert 'ALTER TABLE obra ADD COLUMN activo' in cursor.executions[1][0]
    assert connection.commits == expected_commits
    assert cursor.closed and connection.closed


def test_asegurar_tabla_obra_omite_conexion_ausente_y_limpia_tras_error(monkeypatch):
    monkeypatch.setattr(ObraModel, 'obtener_conexion', staticmethod(lambda: None))
    assert asegurar_tabla_obra() is None

    failed = Connection(Cursor(execute_error=RuntimeError('DDL failed')))
    monkeypatch.setattr(ObraModel, 'obtener_conexion', staticmethod(lambda: failed))
    assert asegurar_tabla_obra() is None
    assert failed.fake_cursor.closed and failed.closed


# EmpleadoModel

def test_empleado_constructor_getters_setters_y_validacion_de_cada_campo():
    model = EmpleadoModel()
    assert model.get_id_empleado() is None
    assert model.get_nombre_empleado() is None
    assert model.get_cargo() is None
    assert model.get_fecha_ingreso() is None
    assert model.get_gerencia_asignada() is None
    assert model.get_cedula_persona() is None
    assert model.get_estado() == 1

    model.set_id_empleado(7)
    model.set_nombre_empleado(" Ana Pérez ")
    model.set_cargo("Inspector")
    model.set_fecha_ingreso("2024-01-20")
    model.set_gerencia_asignada(" Obras Públicas ")
    model.set_cedula_persona("12345678")
    model.set_estado(0)
    assert (model.get_id_empleado(), model.get_nombre_empleado(), model.get_cargo()) == (
        7, "Ana Pérez", "Inspector"
    )
    assert model.get_fecha_ingreso() == "2024-01-20"
    assert model.get_gerencia_asignada() == "Obras Públicas"
    assert model.get_cedula_persona() == 12345678 and model.get_estado() == 0


@pytest.mark.parametrize(
    ("setter", "value"),
    [
        ("set_id_empleado", 0), ("set_id_empleado", "2"),
        ("set_nombre_empleado", "A"), ("set_cargo", "No existe"),
        ("set_fecha_ingreso", "2024/01/01"),
        ("set_gerencia_asignada", "IT"),
        ("set_cedula_persona", "123"), ("set_estado", 2),
    ],
)
def test_empleado_setters_rechazan_valores_fuera_de_regla(setter, value):
    with pytest.raises(ValueError):
        getattr(EmpleadoModel(), setter)(value)


@pytest.mark.parametrize(
    ("method", "valid", "invalid"),
    [
        ("_validar_nombre", "Ana Pérez", "A"),
        ("_validar_gerencia", "Obras Públicas", "IT"),
        ("_validar_fecha", "2024-01-31", "31-01-2024"),
        ("_validar_cedula", "1234567", "123-456"),
        ("_validar_telefono", "04121234567", "12345"),
        ("_validar_correo", "ana@example.test", "bad-email"),
    ],
)
def test_empleado_validadores_aceptan_y_rechazan_formas_especificas(method, valid, invalid):
    model = EmpleadoModel()
    assert getattr(model, method)(valid) is True
    assert getattr(model, method)(invalid) is False


def test_empleado_buscar_o_crear_persona_reusa_o_inserta_fk():
    model = EmpleadoModel()
    model.set_cedula_persona("12345678")
    existing = Cursor(one={"id_persona": 14})
    assert _employee_private(model, "__buscar_o_crear_persona")(existing) == 14
    assert existing.executions == [
        ("SELECT id_persona FROM persona WHERE cedula_persona = %s LIMIT 1", (12345678,))
    ]

    model._EmpleadoModel__direccion = None
    model._EmpleadoModel__parroquia = None
    model._EmpleadoModel__municipio = None
    model._EmpleadoModel__telefono = None
    model._EmpleadoModel__correo = None
    cursor = Cursor(ones=[None, {"siguiente_id": 8}], lastrowid=8)
    assert _employee_private(model, "__buscar_o_crear_persona")(cursor) == 8
    sql, params = cursor.executions[-1]
    assert "INSERT INTO persona" in sql
    assert params == (8, 12345678, "No especificado", "No especificado",
                      "No especificado", "0000000000", "sin_correo@invilara.gob.ve")


def test_empleado_buscar_persona_reintenta_colision_y_falla_tras_tres(monkeypatch):
    model = EmpleadoModel()
    model.set_cedula_persona("12345678")
    class RetryCursor(Cursor):
        def execute(self, sql, params=None):
            super().execute(sql, params)
            if "INSERT INTO persona" in sql:
                raise RuntimeError(1062, "duplicate")
    cursor = RetryCursor(ones=[None, (1,), None, (2,), None, (3,)])
    cursor.connection = Connection()
    with pytest.raises(ValueError, match="tras 3 intentos"):
        _employee_private(model, "__buscar_o_crear_persona")(cursor)
    assert cursor.connection.rollbacks == 3


def test_empleado_guardar_db_inserta_y_cierra_recursos(monkeypatch):
    model = EmpleadoModel()
    _set_employee(model)
    cursor = Cursor(ones=[{"siguiente_id": 3}], lastrowid=3)
    conn = Connection(cursor)
    patch_connection(monkeypatch, model, conn)
    monkeypatch.setattr(model, "_EmpleadoModel__buscar_o_crear_persona", lambda _cur: 19)
    assert _employee_private(model, "__guardar_empleado_db")() == 3
    insert_sql, insert_values = cursor.executions[-1]
    assert "INSERT INTO empleados" in insert_sql
    assert insert_values == (3, "Ana Pérez", "Inspector", "2024-01-20",
                             "Obras Públicas", 19, 1)
    assert conn.commits == 1 and cursor.closed and conn.closed


def test_empleado_guardar_db_sin_conexion_y_error_devuelve_none(monkeypatch):
    model = EmpleadoModel()
    patch_connection(monkeypatch, model, None)
    assert _employee_private(model, "__guardar_empleado_db")() is None
    conn = Connection(Cursor(execute_error=RuntimeError("db error")))
    patch_connection(monkeypatch, model, conn)
    assert _employee_private(model, "__guardar_empleado_db")() is None
    assert conn.rollbacks == 1 and conn.closed


def test_empleado_actualizar_y_eliminar_db_confirman_sql_parametrizado(monkeypatch):
    model = EmpleadoModel()
    _set_employee(model)
    model.set_id_empleado(6)
    conn = Connection(Cursor(rowcount=1))
    patch_connection(monkeypatch, model, conn)
    assert _employee_private(model, "__actualizar_empleado_db")() is True
    assert conn.fake_cursor.executions[0][1] == (
        "Ana Pérez", "Inspector", "2024-01-20", "Obras Públicas", 6
    )
    assert conn.commits == 1

    deleted = Connection(Cursor(rowcount=1))
    patch_connection(monkeypatch, model, deleted)
    assert _employee_private(model, "__eliminar_logico_db")() is True
    assert deleted.fake_cursor.executions[0] == (
        "UPDATE empleados SET estado = 0 WHERE id_empleados = %s", (6,)
    )
    assert deleted.commits == 1


def test_empleado_actualizar_y_eliminar_db_manejan_no_encontrado_error_y_sin_conexion(monkeypatch):
    model = EmpleadoModel()
    model.set_id_empleado(6)
    conn = Connection(Cursor(rowcount=0))
    patch_connection(monkeypatch, model, conn)
    assert _employee_private(model, "__actualizar_empleado_db")() is False
    assert _employee_private(model, "__eliminar_logico_db")() is False
    patch_connection(monkeypatch, model, None)
    assert _employee_private(model, "__actualizar_empleado_db")() is False
    assert _employee_private(model, "__eliminar_logico_db")() is False
    failed = Connection(Cursor(execute_error=RuntimeError("write failed")))
    patch_connection(monkeypatch, model, failed)
    assert _employee_private(model, "__actualizar_empleado_db")() is False
    assert failed.rollbacks == 1


def test_empleado_db_listados_contadores_y_consultas_por_clave(monkeypatch):
    model = EmpleadoModel()
    rows = [{"id_empleados": 3}]
    conn = Connection(Cursor(many=rows))
    patch_connection(monkeypatch, model, conn)
    assert _employee_private(model, "__obtener_todos_empleados_db")(5, 10) == rows
    sql, params = conn.fake_cursor.executions[0]
    assert "LIMIT %s OFFSET %s" in sql and params == [5, 10]
    assert "e.estado = 1" in sql and conn.closed

    count_conn = Connection(Cursor(one=(12,)))
    patch_connection(monkeypatch, model, count_conn)
    assert model.contar_empleados() == 12
    assert "SELECT COUNT(*) FROM empleados WHERE estado = 1" in count_conn.fake_cursor.executions[0][0]

    row_conn = Connection(Cursor(one={"id_empleados": 8}))
    patch_connection(monkeypatch, model, row_conn)
    assert _employee_private(model, "__obtener_empleado_por_id_db")(8) == {"id_empleados": 8}
    assert row_conn.fake_cursor.executions[0][1] == (8,)

    role_conn = Connection(Cursor(many=rows))
    patch_connection(monkeypatch, model, role_conn)
    assert _employee_private(model, "__obtener_empleados_por_cargo_db")("Inspector") == rows
    assert role_conn.fake_cursor.executions[0][1] == ("Inspector",)


def test_empleado_db_listados_y_contadores_degradan_en_error_o_sin_conexion(monkeypatch):
    model = EmpleadoModel()
    patch_connection(monkeypatch, model, None)
    assert _employee_private(model, "__obtener_todos_empleados_db")() == []
    assert model.contar_empleados() == 0
    assert _employee_private(model, "__obtener_empleado_por_id_db")(1) is None
    assert _employee_private(model, "__obtener_empleados_por_cargo_db")("Inspector") == []
    assert _employee_private(model, "__validar_empleado_activo_db")(1) is False

    for method, expected in [
        ("__obtener_todos_empleados_db", []),
        ("__obtener_empleado_por_id_db", None),
        ("__obtener_empleados_por_cargo_db", []),
    ]:
        conn = Connection(Cursor(execute_error=RuntimeError("read failed")))
        patch_connection(monkeypatch, model, conn)
        args = (1, 0) if method == "__obtener_todos_empleados_db" else (1,)
        assert _employee_private(model, method)(*args) == expected


def test_empleado_validar_activo_db_usa_id_y_responde_por_fila(monkeypatch):
    model = EmpleadoModel()
    conn = Connection(Cursor(one=(6,)))
    patch_connection(monkeypatch, model, conn)
    assert _employee_private(model, "__validar_empleado_activo_db")(6) is True
    assert conn.fake_cursor.executions[0] == (
        "SELECT id_empleados FROM empleados WHERE id_empleados = %s AND estado = 1", (6,)
    )
    empty = Connection(Cursor(one=None))
    patch_connection(monkeypatch, model, empty)
    assert _employee_private(model, "__validar_empleado_activo_db")(6) is False


def test_empleado_publicar_registro_valida_datos_y_delega_en_guardado(monkeypatch):
    model = EmpleadoModel()
    saved = []
    monkeypatch.setattr(model, "_EmpleadoModel__guardar_empleado_db",
                        lambda: saved.append(True) or 42)
    data = {"nombre_empleado": "Ana Pérez", "cargo": "Inspector",
            "fecha_ingreso": "2024-01-20", "gerencia_asignada": "Obras Públicas",
            "cedula_empleado": "12345678", "telefono": "04121234567"}
    assert model.registrar_empleado(data) == 42
    assert saved == [True]
    assert model._EmpleadoModel__telefono == "04121234567"
    assert model._EmpleadoModel__direccion == "No especificado"
    with pytest.raises(ValueError):
        model.registrar_empleado({**data, "telefono": "bad"})


def test_empleado_public_update_delete_validan_estado_y_delegan(monkeypatch):
    model = EmpleadoModel()
    monkeypatch.setattr(model, "_EmpleadoModel__validar_empleado_activo_db", lambda _id: True)
    monkeypatch.setattr(model, "_EmpleadoModel__actualizar_empleado_db", lambda: "updated")
    data = {"id_empleado": "6", "nombre_empleado": "Ana Pérez", "cargo": "Inspector",
            "fecha_ingreso": "2024-01-20", "gerencia_asignada": "Obras Públicas"}
    assert model.actualizar_empleado(data) == "updated"
    assert model.get_id_empleado() == 6
    monkeypatch.setattr(model, "_EmpleadoModel__validar_empleado_activo_db", lambda _id: False)
    with pytest.raises(ValueError, match="no existe"):
        model.actualizar_empleado(data)
    with pytest.raises(ValueError, match="no existe"):
        model.eliminar_empleado_logico(6)

    monkeypatch.setattr(model, "_EmpleadoModel__validar_empleado_activo_db", lambda _id: True)
    monkeypatch.setattr(model, "_EmpleadoModel__eliminar_logico_db", lambda: True)
    assert model.eliminar_empleado_logico("6") is True
    with pytest.raises(ValueError):
        model.eliminar_empleado_logico(0)


def test_empleado_public_getters_aplican_paginacion_validacion_y_catalogo(monkeypatch):
    model = EmpleadoModel()
    rows = [{"id_empleados": 1}]
    calls = []
    monkeypatch.setattr(model, "_EmpleadoModel__obtener_todos_empleados_db",
                        lambda *args, **kwargs: calls.append((args, kwargs)) or rows)
    assert model.obtener_todos_empleados() == rows
    assert calls[-1] == ((), {})
    assert model.obtener_empleados_paginados(page=0, per_page=5) == rows
    assert calls[-1] == ((), {"limite": 5, "offset": 0})

    by_id = []
    monkeypatch.setattr(model, "_EmpleadoModel__obtener_empleado_por_id_db",
                        lambda ident: by_id.append(ident) or {"id_empleados": ident})
    assert model.obtener_empleado_por_id("7") == {"id_empleados": 7}
    assert model.obtener_empleado_por_id("x") is None
    assert model.obtener_empleado_por_id(0) is None
    assert by_id == [7]

    roles = []
    monkeypatch.setattr(model, "_EmpleadoModel__obtener_empleados_por_cargo_db",
                        lambda cargo: roles.append(cargo) or rows)
    assert model.obtener_empleados_por_cargo("Inspector") == rows
    assert model.obtener_empleados_por_cargo("Invalid") == []
    assert roles == ["Inspector"]
    monkeypatch.setattr(model, "_EmpleadoModel__validar_empleado_activo_db", lambda ident: ident == 9)
    assert model.validar_empleado_activo("9") is True
    assert model.validar_empleado_activo("bad") is False
    assert set(model.obtener_catalogo_cargos()) == EmpleadoModel.CARGOS_VALIDOS


# BitacoraModel

def test_bitacora_validadores_y_conexion_seguridad(monkeypatch):
    conn = Connection()
    monkeypatch.setattr(BitacoraModel, "obtener_conexion_seguridad", staticmethod(lambda: conn))
    assert BitacoraModel._con() is conn
    assert BitacoraModel._es_texto_valido("Cambio #1, vía") is True
    assert BitacoraModel._es_texto_valido("<script>") is False
    assert BitacoraModel._es_texto_valido("x" * 101) is False
    assert BitacoraModel._es_usuario_valido("Ana Pérez") is True
    assert BitacoraModel._es_usuario_valido("usuario@dominio") is False
    assert BitacoraModel._es_usuario_valido("x" * 16) is False


def test_bitacora_insertar_commit_y_reintento_de_id_duplicado(monkeypatch):
    model = BitacoraModel()
    cursor = Cursor(ones=[{"siguiente_id": 5}, {"siguiente_id": 6}])
    attempts = {"n": 0}
    def fail_first_insert(sql, params):
        if "INSERT INTO bitacora" in sql:
            attempts["n"] += 1
            if attempts["n"] == 1:
                return RuntimeError(1062, "duplicate")
        return None
    cursor.execute_error = fail_first_insert
    conn = Connection(cursor)
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_insertar("Ana", 9, "Obras", "CREAR", "detalle") is True
    inserts = [entry for entry in cursor.executions if "INSERT INTO bitacora" in entry[0]]
    assert len(inserts) == 2
    assert inserts[0][1][0:5] == (5, "Ana", 0, "Obras", "CREAR")
    assert inserts[1][1][0] == 6
    assert isinstance(inserts[1][1][5], datetime)
    assert inserts[1][1][5:8] == (inserts[1][1][5],) * 3
    assert conn.rollbacks == 1 and conn.commits == 1
    assert cursor.closed and conn.closed


def test_bitacora_insertar_sin_conexion_y_error_no_reintenta(monkeypatch):
    model = BitacoraModel()
    monkeypatch.setattr(model, "_con", lambda: None)
    assert model._sql_insertar("Ana", 1, "X", "VER", "") is False
    conn = Connection(Cursor(execute_error=RuntimeError("insert error")))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_insertar("Ana", 1, "X", "VER", "") is False
    assert conn.rollbacks == 0 and conn.closed


def test_bitacora_insertar_falla_despues_de_tres_colisiones(monkeypatch):
    model = BitacoraModel()
    cursor = Cursor(ones=[(3,), (3,), (3,)])
    def always_duplicate(sql, params):
        return RuntimeError(1062, "duplicate") if "INSERT INTO bitacora" in sql else None
    cursor.execute_error = always_duplicate
    conn = Connection(cursor)
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_insertar("Ana", 1, "X", "VER", "") is False
    assert len([e for e in cursor.executions if "INSERT INTO bitacora" in e[0]]) == 3
    assert conn.rollbacks == 3 and conn.commits == 0


@pytest.mark.parametrize(
    ("method", "value", "where", "params"),
    [
        ("_sql_filtrar_por_usuario", "Ana", "usuario LIKE %s", ("%Ana%",)),
        ("_sql_filtrar_por_modulo", "Obras", "modulo = %s", ("Obras",)),
        ("_sql_filtrar_por_accion", "CREAR", "accion = %s", ("CREAR",)),
    ],
)
def test_bitacora_sql_filtros_parametrizan_y_cuidan_recursos(
    monkeypatch, method, value, where, params
):
    model = BitacoraModel()
    rows = [{"id_bitacora": 1}]
    conn = Connection(Cursor(many=rows))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert getattr(model, method)(value) == rows
    sql, actual_params = conn.fake_cursor.executions[0]
    assert where in sql and actual_params == params
    assert "LIMIT 200" in sql
    assert conn.fake_cursor.closed and conn.closed


def test_bitacora_sql_obtener_todos_con_y_sin_limite_y_error(monkeypatch):
    model = BitacoraModel()
    rows = [{"id_bitacora": 1}]
    conn = Connection(Cursor(many=rows))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_obtener_todos() == rows
    assert conn.fake_cursor.executions[0][1] is None
    assert "LIMIT %s" not in conn.fake_cursor.executions[0][0]
    limited = Connection(Cursor(many=rows))
    monkeypatch.setattr(model, "_con", lambda: limited)
    assert model._sql_obtener_todos(11) == rows
    assert limited.fake_cursor.executions[0][1] == (11,)
    assert "LIMIT %s" in limited.fake_cursor.executions[0][0]
    failed = Connection(Cursor(execute_error=RuntimeError("query failed")))
    monkeypatch.setattr(model, "_con", lambda: failed)
    assert model._sql_obtener_todos() == []
    assert failed.closed


def test_bitacora_sql_filtrar_criterios_compone_and_paginacion(monkeypatch):
    model = BitacoraModel()
    rows = [{"id_bitacora": 2}]
    conn = Connection(Cursor(many=rows))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_filtrar_por_criterios("Ana", "Obras", "CREAR", 7, 14) == rows
    sql, params = conn.fake_cursor.executions[0]
    assert "usuario LIKE %s AND modulo = %s AND accion = %s" in sql
    assert params == ("%Ana%", "Obras", "CREAR", 7, 14)
    assert "LIMIT %s OFFSET %s" in sql
    assert conn.closed


def test_bitacora_sql_criterios_sin_filtros_delega_todos_y_maneja_error(monkeypatch):
    model = BitacoraModel()
    rows = [{"id_bitacora": 1}]
    calls = []
    monkeypatch.setattr(model, "_sql_obtener_todos",
                        lambda limit=None: calls.append(limit) or rows)
    conn = Connection()
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_filtrar_por_criterios(limit=12) == rows
    assert calls == [12]
    assert conn.closed and conn.fake_cursor.closed

    failed = Connection(Cursor(execute_error=RuntimeError("query failed")))
    monkeypatch.setattr(model, "_con", lambda: failed)
    assert model._sql_filtrar_por_criterios("Ana") == []
    assert failed.closed


def test_bitacora_sql_estadisticas_y_conteo_devuelven_datos_parametrizados(monkeypatch):
    model = BitacoraModel()
    stats_rows = [{"accion": "CREAR", "total": 3}]
    conn = Connection(Cursor(many=stats_rows))
    monkeypatch.setattr(model, "_con", lambda: conn)
    assert model._sql_contar_por_accion() == {"CREAR": 3}
    assert "GROUP BY accion" in conn.fake_cursor.executions[0][0]

    count = Connection(Cursor(one=(4,)))
    monkeypatch.setattr(model, "_con", lambda: count)
    assert model._sql_contar_filtrados("Ana", "Obras", "CREAR") == 4
    assert count.fake_cursor.executions[0][1] == ("%Ana%", "Obras", "CREAR")
    assert "usuario LIKE %s AND modulo = %s AND accion = %s" in count.fake_cursor.executions[0][0]

    unfiltered = Connection(Cursor(one=(9,)))
    monkeypatch.setattr(model, "_con", lambda: unfiltered)
    assert model._sql_contar_filtrados() == 9
    assert unfiltered.fake_cursor.executions[0] == (
        "SELECT COUNT(*) FROM bitacora", None
    )


def test_bitacora_sql_aggregados_fallan_con_resultado_vacio_o_error(monkeypatch):
    model = BitacoraModel()
    monkeypatch.setattr(model, "_con", lambda: None)
    assert model._sql_contar_por_accion() == {}
    assert model._sql_contar_filtrados() == 0

    failed = Connection(Cursor(execute_error=RuntimeError("db error")))
    monkeypatch.setattr(model, "_con", lambda: failed)
    assert model._sql_contar_por_accion() == {}
    assert model._sql_contar_filtrados("Ana") == 0
    assert failed.closed


def test_bitacora_registrar_normaliza_argumentos_y_delega(monkeypatch):
    model = BitacoraModel()
    calls = []
    monkeypatch.setattr(model, "_sql_insertar",
                        lambda *args: calls.append(args) or True)
    assert model.registrar("  Ana  ", "9", " Obras ", "crear", "detalle") is True
    assert calls[-1] == ("Ana", 9, "Obras", "CREAR", "detalle")
    model.registrar("", "x", "", "", "")
    assert calls[-1] == ("Sistema", 1, "General", "VER", "")
    model.registrar("u" * 20, 7, "m" * 25, "a" * 50)
    assert calls[-1] == ("u" * 15, 7, "m" * 20, "A" * 45, "")


def test_bitacora_obtener_todos_pasa_limite_y_retorna_consulta(monkeypatch):
    model = BitacoraModel()
    rows = [{"id_bitacora": 11}]
    limits = []
    monkeypatch.setattr(
        model, "_sql_obtener_todos",
        lambda limit=None: limits.append(limit) or rows,
    )
    assert model.obtener_todos(limit=25) == rows
    assert limits == [25]


def test_bitacora_fachada_sanitiza_y_rechaza_filtros_invalidos(monkeypatch):
    model = BitacoraModel()
    calls = []
    monkeypatch.setattr(model, "_sql_filtrar_por_usuario",
                        lambda value: calls.append(("usuario", value)) or [value])
    monkeypatch.setattr(model, "_sql_filtrar_por_modulo",
                        lambda value: calls.append(("modulo", value)) or [value])
    monkeypatch.setattr(model, "_sql_filtrar_por_accion",
                        lambda value: calls.append(("accion", value)) or [value])

    assert model.filtrar_por_usuario("A") == []
    assert model.filtrar_por_usuario("Ana<;") == ["Ana"]
    assert calls[-1] == ("usuario", "Ana")
    assert model.filtrar_por_modulo("") == []
    assert model.filtrar_por_modulo("Ob<ras") == ["Obras"]
    assert model.filtrar_por_accion("wat") == []
    assert model.filtrar_por_accion(" crear ") == ["CREAR"]
    assert calls[-1] == ("accion", "CREAR")


def test_bitacora_busqueda_compuesta_limita_pagina_y_usa_consulta_todos(monkeypatch):
    model = BitacoraModel()
    calls = []
    rows = [{"id_bitacora": 1}]
    monkeypatch.setattr(
        model, "_sql_filtrar_por_criterios",
        lambda **kwargs: calls.append(kwargs) or rows,
    )
    assert model.filtrar_por_criterios(
        usuario="Ana<>", modulo="Ob<ras", accion="login", page=3, per_page=7
    ) == rows
    assert calls[-1] == {
        "usuario": "Ana", "modulo": "Obras", "accion": "LOGIN",
        "limit": 7, "offset": 14,
    }
    all_calls = []
    monkeypatch.setattr(model, "obtener_todos",
                        lambda **kwargs: all_calls.append(kwargs) or rows)
    assert model.filtrar_por_criterios(usuario="x", accion="bad") == rows
    assert all_calls == [{}]


def test_bitacora_contar_filtros_limpia_valores_y_delega_estadisticas(monkeypatch):
    model = BitacoraModel()
    calls = []
    monkeypatch.setattr(
        model, "_sql_contar_filtrados",
        lambda **kwargs: calls.append(kwargs) or 6,
    )
    assert model.contar_filtrados("Ana<", "Ob<ras", "delete") == 6
    assert calls[-1] == {
        "usuario": "Ana", "modulo": "Obras", "accion": None,
    }
    monkeypatch.setattr(model, "_sql_contar_por_accion", lambda: {"VER": 2})
    assert model.estadisticas_por_accion() == {"VER": 2}

