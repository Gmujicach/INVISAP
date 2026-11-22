"""Generador del Capítulo IV de INVISAP siguiendo la instrucción de la profesora.

Estructura ESTRICTA de dos apartados principales:
  1. Recomendaciones (hallazgos técnicos concretos fundamentados en resultados reales)
  2. Evolución Previsible del Sistema (incremental: corto, mediano y largo plazo)

Regla de sinceridad de la profesora: NO se simulan resultados. Cada hallazgo cita
la evidencia real (capturas de consola, CSVs de Locust, cobertura de trazabilidad)
y se marca explícitamente lo pendiente (aceptación, UI sin URL, rendimiento sin
autenticar, persistencia real contra MySQL).

Evidencias reales utilizadas:
  - tests/evidence/hibrido_resultados/resultado_*.png  (salida de consola por categoría)
  - tests/evidence/*/report_*.html                      (reportes pytest por categoría)
  - tests/evidence/performance/results/bitacora_rendimiento.csv
  - tests/evidence/performance/results/*_stats.csv      (métricas por módulo)
  - tests/evidence/traceability_coverage_chart.png      (gráfico de cobertura)
  - tests/evidence/organized/traceability_coverage_report_*.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

HERE = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = HERE / "evidence"
DEFAULT_OUTPUT = DEFAULT_EVIDENCE_DIR / "Informe_Capitulo_IV_Profesora.docx"

COLOR_PRIMARIO = RGBColor(0x2C, 0x3E, 0x50)
COLOR_SECUNDARIO = RGBColor(0x34, 0x49, 0x5E)
COLOR_GRIS = RGBColor(0x7F, 0x8C, 0x8D)
COLOR_VERDE = RGBColor(0x27, 0xAE, 0x60)
COLOR_AMBAR = RGBColor(0xF3, 0x9C, 0x12)
COLOR_ROJO = RGBColor(0xE7, 0x4C, 0x3C)

MODULOS = [
    "Solicitudes", "Gravedad de Obra", "Prioridad", "Proyectos", "Maquinaria",
    "Contratación", "Empresa", "Obras", "Empleados", "Inspecciones",
    "Evidencias", "Informe de Avance de Obra", "Publicaciones", "Reportes PDF",
    "Reportes Excel", "Reportes Estadísticos", "Usuarios", "Permisos por Rol",
    "Administración de Respaldos", "Bitácora",
]


class ChapterIVGenerator:
    """Genera el Capítulo IV (solo Recomendaciones + Evolución Previsible)."""

    def __init__(self, evidence_dir: str = None, output_path: str = None):
        self.evidence_dir = Path(evidence_dir) if evidence_dir else DEFAULT_EVIDENCE_DIR
        self.output_path = Path(output_path) if output_path else DEFAULT_OUTPUT
        self.doc = Document()
        self._setup_document()

    # ------------------------------------------------------------------ #
    # Setup
    # ------------------------------------------------------------------ #
    def _setup_document(self):
        style = self.doc.styles["Normal"]
        style.font.name = "Arial"
        style.font.size = Pt(11)
        for section in self.doc.sections:
            section.top_margin = Cm(2.2)
            section.bottom_margin = Cm(2.2)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)

    def _heading(self, text: str, level: int = 1):
        heading = self.doc.add_heading(text, level=level)
        for run in heading.runs:
            run.font.color.rgb = COLOR_PRIMARIO
        return heading

    def _para(self, text: str, bold: bool = False, italic: bool = False,
              color: Optional[RGBColor] = None, size: int = 11):
        p = self.doc.add_paragraph()
        run = p.add_run(text)
        run.bold = bold
        run.italic = italic
        run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color
        return p

    def _bullet(self, text: str, bold_prefix: Optional[str] = None):
        p = self.doc.add_paragraph(style="List Bullet")
        if bold_prefix:
            run = p.add_run(bold_prefix)
            run.bold = True
            run.font.color.rgb = COLOR_PRIMARIO
        p.add_run(text)
        return p

    def _add_table(self, data: List[List[str]], col_widths: List[Cm],
                   header_bg: str = "2C3E50", font_size: int = 9):
        table = self.doc.add_table(rows=len(data), cols=len(data[0]),
                                   style="Table Grid")
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_text in enumerate(row_data):
                cell = table.cell(row_idx, col_idx)
                cell.text = ""
                p = cell.paragraphs[0]
                run = p.add_run(str(cell_text))
                run.font.size = Pt(font_size)
                run.font.name = "Arial"
                if row_idx == 0:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    shading = OxmlElement("w:shd")
                    shading.set(qn("w:fill"), header_bg)
                    shading.set(qn("w:val"), "clear")
                    cell._tc.get_or_add_tcPr().append(shading)
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
        if col_widths:
            for row in table.rows:
                for i, w in enumerate(col_widths):
                    if i < len(row.cells):
                        row.cells[i].width = w
        return table

    def _image_exists(self, name: str) -> bool:
        return (self.evidence_dir / name).exists()

    def _add_image(self, image_path: Path, caption: str, width_cm: float = 16.0,
                   align_center: bool = True):
        if not image_path or not image_path.exists():
            self._para(f"(Evidencia no disponible: {image_path.name if image_path else 'desconocida'})",
                       italic=True, color=COLOR_GRIS)
            return
        resized = self._resize_if_needed(image_path, width_cm)
        try:
            p = self.doc.add_paragraph()
            if align_center:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(resized), width=Cm(width_cm))
            if caption:
                cap = self.doc.add_paragraph()
                cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = cap.add_run(caption)
                run.font.size = Pt(9)
                run.font.italic = True
                run.font.color.rgb = COLOR_GRIS
            self.doc.add_paragraph()
        except Exception as e:
            self._para(f"No se pudo insertar imagen {image_path.name}: {e}",
                       italic=True, color=COLOR_GRIS)

    def _resize_if_needed(self, image_path: Path, max_width_cm: float) -> Path:
        if not PIL_AVAILABLE:
            return image_path
        try:
            with Image.open(image_path) as img:
                max_width_px = int(max_width_cm * 96 / 2.54)
                if img.width > max_width_px:
                    ratio = max_width_px / img.width
                    new_height = int(img.height * ratio)
                    img_resized = img.resize((max_width_px, new_height),
                                             Image.Resampling.LANCZOS)
                    resized_path = image_path.with_stem(f"{image_path.stem}_cap4")
                    img_resized.save(resized_path, "PNG", optimize=True)
                    return resized_path
        except Exception:
            pass
        return image_path

    # ------------------------------------------------------------------ #
    # Datos reales de cobertura
    # ------------------------------------------------------------------ #
    def _coverage_summary(self) -> Optional[Dict]:
        coverage_files = list(self.evidence_dir.glob(
            "organized/traceability_coverage_report_*.json"))
        if not coverage_files:
            return None
        latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
        with open(latest, "r", encoding="utf-8") as f:
            coverage = json.load(f)
        total = len(coverage.get("coverage", {}))
        with_ev = sum(1 for v in coverage.get("coverage", {}).values()
                      if v.get("has_evidence"))
        return {
            "total": total,
            "with_evidence": with_ev,
            "pct": (with_ev / total * 100) if total else 0.0,
            "file": latest.name,
        }

    # ------------------------------------------------------------------ #
    # Portada
    # ------------------------------------------------------------------ #
    def _portada(self):
        for _ in range(3):
            self.doc.add_paragraph()
        title = self.doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("INFORME DEL SISTEMA INVILARA - CAPÍTULO IV")
        run.bold = True
        run.font.size = Pt(22)
        run.font.color.rgb = COLOR_PRIMARIO
        sub = self.doc.add_paragraph()
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = sub.add_run("Recomendaciones y Evolución Previsible del Sistema")
        run.font.size = Pt(15)
        run.font.color.rgb = COLOR_SECUNDARIO
        self.doc.add_paragraph()
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = info.add_run(
            "Proyecto III - Trayecto III\n"
            "Instituto de Vialidad del Estado Lara (INVILARA)\n"
            "UNEFA - Universidad Nacional Experimental Politécnica de la Fuerza Armada\n"
            f"Fecha de generación: {datetime.now().strftime('%d de %B de %Y')}\n"
            "Versión: 1.0 - Documento Final\n"
            "Estructura estricta por instrucción de la profesora: Recomendaciones y "
            "Evolución Previsible del Sistema."
        )
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_GRIS
        self.doc.add_page_break()

    # ------------------------------------------------------------------ #
    # Introducción / Advertencia de sinceridad
    # ------------------------------------------------------------------ #
    def _introduccion(self):
        self._heading("CAPÍTULO IV. Recomendaciones y Evolución Previsible del Sistema", 1)
        self._para(
            "Este capítulo cumple estrictamente la instrucción de la profesora: se compone de dos "
            "apartados principales, (1) Recomendaciones y (2) Evolución Previsible del Sistema. "
            "Ambos están fundamentados exclusivamente en resultados reales de las pruebas de software "
            "ejecutadas y en la evidencia conservada (capturas de consola, reportes HTML de pytest, "
            "bitácora de Locust, matriz de trazabilidad y cubrimiento de trazabilidad)."
        )
        self._para(
            "Advertencia de sinceridad (exigencia de la profesora): no se presentan como ejecutadas "
            "pruebas que no cuentan con soporte real. Se indica explícitamente qué está verificado, "
            "qué está pendiente y qué no se puede afirmar por falta de entorno (base de datos MySQL "
            "real, URL de la aplicación, credenciales de sesión, acta de aceptación firmada)."
        )

        # Tabla de sincronía de evidencias reales
        self._heading("Evidencias reales consultadas", 2)
        ev_data = [
            ["Evidencia", "Archivo", "Contenido"],
            ["Consola pruebas unitarias", "tests/evidence/hibrido_resultados/resultado_unit.png",
             "Salida de pytest de tests/unit (427 casos recolectados, 418 aprobadas, 10 fallidas en Reportes Estadísticos)"],
            ["Consola pruebas de integración", "tests/evidence/hibrido_resultados/resultado_integration.png",
             "Salida de pytest de tests/integration (22 casos aprobados)"],
            ["Consola pruebas API/backend", "tests/evidence/hibrido_resultados/resultado_api.png",
             "Salida de pytest de tests/api (33 casos aprobados)"],
            ["Consola pruebas de humo", "tests/evidence/hibrido_resultados/resultado_smoke.png",
             "Salida de pytest de tests/smoke (21 casos aprobados)"],
            ["Consola pruebas de aceptación", "tests/evidence/hibrido_resultados/resultado_acceptance.png",
             "No ejecutada (pendiente de criterios y validador)"],
            ["Bitácora de rendimiento (Locust)", "tests/performance/results/bitacora_rendimiento.csv",
             "21 módulos, perfil quick, 1 usuario, 5 s; solo Evidencias y Publicaciones HTTP 200; resto 100 % fallos (401/302 sin autenticar)"],
            ["Cubrimiento de trazabilidad", "tests/evidence/organized/traceability_coverage_report_*.json",
             "Cobertura de casos de la Matriz de Trazabilidad de Pruebas con evidencia asociada"],
            ["Gráfico de cobertura", "tests/evidence/traceability_coverage_chart.png",
             "Casos con evidencia vs total por tipo de prueba"],
        ]
        self._add_table(ev_data, [Cm(4.5), Cm(6.5), Cm(7.0)])

    # ------------------------------------------------------------------ #
    # 1. RECOMENDACIONES
    # ------------------------------------------------------------------ #
    def _recomendaciones(self):
        self.doc.add_page_break()
        self._heading("1. Recomendaciones", 1)
        self._para(
            "Las recomendaciones siguientes son hallazgos técnicos concretos, no sugerencias genéricas. "
            "Cada una se fundamenta en resultados reales de las pruebas ejecutadas y en los objetivos del "
            "proyecto INVILARA (gestión de solicitudes, obras, reportes, respaldos y bitácora)."
        )

        recs = [
            ("1.1. Integración real con MySQL (persistencia y transacciones)",
             "Las pruebas de unidad (427 casos), integración (22) y API/backend (33) se ejecutan con "
             "fixtures, dobles de prueba y mocks que aíslan dependencias. Ninguna certifica escrituras, "
             "lecturas reales, restricciones de integridad referencial ni transacciones con rollback contra "
             "una base de datos MySQL. La profesora exige validar lectura, escritura, permisos y restauración "
             "directamente contra MySQL en la infraestructura de INVILARA. Recomendación: ejecutar al menos "
             "las 22 pruebas de integración contra una base de datos MySQL aislada de pruebas, con transacciones "
             "y limpieza de datos (rollback), para certificar persistencia real antes de considerar el módulo "
             "aprobado a nivel de integración."),
            ("1.2. Validación de variables de entorno (.env) y URL de la aplicación",
             "Las pruebas de interfaz (UI) se omitieron por falta de INVISAP_TEST_URL y las pruebas de rendimiento "
             "Locust devolvieron HTTP 401/302 en 18 de 20 módulos porque no se configuró una cookie de sesión válida "
             "ni identificadores de prueba. Recomendación: documentar y cargar obligatoriamente un archivo .env de "
             "entorno de pruebas con INVISAP_TEST_URL, credenciales de sesión de prueba y cookies temporales, sin "
             "almacenar secretos ni credenciales productivas; reejecutar UI y Locust con sesión autenticada antes de "
             "interpretar latencias como línea base."),
            ("1.3. Respaldos periódicos y restauración contra MySQL real",
             "El módulo Administración de Respaldos tiene 26/26 pruebas unitarias aprobadas, pero con dobles de prueba; "
             "no se probó crear un respaldo real, restaurarlo en un entorno aislado ni verificar que el respaldo sea "
             "restaurable. Recomendación: establecer respaldos periódicos automatizados de la base de datos MySQL de "
             "INVILARA, validar la lectura/escritura y permisos contra la base real, y documentar un procedimiento de "
             "restauración probado antes de aceptar el sistema en producción."),
            ("1.4. Seguridad y control de acceso (reCAPTCHA, permisos, listas permitidas)",
             "Las pruebas unitarias cubren listas permitidas de identificadores SQL (39 casos) y controles de "
             "reCAPTCHA aislados del bypass local (secreto ausente y error de red, no verificación real contra Google). "
             "La ejecución de rendimiento mostró que 18 módulos no responden HTTP 200 autenticado. Recomendación: "
             "revisar las 14 advertencias de openpyxl (datetime.utcnow() obsoleto), migrar a datetime.now(timezone.utc), "
             "y ejecutar pruebas de seguridad de regresión (sesión/autorización) con cuenta de pruebas real, sin exponer "
             "contraseñas ni cookies en la evidencia."),
            ("1.5. Reportes y consultas (índices y agrupaciones)",
             "La suite de Reportes Estadísticos reportó 10 fallidas concentradas en agrupaciones por mes/semana con "
             "DATE_FORMAT sobre fechas de solicitudes, obras, empleados, contrataciones y publicaciones. Esto apunta a "
             "problemas en los índices y consultas de reportes que la profesora identifica como área de mejora. "
             "Recomendación: revisar y optimizar las consultas agrupadas de reportes (índices en fecha, tipo de reporte "
             "y autor), corregir los 10 casos fallidos y establecer umbrales de tiempo de respuesta para los módulos de "
             "reportes (PDF, Excel, Estadísticos)."),
            ("1.6. Aceptación y capacitación con usuarios de INVILARA",
             "No hay criterios de aceptación firmados, ni validador designado, ni acta de aceptación. La jornada de "
             "capacitación con gerentes y personal de INVILARA debe registrar asistencia, duración, temario y evaluación "
             "en el formato institucional. Recomendación: completar el Formato de Pruebas de Aceptación (14 casos CP01-01 "
             "a CP14-01), obtener el acta firmada por los responsables (7 gerentes + 7 técnicos) y formalizar la "
             "capacitación (propuesta de 6 h 30 min en dos sesiones) con registro de asistencia y ejercicios prácticos."),
        ]

        for titulo, desc in recs:
            self._bullet(desc, bold_prefix=titulo)

        # Cuadro resumen sincero del estado real
        self._heading("Estado sincero de las pruebas ejecutadas", 2)
        estado = [
            ["Categoría", "Resultado real", "Evidencia", "Estado frente a aceptación"],
            ["Unidad (PyTest)", "418 aprobadas, 10 fallidas (Reportes Estadísticos)", "resultado_unit.png", "Aprobadas con observaciones; 10 fallos por corrección"],
            ["Integración (PyTest)", "22 aprobadas, 0 fallidas", "resultado_integration.png", "Contratos de ruta; persistencia real pendiente"],
            ["Backend/API (PyTest)", "33 aprobadas, 0 fallidas", "resultado_api.png", "Contratos HTTP; Postman no ejecutada (falta cookie/IDs)"],
            ["Humo (PyTest)", "21 aprobadas, 0 fallidas", "resultado_smoke.png", "Rutas esenciales; no recorrido integral"],
            ["Interfaz (Playwright)", "Omitida (falta INVISAP_TEST_URL)", "—", "Pendiente de URL y navegador autenticado"],
            ["Rendimiento (Locust)", "18 módulos HTTP 401/302; solo Evidencias y Publicaciones HTTP 200", "bitacora_rendimiento.csv", "No es línea base autenticada; repetir con sesión"],
            ["Aceptación (usuarios)", "No ejecutada", "—", "Pendiente de criterios firmados y acta"],
        ]
        self._add_table(estado, [Cm(3.5), Cm(5.0), Cm(3.5), Cm(4.0)])

        # Evidencia visual de resultados reales
        self._heading("Evidencia visual de resultados (capturas de consola)", 2)
        for key, label, path in [
            ("unit", "Pruebas Unitarias - salida de consola",
             self.evidence_dir / "hibrido_resultados" / "resultado_unit.png"),
            ("integration", "Pruebas de Integración - salida de consola",
             self.evidence_dir / "hibrido_resultados" / "resultado_integration.png"),
            ("api", "Pruebas de Backend/API - salida de consola",
             self.evidence_dir / "hibrido_resultados" / "resultado_api.png"),
            ("smoke", "Pruebas de Humo - salida de consola",
             self.evidence_dir / "hibrido_resultados" / "resultado_smoke.png"),
        ]:
            self._para(label, bold=True, color=COLOR_PRIMARIO, size=10)
            self._add_image(path, label, width_cm=15.5)

        # Cubrimiento de trazabilidad
        self._heading("Cubrimiento de trazabilidad (Matriz de Trazabilidad de Pruebas)", 2)
        cov = self._coverage_summary()
        if cov:
            self._para(
                f"De {cov['total']} casos definidos en la Matriz de Trazabilidad de Pruebas, "
                f"{cov['with_evidence']} ({cov['pct']:.1f} %) cuentan con evidencia organizada. "
                f"Fuente: {cov['file']}.",
                size=10,
            )
        self._add_image(
            self.evidence_dir / "traceability_coverage_chart.png",
            "Cubrimiento de trazabilidad: casos con evidencia vs total por tipo de prueba",
            width_cm=15.5,
        )

    # ------------------------------------------------------------------ #
    # 2. EVOLUCIÓN PREVISIBLE (incremental)
    # ------------------------------------------------------------------ #
    def _evolucion(self):
        self.doc.add_page_break()
        self._heading("2. Evolución Previsible del Sistema", 1)
        self._para(
            "La evolución se organiza de manera incremental por horizontes temporales, contemplando el "
            "mantenimiento continuo del sistema, las mejoras en los índices y consultas de reportes, y la "
            "adaptación paulatina a los requerimientos cambiantes de la institución INVILARA, sobre los 20 "
            "módulos funcionales y la infraestructura."
        )

        horizontes = [
            ("Corto plazo (0-3 meses)", [
                ("Integración real con MySQL", "Ejecutar las 22 pruebas de integración contra una base de datos MySQL aislada, con transacciones, rollback y limpieza de datos; certificar persistencia, integridad referencial y rendimiento de consultas."),
                ("Validar .env y sesión", "Configurar INVISAP_TEST_URL y credenciales de prueba en el entorno; reejecutar UI y Locust con sesión autenticada para obtener línea base real."),
                ("Corregir Reportes Estadísticos", "Resolver los 10 casos fallidos de agrupación DATE_FORMAT y crear índices en las consultas de reportes."),
                ("Mantenimiento de dependencias", "Migrar datetime.utcnow() a datetime.now(timezone.utc) y eliminar las 14 advertencias de openpyxl."),
                ("Pruebas de humo post-instalación", "Repetir humo tras cada instalación y automatizar en CI/CD a cada merge a main."),
            ]),
            ("Mediano plazo (3-6 meses)", [
                ("Pruebas de contrato de API", "Implementar pruebas de contrato (Pact o similar) para los 20 módulos de backend."),
                ("Pruebas de seguridad", "Añadir OWASP ZAP y Bandit en el pipeline de CI/CD; regresión de sesión y autorización."),
                ("Carga distribuida con Locust", "Configurar pruebas de carga distribuida en Kubernetes con perfiles baseline/stress/spike en entorno autorizado."),
                ("Cobertura de código", "Implementar métricas de cobertura con pytest-cov sobre los 20 módulos."),
                ("Despliegue en staging", "Automatizar despliegue con Docker Compose y entornos aislados de pruebas."),
            ]),
            ("Largo plazo (6-12 meses)", [
                ("Arquitectura de microservicios", "Migrar a microservicios si la carga y los requerimientos cambiantes de la institución lo requieren."),
                ("Observabilidad completa", "Implementar logs, métricas y trazas distribuidas para operación continua."),
                ("Pruebas de caos", "Ejecutar Chaos Engineering para validar resiliencia ante fallos de infraestructura."),
                ("Accesibilidad WCAG 2.1 AA", "Cumplir normas de accesibilidad en los 20 módulos de interfaz."),
                ("Adaptación a requerimientos cambiantes", "Proceso formal de gestión de cambios con actualización de la Matriz de Trazabilidad de Pruebas y reejecución de la suite afectada."),
            ]),
        ]

        for periodo, items in horizontes:
            p = self.doc.add_paragraph()
            run = p.add_run(periodo)
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = COLOR_PRIMARIO
            for titulo, desc in items:
                self._bullet(desc, bold_prefix=f"{titulo}: ")

        # Matriz de evolución por módulos de mantenimiento
        self._heading("Mantenimiento de los 20 módulos por horizonte", 2)
        mod_data = [["Módulo", "Enfoque de mantenimiento", "Horizonte prioritario"]]
        for m in MODULOS:
            if m in ("Reportes PDF", "Reportes Excel", "Reportes Estadísticos"):
                enfoque = "Mejorar índices y consultas de reportes; corregir fallos de agrupación"
                horizonte = "Corto y mediano plazo"
            elif m in ("Administración de Respaldos", "Bitácora", "Permisos por Rol"):
                enfoque = "Validar respaldos reales, restauración y permisos contra MySQL"
                horizonte = "Corto plazo"
            elif m in ("Usuarios", "Evidencias", "Publicaciones"):
                enfoque = "Autenticación, sesión y reCAPTCHA con entorno real"
                horizonte = "Corto y mediano plazo"
            else:
                enfoque = "Mantenimiento correctivo y evolutivo estándar; integración con MySQL real"
                horizonte = "Corto a largo plazo"
            mod_data.append([m, enfoque, horizonte])
        self._add_table(mod_data, [Cm(5.0), Cm(7.0), Cm(4.0)], font_size=8)

        # Cierre sincero
        self._heading("Nota de cierre", 2)
        self._para(
            "Este capítulo no incluye el Plan de Pruebas, la Bitácora de Pruebas, el Plan de Instalación ni el "
            "Plan de Capacitación como apartados principales, por instrucción expresa de la profesora de que el "
            "Capítulo IV se compone estrictamente de Recomendaciones y Evolución Previsible del Sistema. Aquellos "
            "contenidos (plan de pruebas por módulo, bitácora de ejecución, plan de instalación y plan de "
            "capacitación con el formato institucional de INVILARA) se encuentran documentados en el generador "
            "generate_consolidated_report.py (CAPÍTULO IV tradicional) y en los archivos de evidencia de "
            "tests/evidence/. Se recomienda no presentar como ejecutado lo que carece de soporte real: aceptación, "
            "UI sin URL, rendimiento sin autenticar y persistencia contra MySQL.",
            italic=True, color=COLOR_GRIS, size=10,
        )

    # ------------------------------------------------------------------ #
    # Generar
    # ------------------------------------------------------------------ #
    def generate(self, output_path: str = None):
        out = Path(output_path) if output_path else self.output_path
        out.parent.mkdir(parents=True, exist_ok=True)
        self._portada()
        self._introduccion()
        self._recomendaciones()
        self._evolucion()
        self.doc.save(str(out))
        print(f"[CAPÍTULO IV] Generado: {out}")
        return out


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generar Capítulo IV de INVISAP (Recomendaciones + Evolución Previsible)"
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR),
                        help="Directorio base de evidencia")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help="Ruta del documento Word de salida")
    args = parser.parse_args()
    generator = ChapterIVGenerator(evidence_dir=args.evidence_dir,
                                    output_path=args.output)
    generator.generate(args.output)


if __name__ == "__main__":
    main()
