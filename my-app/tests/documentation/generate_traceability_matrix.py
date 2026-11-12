"""Generate the INVISAP traceability matrix using the supplied Word template."""

from __future__ import annotations

import argparse
from copy import deepcopy
from pathlib import Path
import zipfile
import xml.etree.ElementTree as ET


WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
NS = {"w": WORD_NS}

ET.register_namespace("w", WORD_NS)
ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")


def tag(local_name: str) -> str:
    return f"{{{WORD_NS}}}{local_name}"


def paragraph_text(paragraph: ET.Element) -> str:
    return "".join(node.text or "" for node in paragraph.findall(".//w:t", NS))


def set_paragraph_text(
    paragraph: ET.Element,
    text: str,
    run_properties: ET.Element | None = None,
    font_size: int | None = None,
) -> None:
    paragraph_properties = paragraph.find("w:pPr", NS)
    for child in list(paragraph):
        if child is not paragraph_properties:
            paragraph.remove(child)

    lines = text.split("\n")
    for index, line in enumerate(lines):
        run = ET.SubElement(paragraph, tag("r"))
        if run_properties is not None:
            properties = deepcopy(run_properties)
            if font_size is not None:
                for size_tag in ("sz", "szCs"):
                    size = properties.find(f"w:{size_tag}", NS)
                    if size is None:
                        size = ET.SubElement(properties, tag(size_tag))
                    size.set(tag("val"), str(font_size))
            run.append(properties)
        if line:
            value = ET.SubElement(run, tag("t"))
            value.set(f"{{{XML_NS}}}space", "preserve")
            value.text = line
        if index < len(lines) - 1:
            ET.SubElement(run, tag("br"))


def set_cell_text(cell: ET.Element, text: str, font_size: int = 16) -> None:
    paragraph = cell.find("w:p", NS)
    if paragraph is None:
        paragraph = ET.SubElement(cell, tag("p"))
    sample_run = paragraph.find("w:r/w:rPr", NS)
    if sample_run is not None:
        for bold_tag in ("b", "bCs"):
            bold = sample_run.find(f"w:{bold_tag}", NS)
            if bold is not None:
                sample_run.remove(bold)
    set_paragraph_text(paragraph, text, sample_run, font_size)
    for extra in cell.findall("w:p", NS)[1:]:
        cell.remove(extra)


def set_cell_width(cell: ET.Element, width: int) -> None:
    properties = cell.find("w:tcPr", NS)
    if properties is None:
        properties = ET.SubElement(cell, tag("tcPr"))
    cell_width = properties.find("w:tcW", NS)
    if cell_width is None:
        cell_width = ET.SubElement(properties, tag("tcW"))
    cell_width.set(tag("w"), str(width))
    cell_width.set(tag("type"), "dxa")


def _row(
    requirement_id: str,
    requirement: str,
    case_ids: str,
    test_type: str,
    procedure: str,
    expected: str,
) -> tuple[str, str, str, str, str, str]:
    return requirement_id, requirement, case_ids, test_type, procedure, expected


