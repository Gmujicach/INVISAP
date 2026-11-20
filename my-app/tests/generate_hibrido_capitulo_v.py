"""Generador de Capítulo V híbrido para INVISAP.

Incrusta SOLO, como imágenes y cuadros estilo Matriz de Trazabilidad de Pruebas:

1. Reportes (reportes HTML de pytest convertidos a imagen).
2. Cada uno de los resultados de las Pruebas (por categoría: unidad, integración,
   API/backend, humo, aceptación) como imagen de salida de consola.
3. Capturas de aprobadas UI (*_APROVED_*.png y *_PASSED_*.png) con la ID de Caso
   de Prueba de la Matriz de Trazabilidad de Pruebas.
4. Reportes HTML de rendimiento (Locust) convertidos a imagen.
5. Resumen visual de cobertura de trazabilidad (gráfico + tabla detalle).

Todo se inserta en el Capítulo V, como los cuadros de la Matriz de Trazabilidad de
Pruebas.
"""

import os
import re
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# ============================================================
# RUTAS Y CONFIGURACIÓN
# ============================================================
HERE = Path(__file__).resolve().parent
DEFAULT_EVIDENCE_DIR = HERE / "evidence"
DEFAULT_MATRIX_PATH = HERE / "documentation" / "Matriz_Trazabilidad_Pruebas_INVISAP.docx"
DEFAULT_OUTPUT = DEFAULT_EVIDENCE_DIR / "Informe_Hibrido_Capitulo_V.docx"

# Patrones de captura de UI aprobada (prioridad: APROVED tal como lo pide el usuario)
UI_APPROVED_PATTERNS = ["*_APROVED_*.png", "*_APROBADA_*.png", "*_PASSED_*.png"]

# Categorías de prueba pytest y sus directorios
TEST_CATEGORIES = [
    ("unit", "Pruebas Unitarias", "tests/unit", "PyTest"),
    ("integration", "Pruebas de Integración", "tests/integration", "Pytest"),
    ("api", "Pruebas de Backend (API)", "tests/api", "Pytest + Postman"),
    ("smoke", "Pruebas de Humo", "tests/smoke", "Pytest, Selenium y Playwright"),
    ("acceptance", "Pruebas de Aceptación", "tests/acceptance", "Pytest, Selenium y Playwright"),
]

# Colores institucionales
COLOR_PRIMARIO = RGBColor(0x2C, 0x3E, 0x50)
COLOR_SECUNDARIO = RGBColor(0x34, 0x49, 0x5E)
COLOR_GRIS = RGBColor(0x7F, 0x8C, 0x8D)
COLOR_VERDE = RGBColor(0x27, 0xAE, 0x60)
COLOR_ROJO = RGBColor(0xE7, 0x4C, 0x3C)
COLOR_AMBAR = RGBColor(0xF3, 0x9C, 0x12)


