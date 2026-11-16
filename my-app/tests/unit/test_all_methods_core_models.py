"""Focused behavior tests for every active method in the core models."""

import json
from datetime import datetime
from unittest.mock import Mock

import pytest

from models.model_contratacion import ContratacionModel
from models.model_gravedad import GravedadObraModel
from models.model_maquinaria import MaquinariaModel
from models.model_prioridad import PrioridadModel
from models.model_proyecto import ProyectoModel
from models.model_solicitudes import SolicitudModel


def _db(rows=None, row=None):
    cursor = Mock()
    cursor.fetchall.return_value = [] if rows is None else rows
    cursor.fetchone.return_value = row
    cursor.lastrowid = 41
    cursor.rowcount = 1
    connection = Mock()
    connection.cursor.return_value = cursor
    return connection, cursor


def _patch_solicitud_db(monkeypatch, connection):
    monkeypatch.setattr(SolicitudModel, "_con", staticmethod(lambda: connection))


def _patch_prioridad_db(monkeypatch, connection):
    monkeypatch.setattr(
        PrioridadModel, "obtener_conexion_estricta", staticmethod(lambda: connection)
    )


def _valid_contratacion():
    return {
        "empresa_ganadora": "Empresa S.A.",
        "empresa_rif": "J-12345678-9",
        "descripcion": "Mantenimiento vial",
        "numero_contrato": "CTR-001",
        "monto": "1000",
        "tipo_contrato": "Contrato de Obra",
        "modalidad": "Concurso Abierto",
        "objeto": "Ejecución de Obras",
        "fecha_inicio_procedimiento": "2024-01-01",
        "fecha_adjudicacion": "2024-01-02",
        "fecha_registro": "2024-01-03",
    }


# SolicitudModel: initialization, accessors, validation and private helpers.
def test_solicitud_constructor_accessors_and_value_normalization():
    solicitud = SolicitudModel(12)
    assert solicitud.get_id() == 12
    assert solicitud.get_tipo_solicitud() is None
    assert solicitud.get_estatus_solicitud() == "Pendiente"
    assert solicitud.get_problematica() is None
    assert solicitud.get_fecha() is None

    solicitud.set_tipo_solicitud(" Comunidad ")
    solicitud.set_estatus_solicitud("estado desconocido")
    solicitud.set_problematica("La vía necesita reparación urgente")
    solicitud.set_fecha("2025-01-02T03:04:05")
    solicitud.set_fecha()
    assert solicitud.get_tipo_solicitud() == "Comunidad"
    assert solicitud.get_estatus_solicitud() == "Pendiente"
    assert solicitud.get_problematica() == "La vía necesita reparación urgente"
    assert datetime.strptime(solicitud.get_fecha(), "%Y-%m-%d %H:%M:%S")
    solicitud.set_fecha("2025-01-02T03:04:05")
    assert solicitud.get_fecha() == "2025-01-02 03:04:05"


def test_solicitud_setters_enforce_categories_and_problem_limit():
    solicitud = SolicitudModel()
    with pytest.raises(ValueError):
        solicitud.set_tipo_solicitud("No válido")
    with pytest.raises(ValueError):
        solicitud.set_problematica("Descripción suficientemente larga", "No existe")

    solicitud.set_problematica("Descripción de una solicitud concreta", "Vivienda")
    assert solicitud.get_problematica().startswith("[Vivienda] ")
    assert len(solicitud.get_problematica()) <= SolicitudModel.LIMITE_PROBLEMATICA
    solicitud.set_problematica("x" * 800, "Vivienda")
    assert len(solicitud.get_problematica()) == SolicitudModel.LIMITE_PROBLEMATICA
    with pytest.raises(ValueError):
        SolicitudModel().set_problematica("")


@pytest.mark.parametrize(
    ("tipo", "payload", "expected_name_key"),
    [
        ("Comunidad", {"com_cedula": "12345678", "com_telefono": "0412-1234567",
                       "com_correo": "vecino@example.test", "com_municipio": "Iribarren",
                       "com_parroquia": "Concepción", "com_ambito": "Sector norte",
                       "com_nombre": "Comité", "com_sector": "Norte"}, "nombre_comunidad"),
        ("Institucion", {"inst_director_cedula": "12345678", "inst_telefono": "04121234567",
                         "inst_correo": "dir@example.test", "inst_municipio": "Torres",
                         "inst_parroquia": "Centro", "inst_direccion": "Calle 1",
                         "inst_director_nombre": "Ana", "inst_nombre": "Escuela"}, "razon_social"),
        ("Particular", {"part_cedula": "12345678", "part_telefono": "04241234567",
                        "part_correo": "p@example.test", "part_municipio": "Morán",
                        "part_parroquia": "Centro", "part_direccion": "Calle 2",
                        "part_nombre": "Luis", "part_apellido": "Pérez"}, "apellido"),
    ],
)
def test_solicitud_set_solicitante_data_for_each_type(tipo, payload, expected_name_key):
    solicitud = SolicitudModel()
    with pytest.raises(ValueError):
        solicitud.set_solicitante_data(payload)
    solicitud.set_tipo_solicitud(tipo)
    solicitud.set_solicitante_data(payload)
    assert solicitud._solicitante_data["tipo_solicitante"] == tipo
    assert solicitud._solicitante_data["cedula_persona"] == "12345678"
    assert solicitud._solicitante_data[expected_name_key]


def test_solicitud_set_solicitante_data_rejects_bad_fields():
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud("Particular")
    invalid = {
        "part_cedula": "12-34", "part_telefono": "000", "part_correo": "no-email",
        "part_municipio": "Municipio inventado", "part_parroquia": "",
    }
    with pytest.raises(ValueError, match="Cédula"):
        solicitud.set_solicitante_data(invalid)
    invalid["part_cedula"] = "12345678"
    with pytest.raises(ValueError, match="correo"):
        solicitud.set_solicitante_data(invalid)


