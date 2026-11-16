from unittest.mock import MagicMock

from models.model_ReporteEstadistico import ReporteEstadisticoModel
from models.model_bitacora import BitacoraModel
from models.model_contratacion import ContratacionModel
from models.model_empleados import EmpleadoModel
from models.model_empresas import EmpresaModel
from models.model_evidencia import EvidenciaModel
from models.model_gravedad import GravedadObraModel
from models.model_informe_avance import InformeAvanceModel
from models.model_inspeccion import InspeccionModel
from models.model_maquinaria import MaquinariaModel
from models.model_obra import ObraModel
from models.model_prioridad import PrioridadModel
from models.model_proyecto import ProyectoModel
from models.model_publicaciones import PublicacionModel
from models.model_reportesExcel import ReporteExcelModel
from models.model_reportesPDF import ReportePDFModel
from models.model_respaldo import RespaldoModel
from models.model_seguridad import ModuloModel, RolPermisoModel
from models.model_solicitudes import SolicitudModel
from models.model_usuarios import UsuarioModel


def _database(rows=None, row=None):
    cursor = MagicMock()
    cursor.fetchall.return_value = rows if rows is not None else []
    cursor.fetchone.return_value = row
    connection = MagicMock()
    connection.cursor.return_value = cursor
    return connection, cursor


def test_usuario_buscar_por_email_usa_parametro_y_cierra_recursos(monkeypatch):
    row = {'id_usuarios': 8, 'correo': 'ana@example.test'}
    connection, cursor = _database(row=row)
    model = UsuarioModel.__new__(UsuarioModel)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: connection)

    assert model.buscar_por_email('ana@example.test') == row

    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_solicitud_buscar_por_id_devuelve_fila(monkeypatch):
    row = {'id_solicitudes': 7, 'problematica': 'Prueba'}
    connection, cursor = _database(row=row)
    monkeypatch.setattr(
        SolicitudModel,
        '_con',
        staticmethod(lambda: connection),
    )
    monkeypatch.setattr(
        SolicitudModel,
        '_cerrar',
        staticmethod(lambda *_args: None),
    )

    assert SolicitudModel.buscar_por_id(7) == row
    cursor.execute.assert_called_once()


def test_modulo_consultar_activos_devuelve_filas(monkeypatch):
    rows = [{'id_modulo': 2, 'nombre': 'obras', 'estado': 1}]
    connection, cursor = _database(rows=rows)
    model = ModuloModel.__new__(ModuloModel)
    monkeypatch.setattr(model, 'obtener_conexion_seguridad', lambda: connection)

    assert model.consultar_activos() == rows
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_respaldo_listar_respaldos_devuelve_lista_vacia_sin_registros(monkeypatch):
    connection, cursor = _database()
    model = RespaldoModel.__new__(RespaldoModel)
    monkeypatch.setattr(model, '_asegurar_tabla_seguridad', lambda: None)
    monkeypatch.setattr(
        model,
        'obtener_conexion_seguridad_segura',
        lambda: connection,
    )

    assert model.listar_respaldos() == []
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_reporte_pdf_obtener_solicitudes_delega_consulta(monkeypatch):
    rows = [{'id_solicitudes': 3}]
    model = ReportePDFModel.__new__(ReportePDFModel)
    consultas = []
    monkeypatch.setattr(
        model,
        '_ejecutar_query',
        lambda query, params: consultas.append((query, params)) or rows,
    )

    assert model.obtener_solicitudes() == rows
    assert len(consultas) == 1


def test_reporte_excel_obtener_solicitudes_delega_consulta(monkeypatch):
    rows = [{'id_solicitudes': 4}]
    model = ReporteExcelModel.__new__(ReporteExcelModel)
    consultas = []
    monkeypatch.setattr(
        model,
        '_ejecutar_query',
        lambda query, params: consultas.append((query, params)) or rows,
    )

    assert model.obtener_solicitudes_reporte() == rows
    assert len(consultas) == 1


def test_reporte_estadistico_consulta_publicaciones_devuelve_agregados(monkeypatch):
    por_tipo = [{'label': 'Aviso', 'valor': 2}]
    por_autor = [{'label': 'Ana', 'valor': 2}]
    por_fecha = [{'label': '2026-01-01', 'valor': 2}]
    connection, cursor = _database()
    cursor.fetchall.side_effect = [por_tipo, por_autor, por_fecha]
    model = ReporteEstadisticoModel.__new__(ReporteEstadisticoModel)
    monkeypatch.setattr(
        model,
        'obtener_conexion_estricta',
        lambda: connection,
    )

    resultado = model.obtener_estadisticas_publicaciones()

    assert resultado == {
        'por_tipo': por_tipo,
        'por_autor': por_autor,
        'por_fecha': por_fecha,
    }
    connection.close.assert_called_once()