class HybridChapterVGenerator:
    """Genera un documento Word con el Capítulo V híbrido (solo evidencia visual)."""

    def __init__(self, evidence_dir: str = None, matrix_path: str = None,
                 output_path: str = None):
        self.evidence_dir = Path(evidence_dir) if evidence_dir else DEFAULT_EVIDENCE_DIR
        self.matrix_path = Path(matrix_path) if matrix_path else DEFAULT_MATRIX_PATH
        self.output_path = Path(output_path) if output_path else DEFAULT_OUTPUT
        self.doc = Document()
        self._setup_document()

    # ------------------------------------------------------------------ #
    # Setup del documento
    # ------------------------------------------------------------------ #
    def _setup_document(self):
        style = self.doc.styles["Normal"]
        style.font.name = "Arial"
        style.font.size = Pt(11)
        for section in self.doc.sections:
            section.top_margin = Cm(2.0)
            section.bottom_margin = Cm(2.0)
            section.left_margin = Cm(2.5)
            section.right_margin = Cm(2.5)

    def _heading(self, text: str, level: int = 1):
        heading = self.doc.add_heading(text, level=level)
        for run in heading.runs:
            run.font.color.rgb = COLOR_PRIMARIO
        return heading

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

    def _add_image(self, image_path: Path, caption: str, width_cm: float = 16.0,
                   align_center: bool = True):
        if not image_path or not image_path.exists():
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
            print(f"[WARNING] No se pudo insertar imagen {image_path}: {e}")

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
                    resized_path = image_path.with_stem(f"{image_path.stem}_hibrido")
                    img_resized.save(resized_path, "PNG", optimize=True)
                    return resized_path
        except Exception as e:
            print(f"[WARNING] Error redimensionando {image_path}: {e}")
        return image_path

    # ------------------------------------------------------------------ #
    # Utilidades de trazabilidad
    # ------------------------------------------------------------------ #
    @staticmethod
    def _extract_traceability_id(filename: str) -> Tuple[str, str, str]:
        """Extrae ID de trazabilidad, módulo y nombre de prueba del nombre de archivo.

        Patrón esperado: tipoPrueba_modulo_IDcaso_nombrePrueba_resultado_timestamp.ext
        Devuelve (traceability_id, module, test_name).
        """
        stem = Path(filename).stem
        parts = stem.split("_")
        traceability_id = ""
        module = ""
        test_name = ""
        for i, part in enumerate(parts):
            if part.startswith("CP-"):
                traceability_id = part
                if i > 0:
                    module = parts[i - 1]
                if i + 1 < len(parts):
                    resto = "_".join(parts[i + 1:])
                    for suf in ("_APROVED", "_APROBADA", "_PASSED", "_FAILED", "_FALLIDO"):
                        resto = resto.replace(suf, "")
                    test_name = resto
                break
        return traceability_id, module.replace("_", " ").title(), test_name

    def _find_ui_approved_screenshots(self) -> List[Dict]:
        """Busca capturas de UI aprobadas con patrones *_APROVED_*.png (y compatibles)."""
        screenshots = []
        ui_dir = self.evidence_dir / "ui"
        if not ui_dir.exists():
            return screenshots
        for pattern in UI_APPROVED_PATTERNS:
            for img_path in ui_dir.glob(pattern):
                trace_id, module, test_name = self._extract_traceability_id(img_path.name)
                screenshots.append({
                    "path": img_path,
                    "traceability_id": trace_id,
                    "module": module or "Login",
                    "test_name": test_name,
                    "filename": img_path.name,
                    "pattern": pattern,
                })
        # Deduplicar por path
        seen = set()
        unique = []
        for s in screenshots:
            if str(s["path"]) not in seen:
                seen.add(str(s["path"]))
                unique.append(s)
        return unique

    def _find_performance_reports(self) -> List[Dict]:
        reports = []
        perf_dir = self.evidence_dir / "performance"
        if not perf_dir.exists():
            return reports
        for html_path in perf_dir.rglob("*.html"):
            if "report" in html_path.name.lower() or "locust" in html_path.name.lower():
                reports.append({
                    "path": html_path,
                    "name": html_path.stem,
                    "type": "Reporte HTML de Rendimiento (Locust)",
                })
        return reports

    def _find_pytest_reports(self) -> List[Dict]:
        reports = []
        for html_path in self.evidence_dir.rglob("report.html"):
            reports.append({
                "path": html_path,
                "name": html_path.parent.name.upper(),
                "type": "Reporte HTML pytest",
            })
        # También reportes nombrados por categoría
        for html_path in self.evidence_dir.rglob("*report*.html"):
            if html_path.name == "report.html":
                continue
            reports.append({
                "path": html_path,
                "name": html_path.stem,
                "type": "Reporte HTML pytest",
            })
        return reports

    def _generate_traceability_chart(self) -> Optional[Path]:
        if not PIL_AVAILABLE:
            return None
        coverage_files = list(self.evidence_dir.glob(
            "organized/traceability_coverage_report_*.json"))
        if not coverage_files:
            return None
        latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
        with open(latest, "r", encoding="utf-8") as f:
            coverage = json.load(f)
        type_counts: Dict[str, Dict[str, int]] = {}
        for case_info in coverage.get("coverage", {}).values():
            test_type = case_info.get("test_type", "unknown")
            has_ev = case_info.get("has_evidence", False)
            type_counts.setdefault(test_type, {"total": 0, "with_evidence": 0})
            type_counts[test_type]["total"] += 1
            if has_ev:
                type_counts[test_type]["with_evidence"] += 1
        if not type_counts:
            return None
        chart_path = self.evidence_dir / "hibrido_cobertura_trazabilidad.png"
        types = list(type_counts.keys())
        totals = [type_counts[t]["total"] for t in types]
        with_ev = [type_counts[t]["with_evidence"] for t in types]
        bar_height = 44
        padding = 70
        chart_width = 900
        chart_height = len(types) * bar_height + 2 * padding + 140
        img = Image.new("RGB", (chart_width, chart_height), "white")
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 15)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except Exception:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        max_total = max(totals) if totals else 1
        bar_max_width = chart_width - 2 * padding - 170
        draw.text((chart_width // 2, 26), "Resumen Visual de Cobertura de Trazabilidad",
                  fill="black", font=font, anchor="mm")
        draw.text((chart_width // 2, 52), "Casos con evidencia vs total por tipo de prueba "
                  "(Matriz de Trazabilidad de Pruebas)",
                  fill="#555555", font=font_small, anchor="mm")
        for i, (t, total, ev) in enumerate(zip(types, totals, with_ev)):
            y = padding + i * bar_height
            draw.text((padding - 10, y + bar_height // 2), t.capitalize(),
                      fill="black", font=font_small, anchor="rm")
            total_width = int((total / max_total) * bar_max_width)
            draw.rectangle([padding, y, padding + total_width, y + bar_height - 6],
                           fill="#ecf0f1", outline="#bdc3c7")
            ev_width = int((ev / max_total) * bar_max_width) if max_total > 0 else 0
            color = "#27ae60" if ev == total else "#f39c12" if ev > 0 else "#e74c3c"
            draw.rectangle([padding, y, padding + ev_width, y + bar_height - 6],
                           fill=color, outline=color)
            pct = f"{ev / total * 100:.0f}%" if total > 0 else "0%"
            draw.text((padding + total_width + 12, y + bar_height // 2),
                      f"{ev}/{total} ({pct})",
                      fill="black", font=font_small, anchor="lm")
        legend_y = padding + len(types) * bar_height + 26
        draw.rectangle([padding, legend_y, padding + 20, legend_y + 16], fill="#27ae60")
        draw.text((padding + 26, legend_y + 8), "Completa (100%)", fill="black",
                  font=font_small, anchor="lm")
        draw.rectangle([padding + 170, legend_y, padding + 190, legend_y + 16], fill="#f39c12")
        draw.text((padding + 196, legend_y + 8), "Parcial", fill="black",
                  font=font_small, anchor="lm")
        draw.rectangle([padding + 290, legend_y, padding + 310, legend_y + 16], fill="#e74c3c")
        draw.text((padding + 316, legend_y + 8), "Sin evidencia", fill="black",
                  font=font_small, anchor="lm")
        img.save(chart_path)
        return chart_path

    def _coverage_detail_table(self) -> Optional[List[List[str]]]:
        coverage_files = list(self.evidence_dir.glob(
            "organized/traceability_coverage_report_*.json"))
        if not coverage_files:
            return None
        latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
        with open(latest, "r", encoding="utf-8") as f:
            coverage = json.load(f)
        by_module: Dict[str, Dict[str, int]] = {}
        for case_info in coverage.get("coverage", {}).values():
            module = case_info.get("module", "Desconocido")
            by_module.setdefault(module, {"total": 0, "with_evidence": 0})
            by_module[module]["total"] += 1
            if case_info.get("has_evidence"):
                by_module[module]["with_evidence"] += 1
        table_data = [["Módulo", "Total Casos", "Con Evidencia", "Sin Evidencia", "Cobertura %"]]
        for module, counts in sorted(by_module.items()):
            total = counts["total"]
            with_ev = counts["with_evidence"]
            pct = f"{with_ev / total * 100:.1f}%" if total > 0 else "0%"
            table_data.append([module, str(total), str(with_ev),
                               str(total - with_ev), pct])
        grand_total = sum(c["total"] for c in by_module.values())
        grand_with = sum(c["with_evidence"] for c in by_module.values())
        table_data.append(["TOTAL", str(grand_total), str(grand_with),
                           str(grand_total - grand_with),
                           f"{grand_with / grand_total * 100:.1f}%"])
        return table_data

    # ------------------------------------------------------------------ #
    # Resultados de prueba como imagen (consola)
    # ------------------------------------------------------------------ #
    def _run_pytest_category(self, category_dir: str, label: str) -> Tuple[str, int, str]:
        """Ejecuta pytest sobre una categoría y devuelve (texto_salida, exit_code, comando)."""
        cmd = [sys.executable, "-m", "pytest", category_dir, "-q", "-p", "no:cacheprovider"]
        comando = " ".join(cmd)
        try:
            result = subprocess.run(cmd, capture_output=True, text=True,
                                    timeout=300, cwd=HERE.parent)
            salida = result.stdout
            if result.stderr:
                salida += "\n\n--- STDERR ---\n" + result.stderr
            return salida, result.returncode, comando
        except subprocess.TimeoutExpired:
            return "TIEMPO DE EJECUCIÓN AGOTADO (>300s)\nLa categoría no concluyó a tiempo.", -1, comando
        except FileNotFoundError:
            return "No se encontró el ejecutador pytest.", -1, comando
        except Exception as e:
            return f"Error ejecutando pytest: {e}", -1, comando

    @staticmethod
    def _render_text_to_image(text: str, output_path: Path,
                              max_width_px: int = 1400) -> bool:
        """Renderiza texto de consola como imagen PNG (estilo terminal)."""
        if not PIL_AVAILABLE:
            return False
        try:
            try:
                font = ImageFont.truetype("consola.ttf", 14)
                font_small = ImageFont.truetype("consola.ttf", 12)
            except Exception:
                try:
                    font = ImageFont.truetype("cour.ttf", 14)
                    font_small = ImageFont.truetype("cour.ttf", 12)
                except Exception:
                    font = ImageFont.load_default()
                    font_small = ImageFont.load_default()

            lines = text.splitlines()
            # Estimar ancho máximo
            max_line_len = max((len(l) for l in lines), default=80)
            char_w = 14  # aprox ancho de carácter a 14px
            line_h = 18
            pad = 30
            width = min(max_width_px, max(pad * 2 + max_line_len * char_w, 900))
            height = pad * 2 + len(lines) * line_h + 40

            img = Image.new("RGB", (width, height), "#1e1e1e")
            draw = ImageDraw.Draw(img)
            y = pad
            for line in lines:
                # Colorear según estado
                if "PASSED" in line or "APROBADA" in line or "aprobadas" in line.lower():
                    color = "#2ecc71"
                elif "FAILED" in line or "FALLIDA" in line or "fallidas" in line.lower():
                    color = "#e74c3c"
                elif "SKIPPED" in line or "OMITIDA" in line or "omitidas" in line.lower():
                    color = "#f1c40f"
                elif line.startswith("[PRUEBA") or line.startswith("Concluyó"):
                    color = "#3498db"
                else:
                    color = "#d4d4d4"
                draw.text((pad, y), line[:200], fill=color, font=font)
                y += line_h
            img.save(output_path, "PNG", optimize=True)
            return True
        except Exception as e:
            print(f"[WARNING] Error renderizando texto a imagen: {e}")
            return False

    def _capture_category_result_image(self, cat_key: str, cat_label: str,
                                       category_dir: str, out_dir: Path) -> Optional[Path]:
        out_dir.mkdir(parents=True, exist_ok=True)
        img_path = out_dir / f"resultado_{cat_key}.png"
        txt_path = out_dir / f"resultado_{cat_key}.txt"
        salida, exit_code, comando = self._run_pytest_category(category_dir, cat_label)
        # Guardar texto también
        header = f"Comando: {comando}\nCategoría: {cat_label}\nExit code: {exit_code}\n"
        header += f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        header += "=" * 80 + "\n\n"
        full_text = header + salida
        try:
            txt_path.write_text(full_text, encoding="utf-8")
        except Exception:
            pass
        ok = self._render_text_to_image(full_text, img_path)
        if ok:
            return img_path
        return None

    # ------------------------------------------------------------------ #
    # HTML a imagen (reportes y rendimiento)
    # ------------------------------------------------------------------ #
    def _html_to_image(self, html_path: Path, output_path: Path,
                       width: int = 1200, height: int = 900) -> bool:
        if not PLAYWRIGHT_AVAILABLE:
            return False
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": width, "height": height})
                page.goto(f"file://{html_path.absolute()}", wait_until="networkidle")
                page.wait_for_timeout(1500)
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
            return True
        except Exception as e:
            print(f"[WARNING] Error convirtiendo {html_path} a imagen: {e}")
            return False

    # ------------------------------------------------------------------ #
    # Generación del documento
    # ------------------------------------------------------------------ #
    def generate(self, output_path: str = None):
        out = Path(output_path) if output_path else self.output_path
        out.parent.mkdir(parents=True, exist_ok=True)

        # -------------------- Portada híbrida -------------------- #
        for _ in range(3):
            self.doc.add_paragraph()
        title = self.doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run("INFORME HÍBRIDO - CAPÍTULO V")
        run.bold = True
        run.font.size = Pt(24)
        run.font.color.rgb = COLOR_PRIMARIO
        sub = self.doc.add_paragraph()
        sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = sub.add_run("Evidencia Visual de Verificación Automatizada - INVISAP")
        run.font.size = Pt(16)
        run.font.color.rgb = COLOR_SECUNDARIO
        self.doc.add_paragraph()
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = info.add_run(
            "Contenido incrustado (solo Capítulo V):\n"
            "1. Reportes\n"
            "2. Resultados de las Pruebas (por categoría)\n"
            "3. Capturas de UI aprobadas (*_APROVED_*.png) con ID de Caso de Prueba\n"
            "4. Reportes HTML de rendimiento como imagen\n"
            "5. Resumen visual de cobertura de trazabilidad\n"
            f"\nFecha de generación: {datetime.now().strftime('%d de %B de %Y')}\n"
            "Versión: Híbrida 1.0 - Capítulo V"
        )
        run.font.size = Pt(11)
        run.font.color.rgb = COLOR_GRIS
        self.doc.add_page_break()

        # -------------------- Introducción -------------------- #
        self._heading("CAPÍTULO V. Evidencia Visual Híbrida - Capítulo V", 1)
        self.doc.add_paragraph(
            "Este capítulo presenta exclusivamente la evidencia visual generada durante la "
            "ejecución automatizada de pruebas del sistema INVISAP, organizada según la "
            "Matriz de Trazabilidad de Pruebas (Matriz_Trazabilidad_Pruebas_INVISAP.docx). "
            "Se incrustan, como imágenes y cuadros al estilo de la Matriz de Trazabilidad "
            "de Pruebas: reportes, resultados de cada categoría de prueba, capturas de UI "
            "aprobadas con su ID de caso de prueba, reportes HTML de rendimiento convertidos "
            "a imagen y un resumen visual de cobertura de trazabilidad."
        )

        self.doc.add_paragraph()
        self._heading("Alcance de Pruebas Incluidas", 2)
        alcance = [
            ["Categoría", "Herramienta", "Contenido en Capítulo V"],
            ["Pruebas Unitarias", "PyTest", "Resultado de consola como imagen + reporte HTML"],
            ["Pruebas de Integración", "Pytest", "Resultado de consola como imagen + reporte HTML"],
            ["Pruebas de Backend (API)", "Pytest + Postman", "Resultado de consola como imagen + reporte HTML"],
            ["Pruebas de Humo", "Pytest, Selenium y Playwright", "Resultado de consola como imagen"],
            ["Pruebas de Interfaz (UI)", "Playwright y Selenium", "Capturas *_APROVED_*.png con ID de caso"],
            ["Pruebas de Rendimiento", "Locust", "Reportes HTML convertidos a imagen"],
            ["Pruebas de Aceptación", "Pytest, Selenium y Playwright", "Resultado de consola como imagen"],
        ]
        self._add_table(alcance, [Cm(3.5), Cm(4.5), Cm(8)])

        # -------------------- 1. Reportes -------------------- #
        self.doc.add_page_break()
        self._heading("1. Reportes (como Imagen)", 2)
        self.doc.add_paragraph(
            "Los reportes HTML generados por pytest se convierten a imagen y se incrustan "
            "en este capítulo para conservar el estado visual de cada ejecución."
        )
        pytest_reports = self._find_pytest_reports()
        if pytest_reports:
            for rep in pytest_reports:
                img_path = self.evidence_dir / f"hibrido_reporte_{rep['name']}.png"
                if self._html_to_image(rep["path"], img_path):
                    caption = f"Reporte: {rep['name']} ({rep['type']})"
                    self._add_image(img_path, caption, width_cm=16.0)
                else:
                    self.doc.add_paragraph(f"[No se pudo convertir: {rep['name']}]")
        else:
            self.doc.add_paragraph(
                "(No se encontraron reportes HTML de pytest. Ejecute las pruebas con "
                "--html=report.html --self-contained-html para generarlos.)"
            )

        # -------------------- 2. Resultados de pruebas -------------------- #
        self.doc.add_page_break()
        self._heading("2. Resultados de las Pruebas (por Categoría)", 2)
        self.doc.add_paragraph(
            "Cada categoría de prueba se ejecuta con su herramienta designada y el resultado "
            "de consola se incrusta como imagen. A continuación, el resumen tabulado y la "
            "captura de salida de cada categoría."
        )

        resumen_resultados = [["Categoría", "Herramienta", "Estado", "Captura de Consola"]]
        results_dir = self.evidence_dir / "hibrido_resultados"
        results_dir.mkdir(parents=True, exist_ok=True)

        for cat_key, cat_label, cat_dir, herramienta in TEST_CATEGORIES:
            img_path = self._capture_category_result_image(cat_key, cat_label, cat_dir, results_dir)
            estado = "Ejecutado" if img_path else "No ejecutado / sin salida"
            color_estado = COLOR_VERDE if img_path else COLOR_ROJO
            resumen_resultados.append([cat_label, herramienta, estado,
                                       img_path.name if img_path else "-"])
            self.doc.add_paragraph()
            p = self.doc.add_paragraph()
            run = p.add_run(f"{cat_label} - {herramienta}")
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = COLOR_PRIMARIO
            if img_path:
                self._add_image(img_path, f"Salida de consola: {cat_label}", width_cm=16.5)
            else:
                self.doc.add_paragraph(
                    f"(No se pudo capturar la salida de consola para {cat_label}. "
                    f"Verifique que pytest y las dependencias estén instalados.)"
                )

        self.doc.add_paragraph()
        self._heading("Resumen de Resultados por Categoría", 3)
        self._add_table(resumen_resultados, [Cm(4.5), Cm(4.5), Cm(3.5), Cm(3.5)])

        # -------------------- 3. Capturas UI aprobadas -------------------- #
        self.doc.add_page_break()
        self._heading("3. Capturas de Pantalla UI Aprobadas (*_APROVED_*.png)", 2)
        self.doc.add_paragraph(
            "Se incluyen únicamente las capturas de pruebas de interfaz con resultado "
            "APROBADO (patrón *_APROVED_*.png, con compatibilidad *_PASSED_*.png). "
            "Cada captura está vinculada a su ID de Caso de Prueba de la Matriz de "
            "Trazabilidad de Pruebas, presentada en cuadros al estilo de la matriz."
        )
        ui_screenshots = self._find_ui_approved_screenshots()
        if ui_screenshots:
            self.doc.add_paragraph(
                f"Se encontraron {len(ui_screenshots)} captura(s) de UI aprobada(s)."
            )
            # Tabla estilo matriz de trazabilidad: Imagen | ID Caso | Módulo | Prueba
            ui_table_data = [["Captura", "ID Caso (Matriz de Trazabilidad)", "Módulo", "Nombre de Prueba"]]
            for shot in ui_screenshots:
                ui_table_data.append([
                    shot["filename"],
                    shot["traceability_id"] or "-",
                    shot["module"],
                    shot["test_name"],
                ])
            self._add_table(ui_table_data, [Cm(5.5), Cm(4), Cm(3.5), Cm(3)])
            self.doc.add_paragraph()
            # Imágenes a tamaño completo
            p = self.doc.add_paragraph()
            run = p.add_run("Capturas a Tamaño Completo:")
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = COLOR_PRIMARIO
            for shot in ui_screenshots[:6]:
                caption = (f"UI Aprobada: {shot['module']} | "
                           f"Caso: {shot['traceability_id'] or '-'} | "
                           f"Prueba: {shot['test_name'] or '-'} "
                           f"[patrón: {shot['pattern']}]")
                self._add_image(shot["path"], caption, width_cm=15.0)
        else:
            self.doc.add_paragraph(
                "(No se encontraron capturas de UI aprobadas con patrón *_APROVED_*.png "
                "ni *_PASSED_*.png. Ejecute las pruebas UI con INVISAP_TEST_URL configurado: "
                "python -m pytest tests/ui -v)"
            )

        # -------------------- 4. Reportes de rendimiento -------------------- #
        self.doc.add_page_break()
        self._heading("4. Reportes de Rendimiento (Locust) como Imagen", 2)
        self.doc.add_paragraph(
            "Los reportes HTML de Locust se convierten a imagen PNG para su inclusión "
            "directa en el Capítulo V."
        )
        perf_reports = self._find_performance_reports()
        if perf_reports and PLAYWRIGHT_AVAILABLE:
            self.doc.add_paragraph(
                f"Se convirtieron {len(perf_reports)} reporte(s) HTML de Locust a imagen:"
            )
            for report in perf_reports[:5]:
                img_path = self.evidence_dir / f"hibrido_perf_{report['name']}.png"
                if self._html_to_image(report["path"], img_path):
                    caption = f"Rendimiento: {report['name']} | {report['type']}"
                    self._add_image(img_path, caption, width_cm=16.0)
                else:
                    self.doc.add_paragraph(f"[No se pudo convertir: {report['name']}]")
        elif perf_reports:
            self.doc.add_paragraph(
                "Reportes HTML de Locust encontrados pero Playwright no está disponible "
                "para conversión a imagen."
            )
            for report in perf_reports:
                self.doc.add_paragraph(f"• {report['name']} ({report['path']})")
        else:
            self.doc.add_paragraph(
                "(No se encontraron reportes de rendimiento. Ejecute: "
                "python tests/performance/run_performance.py --all --profile quick)"
            )

        # -------------------- 5. Cobertura de trazabilidad -------------------- #
        self.doc.add_page_break()
        self._heading("5. Resumen Visual de Cobertura de Trazabilidad", 2)
        self.doc.add_paragraph(
            "El siguiente gráfico muestra la cobertura de evidencia por tipo de prueba "
            "respecto a los casos definidos en la Matriz de Trazabilidad de Pruebas, "
            "seguido de un detalle por módulo en cuadros estilo matriz."
        )
        chart_path = self._generate_traceability_chart()
        if chart_path:
            self._add_image(chart_path,
                            "Cobertura de Trazabilidad: casos con evidencia vs total por tipo de prueba",
                            width_cm=16.0)
        else:
            self.doc.add_paragraph(
                "(No se pudo generar el gráfico. Requiere Pillow y un reporte de "
                "cobertura organizado/traceability_coverage_report_*.json.)"
            )

        detail_table = self._coverage_detail_table()
        if detail_table:
            self.doc.add_paragraph()
            self._heading("Detalle de Cobertura por Módulo", 3)
            self._add_table(detail_table, [Cm(5), Cm(2.5), Cm(2.5), Cm(2.5), Cm(2.5)])

        # -------------------- Referencias -------------------- #
        self.doc.add_page_break()
        self._heading("Referencias Metodológicas", 2)
        refs = [
            "Matriz de Trazabilidad de Pruebas.docx (formato suministrado). Estructura de seis columnas; los IDs de caso son provisionales y requieren validación contra requisitos aprobados.",
            "Manual Informe de Proyecto III, documento suministrado. Estructura: Plan de Pruebas, Bitácora, Plan de Instalación, Plan de Capacitación y recomendaciones/evolución.",
            "Informe del Sistema INVILARA - Proyecto III (PDF suministrado). Fuente de evidencia histórica.",
            "Pytest Documentation; Locust Documentation; Playwright Documentation; Selenium Documentation.",
        ]
        for i, ref in enumerate(refs, 1):
            self.doc.add_paragraph(f"{i}. {ref}")

        self.doc.save(str(out))
        print(f"[REPORTE HÍBRIDO] Capítulo V generado: {out}")
        return out


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generar Capítulo V híbrido con evidencia visual embebida (INVISAP)"
    )
    parser.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR),
                        help="Directorio base de evidencia")
    parser.add_argument("--matrix", default=str(DEFAULT_MATRIX_PATH),
                        help="Ruta a la Matriz de Trazabilidad de Pruebas DOCX")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT),
                        help="Ruta del documento Word de salida")
    args = parser.parse_args()

    generator = HybridChapterVGenerator(
        evidence_dir=args.evidence_dir,
        matrix_path=args.matrix,
        output_path=args.output,
    )
    generator.generate(args.output)


if __name__ == "__main__":
    main()