def test_solicitud_private_connection_cleaning_and_date_helpers(monkeypatch):
    connection, cursor = _db()
    monkeypatch.setattr(SolicitudModel, "obtener_conexion", staticmethod(lambda: connection))
    assert SolicitudModel._con() is connection
    assert SolicitudModel._limpiar(" <a>; 'b'\\c ", 4) == "a bc"
    SolicitudModel._cerrar(connection, cursor)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
    model = SolicitudModel()
    assert model._formatear_fecha(None) == ""
    dt = datetime(2024, 2, 3, 16, 5, 6)
    assert model._formatear_fecha(dt) == "Sat 03-02-2024 04:05:06 PM"
    assert model._formatear_fecha("2024-02-03 16:05:06.000000") == "Sat 03-02-2024 04:05:06 PM"
    assert model._formatear_fecha("not-a-date") == "not-a-date"
    assert model._formatear_fecha(7) == "7"


@pytest.mark.parametrize(("row", "expected"), [({"id_persona": 8}, 8), ((9,), 9), (None, None)])
def test_solicitud_sql_buscar_persona_uses_bound_cedula(row, expected):
    _, cursor = _db(row=row)
    assert SolicitudModel()._sql_buscar_persona(cursor, "12345678") == expected
    cursor.execute.assert_called_once_with(
        "SELECT id_persona FROM persona WHERE cedula_persona = %s LIMIT 1", ("12345678",)
    )


def test_solicitud_sql_insertar_persona_binds_cleaned_values():
    _, cursor = _db()
    cursor.fetchone.side_effect = [(12,)]
    data = {"cedula_persona": "12.345.678", "direccion": "Calle", "parroquia": "Centro",
            "municipio": "Iribarren", "telefono": "04121234567", "correo": "a@b.test"}
    assert SolicitudModel()._sql_insertar_persona(cursor, data) == 12
    assert cursor.execute.call_args_list[1].args[1] == (
        12, 12345678, "Calle", "Centro", "Iribarren", "04121234567", "a@b.test"
    )


@pytest.mark.parametrize(
    ("tipo", "data_key", "id_field", "name_field"),
    [
        ("Particular", "nombre", "id_particular", "apellido"),
        ("Comunidad", "nombre_comunidad", "id_comunidad", "sector"),
        ("Institucion", "nombre_representante", "id_institucion", "razon_social"),
    ],
)
def test_solicitud_sql_insertar_subtipo_maps_each_kind(tipo, data_key, id_field, name_field):
    _, cursor = _db()
    cursor.fetchone.return_value = {"siguiente_id": 3}
    payload = {"tipo_solicitante": tipo, data_key: "Nombre", name_field: "Detalle"}
    SolicitudModel()._sql_insertar_subtipo(cursor, 10, payload)
    assert cursor.execute.call_count == 2
    if tipo == "Comunidad":
        assert cursor.execute.call_args.args[1] == (3, "Nombre", None, "Detalle", 10)
    else:
        assert cursor.execute.call_args.args[1] == (3, "Nombre", "Detalle", 10)


def test_solicitud_sql_crear_prioridad_pendiente_sets_defaults():
    _, cursor = _db()
    model = SolicitudModel()
    model.set_fecha("2024-01-01")
    assert model._sql_crear_prioridad_pendiente(cursor) == 41
    assert cursor.execute.call_args.args[1] == (
        1.0, "pendiente", "2024-01-01", "Sistema", "Pendiente de clasificación IA", 0
    )


def test_solicitud_asegurar_columna_alters_legacy_schema_and_closes_cursor():
    connection, cursor = _db(row=("problematica", "varchar(255)"))
    SolicitudModel._columna_problematica_verificada = False
    SolicitudModel._asegurar_columna_problematica(connection)
    assert "ALTER TABLE solicitudes" in cursor.execute.call_args_list[1].args[0]
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    assert SolicitudModel._columna_problematica_verificada is True
    SolicitudModel._columna_problematica_verificada = False


def test_solicitud_guardar_commits_insert_and_closes_resources(monkeypatch):
    connection, cursor = _db()
    cursor.lastrowid = 27
    _patch_solicitud_db(monkeypatch, connection)
    monkeypatch.setattr(SolicitudModel, "_asegurar_columna_problematica", staticmethod(lambda _c: None))
    solicitud = SolicitudModel()
    solicitud.set_tipo_solicitud("Particular")
    solicitud.set_problematica("La calle requiere reparaciones urgentes")
    solicitud._solicitante_data = {"cedula_persona": "12345678"}
    monkeypatch.setattr(solicitud, "_sql_buscar_persona", lambda *_: 9)
    monkeypatch.setattr(solicitud, "_sql_crear_prioridad_pendiente", lambda _c: 4)
    assert solicitud.guardar() == 27
    assert cursor.execute.call_args.args[1] == (
        solicitud._fecha, "Particular", "Pendiente",
        "La calle requiere reparaciones urgentes", 9, 4
    )
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_solicitud_guardar_rolls_back_failure_and_returns_false(monkeypatch):
    connection, cursor = _db()
    cursor.execute.side_effect = RuntimeError("insert failed")
    _patch_solicitud_db(monkeypatch, connection)
    monkeypatch.setattr(SolicitudModel, "_asegurar_columna_problematica", staticmethod(lambda _c: None))
    solicitud = SolicitudModel()
    solicitud._tipo_solicitud, solicitud._problematica = "Particular", "Una descripción válida y extensa"
    solicitud._solicitante_data = {"cedula_persona": "1"}
    monkeypatch.setattr(solicitud, "_sql_buscar_persona", lambda *_: 2)
    monkeypatch.setattr(solicitud, "_sql_crear_prioridad_pendiente", lambda _c: 3)
    assert solicitud.guardar() is False
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()


