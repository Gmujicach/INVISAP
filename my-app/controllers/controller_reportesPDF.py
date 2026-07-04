import sys
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from io import BytesIO
from datetime import datetime

from models.model_reportesPDF import ReportePDFModel
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

reporte_pdf_bp = Blueprint('reporte_pdf_bp', __name__, template_folder='../vista')
modelo_reporte = ReportePDFModel()

styles = getSampleStyleSheet()

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.height + doc.topMargin - 30, 'GOBERNACIÓN DEL ESTADO LARA - INVILARA')
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.height + doc.topMargin - 45, 'REPORTE DETALLADO DE GESTIÓN')
    canvas.setFont('Helvetica-Oblique', 10)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.height + doc.topMargin - 60, f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}')
    canvas.setFont('Helvetica-Oblique', 8)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.bottomMargin - 20, f'Página {canvas.getPageNumber()}')
    canvas.restoreState()

@reporte_pdf_bp.route('/reporte-pdf', methods=['GET', 'POST'])
def generarReportePDF():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    filtro = None
    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()
        
        modulos_config = [
            {
                'id': 'solicitudes',
                'label': 'SOLICITUDES',
                'fetch': modelo_reporte.obtener_solicitudes,
                'headers': ['ID', 'Fecha', 'Tipo', 'Estatus', 'Problemática', 'Cédula', 'Prioridad'],
                'fields': ['id_solicitudes', 'fecha', 'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'prioridad']
            },
            {
                'id': 'solicitantes',
                'label': 'SOLICITANTES',
                'fetch': modelo_reporte.obtener_solicitantes,
                'headers': ['Nombre', 'Apellido', 'Cédula'],
                'fields': ['nombre', 'apellido', 'cedula']
            },
            {
                'id': 'empleados',
                'label': 'PERSONAL / EMPLEADOS',
                'fetch': modelo_reporte.obtener_empleados,
                'headers': ['Nombre', 'Profesión', 'Gerencia', 'Ingreso', 'Email', 'Teléfono', 'Estado'],
                'fields': ['nombre_empleado', 'profesion_empleado', 'gerencia_asignada', 'fecha_ingreso', 'email_empleado', 'telefono_empleado', 'estado_empleado']
            },
            {
                'id': 'usuarios',
                'label': 'USUARIOS DEL SISTEMA',
                'fetch': modelo_reporte.obtener_usuarios,
                'headers': ['Nombre', 'Cédula', 'Correo', 'Rol'],
                'fields': ['nombre', 'cedula_usuario', 'correo', 'rol']
            },
            {
                'id': 'contrataciones',
                'label': 'CONTRATACIONES',
                'fetch': modelo_reporte.obtener_contrataciones,
                'headers': ['Empresa', 'RIF', 'Número Contrato', 'Monto', 'Tipo', 'Modalidad'],
                'fields': ['nombre_empresa', 'rif_empresa', 'numero_contrato', 'monto', 'tipo_contrato', 'modalidad']
            },
            {
                'id': 'obras',
                'label': 'OBRAS',
                'fetch': modelo_reporte.obtener_obras,
                'headers': ['Nombre de Obra', 'Ubicación', '% Avance', 'Semáforo', 'Color', 'Contratista'],
                'fields': ['nombre_obra', 'ubicacion_obra', 'porcentaje_avance_obra', 'semaforo', 'color', 'contratista']
            },
            {
                'id': 'publicaciones',
                'label': 'PUBLICACIONES',
                'fetch': lambda: modelo_reporte.obtener_publicaciones_reporte(),
                'headers': ['Título', 'Autor', 'Fecha', 'Tipo'],
                'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada', 'tipo_publicacion']
            }
        ]

        modulos_a_procesar = []
        if not filtro:
            modulos_a_procesar = modulos_config
        else:
            for mod in modulos_config:
                if mod['id'] in filtro:
                    modulos_a_procesar.append(mod)
            
            if not modulos_a_procesar:
                data_pub_filtrada = modelo_reporte.obtener_publicaciones_reporte(filtro)
                if data_pub_filtrada:
                    modulos_a_procesar.append({
                        'label': f'RESULTADOS PARA: "{filtro.upper()}"',
                        'data_override': data_pub_filtrada,
                        'headers': ['Título', 'Autor', 'Fecha', 'Tipo'],
                        'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada', 'tipo_publicacion']
                    })

        if not modulos_a_procesar:
            flash('No se encontraron datos para los criterios ingresados.', 'info')
            return redirect(url_for('reporte_pdf_bp.generarReportePDF'))

        elements = []
        for mod in modulos_a_procesar:
            data = mod.get('data_override') or mod['fetch']()
            if data:
                elements.append(Paragraph(f'<b>SECCIÓN: {mod["label"]}</b>', styles['Heading2']))
                elements.append(Spacer(1, 6))
                table_data = [mod['headers']]
                for row in data:
                    fila = []
                    for field in mod['fields']:
                        val = str(row.get(field, ''))
                        fila.append(val[:60])
                    table_data.append(fila)
                col_w = (letter[0] - 144) / len(mod['headers'])
                tabla = Table(table_data, colWidths=[col_w] * len(mod['headers']), repeatRows=1)
                tabla.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC3545')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ]))
                elements.append(tabla)
                elements.append(Spacer(1, 12))
                elements.append(PageBreak())

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=80,
            bottomMargin=40
        )
        doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
        buffer.seek(0)
        return Response(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Reporte_Invilara.pdf"}
        )
    
    publicaciones_previa = modelo_reporte.obtener_publicaciones_reporte()
    return render_template('reportes/reportePDF.html', publicaciones=publicaciones_previa)
