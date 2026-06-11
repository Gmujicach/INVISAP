import sys
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response

# Configuración de ruta local para la librería fpdf2
base_dir = os.path.dirname(os.path.abspath(__file__))
lib_path = os.path.normpath(os.path.join(base_dir, '..', 'static', 'libs', 'lib_pdf', 'fpdf'))
if lib_path not in sys.path:
    sys.path.append(lib_path)

from models.model_reportesPDF import ReportePDFModel
from fpdf import FPDF
import datetime

reporte_pdf_bp = Blueprint('reporte_pdf_bp', __name__, template_folder='../vista')
modelo_reporte = ReportePDFModel()

class PDF(FPDF):
    def header(self):
        # Encabezado del PDF
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, 'GOBERNACIÓN DEL ESTADO LARA - INVILARA', 0, 1, 'C')
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, 'REPORTE DETALLADO DE GESTIÓN', 0, 1, 'C')
        self.set_font('helvetica', 'I', 10)
        self.cell(0, 10, f'Fecha de Emisión: {datetime.datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 1, 'R')
        self.ln(10)

    def footer(self):
        # Pie de página
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

@reporte_pdf_bp.route('/reporte-pdf', methods=['GET', 'POST'])
def generarReportePDF():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    filtro = None
    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()
        
        # Configuración de los módulos disponibles
        modulos_config = [
            {
                'id': 'solicitantes',
                'label': 'SOLICITANTES',
                'fetch': modelo_reporte.obtener_solicitantes,
                'headers': ['Nombre', 'Apellido', 'Cédula'],
                'fields': ['nombre_solicitante', 'apellido_solicitante', 'cedula_solicitante']
            },
            {
                'id': 'empleados',
                'label': 'PERSONAL / EMPLEADOS',
                'fetch': modelo_reporte.obtener_empleados,
                'headers': ['Nombre', 'Apellido', 'Email', 'Profesión'],
                'fields': ['nombre_empleado', 'apellido_empleado', 'email_empleado', 'profesion_empleado']
            },
            {
                'id': 'usuarios',
                'label': 'USUARIOS DEL SISTEMA',
                'fetch': modelo_reporte.obtener_usuarios,
                'headers': ['Nombre y Apellido', 'Correo Electrónico'],
                'fields': ['name_surname', 'email_user']
            },
            {
                'id': 'contrataciones',
                'label': 'CONTRATACIONES',
                'fetch': modelo_reporte.obtener_contrataciones,
                'headers': ['Empresa', 'RIF'],
                'fields': ['nombre_empresa', 'rif_empresa']
            },
            {
                'id': 'obras',
                'label': 'OBRAS',
                'fetch': modelo_reporte.obtener_obras,
                'headers': ['Nombre de Obra', 'Ubicación', 'Estado'],
                'fields': ['nombre_obra', 'ubicacion_obra', 'estado_obra']
            },
            {
                'id': 'publicaciones',
                'label': 'PUBLICACIONES',
                'fetch': lambda: modelo_reporte.obtener_publicaciones_reporte(),
                'headers': ['Título', 'Autor', 'Fecha'],
                'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada']
            }
        ]

        # Determinar qué módulos incluir
        modulos_a_procesar = []
        if not filtro:
            modulos_a_procesar = modulos_config  # Reporte General
        else:
            # Buscar si el filtro coincide con algún ID de módulo
            for mod in modulos_config:
                if mod['id'] in filtro:
                    modulos_a_procesar.append(mod)
            
            # Si no hay coincidencias directas, intentar filtrar publicaciones como secundario
            if not modulos_a_procesar:
                data_pub_filtrada = modelo_reporte.obtener_publicaciones_reporte(filtro)
                if data_pub_filtrada:
                    modulos_a_procesar.append({
                        'label': f'RESULTADOS PARA: "{filtro.upper()}"',
                        'data_override': data_pub_filtrada,
                        'headers': ['Título', 'Autor', 'Fecha'],
                        'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada']
                    })

        if not modulos_a_procesar:
            flash('No se encontraron datos para los criterios ingresados.', 'info')
            return redirect(url_for('reporte_pdf_bp.generarReportePDF'))

        # Iniciar creación del PDF
        pdf = PDF()
        pdf.alias_nb_pages()
        pdf.add_page()
        
        for mod in modulos_a_procesar:
            data = mod.get('data_override') or mod['fetch']()
            if data:
                # Título del Módulo
                pdf.set_font('helvetica', 'B', 12)
                pdf.set_fill_color(240, 240, 240)
                pdf.cell(0, 10, f'SECCIÓN: {mod["label"]}', 0, 1, 'L', 1)
                pdf.ln(2)

                # Cabeceras de Tabla
                pdf.set_font('helvetica', 'B', 10)
                pdf.set_text_color(255, 255, 255)
                pdf.set_fill_color(220, 53, 69) # Color rojo (danger) para cabeceras
                col_width = (pdf.w - 20) / len(mod['headers'])
                for header in mod['headers']:
                    pdf.cell(col_width, 8, header, 1, 0, 'C', 1)
                pdf.ln()

                # Datos
                pdf.set_font('helvetica', '', 9)
                pdf.set_text_color(0, 0, 0)
                for row in data:
                    if pdf.get_y() > 265: pdf.add_page() # Control de salto de página
                    for field in mod['fields']:
                        val = str(row.get(field, ''))
                        pdf.cell(col_width, 7, val[:50], 1) # Recorte básico para evitar desborde
                    pdf.ln()
                pdf.ln(8)

        # Generar salida y enviar archivo
        pdf_output = pdf.output()
        return Response(
            pdf_output,
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Reporte_Invilara.pdf"}
        )
    
    # Comportamiento GET: mostrar listado general de publicaciones como vista previa
    publicaciones_previa = modelo_reporte.obtener_publicaciones_reporte()
    return render_template('reportes/reportePDF.html', publicaciones=publicaciones_previa)