def test_solicitud_actualizar_delete_and_status_respect_rowcount(monkeypatch):
    connection, cursor = _db()
    cursor.rowcount = 0
    _patch_solicitud_db(monkeypatch, connection)
    monkeypatch.setattr(SolicitudModel, "_asegurar_columna_problematica", staticmethod(lambda _c: None))
    solicitud = SolicitudModel(6)
    solicitud._estatus_solicitud, solicitud._problematica = "Completada", "Descripción suficiente."
    assert solicitud.actualizar() is False
    assert cursor.execute.call_args.args[1] == ("Completada", "Descripción suficiente.", 6)
    cursor.rowcount = 1
    assert SolicitudModel.actualizar_estatus(6, "En Proceso") is True
    assert solicitud.eliminar() is True
    assert connection.commit.call_count == 3
    assert connection.close.call_count == 3


def test_solicitud_mutations_short_circuit_missing_ids_and_db_failure(monkeypatch):
    missing = SolicitudModel()
    assert missing.actualizar() is False
    assert missing.eliminar() is False
    connection, cursor = _db()
    cursor.execute.side_effect = RuntimeError("db issue")
    _patch_solicitud_db(monkeypatch, connection)
    assert SolicitudModel.actualizar_estatus(3, "X") is False
    connection.rollback.assert_called_once()


@pytest.mark.parametrize(
    ("method", "rows", "expected"),
    [
        ("obtener_todas", [{"id_solicitudes": 1, "fecha": "2024-02-03 16:05:06"}],
         [{"id_solicitudes": 1, "fecha": "2024-02-03 16:05:06", "fecha_formateada": "Sat 03-02-2024 04:05:06 PM"}]),
        ("obtener_estadisticas", [{"estatus_solicitud": "Pendiente", "total": 2}], {"Pendiente": 2}),
        ("obtener_estadisticas_por_tipo", [{"tipo_solicitud": "Comunidad", "total": 3}], {"Comunidad": 3}),
        ("obtener_estadisticas_por_parroquia", [{"parroquia": "Centro", "total": 1}], [{"parroquia": "Centro", "total": 1}]),
        ("obtener_solicitudes_pendientes", [{"fecha": None}], [{"fecha": None, "fecha_formateada": ""}]),
    ],
)
def test_solicitud_list_and_statistics_methods(method, rows, expected, monkeypatch):
    connection, cursor = _db(rows=rows)
    _patch_solicitud_db(monkeypatch, connection)
    assert getattr(SolicitudModel, method)() == expected
    cursor.execute.assert_called_once()
    connection.close.assert_called_once()


def test_solicitud_buscar_por_id_and_prioritized_query_bind_parameters(monkeypatch):
    connection, cursor = _db(row={"fecha": None, "id_solicitudes": 5})
    _patch_solicitud_db(monkeypatch, connection)
    found = SolicitudModel.buscar_por_id(5)
    assert found["fecha_formateada"] == ""
    assert cursor.execute.call_args.args[1] == (5,)

    connection2, cursor2 = _db(rows=[{"fecha": None}])
    _patch_solicitud_db(monkeypatch, connection2)
    assert SolicitudModel.obtener_solicitudes_priorizadas(4)[0]["fecha_formateada"] == ""
    assert cursor2.execute.call_args.args[1] == (4,)


def test_solicitud_query_methods_return_safe_defaults_without_connection(monkeypatch):
    _patch_solicitud_db(monkeypatch, None)
    assert SolicitudModel.obtener_todas() == []
    assert SolicitudModel.buscar_por_id(1) is None
    assert SolicitudModel.obtener_estadisticas() == {}
    assert SolicitudModel.obtener_estadisticas_por_tipo() == {}
    assert SolicitudModel.obtener_estadisticas_por_parroquia() == []
    assert SolicitudModel.obtener_solicitudes_priorizadas() == []
    assert SolicitudModel.obtener_solicitudes_pendientes() == []


# GravedadObraModel: entity validation and database operations.
def test_gravedad_constructor_getters_and_validating_setters():
    model = GravedadObraModel("Bajo", 20, 0, 3)
    assert (model.get_id(), model.get_nivel_gravedad(), model.get_criticidad()) == (3, "Bajo", 20)
    model.set_nivel_gravedad("  Crítica ")
    model.set_criticidad("75.8")
    assert model.get_nivel_gravedad() == "Crítica"
    assert model.get_criticidad() == 75
    for bad in ("A", "A1", "x" * 21):
        with pytest.raises(ValueError):
            model.set_nivel_gravedad(bad)
    for bad in ("NaN", -1, 101):
        with pytest.raises(ValueError):
            model.set_criticidad(bad)


def test_gravedad_register_retries_duplicate_then_commits(monkeypatch):
    connection, cursor = _db()
    cursor.fetchone.return_value = (7,)
    cursor.execute.side_effect = [None, RuntimeError(1062), None, None]
    _patch_gravedad = lambda: monkeypatch.setattr(
        GravedadObraModel, "obtener_conexion_estricta", lambda _self: connection
    )
    _patch_gravedad()
    model = GravedadObraModel("Alta", 80)
    assert model.registrar_gravedad() == 7
    assert connection.rollback.call_count == 1
    connection.commit.assert_called_once()
    assert cursor.execute.call_args_list[1].args[1] == (7, "Alta", 80, 1)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_gravedad_list_and_lookup_normalize_criticidad_and_level(monkeypatch):
    connection, cursor = _db(rows=[
        {"criticidad": 0.75, "nivel_gravedad": "baja"},
        {"criticidad": "invalid", "nivel_gravedad": "MEDIA"},
        {"criticidad": 25.9, "nivel_gravedad": "otra"},
    ])
    monkeypatch.setattr(GravedadObraModel, "obtener_conexion_estricta", lambda _self: connection)
    assert GravedadObraModel().consultar_activos() == [
        {"criticidad": 75, "nivel_gravedad": "Bajo"},
        {"criticidad": 0, "nivel_gravedad": "Alto"},
        {"criticidad": 25, "nivel_gravedad": "otra"},
    ]
    cursor.fetchone.return_value = {"criticidad": 0.5, "nivel_gravedad": "alto"}
    assert GravedadObraModel().obtener_gravedad_por_id(9) == {
        "criticidad": 50, "nivel_gravedad": "Alto"
    }
    assert cursor.execute.call_args.args[1] == (9,)


