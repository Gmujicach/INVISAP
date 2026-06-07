from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from models.model_reportesPDF import ReportePDFModel

reporte_pdf_bp = Blueprint('reporte_pdf_bp', __name__)
modelo_reporte = ReportePDFModel()

@reporte_pdf_bp.route('/reporte-pdf', methods=['GET', 'POST'])
def generarReportePDF():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    filtro = None
    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda')
    
    data_publicaciones = modelo_reporte.obtener_publicaciones_reporte(filtro)
    
    if request.method == 'POST' and not data_publicaciones:
        flash('No se encontraron resultados para la búsqueda.', 'info')

    return render_template('reportes/reportePDF.html', publicaciones=data_publicaciones)