MATRIX_ROWS = [
    _row("RF-01", "Gestión de solicitudes: registrar, consultar, actualizar y desactivar solicitudes.", "CP-UNI-RF01-01..43\nCP-INT-RF01-01\nCP-API-RF01-01\nCP-POST-RF01-01\nCP-HUM-RF01-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_solicitudes.py: 43 casos para los 30 métodos públicos/privados, con dobles para SQL; además suites de integración/API/humo. Postman consulta la lista JSON.", "Pytest local aprobado. Postman definido pero no ejecutado; consulta autenticada y persistencia real pendientes."),
    _row("RF-02", "Catálogo y clasificación de gravedad de obras.", "CP-UNI-RF02-01..11\nCP-INT-RF02-01\nCP-API-RF02-01\nCP-POST-RF02-01\nCP-HUM-RF02-01", "Unidad (límites); integración; backend/API; Postman (pendiente); humo", "tests/unit/test_gravedad_obra.py: 11 casos; Postman consulta catálogo JSON.", "Pytest local aprobado. Postman requiere cookie válida y sigue pendiente de ejecución."),
    _row("RF-03", "Cálculo y clasificación de prioridad de solicitudes.", "CP-UNI-RF03-01..31\nCP-INT-RF03-01\nCP-API-RF03-01\nCP-POST-RF03-01\nCP-HUM-RF03-01", "Unidad (equivalencia/límites); integración; backend/API; Postman (pendiente); humo", "tests/unit/test_prioridad.py: 31 casos sobre cálculos, validación y operaciones SQL; Postman consulta prioridad con filtros.", "Pytest local aprobado. Postman requiere cookie válida y sigue pendiente de ejecución."),
    _row("RF-04", "Administración de cuentas de usuario.", "CP-UNI-RF04-01..19\nCP-INT-RF04-01\nCP-API-RF04-01\nCP-POST-RF04-01\nCP-HUM-RF04-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_usuarios.py: 19 casos; Postman consulta un usuario por ID.", "Pytest local aprobado. Postman requiere cookie e ID válidos; ciclo de cuenta desactivada pendiente."),
    _row("RF-05", "Gestión de empleados.", "CP-UNI-RF05-01..14\nCP-INT-RF05-01\nCP-API-RF05-01\nCP-POST-RF05-01\nCP-HUM-RF05-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_empleados.py: 14 casos; limpieza/validación; Postman consulta listado paginado.", "Pytest local aprobado. Solicitud Postman requiere sesión y sigue pendiente."),
    _row("RF-06", "Gestión de empresas.", "CP-UNI-RF06-01..09\nCP-INT-RF06-01\nCP-API-RF06-01\nCP-POST-RF06-01\nCP-HUM-RF06-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_empresa.py: 9 casos sobre RIF, duplicidad y acceso SQL; Postman consulta empresa por RIF.", "Pytest local aprobado. Postman requiere cookie y RIF existente."),
    _row("RF-07", "Gestión de maquinaria.", "CP-UNI-RF07-01..20\nCP-INT-RF07-01\nCP-API-RF07-01\nCP-POST-RF07-01\nCP-HUM-RF07-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_maquinaria.py: 20 casos; Postman consulta listado paginado.", "Pytest local aprobado. Solicitud Postman requiere sesión y sigue pendiente."),
    _row("RF-08", "Gestión de proyectos.", "CP-UNI-RF08-01..22\nCP-INT-RF08-01\nCP-API-RF08-01\nCP-POST-RF08-01\nCP-HUM-RF08-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_proyectos.py: 22 casos sobre serialización, métricas y persistencia simulada; Postman valida código de proyecto.", "Pytest local aprobado. Postman requiere cookie y código de proyecto existente."),
    _row("RF-09", "Gestión de contrataciones vinculadas a empresas y obras.", "CP-UNI-RF09-01..20\nCP-INT-RF09-01..03\nCP-API-RF09-01\nCP-POST-RF09-01\nCP-HUM-RF09-01", "Unidad; integración (incluye flujo Bitácora); backend/API; Postman (pendiente); humo", "tests/unit/test_contratacion.py (9) y test_bitacora.py (11); Postman consulta catálogo JSON de empresas para contratos.", "Pytest local aprobado con dobles. Postman no modifica contrataciones y requiere sesión."),
    _row("RF-10", "Gestión de obras y sus referencias a proyecto/contratación.", "CP-UNI-RF10-01..14\nCP-INT-RF10-01\nCP-API-RF10-01\nCP-POST-RF10-01\nCP-HUM-RF10-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_obras.py: 14 casos de validación, fechas y operaciones de datos; Postman consulta estados.", "Pytest local aprobado. Solicitud Postman requiere sesión y sigue pendiente."),
    _row("RF-11", "Registro y consulta de inspecciones ligadas a una obra.", "CP-UNI-RF11-01..18\nCP-INT-RF11-01\nCP-API-RF11-01\nCP-POST-RF11-01\nCP-HUM-RF11-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_inspecciones.py: 18 casos; Postman consulta catálogo de inspectores.", "Pytest local aprobado. Solicitud Postman requiere sesión y sigue pendiente."),
    _row("RF-12", "Gestión segura y trazable de evidencias.", "CP-UNI-RF12-01..13\nCP-INT-RF12-01\nCP-API-RF12-01\nCP-POST-RF12-01\nCP-HUM-RF12-01", "Unidad (equivalencia/seguridad); integración; backend/API; Postman (pendiente); humo", "tests/unit/test_evidencias.py: 13 casos para archivo/URL, traversal y operaciones simuladas; Postman valida una evidencia por ID.", "Pytest local aprobado. Postman requiere cookie e ID existente."),
    _row("RF-13", "Registro, consulta y detalle de informes de avance de obra.", "CP-UNI-RF13-01..21\nCP-INT-RF13-01\nCP-API-RF13-01\nCP-POST-RF13-01\nCP-HUM-RF13-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_informe_avance.py: 21 casos; test_informe_validacion.py agrega 3 validaciones. Postman consulta listado JSON.", "Pytest local aprobado con dobles. Postman requiere sesión y sigue pendiente."),
    _row("RF-14", "Gestión de publicaciones institucionales.", "CP-UNI-RF14-01..14\nCP-INT-RF14-01\nCP-API-RF14-01\nCP-POST-RF14-01\nCP-HUM-RF14-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_publicaciones.py: 14 casos; Postman valida un informe asociado.", "Pytest local aprobado. Postman requiere cookie e ID de informe válido."),
    _row("RF-15", "Generación y filtrado de reportes PDF, Excel y estadísticos.", "CP-UNI-RF15-01..46\nCP-INT-RF15-01..03\nCP-API-RF15-01..16\nCP-POST-RF15-01..03\nCP-HUM-RF15-01..03", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_reportes_pdf.py (11), test_reportes_excel.py (16) y test_reportes_estadisticos.py (19); Postman abre formularios y consulta datos.", "Pytest local aprobado; pruebas compartidas de listas SQL se registran en RNF-05. Postman requiere sesión y no acredita generación final."),
    _row("RF-16", "Administración de respaldos: crear, listar, descargar, importar y eliminar.", "CP-UNI-RF16-01..26\nCP-INT-RF16-01\nCP-API-RF16-01\nCP-POST-RF16-01\nCP-HUM-RF16-01", "Unidad; integración; backend/API; Postman (pendiente); humo", "tests/unit/test_administracion_respaldos.py: 26 casos; Postman consulta listado JSON y no ejecuta operaciones destructivas.", "Pytest local aprobado. Postman requiere sesión y no valida restauración real."),
    _row("RF-17", "Notificaciones de cambios y vencimientos.", "CP-PEND-RF17-01", "Pendiente", "No hay suite automatizada dedicada en tests/unit, tests/api o tests/smoke; definir casos por evento, destinatario y estado de lectura.", "Pendiente: notificación correcta para evento válido y ninguna entrega indebida; no se declara requisito cubierto."),
    _row("RF-18", "Panel principal e indicadores respetando permisos.", "CP-PEND-RF18-01", "Pendiente", "No se identificó un caso de aceptación dedicado para widgets, agregados y aislamiento por rol.", "Pendiente: datos/indicadores coinciden con fuentes autorizadas y no revelan información de otro rol."),
    _row("RF-19", "Consulta y actualización del perfil de usuario.", "CP-PEND-RF19-01", "Pendiente", "La suite de usuarios cubre administración general, no un recorrido específico del perfil.", "Pendiente: el perfil muestra y actualiza únicamente los datos permitidos del usuario autenticado."),
    _row("RF-20", "Manual de usuario y tours interactivos.", "CP-PEND-RF20-01", "Pendiente", "verificar_tours.py no forma parte de la suite pytest ejecutada; falta registrar una prueba reproducible del recurso y del inicio del tour.", "Pendiente: manual accesible y tour inicia en el módulo correspondiente cuando está configurado."),
    _row("RNF-01", "Autenticación y sesión.", "CP-UNI-RNF01-01..02\nCP-HUM-RNF01-01\nCP-UI-RNF01-01 (omitido)", "Unidad; humo; interfaz (omitida)", "tests/unit/test_security_controls.py comprueba secreto ausente y error de red con el bypass aislado; el humo alcanza la ruta de acceso. Playwright requiere INVISAP_TEST_URL.", "Casos unitarios/humo aprobados; UI omitida. No equivale a probar una autenticación real contra el despliegue."),
    _row("RNF-02", "Ciclo seguro de cuentas: alta, edición, desactivación y bloqueo posterior.", "CP-UNI-RNF02-01\nCP-API-RNF02-01", "Unidad; backend/API (parcial)", "Suites de usuarios prueban validaciones y contrato; agregar un flujo de cuenta desactivada seguido de intento de inicio de sesión.", "Pendiente de demostrar que una cuenta desactivada no inicia sesión y que sus permisos se revocan."),
    _row("RNF-03", "Autorización por rol, módulo y acción.", "CP-UNI-RNF03-01..02\nCP-INT-RNF03-01\nCP-API-RNF03-01\nCP-HUM-RNF03-01", "Unidad; integración; backend/API; humo", "Ejecutar tests/unit/test_permisos_por_rol.py y las suites de permisos; contrastar acceso permitido y denegado.", "Acciones no autorizadas se bloquean sin mutar datos. Casos disponibles aprobados; la matriz completa de rol/módulo/acción requiere ampliación."),
    _row("RNF-04", "Protección de claves y sesión.", "CP-PEND-RNF04-01", "Pendiente", "No hay evidencia en esta corrida de pruebas exhaustivas de hash de contraseñas, expiración, renovación y cierre de sesión.", "Pendiente: credenciales no se exponen y la sesión cumple las reglas acordadas."),
    _row("RNF-05", "Validación y saneamiento de entradas.", "CP-UNI-RNF05-01..39", "Unidad (partición, límites y listas permitidas)", "tests/unit/test_sql_filter_allowlists.py: 39 casos de filtros y columnas permitidos; las suites de módulo agregan pruebas de entradas límite y valores inválidos.", "Los casos locales están aprobados; la cobertura total de entradas y métodos permanece pendiente."),
    _row("RNF-06", "Bitácora y trazabilidad de operaciones.", "CP-UNI-RNF06-01..02\nCP-INT-RNF06-01..02\nCP-API-RNF06-01\nCP-HUM-RNF06-01", "Unidad; integración; backend/API; humo", "Ejecutar tests/unit/test_bitacora.py, test_contrataciones_bitacora.py y suites de Bitácora.", "La operación probada deja evento con usuario/módulo/acción según el flujo; casos aprobados con dobles. Persistencia real pendiente."),
    _row("RNF-07", "Navegabilidad y consistencia entre pantallas.", "CP-HUM-RNF07-01..20\nCP-UI-RNF07-01 (omitido)", "Humo; interfaz (omitida)", "Los humos comprueban rutas esenciales; Playwright no se ejecutó en la última corrida por falta de INVISAP_TEST_URL.", "Rutas esenciales responden según su contrato; navegación completa y consistencia visual pendientes."),
    _row("RNF-08", "Usabilidad y formularios.", "CP-UI-RNF08-01 (omitido)", "Interfaz (Playwright omitida)", "tests/ui/test_login_ui.py requiere una URL configurada; no se abrió navegador el 2026-11-12.", "Pendiente: controles visibles, mensajes comprensibles, entradas y validación observables en interfaz."),
    _row("RNF-09", "Adaptabilidad y portabilidad web.", "CP-PEND-RNF09-01", "Pendiente", "No se ejecutaron pruebas automatizadas de tamaños de pantalla ni de varios navegadores.", "Pendiente: vistas operables en navegadores y resoluciones acordados."),
    _row("RNF-10", "Rendimiento: 20 usuarios, promedio menor a 2 s y 0 % de errores HTTP.", "CP-LOC-RNF10-01 (no concluyente)", "Rendimiento (Locust; repetir)", "Los registros quick/baseline del 2026-10-29 incluyeron 401/302 en rutas protegidas; repetir con cuenta/roles de prueba y guardar CSV sin secretos.", "No aprobado ni rechazado: la corrida histórica no fue autenticada. Criterio esperado: promedio <2 s y 0 % de errores con carga autorizada."),
    _row("RNF-11", "Escalabilidad y uso de CPU/memoria.", "CP-PEND-RNF11-01", "Rendimiento (pendiente)", "No se recogieron métricas de CPU/memoria ni series de concurrencia válidas en esta auditoría.", "Pendiente: medir RPS/TPS, latencia, CPU y memoria con carga acordada y registrar umbrales."),
    _row("RNF-12", "Fiabilidad y recuperación ante fallos.", "CP-INT-RNF12-01..02", "Integración (fallo controlado)", "test_contrataciones_bitacora.py inyecta colisión de ID y verifica reintento; no incluye recuperación de BD ni restauración.", "El reintento recupera la colisión simulada. Recuperación ante fallos de servicio/base de datos pendiente."),
    _row("RNF-13", "Disponibilidad.", "CP-PEND-RNF13-01", "Pendiente", "No se ejecutaron pruebas de disponibilidad/continuidad con duración y ambiente acordados.", "Pendiente: servicio disponible según el umbral que apruebe la institución."),
    _row("RNF-14", "Mantenibilidad y modularidad.", "CP-PEND-RNF14-01", "Cobertura de código (pendiente)", "Se ejecutaron 427 casos unitarios en 20 suites de módulo y suites transversales; no se midieron cobertura de líneas/ramas ni correspondencia de todos los métodos a casos.", "Pendiente: publicar medición de cobertura reproducible y revisar métodos públicos/privados no ejercitados."),
    _row("RNF-15", "Integridad y restauración de respaldos.", "CP-PEND-RNF15-01", "Integración con MySQL (pendiente)", "Las pruebas de respaldo existentes usan dobles/contratos; no se restauró un dump en una base aislada.", "Pendiente: restaurar y comparar los conteos/inventario acordados en una base de ensayo."),
    _row("RNF-16", "Aislamiento de módulos y mínimo privilegio.", "CP-UNI-RNF16-01..02\nCP-API-RNF16-01", "Unidad; backend/API (parcial)", "Suites de permisos prueban reglas seleccionadas; completar pruebas negativas por rol, módulo y acción.", "Las peticiones sin permiso no revelan datos ni modifican registros; matriz completa pendiente."),
    _row("RNF-17", "Respuestas de error seguras.", "CP-API-RNF17-01\nCP-HUM-RNF17-01", "Backend/API; humo (parcial)", "Suites API comprueban algunos códigos y respuestas de rutas; revisar que no expongan trazas ni datos internos.", "Errores se responden con estado y mensaje seguros; revisión completa pendiente."),
    _row("RNF-18", "Portabilidad y reproducibilidad de instalación.", "CP-PEND-RNF18-01", "Instalación (pendiente)", "El plan de instalación está documentado; no se repitió la instalación en un equipo limpio durante esta ejecución.", "Pendiente: instalar desde instrucciones, configurar ambiente y verificar arranque con evidencia."),
]


def update_table(document_xml: bytes) -> bytes:
    document = ET.fromstring(document_xml)
    body = document.find("w:body", NS)
    table = body.find("w:tbl", NS)
    if table is None:
        raise ValueError("The supplied template does not contain a traceability table.")

    children = list(body)
    table_index = children.index(table)
    for paragraph in children[:table_index]:
        if paragraph.tag != tag("p"):
            continue
        text = paragraph_text(paragraph)
        if text.startswith("Proyeco:") or text.startswith("Proyecto:"):
            set_paragraph_text(
                paragraph,
                "Proyecto: Sistema INVISAP — Trayecto III",
                paragraph.find("w:r/w:rPr", NS),
                20,
            )

    status_text = (
        "Documento de trabajo | SRS versión 1.0 en borrador | Ejecución: "
        "2026-11-12 | IDs CP provisionales; las filas pendientes no "
        "constituyen evidencia de aprobación."
    )
    preceding_title = False
    status_added = False
    for paragraph in children[:table_index]:
        if paragraph.tag != tag("p"):
            continue
        text = paragraph_text(paragraph)
        if preceding_title and not text.strip():
            set_paragraph_text(
                paragraph,
                status_text,
                paragraph.find("w:r/w:rPr", NS),
                16,
            )
            status_added = True
            break
        preceding_title = text.strip() == "Matriz de Trazabilidad de Pruebas"
    if not status_added:
        status_paragraph = ET.Element(tag("p"))
        set_paragraph_text(status_paragraph, status_text, font_size=16)
        body.insert(table_index, status_paragraph)

    rows = table.findall("w:tr", NS)
    if len(rows) < 2:
        raise ValueError("The supplied template must have a header and a sample row.")
    sample_row = rows[1]
    for row in rows[1:]:
        table.remove(row)

    widths = [1450, 2200, 1900, 1500, 3300, 2088]
    grid = table.find("w:tblGrid", NS)
    if grid is not None:
        for column, width in zip(grid.findall("w:gridCol", NS), widths):
            column.set(tag("w"), str(width))
    table_properties = table.find("w:tblPr", NS)
    if table_properties is not None:
        table_width = table_properties.find("w:tblW", NS)
        if table_width is not None:
            table_width.set(tag("w"), str(sum(widths)))
            table_width.set(tag("type"), "dxa")

    header_row = rows[0]
    for cell, width in zip(header_row.findall("w:tc", NS), widths):
        set_cell_width(cell, width)
    header_properties = header_row.find("w:trPr", NS)
    if header_properties is None:
        header_properties = ET.Element(tag("trPr"))
        header_row.insert(0, header_properties)
    if header_properties.find("w:tblHeader", NS) is None:
        ET.SubElement(header_properties, tag("tblHeader"))

    for values in MATRIX_ROWS:
        new_row = deepcopy(sample_row)
        cells = new_row.findall("w:tc", NS)
        if len(cells) != 6:
            raise ValueError("The matrix template must contain exactly six columns.")
        for cell, value, width in zip(cells, values, widths):
            set_cell_text(cell, value)
            set_cell_width(cell, width)
        table.append(new_row)

    section = body.find("w:sectPr", NS)
    if section is not None:
        page_size = section.find("w:pgSz", NS)
        if page_size is not None:
            page_size.set(tag("w"), "15840")
            page_size.set(tag("h"), "12240")
            page_size.set(tag("orient"), "landscape")

    return ET.tostring(document, encoding="utf-8", xml_declaration=True)


def generate(template: Path, output: Path) -> None:
    if not template.is_file():
        raise FileNotFoundError(f"Word template not found: {template}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(template, "r") as source:
        files = {item.filename: source.read(item.filename) for item in source.infolist()}
    if "word/document.xml" not in files:
        raise ValueError("The supplied file is not a valid Word document.")
    files["word/document.xml"] = update_table(files["word/document.xml"])

    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as result:
        for filename, content in files.items():
            result.writestr(filename, content)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("Matriz_Trazabilidad_Pruebas_INVISAP.docx"),
    )
    arguments = parser.parse_args()
    generate(arguments.template, arguments.output)
    print(f"Generated {arguments.output} with {len(MATRIX_ROWS)} traceability rows.")


if __name__ == "__main__":
    main()