@pytest.mark.parametrize(("method", "rowcount", "expected"), [
    ("actualizar_gravedad", 1, True), ("eliminar_gravedad", 0, False),
])
def test_gravedad_updates_commit_and_report_rowcount(method, rowcount, expected, monkeypatch):
    connection, cursor = _db()
    cursor.rowcount = rowcount
    monkeypatch.setattr(GravedadObraModel, "obtener_conexion_estricta", lambda _self: connection)
    model = GravedadObraModel("Bajo", 10, id_gravedad=3)
    assert getattr(model, method)() is expected
    connection.commit.assert_called_once()
    connection.close.assert_called_once()
    if method == "eliminar_gravedad":
        assert cursor.execute.call_args.args[1] == (3,)


@pytest.mark.parametrize(("exclude", "row", "expected"), [(None, {"x": 1}, True), (7, None, False)])
def test_gravedad_validar_nivel_uses_optional_exclusion(exclude, row, expected, monkeypatch):
    connection, cursor = _db(row=row)
    monkeypatch.setattr(GravedadObraModel, "obtener_conexion_estricta", lambda _self: connection)
    model = GravedadObraModel("Bajo")
    assert model.validar_nivel_existente(exclude) is expected
    assert cursor.execute.call_args.args[1] == (("Bajo", exclude) if exclude else ("Bajo",))


# ProyectoModel: serializers, validation, transactional operations and aggregates.
def test_proyecto_constructor_and_metric_helpers_cover_legacy_and_json_values():
    assert ProyectoModel().__dict__ == {}
    assert ProyectoModel._parsear_computos_metricos(None) == []
    assert ProyectoModel._parsear_computos_metricos([]) == []
    source = [{"metrica": "Longitud", "opcion": "10 km", "costo": "500"}]
    encoded = ProyectoModel._serializar_computos_metricos(source)
    assert json.loads(encoded) == source
    assert ProyectoModel._parsear_computos_metricos(encoded) == source
    assert ProyectoModel._parsear_computos_metricos("  ") == []
    assert ProyectoModel._parsear_computos_metricos("10 km") == [
        {"metrica": "", "opcion": "10 km", "costo": ""}
    ]
    assert ProyectoModel._parsear_computos_metricos(4) == []
    assert ProyectoModel._serializar_computos_metricos(None) == "[]"
    assert ProyectoModel._serializar_computos_metricos(" ") == "[]"
    assert json.loads(ProyectoModel._serializar_computos_metricos([" 10 km ", "", None])) == [
        {"metrica": "", "opcion": "10 km", "costo": ""}
    ]
    assert ProyectoModel._serializar_computos_metricos("  [1] ") == "[1]"
    assert ProyectoModel._formatear_computos_metricos(source) == "500 Longitud 10 km"
    assert ProyectoModel._formatear_computos_metricos([{"metrica": "", "opcion": "", "costo": ""}]) == ""


def test_proyecto_ensure_description_column_alters_legacy_column():
    connection, cursor = _db(row=("descripcion_tecnica", "varchar(100)"))
    ProyectoModel()._asegurar_descripcion_tecnica(connection)
    assert "ALTER TABLE proyecto" in cursor.execute.call_args_list[1].args[0]
    connection.commit.assert_called_once()
    cursor.close.assert_called_once()


@pytest.mark.parametrize(("row", "expected"), [
    ({"estado": 1}, {"existe_activo": True}),
    ({"estado": 0}, {"existe_eliminado": True}),
    (None, {"disponible": True}),
])
def test_proyecto_validar_codigo_returns_state(row, expected, monkeypatch):
    connection, cursor = _db(row=row)
    model = ProyectoModel()
    monkeypatch.setattr(model, "obtener_conexion_estricta", lambda: connection)
    assert model.validar_codigo_proyecto("PR-1") == expected
    assert cursor.execute.call_args.args[1] == ("PR-1",)
    connection.close.assert_called_once()


def test_proyecto_registrar_binds_serialized_data_and_linked_resources(monkeypatch):
    connection, cursor = _db()
    cursor.fetchone.return_value = {"persona_id_persona": 4, "prioridad_id_gestion_prioridad": 8}
    monkeypatch.setattr(ProyectoModel, "validar_codigo_proyecto", lambda _self, _code: {"disponible": True})
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection)
    monkeypatch.setattr(ProyectoModel, "_asegurar_descripcion_tecnica", lambda *_: None)
    datos = {"Codigo_p": "P-100", "fecha_p": "2025-01-01", "observaciones": "Detalle",
             "computos_p": [{"metrica": "Km", "opcion": "2", "costo": "10"}],
             "estimacion_p": "100", "proyectista_p": "12", "solicitud_id_p": 5,
             "maquinaria_0": "7", "maquinaria_1": "n/a"}
    assert ProyectoModel().registrar_proyecto(datos) == 1
    insert_values = cursor.execute.call_args_list[0].args[1]
    assert insert_values[0] == "P-100"
    assert insert_values[2:6] == (
        "Detalle", json.dumps(datos["computos_p"]), "100", 12
    )
    assert (("P-100", 5, 4, 8)) in [c.args[1] for c in cursor.execute.call_args_list if len(c.args) > 1]
    assert (("P-100", 7)) in [c.args[1] for c in cursor.execute.call_args_list if len(c.args) > 1]
    connection.commit.assert_called_once()
    connection.close.assert_called_once()


