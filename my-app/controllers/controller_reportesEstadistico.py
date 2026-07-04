from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from io import BytesIO
from datetime import datetime

from models.model_ReporteEstadistico import ReporteEstadisticoModel
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import LineChart
from reportlab.graphics import renderPDF
from reportlab.lib import colors

reporte_estadistico_bp = Blueprint('reporte_estadistico_bp', __name__, template_folder='../vista')
modelo_estadistico = ReporteEstadisticoModel()

W, H = letter
MARGIN = 72


@reporte_estadistico_bp.route('/reporte-estadistico', methods=['GET', 'POST'])
def generarReporteEstadistico():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    filtro = None
    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()

    stats = modelo_estadistico.obtener_estadisticas_solicitudes(filtro)

    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    page_num = 1

    def encabezado():
        c.setFont('Helvetica-Bold', 16)
        c.drawCentredString(W / 2, H - 50, 'GOBERNACIÓN DEL ESTADO LARA - INVILARA')
        c.setFont('Helvetica-Bold', 12)
        c.drawCentredString(W / 2, H - 70, 'REPORTE ESTADÍSTICO')
        c.setFont('Helvetica-Oblique', 10)
        c.drawRightString(W - MARGIN, H - 90, f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}')

    def pie():
        c.setFont('Helvetica-Oblique', 8)
        c.drawCentredString(W / 2, 30, f'Página {page_num}')

    y_base = H - 120

    encabezado()
    c.setFont('Helvetica-Bold', 14)
    c.drawString(MARGIN, y_base, 'ANÁLISIS ESTADÍSTICO DE SOLICITUDES')
    y_base -= 30

    if stats.get('por_tipo'):
        c.setFont('Helvetica-Bold', 12)
        c.drawString(MARGIN, y_base, 'Distribución por Tipo de Solicitud')
        y_base -= 20
        d = Drawing(460, 220)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 130
        bc.width = 360
        bc.data = [[dato['valor'] for dato in stats['por_tipo']]]
        bc.categoryAxis.categoryNames = [str(dato['label']) for dato in stats['por_tipo']]
        bc.bars[0].fillColor = colors.HexColor('#0d6efd')
        d.add(bc)
        renderPDF.draw(d, c, MARGIN, y_base - 150)
        y_base -= 180

    if y_base < 200:
        pie()
        c.showPage()
        page_num += 1
        encabezado()
        y_base = H - 120
        c.setFont('Helvetica-Bold', 14)
        c.drawString(MARGIN, y_base, 'ANÁLISIS ESTADÍSTICO DE SOLICITUDES')
        y_base -= 30

    if stats.get('por_estatus'):
        c.setFont('Helvetica-Bold', 12)
        c.drawString(MARGIN, y_base, 'Distribución por Estatus de Solicitud')
        y_base -= 20
        d = Drawing(460, 220)
        bc = VerticalBarChart()
        bc.x = 50
        bc.y = 50
        bc.height = 130
        bc.width = 360
        bc.data = [[dato['valor'] for dato in stats['por_estatus']]]
        bc.categoryAxis.categoryNames = [str(dato['label']) for dato in stats['por_estatus']]
        bc.bars[0].fillColor = colors.HexColor('#198754')
        d.add(bc)
        renderPDF.draw(d, c, MARGIN, y_base - 150)
        y_base -= 180

    if y_base < 200:
        pie()
        c.showPage()
        page_num += 1
        encabezado()
        y_base = H - 120
        c.setFont('Helvetica-Bold', 14)
        c.drawString(MARGIN, y_base, 'ANÁLISIS ESTADÍSTICO DE SOLICITUDES')
        y_base -= 30

    if stats.get('por_fecha'):
        c.setFont('Helvetica-Bold', 12)
        c.drawString(MARGIN, y_base, 'Tendencia de Solicitudes por Fecha')
        y_base -= 20
        d = Drawing(460, 220)
        lc = LineChart()
        lc.x = 50
        lc.y = 50
        lc.height = 130
        lc.width = 360
        lc.data = [[dato['valor'] for dato in stats['por_fecha']]]
        labels = []
        for dato in stats['por_fecha']:
            lbl = dato['label']
            if hasattr(lbl, 'strftime'):
                labels.append(lbl.strftime('%d/%m/%Y'))
            else:
                labels.append(str(lbl))
        lc.categoryAxis.categoryNames = labels
        lc.lines[0].strokeColor = colors.HexColor('#dc3545')
        lc.lines[0].strokeWidth = 2
        d.add(lc)
        renderPDF.draw(d, c, MARGIN, y_base - 150)

    pie()
    c.showPage()
    c.save()
    buffer.seek(0)
    return Response(
        buffer.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Reporte_Estadistico_Solicitudes.pdf"}
    )
