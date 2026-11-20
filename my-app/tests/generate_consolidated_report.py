"""Generate consolidated Word report for INVISAP - Chapter IV & V with evidence."""

import os
import json
import re
import base64
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

# Try to import playwright for HTML-to-image conversion
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Try to import PIL for image handling
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class ConsolidatedReportGenerator:
    """Generate Word report for Chapter IV & V with test evidence."""
    
    def __init__(self, evidence_dir: str, matrix_path: str = None):
        self.evidence_dir = Path(evidence_dir)
        self.matrix_path = matrix_path
        self.doc = Document()
        self._setup_document()
    
    def _setup_document(self):
        """Configure document styles and page setup."""
        # Set default font
        style = self.doc.styles['Normal']
        font = style.font
        font.name = 'Arial'
        font.size = Pt(11)
        
        # Configure page margins
        for section in self.doc.sections:
            section.top_margin = Cm(2.5)
            section.bottom_margin = Cm(2.5)
            section.left_margin = Cm(3.0)
            section.right_margin = Cm(3.0)
    
    def _add_heading_styled(self, text: str, level: int):
        """Add heading with custom styling."""
        heading = self.doc.add_heading(text, level=level)
        for run in heading.runs:
            run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        return heading
    
    def _add_table_styled(self, rows: int, cols: int, data: List[List[str]], 
                          header_row: bool = True, col_widths: List[Cm] = None):
        """Add a styled table to the document."""
        table = self.doc.add_table(rows=rows, cols=cols, style='Table Grid')
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Set column widths if provided
        if col_widths:
            for i, width in enumerate(col_widths):
                for row in table.rows:
                    row.cells[i].width = width
        
        # Fill data
        for row_idx, row_data in enumerate(data):
            for col_idx, cell_text in enumerate(row_data):
                cell = table.cell(row_idx, col_idx)
                cell.text = ""
                p = cell.paragraphs[0]
                run = p.add_run(str(cell_text))
                run.font.size = Pt(9)
                run.font.name = 'Arial'
                if header_row and row_idx == 0:
                    run.bold = True
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                    # Set header background color
                    shading = OxmlElement('w:shd')
                    shading.set(qn('w:fill'), '2C3E50')
                    shading.set(qn('w:val'), 'clear')
                    cell._tc.get_or_add_tcPr().append(shading)
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
        
        return table
    
    def _html_to_image(self, html_path: Path, output_path: Path, width: int = 1200, height: int = 800) -> bool:
        """Convert HTML file to PNG image using Playwright."""
        if not PLAYWRIGHT_AVAILABLE:
            return False
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width': width, 'height': height})
                page.goto(f"file://{html_path.absolute()}", wait_until='networkidle')
                page.wait_for_timeout(1000)  # Wait for any JS to render
                page.screenshot(path=str(output_path), full_page=True)
                browser.close()
            return True
        except Exception as e:
            print(f"[WARNING] Error converting {html_path} to image: {e}")
            return False
    
    def _resize_image_if_needed(self, image_path: Path, max_width_cm: float = 16.0) -> Path:
        """Resize image if wider than max_width_cm, return path to resized image."""
        if not PIL_AVAILABLE:
            return image_path
        
        try:
            with Image.open(image_path) as img:
                # Convert cm to pixels (assuming 96 DPI)
                max_width_px = int(max_width_cm * 96 / 2.54)
                if img.width > max_width_px:
                    ratio = max_width_px / img.width
                    new_height = int(img.height * ratio)
                    img_resized = img.resize((max_width_px, new_height), Image.Resampling.LANCZOS)
                    resized_path = image_path.with_stem(f"{image_path.stem}_resized")
                    img_resized.save(resized_path, 'PNG', optimize=True)
                    return resized_path
        except Exception as e:
            print(f"[WARNING] Error resizing {image_path}: {e}")
        return image_path
    
    def _find_ui_screenshots(self) -> List[Dict]:
        """Find UI screenshots with traceability info from filename."""
        screenshots = []
        ui_dir = self.evidence_dir / "ui"
        if not ui_dir.exists():
            return screenshots
        
        for img_path in ui_dir.glob("*_PASSED_*.png"):
            # Parse filename: ui_Login_CP-UI-RNF01_test_formulario_acceso_PASSED_20261120_103000.png
            name = img_path.stem
            parts = name.split('_')
            
            traceability_id = ""
            module = ""
            test_name = ""
            
            for i, part in enumerate(parts):
                if part.startswith("CP-"):
                    traceability_id = part
                    if i > 0:
                        module = parts[i-1]
                    if i+1 < len(parts):
                        test_name = "_".join(parts[i+1:]).replace("_PASSED", "").replace("_FAILED", "")
                    break
            
            screenshots.append({
                "path": img_path,
                "traceability_id": traceability_id,
                "module": module.replace('_', ' ').title() if module else "Login",
                "test_name": test_name,
                "filename": img_path.name
            })
        
        return screenshots
    
    def _find_performance_reports(self) -> List[Dict]:
        """Find performance HTML reports."""
        reports = []
        perf_dir = self.evidence_dir / "performance"
        if not perf_dir.exists():
            return reports
        
        for html_path in perf_dir.glob("locust_report_*.html"):
            reports.append({
                "path": html_path,
                "name": html_path.stem,
                "type": "Locust HTML Report"
            })
        
        # Also check for module-specific reports
        for module_dir in perf_dir.iterdir():
            if module_dir.is_dir():
                for html_path in module_dir.glob("*.html"):
                    reports.append({
                        "path": html_path,
                        "name": f"{module_dir.name}_{html_path.stem}",
                        "type": "Module Performance Report"
                    })
        
        return reports
    
    def _generate_traceability_coverage_chart(self) -> Optional[Path]:
        """Generate a visual chart of traceability coverage."""
        if not PIL_AVAILABLE:
            return None
        
        coverage_files = list(self.evidence_dir.glob("organized/traceability_coverage_report_*.json"))
        if not coverage_files:
            return None
        
        latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
        with open(latest, 'r', encoding='utf-8') as f:
            coverage = json.load(f)
        
        # Count by test type
        type_counts = {}
        for case_info in coverage.get("coverage", {}).values():
            test_type = case_info.get("test_type", "unknown")
            has_ev = case_info.get("has_evidence", False)
            if test_type not in type_counts:
                type_counts[test_type] = {"total": 0, "with_evidence": 0}
            type_counts[test_type]["total"] += 1
            if has_ev:
                type_counts[test_type]["with_evidence"] += 1
        
        if not type_counts:
            return None
        
        # Create chart image
        chart_path = self.evidence_dir / "traceability_coverage_chart.png"
        
        # Simple bar chart using PIL
        types = list(type_counts.keys())
        totals = [type_counts[t]["total"] for t in types]
        with_ev = [type_counts[t]["with_evidence"] for t in types]
        
        # Chart dimensions
        bar_height = 40
        padding = 60
        chart_width = 800
        chart_height = len(types) * bar_height + 2 * padding + 100
        
        img = Image.new('RGB', (chart_width, chart_height), 'white')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
            font_small = ImageFont.truetype("arial.ttf", 11)
        except:
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        max_total = max(totals) if totals else 1
        bar_max_width = chart_width - 2 * padding - 150
        
        # Title
        draw.text((chart_width // 2, 20), "Cobertura de Trazabilidad por Tipo de Prueba", 
                  fill='black', font=font, anchor="mm")
        
        for i, (t, total, ev) in enumerate(zip(types, totals, with_ev)):
            y = padding + i * bar_height
            # Label
            draw.text((padding - 10, y + bar_height // 2), t.capitalize(), 
                      fill='black', font=font_small, anchor="rm")
            
            # Total bar (background)
            total_width = int((total / max_total) * bar_max_width)
            draw.rectangle([padding, y, padding + total_width, y + bar_height - 5], 
                           fill='#ecf0f1', outline='#bdc3c7')
            
            # Evidence bar (foreground)
            ev_width = int((ev / max_total) * bar_max_width) if max_total > 0 else 0
            color = '#27ae60' if ev == total else '#f39c12' if ev > 0 else '#e74c3c'
            draw.rectangle([padding, y, padding + ev_width, y + bar_height - 5], 
                           fill=color, outline=color)
            
            # Numbers
            draw.text((padding + total_width + 10, y + bar_height // 2), 
                      f"{ev}/{total} ({ev/total*100:.0f}%)", 
                      fill='black', font=font_small, anchor="lm")
        
        # Legend
        legend_y = padding + len(types) * bar_height + 20
        draw.rectangle([padding, legend_y, padding + 20, legend_y + 15], fill='#27ae60')
        draw.text((padding + 25, legend_y + 7), "Completa (100%)", fill='black', font=font_small, anchor="lm")
        draw.rectangle([padding + 150, legend_y, padding + 170, legend_y + 15], fill='#f39c12')
        draw.text((padding + 175, legend_y + 7), "Parcial", fill='black', font=font_small, anchor="lm")
        draw.rectangle([padding + 250, legend_y, padding + 270, legend_y + 15], fill='#e74c3c')
        draw.text((padding + 275, legend_y + 7), "Sin evidencia", fill='black', font=font_small, anchor="lm")
        
        img.save(chart_path)
        return chart_path
    
    def _add_image_with_caption(self, image_path: Path, caption: str, width_cm: float = 16.0):
        """Add image to document with caption."""
        if not image_path.exists():
            return
        
        # Resize if needed
        resized_path = self._resize_image_if_needed(image_path, width_cm)
        
        try:
            self.doc.add_picture(str(resized_path), width=Cm(width_cm))
            # Add caption
            caption_para = self.doc.add_paragraph()
            caption_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = caption_para.add_run(caption)
            run.font.size = Pt(9)
            run.font.italic = True
            run.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
            self.doc.add_paragraph()  # spacing
        except Exception as e:
            print(f"[WARNING] Error adding image {image_path}: {e}")
    
    def _add_evidence_table_with_images(self, screenshots: List[Dict], cols: int = 3):
        """Add a table with screenshot thumbnails and traceability info."""
        if not screenshots:
            return
        
        # Group by module
        by_module = {}
        for s in screenshots:
            module = s["module"]
            if module not in by_module:
                by_module[module] = []
            by_module[module].append(s)
        
        for module, shots in by_module.items():
            self.doc.add_paragraph()
            p = self.doc.add_paragraph()
            run = p.add_run(f"Módulo: {module}")
            run.bold = True
            run.font.size = Pt(11)
            run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
            
            # Table: Image | Traceability ID | Test Name
            rows = len(shots) + 1
            table = self.doc.add_table(rows=rows, cols=3, style='Table Grid')
            table.alignment = WD_TABLE_ALIGNMENT.CENTER
            
            # Header
            headers = ['Captura', 'ID Caso (Matriz)', 'Nombre de Prueba']
            for i, h in enumerate(headers):
                cell = table.cell(0, i)
                cell.text = ""
                p = cell.paragraphs[0]
                run = p.add_run(h)
                run.bold = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
                shading = OxmlElement('w:shd')
                shading.set(qn('w:fill'), '2C3E50')
                shading.set(qn('w:val'), 'clear')
                cell._tc.get_or_add_tcPr().append(shading)
            
            for row_idx, shot in enumerate(shots, 1):
                # Image cell
                cell_img = table.cell(row_idx, 0)
                cell_img.text = ""
                p = cell_img.paragraphs[0]
                try:
                    run = p.add_run()
                    run.add_picture(str(shot["path"]), width=Cm(5))
                except:
                    p.add_run("[Imagen no disponible]").font.size = Pt(8)
                
                # Traceability ID
                cell_id = table.cell(row_idx, 1)
                cell_id.text = ""
                p = cell_id.paragraphs[0]
                run = p.add_run(shot["traceability_id"])
                run.font.size = Pt(9)
                run.font.name = 'Consolas'
                
                # Test name
                cell_name = table.cell(row_idx, 2)
                cell_name.text = ""
                p = cell_name.paragraphs[0]
                run = p.add_run(shot["test_name"])
                run.font.size = Pt(9)
            
            # Set column widths
            for row in table.rows:
                row.cells[0].width = Cm(6)
                row.cells[1].width = Cm(4)
                row.cells[2].width = Cm(6)
    
    def generate(self, output_path: str):
        """Generate the complete report."""
        # Title page
        self._add_title_page()
        
        # Table of contents placeholder
        self.doc.add_page_break()
        self._add_heading_styled('Tabla de Contenidos', 1)
        self.doc.add_paragraph('(Generar automáticamente en Word: Referencias > Tabla de contenidos)')
        
        # Chapter IV
        self.doc.add_page_break()
        self._generate_chapter_iv()
        
        # Chapter V
        self.doc.add_page_break()
        self._generate_chapter_v()
        
        # Save
        self.doc.save(output_path)
        print(f"[REPORTE] Informe generado: {output_path}")
    
    def _add_title_page(self):
        """Add title page."""
        for _ in range(4):
            self.doc.add_paragraph()
        
        title = self.doc.add_paragraph()
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = title.add_run('INFORME DEL SISTEMA INVILARA')
        run.bold = True
        run.font.size = Pt(24)
        run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        
        subtitle = self.doc.add_paragraph()
        subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = subtitle.add_run('Proyecto III - Trayecto III')
        run.font.size = Pt(18)
        run.font.color.rgb = RGBColor(0x34, 0x49, 0x5E)
        
        self.doc.add_paragraph()
        
        chapter = self.doc.add_paragraph()
        chapter.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = chapter.add_run('Capítulo IV: Plan de Pruebas, Bitácora, Instalación y Capacitación\n'
                               'Capítulo V: Recomendaciones y Evolución Previsible')
        run.font.size = Pt(14)
        run.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
        
        self.doc.add_paragraph()
        self.doc.add_paragraph()
        
        info = self.doc.add_paragraph()
        info.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = info.add_run(f'Instituto de Vialidad del Estado Lara (INVILARA)\n'
                           f'UNEFA - Universidad Nacional Experimental Politécnica de la Fuerza Armada\n'
                           f'Fecha de generación: {datetime.now().strftime("%d de %B de %Y")}\n'
                           f'Versión: 1.0 - Documento Final')
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x7F, 0x8C, 0x8D)
        
        self.doc.add_page_break()
    
    def _generate_chapter_iv(self):
        """Generate Chapter IV content."""
        self._add_heading_styled('CAPÍTULO IV. Plan de Pruebas, Bitácora, Instalación y Capacitación', 1)
        
        # Introduction
        self.doc.add_paragraph(
            'Este capítulo presenta el plan de verificación del sistema INVISAP (Sistema de Gestión e '
            'Información para el Seguimiento y Control de Solicitudes con módulo de Análisis y Priorización), '
            'las metodologías aplicadas por nivel y tipo de prueba, los resultados de las ejecuciones '
            'automatizadas documentadas, y los planes de instalación y capacitación. La existencia de una '
            'prueba automatizada no significa por sí sola que un requerimiento haya sido aprobado por el '
            'usuario: la validación funcional y la firma de los responsables deben quedar registradas '
            'en los formatos de este proyecto.'
        )
        
        # 4.1 Plan de Pruebas
        self._add_heading_styled('4.1 Plan de Pruebas', 2)
        
        # Objective
        self._add_heading_styled('4.1.1 Objetivo', 3)
        self.doc.add_paragraph(
            'Verificar progresivamente los componentes, sus conexiones y el comportamiento '
            'del sistema INVISAP, registrar los resultados observados, facilitar la '
            'reproducción de errores y dejar trazabilidad entre requisitos funcionales, '
            'casos de prueba y correcciones.'
        )
        
        # Scope
        self._add_heading_styled('4.1.2 Alcance y Niveles', 3)
        self.doc.add_paragraph(
            'El alcance comprende los veinte (20) módulos funcionales del sistema:'
        )
        
        modules = [
            'Solicitudes', 'Gravedad de Obra', 'Prioridad', 'Proyectos', 'Maquinaria',
            'Contratación', 'Empresa', 'Obras', 'Empleados', 'Inspecciones',
            'Evidencias', 'Informe de Avance de Obra', 'Publicaciones', 'Reportes PDF',
            'Reportes Excel', 'Reportes Estadísticos', 'Usuarios', 'Permisos por Rol',
            'Administración de Respaldos', 'Bitácora'
        ]
        
        for i, module in enumerate(modules, 1):
            self.doc.add_paragraph(f'{i}. {module}', style='List Number')
        
        self.doc.add_paragraph(
            'La planificación sigue tres niveles de prueba:'
        )
        
        levels = [
            ('Nivel 1 - Unidad', 'Verifica funciones y reglas pequeñas de manera aislada.'),
            ('Nivel 2 - Integración', 'Verifica contratos y conexiones entre componentes, de forma incremental. '
             'La integración con una base de datos real se ejecuta en un ambiente de pruebas separado.'),
            ('Nivel 3 - Sistema', 'Verifica el producto ensamblado desde sus interfaces HTTP y visuales. '
             'Incluye humo, API, interfaz y rendimiento; la aceptación requiere además criterios '
             'y conformidad de los usuarios responsables.')
        ]
        
        for level, desc in levels:
            p = self.doc.add_paragraph()
            run = p.add_run(f'{level}: ')
            run.bold = True
            p.add_run(desc)
        
        # Methodology
        self._add_heading_styled('4.1.3 Metodología Diferenciada por Tipo de Prueba', 3)
        
        methodology_data = [
            ['Tipo', 'Objetivo y Metodología', 'Herramientas y Datos', 'Evidencia y Límites'],
            ['Unidad', 
             'Caja negra con particiones de equivalencia y valores límite; caja blanca para reglas y ramas seleccionadas; Preparar-Actuar-Verificar con fixtures/mocks. No se midió cobertura de ramas ni caminos independientes.',
             'Pytest, pytest.mark.parametrize, fixtures y mocks.',
             'tests/unit: 20 suites de módulo con 376 casos, más 51 casos transversales (427 en total). Se amplió la prueba de métodos y sus interacciones SQL simuladas; no se midió cobertura de ramas ni persistencia real.'],
            ['Integración',
             'Integración incremental: 20 contratos Flask y dos flujos Contratación→Bitácora. Se verifica colaboración y auditoría; una colisión de ID inyectada comprueba el reintento. Los dobles aíslan dependencias.',
             'Pytest, cliente Flask, mocks y fallo controlado.',
             'tests/integration: 22 casos aprobados. No equivale a transacciones reales contra MySQL.'],
            ['Backend/API',
             'Contratos HTTP positivos y negativos: estado, JSON, autenticación/autorización, filtros, paginación y parámetros propagados al servicio/modelo. PDF/Excel verifican formularios GET; no generan archivos.',
             'Pytest/cliente Flask con modelos simulados; Postman Desktop para solicitudes HTTP del entorno configurado. No se instaló Guzzle porque el backend es Python.',
             'tests/api: 20 suites por módulo y parametrización de reportes. postman/collections: contratos HTTP y caso sin sesión; los contratos positivos requieren cookie e IDs de prueba.'],
            ['Humo',
             'Una ruta esencial por módulo; comprobación rápida de respuesta HTTP sin error 404/500. Un 401/302 de autenticación confirma que se alcanzó una ruta protegida, no que la función autenticada opere correctamente.',
             'Pytest y cliente Flask; HTTP real o navegador complementan cuando hay servidor activo.',
             'tests/smoke: 20 módulos y acceso. Distinguir la suite local de las verificaciones HTTP en vivo documentadas por separado.'],
            ['Interfaz',
             'Extremo a extremo desde navegador: abrir pantalla, comprobar respuesta y controles visibles, descartar mensajes incorrectos y guardar captura. No se intenta una navegación autenticada en el caso existente.',
             'Playwright + Chromium; Selenium estaba instalado en la ejecución histórica, pero no se utilizó.',
             'tests/ui: un caso de acceso. La ejecución actual se omitió por falta de INVISAP_TEST_URL; existe una ejecución histórica aprobada solo para /login.'],
            ['Rendimiento',
             'Solicitudes GET de solo lectura por módulo con perfiles quick, baseline, stress y spike; se registran solicitudes, fallos y percentiles. Antes de interpretar tiempos se requiere acceso autenticado y carga/datos controlados.',
             'Locust, cookie de sesión de prueba e identificadores existentes cuando la ruta los requiere.',
             'Se ejecutaron dos series quick para los 20 módulos y una baseline para Solicitudes. En la serie más reciente, 18 módulos devolvieron 401/302 y dos 200; no es una medición autenticada aprobada.'],
            ['Aceptación',
             'Caja negra basada en requisito e historia: Dado/Cuando/Entonces, flujo completo, resultado observable y evaluación del validador. Registrar errores, correcciones, retest y firma.',
             'Pytest con Playwright/Selenium puede apoyar el recorrido; la decisión final requiere el formato de especificación y acta firmados por usuarios.',
             'Pendiente: no hay criterios firmados, validador designado ni acta de aceptación; no se ejecutó una suite de aceptación.']
        ]
        
        self._add_table_styled(len(methodology_data), 4, methodology_data, 
                               col_widths=[Cm(2.5), Cm(5.5), Cm(4.5), Cm(4.5)])
        
        # Test Suite Organization
        self._add_heading_styled('4.1.4 Organización de las Suites por Módulo', 3)
        self.doc.add_paragraph(
            'Las pruebas no están concentradas en un único archivo. Unidad, integración, '
            'API y humo tienen un archivo independiente para cada módulo; los nombres '
            'exactos se indican abajo. El ejecutor pytest descubre y ejecuta esas suites '
            'por categoría o todas juntas. Locust también tiene un escenario por módulo, '
            'pero run_performance.py --all los ejecuta secuencialmente. Las comprobaciones '
            'de interfaz actuales son transversales al formulario de acceso y no hay casos '
            'automatizados de aceptación por módulo.'
        )
        
        # Suite table (abbreviated for space)
        suite_data = [['Módulo', 'Unidad', 'Integración', 'API', 'Humo', 'Rendimiento']]
        module_files = {
            'Solicitudes': ('test_solicitudes.py', 'test_integracion_solicitudes.py', 'test_api_solicitudes.py', 'test_humo_solicitudes.py', 'locust_solicitudes.py'),
            'Gravedad de Obra': ('test_gravedad_obra.py', 'test_integracion_gravedad_obra.py', 'test_api_gravedad_obra.py', 'test_humo_gravedad_obra.py', 'locust_gravedad_obra.py'),
            'Prioridad': ('test_prioridad.py', 'test_integracion_prioridad.py', 'test_api_prioridad.py', 'test_humo_prioridad.py', 'locust_prioridad.py'),
            'Proyectos': ('test_proyectos.py', 'test_integracion_proyectos.py', 'test_api_proyectos.py', 'test_humo_proyectos.py', 'locust_proyectos.py'),
            'Maquinaria': ('test_maquinaria.py', 'test_integracion_maquinaria.py', 'test_api_maquinaria.py', 'test_humo_maquinaria.py', 'locust_maquinaria.py'),
            'Contratación': ('test_contratacion.py', 'test_integracion_contratacion.py', 'test_api_contratacion.py', 'test_humo_contratacion.py', 'locust_contratacion.py'),
            'Empresa': ('test_empresa.py', 'test_integracion_empresa.py', 'test_api_empresa.py', 'test_humo_empresa.py', 'locust_empresa.py'),
            'Obras': ('test_obras.py', 'test_integracion_obras.py', 'test_api_obras.py', 'test_humo_obras.py', 'locust_obras.py'),
            'Empleados': ('test_empleados.py', 'test_integracion_empleados.py', 'test_api_empleados.py', 'test_humo_empleados.py', 'locust_empleados.py'),
            'Inspecciones': ('test_inspecciones.py', 'test_integracion_inspecciones.py', 'test_api_inspecciones.py', 'test_humo_inspecciones.py', 'locust_inspecciones.py'),
            'Evidencias': ('test_evidencias.py', 'test_integracion_evidencias.py', 'test_api_evidencias.py', 'test_humo_evidencias.py', 'locust_evidencias.py'),
            'Informe de Avance': ('test_informe_avance.py', 'test_integracion_informe_avance.py', 'test_api_informe_avance.py', 'test_humo_informe_avance.py', 'locust_informe_avance.py'),
            'Publicaciones': ('test_publicaciones.py', 'test_integracion_publicaciones.py', 'test_api_publicaciones.py', 'test_humo_publicaciones.py', 'locust_publicaciones.py'),
            'Reportes PDF': ('test_reportes_pdf.py', 'test_integracion_reportes_pdf.py', 'test_api_reportes_pdf.py', 'test_humo_reportes_pdf.py', 'locust_reportes_pdf.py'),
            'Reportes Excel': ('test_reportes_excel.py', 'test_integracion_reportes_excel.py', 'test_api_reportes_excel.py', 'test_humo_reportes_excel.py', 'locust_reportes_excel.py'),
            'Reportes Estadísticos': ('test_reportes_estadisticos.py', 'test_integracion_reportes_estadisticos.py', 'test_api_reportes_estadisticos.py', 'test_humo_reportes_estadisticos.py', 'locust_reportes_estadisticos.py'),
            'Usuarios': ('test_usuarios.py', 'test_integracion_usuarios.py', 'test_api_usuarios.py', 'test_humo_usuarios.py', 'locust_usuarios.py'),
            'Permisos por Rol': ('test_permisos_por_rol.py', 'test_integracion_permisos_por_rol.py', 'test_api_permisos_por_rol.py', 'test_humo_permisos_por_rol.py', 'locust_permisos_por_rol.py'),
            'Administración de Respaldos': ('test_administracion_respaldos.py', 'test_integracion_administracion_respaldos.py', 'test_api_administracion_respaldos.py', 'test_humo_administracion_respaldos.py', 'locust_administracion_respaldos.py'),
            'Bitácora': ('test_bitacora.py', 'test_integracion_bitacora.py', 'test_api_bitacora.py', 'test_humo_bitacora.py', 'locust_bitacora.py'),
        }
        
        for module, files in module_files.items():
            suite_data.append([module] + list(files))
        
        self._add_table_styled(len(suite_data), 6, suite_data,
                               col_widths=[Cm(3.5), Cm(3), Cm(3), Cm(3), Cm(3), Cm(3)])
        
        # Locust endpoints
        self._add_heading_styled('Endpoints de Lectura para Pruebas de Rendimiento (Locust)', 4)
        
        endpoint_data = [['Módulo', 'Endpoint de Lectura']]
        endpoints = {
            'Solicitudes': '/api/obtener-solicitudes-json',
            'Gravedad de Obra': '/api/gravedad/listar',
            'Prioridad': '/api/prioridad/listar',
            'Proyectos': '/api/proyecto/validar-codigo/<código>',
            'Maquinaria': '/api/maquinaria/listar',
            'Contratación': '/api/obtener-empresas-json',
            'Empresa': '/api/empresas/<RIF>',
            'Obras': '/api/obra/estados',
            'Empleados': '/empleados/api/listar-json',
            'Inspecciones': '/inspecciones/api/inspectores/listar',
            'Evidencias': '/api/evidencias/validar/<id>',
            'Informe de Avance': '/api/informes/listar-json',
            'Publicaciones': '/api/publicaciones/validar-informe/<id>',
            'Reportes PDF': '/reportes/reporte-pdf (formulario GET)',
            'Reportes Excel': '/reportes/reporte-excel (formulario GET)',
            'Reportes Estadísticos': '/reporte-estadistico/data',
            'Usuarios': '/api/users/<id>',
            'Permisos por Rol': '/api/seguridad/permisos/obtener/<id_rol>',
            'Administración de Respaldos': '/respaldo/api/listar-json',
            'Bitácora': '/api/obtener-bitacora-json',
        }
        
        for module, endpoint in endpoints.items():
            endpoint_data.append([module, endpoint])
        
        self._add_table_styled(len(endpoint_data), 2, endpoint_data,
                               col_widths=[Cm(6), Cm(10)])
        
        # Planning table
        self._add_heading_styled('4.1.5 Planificación de Unidad, Integración y Sistema', 3)
        
        planning_data = [
            ['Nivel', 'Objetivo Específico', 'Actividades', 'Lugar / Fecha', 'Responsables', 'Evidencia / Estado'],
            ['Unidad', 'Evaluar reglas y validadores aislados en las 20 suites.',
             'Particiones válidas/inválidas, límites, parametrización, mocks y contraste esperado/observado.',
             'Ejecución local automatizada, 2026-11-12.',
             'Equipo de desarrollo ejecutó; validador funcional por designar.',
             '427/427 aprobadas; 376 casos en las 20 suites y 51 transversales. Cobertura de métodos/ramas no medida.'],
            ['Integración', 'Comprobar contratos Flask y colaboración entre componentes.',
             '20 contratos de ruta; 2 flujos Contratación/Bitácora, incluido error de duplicado inyectado y reintento.',
             'Ejecución local automatizada, 2026-11-12.',
             'Equipo de desarrollo ejecutó; DBA/tutor deberá validar transacciones reales.',
             '22/22 aprobadas; no certifica escrituras/transacciones reales de MySQL.'],
            ['Sistema', 'Verificar el sistema ensamblado y reportar límites de HTTP, UI, carga y aceptación.',
             'Ejecutar API/humo local; UI omitida por falta de URL; revisar los registros Locust del 2026-10-29 y la carga histórica de / y /login del 2026-10-23; aceptación con usuarios pendiente.',
             'Pytest local el 2026-11-12; Locust contra 127.0.0.1:5600 el 2026-10-29; carga general documentada el 2026-10-23.',
             'Equipo de desarrollo ejecutó; responsables funcionales pendientes.',
             'API 33/33 y humo 21/21; UI 1 omitida; Locust por módulo: 2/20 escenarios HTTP aprobados; 18 no recibieron una respuesta HTTP 200 autenticada; aceptación pendiente.']
        ]
        
        self._add_table_styled(len(planning_data), 6, planning_data,
                               col_widths=[Cm(2), Cm(3), Cm(4), Cm(3), Cm(3), Cm(4)])
        
        # Entry/Exit criteria
        self._add_heading_styled('4.1.6 Criterios de Entrada, Salida y Gestión de Defectos', 3)
        
        criteria = [
            ('Entrada:', 'Versión de código identificada; ambiente y datos de prueba autorizados; '
             'requerimiento y resultado esperado trazables; dependencias de las pruebas disponibles.'),
            ('Salida por caso:', 'Resultado observado registrado, evidencia conservada, error vinculado a un '
             'identificador y reejecución después de cualquier corrección.'),
            ('Salida de unidad/integración automatizadas:', 'Ninguna prueba fallida; los warnings y las '
             'limitaciones de entorno se reportan, no se ocultan.'),
            ('Salida de sistema/aceptación:', 'Todos los criterios acordados ejecutados, defectos bloqueantes '
             'resueltos, retest satisfactorio y aprobación del validador funcional registrada. '
             'Estos últimos criterios aún no cuentan con firma de usuario.'),
            ('Rendimiento:', 'No se define un umbral de milisegundos arbitrario. El tutor/comunidad debe '
             'acordarlo antes de interpretar una carga como aprobada.')
        ]
        
        for title, desc in criteria:
            p = self.doc.add_paragraph()
            run = p.add_run(title + ' ')
            run.bold = True
            p.add_run(desc)
        
        self.doc.add_paragraph(
            'Las plantillas editables para completar el plan y cada caso funcional están en '
            'tests/documentation/. La matriz con los campos del formato institucional está en '
            'Matriz_Trazabilidad_Pruebas_INVISAP.docx; sus IDs CP son provisionales y las '
            'filas marcadas pendientes no representan pruebas ejecutadas.'
        )
        
        # 4.2 Bitácora de Pruebas
        self._add_heading_styled('4.2 Bitácora de Pruebas', 2)
        
        # Execution data
        self._add_heading_styled('4.2.1 Datos de Ejecución', 3)
        
        exec_data = [
            ['Parámetro', 'Valor'],
            ['Fecha de la suite completa', '2026-11-12'],
            ['Ambiente', 'Ejecución local automatizada en Windows, Python 3.14.3 y pytest 9.1.1'],
            ['Responsable técnico', 'Equipo de desarrollo (ejecución automatizada)'],
            ['Validador funcional', 'Pendiente de designación y firma del tutor/usuarios responsables'],
            ['Alcance de datos', 'Los casos de unidad, API y flujos integrados usan fixtures/dobles para '
             'aislar dependencias; esta ejecución no certifica persistencia contra una base real.'],
            ['Comando', 'python -m pytest tests\\unit tests\\integration tests\\api tests\\smoke tests\\ui -q '
             'con salida JUnit temporal para verificar el desglose por categoría'],
            ['Duración', '7.45 s en la última corrida; no se usa el tiempo de ejecución '
             'de pytest como criterio de rendimiento funcional']
        ]
        
        self._add_table_styled(len(exec_data), 2, exec_data,
                               col_widths=[Cm(5), Cm(11)])
        
        # Results observed
        self._add_heading_styled('4.2.2 Resultados Observados', 3)
        
        results_data = [
            ['Nivel / Categoría', 'Comando Ejecutado', 'Resultado', 'Duración', 'Observaciones'],
            ['Unidad', 'python -m pytest tests\\unit', '427 aprobadas, 0 fallidas, 0 omitidas', 'Incluida', 
             '20 suites de módulo con 376 casos, más 51 casos transversales; los accesos SQL se simulan y no se prueba persistencia real.'],
            ['Integración', 'python -m pytest tests\\integration', '22 aprobadas, 0 fallidas, 0 omitidas', 'Incluida',
             '20 contratos de ruta y 2 flujos Contratación/Bitácora; no valida transacciones reales de MySQL.'],
            ['Backend/API (Pytest)', 'python -m pytest tests\\api', '33 aprobadas, 0 fallidas, 0 omitidas', 'Incluida',
             'Cliente Flask y dobles de modelos; 20 suites por módulo y 13 casos parametrizados de reportes.'],
            ['Backend/API (Postman)', 'Colección postman/collections/INVISAP - Pruebas de Contrato HTTP', 'No ejecutada en esta auditoría', '—',
             '20 contratos GET, login y comprobación negativa sin sesión. Para la ejecución positiva faltan cookie de sesión e IDs válidos.'],
            ['Humo', 'python -m pytest tests\\smoke', '21 aprobadas, 0 fallidas, 0 omitidas', 'Incluida',
             '20 módulos y un caso de acceso; no es un recorrido integral.'],
            ['Interfaz', 'python -m pytest tests\\ui', '0 aprobadas, 0 fallidas, 1 omitida', 'Incluida',
             'Omitida por falta de INVISAP_TEST_URL; esta corrida no abrió navegador.'],
            ['Rendimiento', 'python tests\\performance\\run_performance.py --all --profile quick (2026-10-29)', 
             'Última serie: 2 módulos con HTTP 200 y 18 para revisar por HTTP 401/302', '2 series de 5 s por módulo',
             'La bitácora no permite confirmar una sesión autorizada; las latencias de respuestas rechazadas no constituyen línea base de rendimiento aprobada.'],
            ['Aceptación', 'Recorrido de usuario según requisito aprobado', 'Pendiente', '—',
             'Sin criterios validados ni aprobación/evidencia de usuario.']
        ]
        
        self._add_table_styled(len(results_data), 5, results_data,
                               col_widths=[Cm(3), Cm(4), Cm(3), Cm(2), Cm(4)])
        
        self.doc.add_paragraph(
            'La ejecución completa recogió 503 aprobadas, 0 fallidas y 1 omitida (504 casos recopilados), '
            'con 14 advertencias. Las advertencias son DeprecationWarning de openpyxl por usar '
            'datetime.datetime.utcnow() al generar Excel; no son fallos de aserción. La omisión de '
            'interfaz se debe a la falta de URL. Rendimiento y aceptación se registran con sus propios '
            'resultados y límites, separados de esta corrida.'
        )
        
        # Results by module
        self._add_heading_styled('4.2.3 Resultado Exacto por Módulo', 3)
        
        module_results = [
            ['Módulo', 'Unidad', 'Contrato Integración', 'API', 'Humo'],
            ['Solicitudes', '43/43', '1/1', '1/1', '1/1'],
            ['Gravedad de Obra', '11/11', '1/1', '1/1', '1/1'],
            ['Prioridad', '31/31', '1/1', '1/1', '1/1'],
            ['Proyectos', '22/22', '1/1', '1/1', '1/1'],
            ['Maquinaria', '20/20', '1/1', '1/1', '1/1'],
            ['Contratación', '9/9', '1/1', '1/1', '1/1'],
            ['Empresa', '9/9', '1/1', '1/1', '1/1'],
            ['Obras', '14/14', '1/1', '1/1', '1/1'],
            ['Empleados', '14/14', '1/1', '1/1', '1/1'],
            ['Inspecciones', '18/18', '1/1', '1/1', '1/1'],
            ['Evidencias', '13/13', '1/1', '1/1', '1/1'],
            ['Informe de Avance', '21/21', '1/1', '1/1', '1/1'],
            ['Publicaciones', '14/14', '1/1', '1/1', '1/1'],
            ['Reportes PDF', '11/11', '1/1', '7/7', '1/1'],
            ['Reportes Excel', '16/16', '1/1', '8/8', '1/1'],
            ['Reportes Estadísticos', '19/19', '1/1', '1/1', '1/1'],
            ['Usuarios', '19/19', '1/1', '1/1', '1/1'],
            ['Permisos por Rol', '35/35', '1/1', '1/1', '1/1'],
            ['Administración de Respaldos', '26/26', '1/1', '1/1', '1/1'],
            ['Bitácora', '11/11', '1/1', '1/1', '1/1'],
        ]
        
        self._add_table_styled(len(module_results), 5, module_results,
                               col_widths=[Cm(4), Cm(2.5), Cm(3), Cm(2.5), Cm(2.5)])
        
        self.doc.add_paragraph(
            'Las suites unitarias de los veinte módulos suman 376 casos. Los 51 casos '
            'transversales corresponden a BaseModel (5), formatos/logos de reportes (2), '
            'validación de informes (3), controles de reCAPTCHA (2) y listas permitidas de '
            'filtros SQL (39). Los 2 casos extra de integración cubren auditoría y '
            'recuperación ante colisión de ID. La suite de humo suma un caso para acceso de INVISAP.'
        )
        
        # Performance results
        self._add_heading_styled('4.2.4 Resultados Exactos de Rendimiento por Módulo', 3)
        
        self.doc.add_paragraph(
            'La bitácora tests/performance/results/bitacora_rendimiento.csv conserva 41 '
            'registros: dos series quick de los 20 módulos y una serie baseline de '
            'Solicitudes. La tabla resume la segunda serie completa, ejecutada el '
            '2026-10-29 entre 22:44:23 y 22:46:14 (UTC−04:00), con un usuario durante 5 s '
            'por módulo. "Fallos" son respuestas distintas de HTTP 200 detectadas por el '
            'escenario; el promedio y P95 son tiempos de respuesta observados aun cuando '
            'la solicitud no fue autorizada.'
        )
        
        perf_data = [
            ['Módulo', 'Solicitudes / Fallos', 'Fallos', 'Promedio (ms)', 'P95 (ms)', 'Evaluación'],
            ['Solicitudes', '3 / 3', '100 %', '11.44', '14', 'Revisar: HTTP 401'],
            ['Gravedad de Obra', '3 / 3', '100 %', '8.72', '10', 'Revisar: HTTP 401'],
            ['Prioridad', '4 / 4', '100 %', '8.40', '9', 'Revisar: HTTP 401'],
            ['Proyectos', '3 / 3', '100 %', '8.76', '12', 'Revisar: HTTP 401'],
            ['Maquinaria', '3 / 3', '100 %', '8.34', '9', 'Revisar: HTTP 401'],
            ['Contratación', '3 / 3', '100 %', '11.05', '14', 'Revisar: HTTP 401'],
            ['Empresa', '3 / 3', '100 %', '9.36', '11', 'Revisar: HTTP 401'],
            ['Obras', '3 / 3', '100 %', '9.14', '12', 'Revisar: HTTP 401'],
            ['Empleados', '3 / 3', '100 %', '8.58', '12', 'Revisar: HTTP 401'],
            ['Inspecciones', '3 / 3', '100 %', '7.46', '10', 'Revisar: HTTP 401'],
            ['Evidencias', '3 / 0', '0 %', '28.62', '37', 'HTTP 200; respuesta funcional no validada por Locust'],
            ['Informe de Avance', '3 / 3', '100 %', '11.21', '16', 'Revisar: HTTP 401'],
            ['Publicaciones', '3 / 0', '0 %', '25.10', '33', 'HTTP 200; respuesta funcional no validada por Locust'],
            ['Reportes PDF', '3 / 3', '100 %', '10.44', '11', 'Revisar: HTTP 302'],
            ['Reportes Excel', '3 / 3', '100 %', '9.67', '11', 'Revisar: HTTP 302'],
            ['Reportes Estadísticos', '3 / 3', '100 %', '9.61', '13', 'Revisar: HTTP 401'],
            ['Usuarios', '4 / 4', '100 %', '10.16', '12', 'Revisar: HTTP 401'],
            ['Permisos por Rol', '4 / 4', '100 %', '10.05', '14', 'Revisar: HTTP 401'],
            ['Administración de Respaldos', '3 / 3', '100 %', '9.74', '12', 'Revisar: HTTP 401'],
            ['Bitácora', '3 / 3', '100 %', '11.27', '17', 'Revisar: HTTP 401'],
        ]
        
        self._add_table_styled(len(perf_data), 6, perf_data,
                               col_widths=[Cm(3.5), Cm(2.5), Cm(2), Cm(2.5), Cm(2), Cm(3.5)])
        
        self.doc.add_paragraph(
            'En ambas series quick los mismos 18 escenarios protegidos no recibieron una '
            'respuesta HTTP 200 autenticada: 16 devolvieron HTTP 401 y los formularios PDF/Excel '
            'redirigieron con HTTP 302. Evidencias y Publicaciones devolvieron HTTP 200. No '
            'se puede comprobar desde la bitácora si faltó la cookie de sesión, si expiró o '
            'si no autorizaba esos endpoints, porque el valor y el rol no se almacenan. Por '
            'ello, el resultado no permite concluir que los 18 módulos tengan defectos '
            'funcionales o de velocidad. Debe repetirse con una cuenta de pruebas y los '
            'identificadores requeridos, sin registrar la cookie.'
        )
        
        self.doc.add_paragraph(
            'El 2026-10-29 también se ejecutó baseline solo para Solicitudes: 5 usuarios '
            'durante 30 s, 91 solicitudes, 91 fallos (100 %), promedio 6.15 ms y P95 de '
            '10 ms, todos por HTTP 401. No es una línea base válida de carga autenticada.'
        )
        
        self.doc.add_paragraph(
            'Como evidencia histórica independiente, el informe completo del proyecto '
            'registra Locust 2.46.7 el 2026-10-23 sobre GET / y /login con usuarios '
            'anónimos: 20 usuarios, 195 s totales (185 s estables), 0 fallos; el resumen de '
            'terminal indicó 1,880 solicitudes, promedio 8 ms y máximo 31 ms, mientras que '
            'el CSV indicó 1,875, promedio 8.25 ms y máximo 31.9 ms. La diferencia de cinco '
            'solicitudes se conserva como observación. Esa ejecución aprobó el umbral '
            'documentado para esas dos rutas solamente; no representa los 20 módulos.'
        )
        
        # Representative cases
        self._add_heading_styled('4.2.5 Casos Representativos de Unidad e Integración', 3)
        
        cases_data = [
            ['ID Seguimiento', 'Nivel', 'Requerimiento/Función', 'Entradas y Procedimiento', 
             'Resultado Esperado / Observado', 'Errores y Corrección', 'Evaluación'],
            ['UT-GRA-001', 'Unidad', 'Clasificación del nivel de gravedad a partir de criticidad.',
             'Valores parametrizados 0, 50, 51 y 100; invocar _calcular_nivel_gravedad.',
             'Límites bajos y altos devuelven respectivamente "Bajo" y "Alto"; los cuatro casos pasaron.',
             'Ningún defecto detectado en esta ejecución; no se necesitó corrección.',
             'Aprobada automáticamente; pendiente de conformidad funcional.'],
            ['UT-GRA-002', 'Unidad', 'Rechazo de criticidad fuera del rango admitido.',
             'Enviar 101 a set_criticidad; verificar ValueError.',
             'Se rechaza el valor inválido; caso aprobado.',
             'Ningún defecto detectado; sin corrección requerida.',
             'Aprobada automáticamente.'],
            ['IT-ROUTE-01', 'Integración', 'Contrato de la ruta API de Gravedad de Obra.',
             'Inspeccionar /api/gravedad/listar, endpoint, método HTTP y construcción de URL Flask.',
             'Ruta y endpoint registrados y URL generada según el contrato; caso aprobado.',
             'Sin error de contrato observado; sin corrección requerida.',
             'Aprobada dentro del alcance del contrato de rutas; no cubre BD.'],
            ['IT-CON-01', 'Integración', 'Registro de contratación y auditoría de la acción.',
             'Enviar POST de contratación usando modelo y servicio de bitácora simulados; verificar llamada de auditoría.',
             'Respuesta esperada y registro CREAR en Bitácora; caso aprobado.',
             'Ningún defecto detectado en el flujo simulado; sin corrección requerida.',
             'Aprobada dentro del alcance de los dobles de prueba.'],
            ['IT-CON-02', 'Integración', 'Recuperación ante colisión de identificador al registrar contratación.',
             'Simular colisión de clave primaria y comprobar el reintento con nuevo ID.',
             'El primer error simulado aparece en consola; el reintento termina con registro exitoso.',
             'La colisión es una falla inyectada deliberadamente para probar recuperación, no un defecto pendiente.',
             'Aprobada; persistencia real pendiente de probar con BD de pruebas.']
        ]
        
        self._add_table_styled(len(cases_data), 7, cases_data,
                               col_widths=[Cm(2), Cm(1.5), Cm(2.5), Cm(3), Cm(3), Cm(3), Cm(2.5)])
        
        # Experience
        self._add_heading_styled('4.2.6 Experiencia de Ejecución, Errores y Acciones', 3)
        
        self.doc.add_paragraph(
            'Durante la corrida del 2026-11-12 no se detectaron fallos de aserción en '
            'Unidad, Integración, API ni Humo. La ampliación de Usuarios detectó que '
            'existe_y_activo referenciaba self dentro de un método estático; se convirtió '
            'en método de instancia y se añadió una prueba de resultados positivo/negativo '
            'y cierre de recursos. Los fixtures y dobles permiten reproducir validaciones, '
            'contratos HTTP y colaboración entre componentes, pero no certifican '
            'persistencia real. Para completar esa evidencia se requiere una fase de '
            'integración con MySQL de pruebas y rollback/limpieza de datos. Las '
            'pruebas de reCAPTCHA se aislaron del bypass configurado localmente; la '
            'ejecución comprueba los casos de secreto ausente y error de red, no una '
            'verificación real contra Google.'
        )
        
        self.doc.add_paragraph(
            'La corrección de existe_y_activo quedó cubierta por la prueba unitaria de '
            'Usuarios; debe confirmarse también en un entorno con base de datos. Las '
            'correcciones siguientes constan en ejecuciones anteriores del informe '
            'completo y no deben confundirse con hallazgos de esta corrida: se ajustó la '
            'verificación estricta de reCAPTCHA, se corrigió el aviso falso de sesión al '
            'abrir /login, se implementó el reintento tras colisión de ID, se restringieron '
            'permisos de directorios de carga y se parametrizaron consultas y listas '
            'permitidas de identificadores SQL. El mensaje Duplicate entry \'5\' '
            'que aparece en test_registrar_contratacion_reintenta_si_hay_id_duplicado es el error '
            'inyectado por el caso para comprobar que el modelo reintenta con otro ID; el '
            'resultado final fue aprobado (2/2 casos del archivo integrador). Las 14 '
            'advertencias de openpyxl se originan en el uso obsoleto de utcnow() al '
            'generar Excel; no se corrigió en esta ejecución.'
        )
        
        self.doc.add_paragraph(
            'El informe completo registra además un smoke HTTP en vivo con GET / y '
            '/login en HTTP 200, y una prueba Playwright/Chromium anterior para /login '
            '(1 formulario y 2 campos visibles, captura test-results/playwright_login.png). '
            'Son evidencias históricas de esas rutas; la corrida actual omitió UI por falta '
            'de INVISAP_TEST_URL. La aceptación con usuarios continúa pendiente.'
        )
        
        # 4.3 Plan de Instalación
        self._add_heading_styled('4.3 Plan de Instalación', 2)
        
        self._add_heading_styled('4.3.1 Registro Disponible', 3)
        
        self.doc.add_paragraph(
            'El informe integral y la Agenda JAD registran una actividad de instalación '
            'local en la institución el 2026-09-07, a cargo del equipo de proyecto con '
            'participación de la tutora Ing. Jhoanly Hernandez. Ese registro documenta una '
            'actividad realizada, pero no certifica que el servicio siga disponible ni que '
            'se hayan repetido todos los pasos en la versión examinada el 2026-11-12. La '
            'conexión MySQL comprobada en el informe llegó a ejecutar SELECT 1; no se '
            'registraron escrituras, restauración de respaldo ni pruebas CRUD completas.'
        )
        
        self._add_heading_styled('4.3.2 Procedimiento Previsto para una Instalación Reproducible', 3)
        
        install_data = [
            ['Fase', 'Actividad y Evidencia de Salida', 'Responsable'],
            ['Preparación', 'Identificar versión/commit, equipo y sistema operativo; confirmar disponibilidad, autorización, puertos y acceso a MySQL.', 'Administrador de infraestructura y equipo del proyecto.'],
            ['Respaldo', 'Crear respaldo de la base existente y comprobar que pueda restaurarse en un entorno aislado antes de importar o migrar datos.', 'Administrador de base de datos.'],
            ['Dependencias', 'Instalar la versión de Python documentada para el proyecto (Python 3.14), crear el entorno virtual e instalar requirements.txt; instalar por separado tests/performance/requirements.txt para Locust. Instalar Playwright/Chromium solo si se ejecutará UI.', 'Soporte técnico.'],
            ['Configuración', 'Configurar conexión a MySQL, URL, secretos, cuentas y datos ficticios de prueba; importar BD/invilara.sql solo en una base aprobada. No copiar credenciales, cookies ni datos productivos sin autorización.', 'Administrador/DBA.'],
            ['Verificación', 'Iniciar la aplicación y comprobar primero el acceso; después ejecutar unidad, integración, API y humo. Ejecutar UI con URL disponible y carga solo en ambiente autorizado, con sesión de prueba e identificadores válidos.', 'Equipo técnico y validadores.'],
            ['Cierre/reversión', 'Registrar versión, fecha, responsables, errores, evidencia y resultado; documentar cómo restaurar el respaldo o revertir la versión.', 'Responsable de instalación.']
        ]
        
        self._add_table_styled(len(install_data), 3, install_data,
                               col_widths=[Cm(2.5), Cm(10), Cm(4.5)])
        
        self.doc.add_paragraph(
            'El informe fuente propone MySQL 9.4; la versión debe confirmarse con el '
            'administrador antes de instalar, pues no se verificó aquí el servidor '
            'institucional. En el checkout actual existen BD/invilara.sql y run.py, '
            'pero no se encontraron Containerfile, Dockerfile ni directorio wheels/. '
            'Por tanto, una instalación offline en contenedor no está demostrada y debe '
            'resolverse o descartarse formalmente antes de presentarla como procedimiento '
            'reproducible.'
        )
        
        # Installation record
        self._add_heading_styled('4.3.3 Registro de Instalación', 3)
        
        install_record = [
            ['Registro de Instalación', 'Dato por Completar'],
            ['Fecha, hora, lugar y versión/commit instalada', 'Pendiente de nueva ejecución institucional'],
            ['Responsable técnico y administrador de base de datos', 'Por designar'],
            ['Resultado de verificación funcional y conexión', 'SELECT 1 está documentado históricamente; CRUD completo pendiente'],
            ['Ubicación de evidencia y respaldo restaurable', 'Por registrar en ambiente autorizado'],
            ['Aprobación y observaciones', 'Firma del responsable y tutor pendientes']
        ]
        
        self._add_table_styled(len(install_record), 2, install_record,
                               col_widths=[Cm(6), Cm(10)])
        
        # 4.4 Plan de Capacitación
        self._add_heading_styled('4.4 Plan de Capacitación', 2)
        
        self._add_heading_styled('4.4.1 Estado y Objetivo', 3)
        
        self.doc.add_paragraph(
            'La Agenda JAD registra una fecha asociada a instalación/capacitación el '
            '2026-09-07, pero los documentos revisados no incluyen asistencia, duración, '
            'temario impartido ni evaluación. Por ello, no se presenta la capacitación '
            'como completada. La siguiente agenda es una propuesta para capacitar a '
            'usuarios finales, administradores y personal de soporte antes de la aceptación.'
        )
        
        self.doc.add_paragraph(
            'El objetivo es que cada participante pueda operar las funciones pertinentes a '
            'su rol, reconocer restricciones de acceso, completar procesos con datos '
            'ficticios y comunicar incidencias con evidencia suficiente para reproducirlas. '
            'La metodología combina explicación breve, demostración guiada, práctica por '
            'rol en un ambiente de prueba, preguntas y ejercicio de cierre.'
        )
        
        self._add_heading_styled('4.4.2 Agenda Propuesta', 3)
        
        agenda_data = [
            ['Bloque', 'Tema', 'Duración', 'Actividad Práctica'],
            ['1', 'Introducción, objetivos y navegación del sistema', '30 min', 'Identificar funciones y canales de soporte.'],
            ['2', 'Acceso, perfiles y permisos', '30 min', 'Ingresar con una cuenta de capacitación y verificar el alcance del rol.'],
            ['3', 'Solicitudes, gravedad y prioridad', '60 min', 'Registrar y consultar una solicitud ficticia y revisar su clasificación.'],
            ['4', 'Proyectos, obras, empresas, contratación, maquinaria y empleados', '60 min', 'Recorrer la gestión relacionada con una obra de práctica.'],
            ['5', 'Inspecciones, evidencias e informes de avance', '75 min', 'Registrar una inspección ficticia, adjuntar evidencia de prueba y consultar avance.'],
            ['6', 'Publicaciones y reportes PDF, Excel y estadísticos', '45 min', 'Consultar resultados y reconocer filtros/formatos disponibles.'],
            ['7', 'Seguridad, bitácora y administración de respaldos', '30 min', 'Revisar permisos, actividad registrada y procedimiento de respaldo.'],
            ['8', 'Administración de usuarios y roles', '30 min', 'Practicar una tarea administrativa con cuenta autorizada.'],
            ['9', 'Práctica integradora y evaluación', '30 min', 'Completar una tarea asignada al rol y registrar dudas/observaciones.'],
            ['Total', 'Dos sesiones propuestas: 3 h y 3 h 30 min', '6 h 30 min', 'No incluye pausas.']
        ]
        
        self._add_table_styled(len(agenda_data), 4, agenda_data,
                               col_widths=[Cm(1.5), Cm(6), Cm(2), Cm(6.5)])
        
        self._add_heading_styled('4.4.3 Recursos, Responsables y Registro', 3)
        
        self.doc.add_paragraph(
            'Se requiere un servidor aislado de capacitación, navegador actualizado, '
            'cuentas separadas por rol, datos completamente ficticios, proyector, guía de '
            'usuario y acceso a los recorridos guiados disponibles. Facilitarían el equipo '
            'del proyecto y el responsable institucional del sistema; los nombres, '
            'participantes, fecha, lugar y disponibilidad deben confirmarse con la '
            'institución. La evaluación propuesta combina observación de la práctica, '
            'verificación del resultado esperado y registro de preguntas; no existe aún un '
            'resultado de capacitación ni una calificación que pueda reportarse.'
        )
        
        self.doc.add_paragraph(
            'Registrar cada sesión en el formato institucional con introducción, '
            'justificación, objetivos, metodología, temas, logística, facilitadores, '
            'asistencia, resultados esperados y observaciones. Adjuntar la evidencia y '
            'separar claramente una asistencia planificada de una capacitación efectivamente '
            'impartida.'
        )
        
        training_record = [
            ['Registro de Capacitación', 'Dato por Completar'],
            ['Fecha, horario, lugar y duración efectiva', 'Pendiente de coordinación'],
            ['Facilitadores, participantes y rol', 'Por confirmar y registrar'],
            ['Asistencia y ejercicios completados', 'Pendiente de ejecución'],
            ['Resultado de evaluación, observaciones y acuerdos', 'Pendiente de ejecución'],
            ['Firmas de participantes y responsable', 'Pendientes']
        ]
        
        self._add_table_styled(len(training_record), 2, training_record,
                               col_widths=[Cm(6), Cm(10)])
        
        # 4.5 Evidencia Automatizada y Trazabilidad
        self._add_heading_styled('4.5 Evidencia Automatizada y Trazabilidad', 2)
        
        self.doc.add_paragraph(
            'Como parte de la modernización del proceso de verificación, se ha implementado '
            'un marco de automatización que captura evidencia visual y documental para cada '
            'caso de prueba, organizándola según la Matriz de Trazabilidad de Pruebas '
            '(Matriz_Trazabilidad_Pruebas_INVISAP.docx).'
        )
        
        self._add_heading_styled('4.5.1 Nomenclatura de Archivos de Evidencia', 3)
        
        self.doc.add_paragraph(
            'Todos los archivos de evidencia (capturas de pantalla, reportes HTML, JSON, CSV) '
            'siguen la convención de nomenclatura estructurada:'
        )
        
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run('tipoPrueba_modulo_IDcaso_nombrePrueba_resultado_timestamp.extensión')
        run.bold = True
        run.font.size = Pt(11)
        run.font.name = 'Consolas'
        run.font.color.rgb = RGBColor(0x2C, 0x3E, 0x50)
        
        self.doc.add_paragraph()
        
        examples = [
            ('Captura Playwright (éxito)', 'ui_Login_CP-UI-RNF01_test_formulario_acceso_PASSED_20261120_103000.png'),
            ('Captura Playwright (fallo)', 'ui_Login_CP-UI-RNF01_test_formulario_acceso_FAILED_20261120_103005.png'),
            ('Reporte Locust HTML', 'performance_Solicitudes_CP-LOC-RF01_locust_solicitudes_PASSED_20261120_103010.html'),
            ('Evidencia Postman JSON', 'api_Solicitudes_CP-POST-RF01_postman_solicitudes_PASSED_20261120_103015.json'),
            ('Reporte pytest HTML', 'unit_Solicitudes_CP-UNI-RF01-01_test_crear_solicitud_PASSED_20261120_103020.html'),
            ('Resumen de evidencia', 'evidence_summary_20261120_103025.json'),
        ]
        
        example_data = [['Tipo de Evidencia', 'Ejemplo de Nombre de Archivo']]
        for desc, example in examples:
            example_data.append([desc, example])
        
        self._add_table_styled(len(example_data), 2, example_data,
                               col_widths=[Cm(4), Cm(12)])
        
        self._add_heading_styled('4.5.2 Estructura de Directorios de Evidencia', 3)
        
        dir_structure = """tests/evidence/
├── unit/                 # Capturas y reportes de pruebas unitarias
├── integration/          # Evidencia de pruebas de integración
├── api/                  # Evidencia de pruebas API (pytest + Postman)
├── smoke/                # Evidencia de pruebas de humo
├── ui/                   # Capturas de pantalla Playwright/Selenium
├── performance/          # Reportes Locust (HTML, CSV, JSON)
├── acceptance/           # Evidencia de pruebas de aceptación
├── organized/            # Evidencia organizada por matriz de trazabilidad
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── smoke/
│   ├── ui/
│   └── performance/
├── evidence_summary.json # Resumen consolidado de todas las capturas
└── traceability_coverage_report_*.json  # Cobertura vs matriz de trazabilidad"""
        
        p = self.doc.add_paragraph()
        run = p.add_run(dir_structure)
        run.font.name = 'Consolas'
        run.font.size = Pt(9)
        
        self._add_heading_styled('4.5.3 Integración Continua (CI/CD)', 3)
        
        self.doc.add_paragraph(
            'El pipeline de GitHub Actions (.github/workflows/test-with-evidence.yml) '
            'ejecuta automáticamente todas las suites de prueba en cada push y pull request, '
            'captura la evidencia, la organiza según la matriz de trazabilidad y publica '
            'los artifacts para su descarga. Los artifacts se retienen por 30 días '
            '(evidencia por tipo de prueba) y 90 días (evidencia organizada e informe consolidado).'
        )
        
        self.doc.add_paragraph(
            'El workflow incluye jobs para: configuración, pruebas unitarias, integración, '
            'API, humo, interfaz (Playwright), rendimiento (Locust), organización de '
            'evidencia por trazabilidad, generación de informe consolidado y publicación '
            'de resumen en Pull Requests.'
        )
    
    def _generate_chapter_v(self):
        """Generate Chapter V content with hybrid evidence embedding."""
        self._add_heading_styled('CAPÍTULO V. Recomendaciones y Evolución Previsible del Sistema', 1)
        
        self.doc.add_paragraph(
            'A partir de los hallazgos documentados en el Capítulo IV, se presentan las '
            'siguientes recomendaciones para la evolución y madurez del sistema INVISAP:'
        )
        
        recommendations = [
            ('1. IDs estables y trazabilidad completa',
             'Vincular cada requisito funcional aprobado con un ID estable y con al menos '
             'un caso de prueba trazable; no asignar IDs definitivos hasta validar el '
             'documento de requisitos con el tutor/comunidad. Completar la matriz de '
             'trazabilidad para RF-17, RF-18, RF-19, RF-20 y RNF-04, RNF-09, RNF-11, '
             'RNF-13, RNF-14, RNF-15, RNF-18 que actualmente están pendientes.'),
            
            ('2. Integración real con MySQL',
             'Complementar los contratos de rutas con integración real de controladores, '
             'modelos y MySQL en una base aislada, con transacciones y limpieza de datos '
             '(rollback). Ejecutar las 22 pruebas de integración contra una base de datos '
             'real para certificar persistencia, restricciones de integridad referencial y '
             'rendimiento de consultas complejas.'),
            
            ('3. Criterios de aceptación firmados',
             'Definir los criterios de aceptación con usuarios y registrar firma, fecha y '
             'evidencia antes de declarar entregado el sistema. Completar el formato de '
             'Pruebas de Aceptación (Formato Pruebas de Aceptación - INVILARA) con los '
             '14 casos de prueba (CP01-01 a CP14-01) y obtener el acta final firmada '
             'por los 14 participantes (7 gerentes + 7 técnicos).'),
            
            ('4. Expansión de pruebas de interfaz (Playwright)',
             'Ejecutar Playwright en un despliegue local/institucional estable y ampliar '
             'progresivamente la cobertura de interfaz más allá del formulario de acceso. '
             'Crear casos para: login con OTP, navegación por menús, formularios CRUD de '
             'cada módulo, validaciones visuales, responsive design y flujos completos '
             'de usuario. Configurar INVISAP_TEST_URL en el entorno de CI/CD.'),
            
            ('5. Pruebas de rendimiento con criterios acordados',
             'Ejecutar Locust en un ambiente controlado y determinar umbrales de '
             'rendimiento con la comunidad; repetir primero los 18 escenarios no '
             'autorizados con cookie temporal e identificadores de prueba, y conservar '
             'CSV y bitácora por versión. Establecer línea base para el criterio RNF-10: '
             '20 usuarios concurrentes, tiempo de respuesta promedio < 2 segundos, '
             '0% errores HTTP en endpoints autenticados.'),
            
            ('6. Mantenimiento de dependencias y warnings',
             'Revisar periódicamente las 14 advertencias reportadas por pytest '
             '(DeprecationWarning de openpyxl por datetime.utcnow()) y actualizar '
             'dependencias de forma planificada, validando compatibilidad. Migrar a '
             'datetime.datetime.now(datetime.UTC) en Python 3.11+ o usar '
             'datetime.datetime.now(timezone.utc).'),
            
            ('7. Repetición de humo post-instalación y regresión',
             'Repetir las pruebas de humo después de instalar una versión y las de unidad, '
             'integración y sistema después de cada cambio significativo. Automatizar '
             'este proceso en el pipeline de CI/CD para que se ejecute en cada merge a main.'),
            
            ('8. Formalización de aceptación y capacitación',
             'Formalizar la aceptación con criterios y responsables acordados, y realizar '
             'la capacitación propuesta (6 h 30 min en dos sesiones) con asistencia y '
             'evaluación registradas en el formato institucional (Formato del Plan de '
             'Capacitación - INVILARA). Completar el manual de usuario (actualmente EN '
             'PROCESO con entrega estimada 30/11/2026) y los tours interactivos (RF-20).')
        ]
        
        for i, (title, desc) in enumerate(recommendations, 1):
            p = self.doc.add_paragraph()
            run = p.add_run(f'Recomendación {i}: {title}')
            run.bold = True
            run.font.size = Pt(11)
            self.doc.add_paragraph(desc)
        
        self.doc.add_paragraph()
        
        # Evolution perspectives
        self._add_heading_styled('Evolución Previsible del Sistema', 2)
        
        evolutions = [
            ('Corto plazo (0-3 meses)', [
                'Completar integración real con MySQL en ambiente de pruebas',
                'Ejecutar suite de aceptación con usuarios y obtener firmas',
                'Expandir cobertura Playwright a 5 módulos críticos',
                'Resolver warnings de openpyxl y actualizar Python a 3.12+',
                'Completar manual de usuario y tours interactivos'
            ]),
            ('Mediano plazo (3-6 meses)', [
                'Implementar pruebas de contrato con Pact o similar para API',
                'Añadir pruebas de seguridad (OWASP ZAP, Bandit en CI)',
                'Configurar pruebas de carga distribuida con Locust en Kubernetes',
                'Implementar métricas de cobertura de código (pytest-cov)',
                'Automatizar despliegue en staging con Docker Compose'
            ]),
            ('Largo plazo (6-12 meses)', [
                'Migración a arquitectura de microservicios si la carga lo requiere',
                'Implementar observabilidad completa (logs, métricas, trazas)',
                'Pruebas de caos (Chaos Engineering) para resiliencia',
                'Portal de desarrolladores con documentación de API auto-generada',
                'Cumplimiento de normas de accesibilidad (WCAG 2.1 AA)'
            ])
        ]
        
        for period, items in evolutions:
            p = self.doc.add_paragraph()
            run = p.add_run(period)
            run.bold = True
            run.font.size = Pt(11)
            
            for item in items:
                self.doc.add_paragraph(item, style='List Bullet')
        
        # ============================================================
        # EVIDENCIA VISUAL HÍBRIDA - CAPÍTULO V
        # ============================================================
        self.doc.add_page_break()
        self._add_heading_styled('Evidencia Visual de Verificación Automatizada', 1)
        
        self.doc.add_paragraph(
            'Esta sección presenta la evidencia visual generada durante la ejecución '
            'automatizada de pruebas, organizada según la Matriz de Trazabilidad de Pruebas '
            '(Matriz_Trazabilidad_Pruebas_INVISAP.docx). Se incluyen capturas de pantalla '
            'de pruebas de interfaz aprobadas, reportes de rendimiento convertidos a imagen '
            'y un resumen visual de cobertura de trazabilidad.'
        )
        
        # 1. UI Screenshots (PASSED) with Traceability IDs
        self._add_heading_styled('Capturas de Pantalla - Pruebas de Interfaz (APROBADAS)', 2)
        
        ui_screenshots = self._find_ui_screenshots()
        if ui_screenshots:
            self.doc.add_paragraph(
                f'Se encontraron {len(ui_screenshots)} capturas de pruebas de interfaz aprobadas. '
                'Cada captura está vinculada a su ID de caso de prueba en la matriz de trazabilidad:'
            )
            self._add_evidence_table_with_images(ui_screenshots)
            
            # Also add full-size images for key screenshots
            self.doc.add_paragraph()
            p = self.doc.add_paragraph()
            run = p.add_run('Capturas a Tamaño Completo:')
            run.bold = True
            run.font.size = Pt(11)
            
            for shot in ui_screenshots[:5]:  # Limit to first 5 to avoid huge doc
                caption = f"UI: {shot['module']} | Caso: {shot['traceability_id']} | Prueba: {shot['test_name']}"
                self._add_image_with_caption(shot["path"], caption, width_cm=15.0)
        else:
            self.doc.add_paragraph(
                '(No se encontraron capturas de interfaz aprobadas. Ejecute las pruebas UI '
                'con INVISAP_TEST_URL configurado para generar evidencia: '
                'python -m pytest tests/ui -v)'
            )
        
        # 2. Performance Reports as Images
        self.doc.add_page_break()
        self._add_heading_styled('Reportes de Rendimiento (Locust) - Convertidos a Imagen', 2)
        
        perf_reports = self._find_performance_reports()
        if perf_reports and PLAYWRIGHT_AVAILABLE:
            self.doc.add_paragraph(
                f'Se convirtieron {len(perf_reports)} reportes HTML de Locust a imágenes PNG '
                'para su inclusión en el documento:'
            )
            
            for report in perf_reports[:3]:  # Limit to avoid huge doc
                img_path = self.evidence_dir / f"{report['name']}.png"
                if self._html_to_image(report["path"], img_path):
                    caption = f"Rendimiento: {report['name']} | {report['type']}"
                    self._add_image_with_caption(img_path, caption, width_cm=16.0)
                else:
                    self.doc.add_paragraph(f"[No se pudo convertir: {report['name']}]")
        elif perf_reports:
            self.doc.add_paragraph(
                'Reportes HTML de Locust encontrados pero Playwright no está disponible '
                'para conversión a imagen. Instale con: pip install playwright && playwright install chromium'
            )
            for report in perf_reports:
                self.doc.add_paragraph(f"• {report['name']} ({report['path']})")
        else:
            self.doc.add_paragraph(
                '(No se encontraron reportes de rendimiento. Ejecute: '
                'python tests/performance/run_performance.py --all --profile quick)'
            )
        
        # 3. Traceability Coverage Visual Summary
        self.doc.add_page_break()
        self._add_heading_styled('Resumen Visual de Cobertura de Trazabilidad', 2)
        
        self.doc.add_paragraph(
            'El siguiente gráfico muestra la cobertura de evidencia por tipo de prueba '
            'respecto a los casos definidos en la Matriz de Trazabilidad de Pruebas:'
        )
        
        chart_path = self._generate_traceability_coverage_chart()
        if chart_path:
            self._add_image_with_caption(
                chart_path, 
                "Cobertura de Trazabilidad: casos con evidencia vs total por tipo de prueba",
                width_cm=16.0
            )
            
            # Also add detailed table
            self.doc.add_paragraph()
            self._add_traceability_coverage_detail_table()
        else:
            self.doc.add_paragraph(
                '(No se pudo generar el gráfico. Requiere Pillow: pip install pillow. '
                'También verifique que exista organized/traceability_coverage_report_*.json)'
            )
        
        # Evidence summary (existing)
        self.doc.add_page_break()
        self._add_heading_styled('Resumen Consolidado de Evidencia Generada', 2)
        
        self.doc.add_paragraph(
            'Durante la ejecución automatizada documentada en este informe, se ha generado '
            'evidencia estructurada y organizada según la Matriz de Trazabilidad de Pruebas. '
            'A continuación se presenta un resumen consolidado:'
        )
        
        # Load actual evidence summary if available
        summary_path = self.evidence_dir / "evidence_summary.json"
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                evidence_summary = json.load(f)
            
            summary_data = [['Tipo de Prueba', 'Capturas/Reportes Generados']]
            for test_type, count in evidence_summary.get("screenshots_captured", {}).items():
                if isinstance(count, int) and count > 0:
                    summary_data.append([test_type.capitalize(), str(count)])
            
            self._add_table_styled(len(summary_data), 2, summary_data,
                                   col_widths=[Cm(5), Cm(5)])
        else:
            self.doc.add_paragraph(
                '(La evidencia se genera durante la ejecución del pipeline de CI/CD. '
                'Ejecute el workflow test-with-evidence.yml para generar capturas reales.)'
            )
        
        # Traceability coverage
        coverage_path = self.evidence_dir / "organized" / "traceability_coverage_report_*.json"
        coverage_files = list(self.evidence_dir.glob("organized/traceability_coverage_report_*.json"))
        if coverage_files:
            latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
            with open(latest, 'r', encoding='utf-8') as f:
                coverage = json.load(f)
            
            total = len(coverage.get("coverage", {}))
            with_ev = sum(1 for v in coverage.get("coverage", {}).values() if v.get("has_evidence"))
            
            self.doc.add_paragraph()
            p = self.doc.add_paragraph()
            run = p.add_run(f'Cobertura de Trazabilidad: {with_ev}/{total} casos con evidencia ({with_ev/total*100:.1f}%)')
            run.bold = True
        
        # References
        self._add_heading_styled('Referencias Metodológicas', 2)
        
        refs = [
            'Célad Álvarez, A. y Ruíz Calle, J. D. (2009). Metodologías de testing de software y su aplicación en el Centro de Informática de la Universidad EAFIT. Universidad EAFIT. Documento suministrado para esta planificación; se adaptan sus niveles de prueba (pp. 44–60) y técnicas de caja negra, caja blanca, interfaz y desempeño (pp. 60–75).',
            'Metodologias Testing de Software.pdf (documento suministrado). Referencia para niveles, clases de equivalencia, análisis de valores límite, tablas de decisión y cobertura estructural; solo se atribuyen a la ejecución las técnicas efectivamente aplicadas y descritas en este capítulo.',
            'Matriz de Trazabilidad de Pruebas.docx (formato suministrado). Se conserva su estructura de seis columnas en la matriz de INVISAP; los IDs de caso son provisionales y requieren validación contra requisitos aprobados.',
            'Manual Informe de Proyecto III, documento suministrado. Estructura usada: p. 3: Plan de Pruebas, Bitácora, Plan de Instalación, Plan de Capacitación y recomendaciones/evolución.',
            'Informe del Sistema INVILARA - Proyecto III (PDF suministrado), pp. 143–157. Fuente de evidencia histórica para la instalación, las pruebas HTTP/UI, Locust sobre / y /login, y las actividades de capacitación registradas.',
            'Indiring. (s. f.). Planificación Prueba del Software: Unidad, Integración y Sistema y Especificación de Pruebas de los Requerimientos Funcionales. Calaméo, perfil compartido por el solicitante: https://www.calameo.com/accounts/6325204. Se adaptan sus campos de objetivos, actividades, responsables, entradas, resultados, errores, correcciones y evaluación.',
            'Formato del Plan de Capacitación (1).docx (documento suministrado). Se utiliza como guía para organizar objetivos, metodología, temas, logística, facilitadores y evaluación; no se reporta una sesión impartida sin asistencia/evidencia.',
            'Gómez Rodríguez, N. (s. f.). PFC suministrado, sección 2.2.1, "Pruebas de Componentes", p. 18. Referencia conceptual; no se toman sus resultados como evidencia de INVISAP.',
            'Las hojas de cálculo editables de tests/documentation adaptan los formatos de planificación y especificación con trazabilidad y evidencia automatizada.',
            'Pytest Documentation; Locust Documentation; Playwright Documentation.'
        ]
        
        for i, ref in enumerate(refs, 1):
            self.doc.add_paragraph(f'{i}. {ref}')
        
        self.doc.add_paragraph()
        self.doc.add_paragraph(
            'Los PDF de proyectos ajenos se usaron únicamente como referencia conceptual y '
            'no como evidencia de resultados de INVISAP. El archivo de pruebas de caja '
            'blanca/caja negra de José Manuel Sánchez Peña está cifrado y no se utilizó '
            'para fundamentar este capítulo.'
        )
    
    def _add_traceability_coverage_detail_table(self):
        """Add detailed traceability coverage table by module."""
        coverage_files = list(self.evidence_dir.glob("organized/traceability_coverage_report_*.json"))
        if not coverage_files:
            return
        
        latest = max(coverage_files, key=lambda f: f.stat().st_mtime)
        with open(latest, 'r', encoding='utf-8') as f:
            coverage = json.load(f)
        
        # Group by module
        by_module = {}
        for case_key, case_info in coverage.get("coverage", {}).items():
            module = case_info.get("module", "Unknown")
            if module not in by_module:
                by_module[module] = {"total": 0, "with_evidence": 0}
            by_module[module]["total"] += 1
            if case_info.get("has_evidence"):
                by_module[module]["with_evidence"] += 1
        
        # Create table
        table_data = [['Módulo', 'Total Casos', 'Con Evidencia', 'Sin Evidencia', 'Cobertura %']]
        for module, counts in sorted(by_module.items()):
            total = counts["total"]
            with_ev = counts["with_evidence"]
            without = total - with_ev
            pct = f"{with_ev/total*100:.1f}%" if total > 0 else "0%"
            table_data.append([module, str(total), str(with_ev), str(without), pct])
        
        # Totals row
        grand_total = sum(c["total"] for c in by_module.values())
        grand_with = sum(c["with_evidence"] for c in by_module.values())
        table_data.append(['TOTAL', str(grand_total), str(grand_with), str(grand_total - grand_with), f"{grand_with/grand_total*100:.1f}%"])
        
        self._add_table_styled(len(table_data), 5, table_data,
                               col_widths=[Cm(5), Cm(2.5), Cm(2.5), Cm(2.5), Cm(2.5)])


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate consolidated INVISAP report Chapter IV & V")
    parser.add_argument("--evidence-dir", default="tests/evidence", help="Evidence directory")
    parser.add_argument("--matrix", help="Path to traceability matrix DOCX")
    parser.add_argument("--output", default="tests/evidence/Informe_Consolidado_Capitulo_IV_V.docx", help="Output Word document")
    
    args = parser.parse_args()
    
    generator = ConsolidatedReportGenerator(args.evidence_dir, args.matrix)
    generator.generate(args.output)


if __name__ == "__main__":
    main()