def test_proyecto_registrar_rejects_existing_code_and_rolls_back_link_failure(monkeypatch):
    model = ProyectoModel()
    monkeypatch.setattr(model, "validar_codigo_proyecto", lambda _code: {"existe_activo": True})
    assert model.registrar_proyecto({"Codigo_p": "DUP"}) is False
    connection, cursor = _db()
    cursor.fetchone.return_value = None
    monkeypatch.setattr(model, "validar_codigo_proyecto", lambda _code: {"disponible": True})
    monkeypatch.setattr(model, "obtener_conexion_estricta", lambda: connection)
    monkeypatch.setattr(model, "_asegurar_descripcion_tecnica", lambda _c: None)
    assert model.registrar_proyecto({"Codigo_p": "P1", "solicitud_id_p": 9}) is False
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()


def test_proyecto_getters_normalize_metric_data_and_handle_missing_project(monkeypatch):
    connection, cursor = _db(rows=[{"computos_metricos": "10 km"}])
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection)
    project = ProyectoModel()
    projects = project.obtener_proyectos()
    assert projects[0]["computos_metricos"][0]["opcion"] == "10 km"
    assert projects[0]["computos_metricos_texto"] == "10 km"
    cursor.fetchone.return_value = None
    assert project.obtener_proyecto_por_id("P-1") is None
    assert cursor.execute.call_args.args[1] == ("P-1",)

    connection2, cursor2 = _db(row={"computos_metricos": '[{"opcion":"5 km"}]'})
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection2)
    found = project.obtener_proyecto_por_id("P-2")
    assert found["computos_metricos"] == [{"opcion": "5 km"}]
    assert found["computos_metricos_texto"] == "5 km"
    assert cursor2.execute.call_args.args[1] == ("P-2",)


def test_proyecto_detalle_returns_related_rows_and_empty_when_missing(monkeypatch):
    connection, cursor = _db()
    cursor.fetchone.return_value = {"computos_metricos": "[]"}
    cursor.fetchall.side_effect = [[{"id_solicitudes": 2}], [{"id_maquinaria": 3}]]
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection)
    result = ProyectoModel().obtener_detalle_proyecto_por_codigo("P-2")
    assert result["solicitudes"] == [{"id_solicitudes": 2}]
    assert result["maquinaria"] == [{"id_maquinaria": 3}]
    assert cursor.execute.call_count == 3

    connection2, cursor2 = _db(row=None)
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection2)
    assert ProyectoModel().obtener_detalle_proyecto_por_codigo("missing") is None
    assert cursor2.execute.call_count == 1


def test_proyecto_actualizar_handles_linked_request_machinery_and_commit(monkeypatch):
    connection, cursor = _db()
    cursor.fetchone.side_effect = [
        {"fecha_planificacion": "2024-01-01 10:00:00"},
        {"persona_id_persona": 2, "prioridad_id_gestion_prioridad": 6},
    ]
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection)
    monkeypatch.setattr(ProyectoModel, "_asegurar_descripcion_tecnica", lambda *_: None)
    data = {"Codigo_p": "P2", "observaciones_p": "Actualizado", "solicitud_id_p": 3,
            "computos_p": [], "estimacion_p": "20", "proyectista_p": "bad", "maquinaria_0": "9"}
    assert ProyectoModel().actualizar_proyecto("P1", data) is True
    update_values = cursor.execute.call_args_list[1].args[1]
    assert update_values == ("P2", "2024-01-01 10:00:00", "Actualizado", "", "20", None, "P1")
    assert ("P2", 9) in [c.args[1] for c in cursor.execute.call_args_list if len(c.args) > 1]
    connection.commit.assert_called_once()


def test_proyecto_eliminar_and_counters_report_database_results(monkeypatch):
    connection, cursor = _db(rows=[
        {"tipo_solicitud": "En Proceso"}, {"tipo_solicitud": "Completada"},
        {"tipo_solicitud": "Finalizado"}, {"tipo_solicitud": "Comunidad"},
    ])
    monkeypatch.setattr(ProyectoModel, "obtener_conexion_estricta", lambda _self: connection)
    model = ProyectoModel()
    assert model.eliminar_proyecto("P1") is True
    assert model.obtener_contadores_proyectos() == {
        "total_registrados": 4, "en_proceso": 1, "completadas": 2, "total": 4
    }
    assert connection.commit.call_count == 1
    assert connection.close.call_count == 2


# PrioridadModel: constructor/properties, validation, persistence and classification.
def test_prioridad_constructor_getters_setters_and_validation_boundaries():
    model = PrioridadModel(1, 2, 0.5, "Motivo válido", "Ana", 1, "Obra Mayor", "Alta", "ia")
    assert (model.get_id(), model.get_solicitud_id(), model.get_rango()) == (1, 2, 0.5)
    assert (model.get_justificacion(), model.get_responsable(), model.get_estado()) == (
        "Motivo válido", "Ana", 1
    )
    assert (model.get_origen(), model.get_tipo_obra(), model.get_gravedad_sugerida()) == (
        "ia", "Obra Mayor", "Alta"
    )
    model.set_rango("0.7564")
    model.set_justificacion("Ajuste por urgencia")
    model.set_responsable("Luis 2")
    model.set_estado("0")
    model.set_origen("heuristica")
    model.set_tipo_obra("Obra Menor")
    model.set_gravedad_sugerida("Baja")
    assert model.get_rango() == 0.756
    assert model.get_estado() == 0
    assert model.get_origen() == "heuristica"
    for setter, bad in [
        (model.set_rango, 1.01), (model.set_justificacion, "x"),
        (model.set_responsable, "!"), (model.set_origen, "bad"),
        (model.set_tipo_obra, "Obra"), (model.set_gravedad_sugerida, "Media"),
    ]:
        with pytest.raises(ValueError):
            setter(bad)