def test_publicaciones_obtener_todas_devuelve_filas(monkeypatch):
    rows = [{'id_publicacion': 5}]
    connection, cursor = _database(rows=rows)
    model = PublicacionModel.__new__(PublicacionModel)
    monkeypatch.setattr(model, 'obtener_conexion', lambda: connection)

    assert model.obtener_todas_las_publicaciones() == rows
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_informe_obtener_todos_delega_en_consulta_db(monkeypatch):
    rows = [{'id_informe': 9}]
    model = InformeAvanceModel.__new__(InformeAvanceModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_InformeAvanceModel__obtener_todos_informes_db',
        lambda: llamadas.append(True) or rows,
    )

    assert model.obtener_todos_informes() == rows
    assert llamadas == [True]


def test_gravedad_consultar_activos_devuelve_filas(monkeypatch):
    rows = [{'id_gravedad': 1, 'estado': 1}]
    connection, cursor = _database(rows=rows)
    model = GravedadObraModel.__new__(GravedadObraModel)
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)

    assert model.consultar_activos() == rows
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_evidencias_obtener_todas_pasa_paginacion_al_repo(monkeypatch):
    rows = [{'id_evidencia': 2}]
    model = EvidenciaModel.__new__(EvidenciaModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_EvidenciaModel__obtener_todas_evidencias_db',
        lambda page, per_page: llamadas.append((page, per_page)) or rows,
    )

    assert model.obtener_todas_evidencias(page=2, per_page=5) == rows
    assert llamadas == [(2, 5)]


def test_empresa_obtener_todas_delega_consulta(monkeypatch):
    rows = [{'rif': 'J-123'}]
    model = EmpresaModel.__new__(EmpresaModel)
    consultas = []
    monkeypatch.setattr(
        model,
        '_ejecutar_consulta',
        lambda sql: consultas.append(sql) or rows,
    )

    assert model.obtener_todas_las_empresas() == rows
    assert len(consultas) == 1


def test_empleado_obtener_todos_delega_en_consulta_db(monkeypatch):
    rows = [{'id_empleados': 3}]
    model = EmpleadoModel.__new__(EmpleadoModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_EmpleadoModel__obtener_todos_empleados_db',
        lambda: llamadas.append(True) or rows,
    )

    assert model.obtener_todos_empleados() == rows
    assert llamadas == [True]


def test_contratacion_obtener_todas_devuelve_filas(monkeypatch):
    rows = [{'id_contratacion': 6}]
    connection, cursor = _database(rows=rows)
    model = ContratacionModel.__new__(ContratacionModel)
    monkeypatch.setattr(model, 'obtener_conexion', lambda: connection)

    assert model.obtener_todas_las_contrataciones() == rows
    cursor.execute.assert_called_once()
    connection.close.assert_called_once()


def test_bitacora_obtener_todos_delega_limite_y_resultado(monkeypatch):
    rows = [{'id_bitacora': 1}]
    model = BitacoraModel.__new__(BitacoraModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_sql_obtener_todos',
        lambda limit=None: llamadas.append(limit) or rows,
    )

    assert model.obtener_todos(limit=12) == rows
    assert llamadas == [12]


def test_obra_obtener_todas_delega_consulta_sql(monkeypatch):
    rows = [{'id_obra': 4}]
    model = ObraModel.__new__(ObraModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_sql_obtener_todas',
        lambda: llamadas.append(True) or rows,
    )

    assert model.obtener_todas() == rows
    assert llamadas == [True]


def test_maquinaria_obtener_lista_devuelve_filas_paginadas(monkeypatch):
    rows = [{'id_maquinaria': 3}]
    connection, cursor = _database(rows=rows)
    model = MaquinariaModel.__new__(MaquinariaModel)
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: connection)

    assert model.obtener_maquinarias(page=2, per_page=5) == rows
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


def test_inspeccion_obtener_todas_delega_en_consulta_db(monkeypatch):
    rows = [{'id_inspeccion': 8}]
    model = InspeccionModel.__new__(InspeccionModel)
    llamadas = []
    monkeypatch.setattr(
        model,
        '_InspeccionModel__obtener_todas_inspecciones_db',
        lambda: llamadas.append(True) or rows,
    )

    assert model.obtener_todas_inspecciones() == rows
    assert llamadas == [True]


def test_proyecto_obtener_lista_sin_conexion_es_vacia(monkeypatch):
    model = ProyectoModel.__new__(ProyectoModel)
    monkeypatch.setattr(model, 'obtener_conexion_estricta', lambda: None)

    assert model.obtener_proyectos() == []


def test_prioridad_buscar_por_id_devuelve_fila(monkeypatch):
    row = {'id_prioridad': 7, 'rango_prioridad': 8.5}
    connection, cursor = _database(row=row)
    monkeypatch.setattr(
        PrioridadModel,
        'obtener_conexion_estricta',
        staticmethod(lambda: connection),
    )

    assert PrioridadModel.obtener_por_id(7) == row
    cursor.execute.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