def test_prioridad_persistence_validation_and_sql_transactions(monkeypatch):
    invalid = PrioridadModel()
    with pytest.raises(ValueError, match="obligatoria"):
        invalid._validar_para_persistencia()
    model = PrioridadModel(rango_prioridad=0.25, justificacion="Motivo suficiente")
    model._validar_para_persistencia()
    connection, cursor = _db()
    _patch_prioridad_db(monkeypatch, connection)
    assert model.registrar() == 41
    assert cursor.execute.call_args.args[1][0:4] == (0.25, None, None, "manual")
    assert connection.commit.call_count == 1

    cursor.rowcount = 0
    assert model.actualizar() is False
    assert model.eliminar_logico() is False
    assert connection.commit.call_count == 3
    assert cursor.execute.call_args.args[1] == (41,)
    assert cursor.close.call_count == 3
    assert connection.close.call_count == 3


@pytest.mark.parametrize(("method", "row", "expected"), [
    ("obtener_detalle_completo", {"id_gestion_prioridad": 2}, {"id_gestion_prioridad": 2}),
    ("obtener_por_id", {"id_gestion_prioridad": 3}, {"id_gestion_prioridad": 3}),
    ("obtener_datos_solicitud", {"descripcion": "d"}, {"descripcion": "d"}),
    ("obtener_gravedad_obra", {"id_gravedad": 4}, {"id_gravedad": 4}),
])
def test_prioridad_single_row_queries_bind_id_and_close_resources(method, row, expected, monkeypatch):
    connection, cursor = _db(row=row)
    _patch_prioridad_db(monkeypatch, connection)
    assert getattr(PrioridadModel, method)(8) == expected
    assert cursor.execute.call_args.args[1] == (8,)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_prioridad_list_query_filters_orders_pages_and_normalizes(monkeypatch):
    connection, cursor = _db()
    cursor.fetchone.return_value = {"total": 6}
    cursor.fetchall.return_value = [{"rango_prioridad": "0.125"}]
    _patch_prioridad_db(monkeypatch, connection)
    rows, total = PrioridadModel.listar_priorizadas(
        page=2, per_page=5, q="vial", riesgo="ALTA", orden="fecha_desc"
    )
    assert rows == [{"rango_prioridad": 0.125}]
    assert total == 6
    count_sql, count_params = cursor.execute.call_args_list[0].args
    assert "LIKE %s" in count_sql and "p.rango_prioridad <= 0.30" in count_sql
    assert count_params == ["%vial%"] * 12
    listing_sql, listing_params = cursor.execute.call_args_list[1].args
    assert "ORDER BY p.fecha_asignacion DESC" in listing_sql
    assert listing_params == ("%vial%",) * 12 + (5, 5)
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize("method", ["obtener_solicitudes_sin_priorizar", "obtener_todas_solicitudes"])
def test_prioridad_solicitud_lists_return_rows(method, monkeypatch):
    connection, cursor = _db(rows=[{"id": 4}])
    _patch_prioridad_db(monkeypatch, connection)
    assert getattr(PrioridadModel, method)() == [{"id": 4}]
    cursor.execute.assert_called_once()
    assert cursor.execute.call_args.args[1] == ()
    connection.close.assert_called_once()


def test_prioridad_weighted_score_handles_known_and_invalid_inputs():
    score = PrioridadModel._calcular_puntaje_ponderado("Comunidad", 3, "Obra Mayor", 3)
    assert score == {
        "puntaje_ponderado": 3.0, "rango_prioridad": 0.0, "peso_solicitante": 3,
        "peso_gravedad": 3, "peso_tipo_obra": 3, "peso_zona_agricola": 3,
    }
    fallback = PrioridadModel._calcular_puntaje_ponderado(None, "bad", "bad", None)
    assert fallback["peso_solicitante"] == fallback["peso_gravedad"] == 1
    assert fallback["peso_tipo_obra"] == fallback["peso_zona_agricola"] == 1


def test_prioridad_clasificar_nueva_solicitud_not_found_and_insert(monkeypatch):
    monkeypatch.setattr(PrioridadModel, "obtener_datos_solicitud", staticmethod(lambda _id: None))
    assert PrioridadModel.clasificar_nueva_solicitud(99) == {
        "success": False, "message": "Solicitud no encontrada."
    }
    monkeypatch.setattr(PrioridadModel, "obtener_datos_solicitud", staticmethod(
        lambda _id: {"descripcion": "Bache", "tipo_solicitante": "Comunidad"}
    ))
    import services.ia_prioridad_service as service
    monkeypatch.setattr(service, "clasificar_solicitud_ia", lambda *_: {
        "gravedad_valor": 3, "tipo_obra": "Obra Mayor", "es_zona_agricola": 3,
        "justificacion": "Daño urgente", "origen": "ia"
    })
    connection, cursor = _db()
    cursor.fetchone.return_value = {"pid": None}
    _patch_prioridad_db(monkeypatch, connection)
    result = PrioridadModel.clasificar_nueva_solicitud(5, "Robot")
    assert result["success"] is True
    assert result["data"]["id_prioridad"] == 41
    assert result["data"]["justificacion"] == "Daño urgente"
    assert connection.commit.call_count == 1
    assert cursor.execute.call_args_list[-1].args[1] == (41, 5)


def test_prioridad_clasificar_nueva_solicitud_updates_existing_priority(monkeypatch):
    monkeypatch.setattr(PrioridadModel, "obtener_datos_solicitud", staticmethod(
        lambda _id: {"descripcion": "Bache"}
    ))
    import services.ia_prioridad_service as service
    monkeypatch.setattr(service, "clasificar_solicitud_ia", lambda *_: {
        "gravedad_valor": 1, "tipo_obra": "Obra Menor", "es_zona_agricola": 1
    })
    connection, cursor = _db()
    cursor.fetchone.side_effect = [{"pid": 7}, {"id_gestion_prioridad": 7}]
    _patch_prioridad_db(monkeypatch, connection)
    result = PrioridadModel.clasificar_nueva_solicitud(3)
    assert result["success"] is True and result["data"]["id_prioridad"] == 7
    assert connection.commit.call_count == 1
    assert "UPDATE prioridad" in cursor.execute.call_args.args[0]


@pytest.mark.parametrize(
    ("method", "source_method", "empty_message", "complete_message"),
    [
        ("procesar_solicitudes_pendientes_batch", "obtener_solicitudes_sin_priorizar",
         "No hay solicitudes pendientes.", "Proceso completado."),
        ("procesar_todas_solicitudes_batch", "obtener_todas_solicitudes",
         "No hay solicitudes para procesar.", "Re-clasificación completada."),
    ],
)
def test_prioridad_batch_processing_empty_and_successful(
    method, source_method, empty_message, complete_message, monkeypatch
):
    monkeypatch.setattr(PrioridadModel, source_method, staticmethod(lambda: []))
    assert getattr(PrioridadModel, method)()["message"] == empty_message
    monkeypatch.setattr(PrioridadModel, source_method, staticmethod(lambda: [{"id": 8}]))
    monkeypatch.setattr(PrioridadModel, "clasificar_nueva_solicitud", staticmethod(
        lambda *_: {"success": True, "data": {"id_prioridad": 4, "rango": 0.3,
                                               "tipo_obra": "Obra Mayor", "gravedad_sugerida": "Alta"}}
    ))
    result = getattr(PrioridadModel, method)("Analista")
    assert result["success"] is True
    assert result["procesadas"] == 1
    assert result["detalle"][0]["solicitud_id"] == 8
    assert result["message"].startswith(complete_message)


def test_prioridad_clasificar_solicitud_con_ia_inserts_and_updates(monkeypatch):
    import services.ia_prioridad_service as service
    monkeypatch.setattr(service, "calcular_prioridad_con_ia", lambda *_: {
        "prioridad": 0.2, "justificacion": "Manual", "tipo_obra": "Obra Mayor",
        "gravedad_sugerida": "Alta", "origen": "ia"
    })
    connection, cursor = _db()
    cursor.fetchone.side_effect = [{"pid": None}, {"siguiente_id": 14}, {"pid": 9}]
    _patch_prioridad_db(monkeypatch, connection)
    assert PrioridadModel.clasificar_solicitud_con_ia(2, "D") == {
        "id_prioridad": 14, "rango": 0.2, "justificacion": "Manual"
    }
    assert connection.commit.call_count == 1
    assert cursor.execute.call_args_list[-1].args[1] == (14, 2)

    cursor.fetchone.return_value = {"pid": 9}
    assert PrioridadModel.clasificar_solicitud_con_ia(2, "D")["id_prioridad"] == 9


# MaquinariaModel: validation, pagination, soft-delete and restoration.
def test_maquinaria_query_methods_bind_pagination_and_return_counts(monkeypatch):
    connection, cursor = _db(rows=[{"id_maquinaria": 3}])
    monkeypatch.setattr(MaquinariaModel, "obtener_conexion_estricta", lambda _self: connection)
    model = MaquinariaModel()
    assert model.obtener_maquinarias(3, 4) == [{"id_maquinaria": 3}]
    assert cursor.execute.call_args.args[1] == (4, 8)
    cursor.fetchone.return_value = (11,)
    assert model.contar_maquinarias() == 11
    cursor.fetchall.return_value = [{"id_maquinaria": 2, "estado": 0}]
    assert model.obtener_maquinarias_eliminadas() == [{"id_maquinaria": 2, "estado": 0}]
    assert connection.close.call_count == 3


def test_maquinaria_validation_accepts_catalog_and_rejects_boundaries():
    model = MaquinariaModel()
    assert model.validar_nombre(" Excavadora-1 ") == {"valido": True}
    assert model.validar_nombre("")["valido"] is False
    assert model.validar_nombre("AB")["valido"] is False
    assert model.validar_nombre("Bomba/*")["valido"] is False
    assert model.validar_tipo("Vehículo") == {"valido": True}
    assert model.validar_tipo("vehículo")["valido"] is False


@pytest.mark.parametrize(("rowcount", "expected"), [
    (1, {"success": True, "message": "Maquinaria restaurada correctamente"}),
    (0, {"success": False, "message": "Maquinaria no encontrada o ya está activa"}),
])
def test_maquinaria_restore_returns_rowcount_status(rowcount, expected, monkeypatch):
    connection, cursor = _db()
    cursor.rowcount = rowcount
    monkeypatch.setattr(MaquinariaModel, "obtener_conexion_estricta", lambda _self: connection)
    assert MaquinariaModel().restaurar_maquinaria(5) == expected
    assert cursor.execute.call_args.args[1] == (5,)
    connection.commit.assert_called_once()


def test_maquinaria_registro_validation_duplicate_restore_and_insert(monkeypatch):
    model = MaquinariaModel()
    assert model.registrar_maquinaria("AB", "Pesada")["success"] is False
    connection, cursor = _db()
    cursor.fetchone.return_value = {"id_maquinaria": 8, "estado": 1}
    monkeypatch.setattr(model, "obtener_conexion_estricta", lambda: connection)
    assert model.registrar_maquinaria("Excavadora", "Pesada")["success"] is False
    cursor.fetchone.return_value = {"id_maquinaria": 8, "estado": 0}
    restored = model.registrar_maquinaria("Excavadora", "Pesada")
    assert restored["restaurada"] is True and restored["id"] == 8
    assert connection.commit.call_count == 1

    cursor.fetchone.side_effect = [None, (9,)]
    cursor.lastrowid = 10
    inserted = model.registrar_maquinaria("Cargador", "Liviana")
    assert inserted["success"] is True and inserted["id"] == 10
    assert cursor.execute.call_args_list[-1].args[1] == (9, "Cargador", "Liviana")
    assert connection.commit.call_count == 2


def test_maquinaria_lookup_update_and_delete_branches(monkeypatch):
    connection, cursor = _db(row={"id_maquinaria": 5})
    monkeypatch.setattr(MaquinariaModel, "obtener_conexion_estricta", lambda _self: connection)
    model = MaquinariaModel()
    assert model.obtener_maquinaria_por_id(5) == {"id_maquinaria": 5}
    assert cursor.execute.call_args.args[1] == (5,)
    assert model.actualizar_maquinaria(5, "Grúa", "Pesada")["success"] is True
    assert cursor.execute.call_args.args[1] == ("Grúa", "Pesada", 5)
    cursor.fetchone.return_value = {"count": 1}
    assert model.eliminar_maquinaria(5) == "utilizada"
    cursor.fetchone.return_value = (0,)
    assert model.eliminar_maquinaria(5) == "eliminada"
    assert connection.commit.call_count == 2


# ContratacionModel: private validator and all public operations.
def test_contratacion_private_validator_checks_required_fields_choices_and_dates():
    model = ContratacionModel()
    data = _valid_contratacion()
    assert model._ContratacionModel__validar_datos(data) == (True, "Validación exitosa")
    for key in data:
        invalid = dict(data)
        invalid[key] = ""
        assert model._ContratacionModel__validar_datos(invalid)[0] is False
    bad = dict(data, descripcion="abcd")
    assert "5 caracteres" in model._ContratacionModel__validar_datos(bad)[1]
    assert "3 caracteres" in model._ContratacionModel__validar_datos(dict(data, numero_contrato="1"))[1]
    assert "Tipo" in model._ContratacionModel__validar_datos(dict(data, tipo_contrato="Otro"))[1]
    assert "Modalidad" in model._ContratacionModel__validar_datos(dict(data, modalidad="Otro"))[1]
    assert "Objeto" in model._ContratacionModel__validar_datos(dict(data, objeto="Otro"))[1]
    assert "Formato de fecha" in model._ContratacionModel__validar_datos(
        dict(data, fecha_adjudicacion="01/02/2024")
    )[1]
    assert "Error crítico" in model._ContratacionModel__validar_datos(None)[1]


def test_contratacion_register_inserts_and_covers_duplicate_conflicts(monkeypatch):
    model = ContratacionModel()
    connection, cursor = _db()
    cursor.fetchone.return_value = (5,)
    monkeypatch.setattr(model, "obtener_conexion", lambda: connection)
    assert model.registrar_contrataciones(_valid_contratacion()) == (
        True, "Contratación registrada correctamente."
    )
    assert cursor.execute.call_args_list[-1].args[1][0] == 5
    connection.commit.assert_called_once()
    assert connection.close.call_count == 1

    cursor.execute.side_effect = [None, Exception("1062 Duplicate PRIMARY id_contratacion"), None,
                                  Exception("1062 Duplicate PRIMARY id_contratacion"), None,
                                  Exception("1062 Duplicate PRIMARY id_contratacion")]
    assert model.registrar_contrataciones(_valid_contratacion())[0] is False
    assert connection.close.call_count == 2


def test_contratacion_reads_update_delete_and_company_query(monkeypatch):
    connection, cursor = _db(rows=[{"id_contratacion": 1}], row={"id_contratacion": 1})
    model = ContratacionModel()
    monkeypatch.setattr(model, "obtener_conexion", lambda: connection)
    assert model.obtener_todas_las_contrataciones() == [{"id_contratacion": 1}]
    assert model.obtener_contratacion_por_id(1) == {"id_contratacion": 1}
    assert cursor.execute.call_args.args[1] == (1,)
    data = dict(_valid_contratacion(), id_contratacion=1)
    assert model.actualizar_contratacion(data) == (True, "Contratación modificada correctamente.")
    assert cursor.execute.call_args.args[1][-1] == 1
    assert model.eliminar_contratacion(1) is True
    assert cursor.execute.call_args.args[1] == (1,)
    assert model.obtener_empresas() == [{"id_contratacion": 1}]
    assert connection.commit.call_count == 2
    assert connection.close.call_count == 5


def test_contratacion_rejects_invalid_update_and_handles_missing_connection(monkeypatch):
    model = ContratacionModel()
    assert model.actualizar_contratacion({})[0] is False
    invalid = dict(_valid_contratacion())
    assert "Falta el ID" in model.actualizar_contratacion(invalid)[1]
    monkeypatch.setattr(model, "obtener_conexion", lambda: None)
    assert model.registrar_contrataciones(_valid_contratacion())[0] is False
    assert model.obtener_todas_las_contrataciones() == []
    assert model.obtener_contratacion_por_id(1) is None
    assert model.actualizar_contratacion(dict(_valid_contratacion(), id_contratacion=1))[0] is False
    assert model.eliminar_contratacion(1) is False
    assert model.obtener_empresas() == []
