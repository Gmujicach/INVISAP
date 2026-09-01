import sys
import os
from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response
from io import BytesIO
from datetime import datetime, date

from models.model_reportesPDF import ReportePDFModel
from services.bitacora_service import BitacoraService
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

reporte_pdf_bp = Blueprint('reporte_pdf_bp', __name__, template_folder='../vista')
modelo_reporte = ReportePDFModel()

styles = getSampleStyleSheet()
estilo_celda = ParagraphStyle(
    'CeldaPDF',
    parent=styles['Normal'],
    fontSize=7,
    leading=9,
    spaceAfter=0,
    spaceBefore=0,
    wordWrap='CJK'
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_GOBERNACION = os.path.join(BASE_DIR, 'static', 'assets', 'img', 'NUEVO LOGO GOBERNACION DE LARA JUNIO 2025.png')
LOGO_INVILARA = os.path.join(BASE_DIR, 'static', 'assets', 'img', 'INVILARA LOGO OFICIAL HORIZONTAL.png')

LOGO_W = 120
LOGO_H = 40


def header_footer(canvas, doc):
    canvas.saveState()
    page_w, page_h = doc.pagesize
    top_y = doc.height + doc.topMargin - 8

    canvas.setFont('Helvetica-Oblique', 8)
    canvas.drawRightString(page_w - doc.rightMargin - 5, top_y + 8, f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")}')

    if os.path.exists(LOGO_GOBERNACION):
        try:
            canvas.drawImage(LOGO_GOBERNACION, doc.leftMargin, top_y - LOGO_H,
                             width=LOGO_W, height=LOGO_H,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    if os.path.exists(LOGO_INVILARA):
        try:
            canvas.drawImage(LOGO_INVILARA, page_w - doc.rightMargin - LOGO_W, top_y - LOGO_H,
                             width=LOGO_W, height=LOGO_H,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    text_y = top_y - LOGO_H - 8
    canvas.setFont('Helvetica-Bold', 12)
    canvas.drawCentredString(page_w / 2, text_y, 'GOBERNACIÓN DEL ESTADO LARA - INVILARA')
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawCentredString(page_w / 2, text_y - 15, 'REPORTE DETALLADO DE GESTIÓN')
    canvas.setFont('Helvetica-Oblique', 8)
    canvas.drawCentredString(page_w / 2, doc.bottomMargin - 20, f'Página {canvas.getPageNumber()}')
    canvas.restoreState()


def construir_modulos_config():
    return [
        {
            'id': 'solicitudes',
            'label': 'SOLICITUDES',
            'keywords': ['solicitudes', 'solicitud'],
            'fetch': modelo_reporte.obtener_solicitudes,
            'headers': ['ID', 'Fecha', 'Tipo', 'Estatus', 'Problemática', 'Cédula', 'Prioridad'],
            'fields': ['id_solicitudes', 'fecha', 'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'prioridad']
        },
        {
            'id': 'solicitantes',
            'label': 'SOLICITANTES',
            'keywords': ['solicitantes', 'solicitante', 'personas', 'particular'],
            'fetch': modelo_reporte.obtener_solicitantes,
            'headers': ['Nombre', 'Apellido', 'Cédula'],
            'fields': ['nombre', 'apellido', 'cedula']
        },
        {
            'id': 'empleados',
            'label': 'PERSONAL / EMPLEADOS',
            'keywords': ['empleados', 'empleado', 'personal', 'trabajadores'],
            'fetch': modelo_reporte.obtener_empleados,
            'headers': ['Nombre', 'Profesión', 'Gerencia', 'Ingreso', 'Email', 'Teléfono', 'Estado'],
            'fields': ['nombre_empleado', 'profesion_empleado', 'gerencia_asignada', 'fecha_ingreso', 'email_empleado', 'telefono_empleado', 'estado_empleado']
        },
        {
            'id': 'usuarios',
            'label': 'USUARIOS DEL SISTEMA',
            'keywords': ['usuarios', 'usuario', 'accesos', 'seguridad'],
            'fetch': modelo_reporte.obtener_usuarios,
            'headers': ['Nombre', 'Cédula', 'Correo', 'Rol'],
            'fields': ['nombre', 'cedula_usuario', 'correo', 'rol']
        },
        {
            'id': 'contrataciones',
            'label': 'CONTRATACIONES',
            'keywords': ['contrataciones', 'contratacion', 'contratos'],
            'fetch': modelo_reporte.obtener_contrataciones,
            'headers': ['Empresa', 'RIF', 'N° Contrato', 'Monto', 'Descripción', 'Observación', 'Tipo', 'Modalidad', 'Objeto', 'Registro', 'Inicio', 'Adjudicación'],
            'fields': ['nombre_empresa', 'rif_empresa', 'numero_contrato', 'monto', 'descripcion', 'observacion', 'tipo_contrato', 'modalidad', 'objeto', 'fecha_registro', 'fecha_inicio', 'fecha_adjudicacion']
        },
        {
            'id': 'obras',
            'label': 'OBRAS',
            'keywords': ['obras', 'obra'],
            'fetch': modelo_reporte.obtener_obras,
            'headers': ['Nombre de Obra', 'Ubicación', '% Avance', 'Semáforo', 'Color', 'Contratista'],
            'fields': ['nombre_obra', 'ubicacion_obra', 'porcentaje_avance_obra', 'semaforo', 'color', 'contratista']
        },
        {
            'id': 'publicaciones',
            'label': 'PUBLICACIONES',
            'keywords': ['publicaciones', 'publicacion', 'noticias', 'avisos'],
            'fetch': lambda filt=None: modelo_reporte.obtener_publicaciones_reporte(filt),
            'headers': ['Título', 'Autor', 'Fecha', 'Tipo'],
            'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada', 'tipo_publicacion']
        }
    ]


def _detectar_tipo_filtro(filtros, modulo_id):
    if not filtros:
        return None
    if modulo_id == 'solicitudes' and any(k in filtros for k in ('cedula', 'correo', 'correo_dominio')):
        return 'solicitante'
    if modulo_id == 'obras' and any(k in filtros for k in ('ubicacion_obra', 'semaforo_estado', 'contratista', 'criticidad', 'nivel_gravedad', 'gerente')):
        return 'obra'
    return None


def _get_modulo_reconfigurado(mod_config, tipo_filtro):
    if tipo_filtro == 'solicitante' and mod_config['id'] == 'solicitudes':
        return {
            'id': mod_config['id'],
            'label': mod_config['label'],
            'keywords': mod_config['keywords'],
            'fetch': mod_config['fetch'],
            'headers': ['Cédula', 'Nombre del Solicitante', 'Correo', 'Teléfono', 'Descripción de la Solicitud', 'Fecha', 'Estatus', 'Municipio/Parroquia'],
            'fields': ['cedula', 'nombre_solicitante', 'correo', 'telefono', 'problematica', 'fecha', 'estatus_solicitud', 'municipio_parroquia']
        }
    if tipo_filtro == 'obra' and mod_config['id'] == 'obras':
        return {
            'id': mod_config['id'],
            'label': mod_config['label'],
            'keywords': mod_config['keywords'],
            'fetch': mod_config['fetch'],
            'headers': ['ID Obra', 'Nivel de Criticidad', 'Gerencia Responsable', 'Estatus', 'Avance (%)', 'Fecha de Registro'],
            'fields': ['id_obra', 'nivel_gravedad', 'gerente', 'semaforo', 'porcentaje_avance_obra', 'fecha_inicio']
        }
    return mod_config


def obtener_modulos_por_filtro(filtro):
    modulos_config = construir_modulos_config()
    if not filtro:
        return modulos_config
    texto = filtro.lower().strip()
    for mod in modulos_config:
        if texto == mod['id'].lower():
            return [mod]
    return []


CAMPOS_COMUNES = [
    'nombre_solicitante', 'cedula', 'telefono', 'correo', 'correo_dominio',
    'fecha_desde', 'fecha_hasta', 'municipio', 'direccion',
]

CAMPOS_POR_MODULO_PDF = {
    'solicitudes': [
        'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'nombre_solicitante',
        'fecha_desde', 'fecha_hasta', 'municipio', 'parroquia', 'direccion', 'telefono', 'correo',
        'correo_dominio', 'sector', 'ambito',
    ],
    'empleados': [
        'nombre_empleado', 'cargo', 'fecha_ingreso_desde', 'fecha_ingreso_hasta', 'estado_empleado',
        'cedula_persona', 'telefono', 'correo', 'direccion', 'parroquia', 'municipio', 'gerencia_asignada',
    ],
    'usuarios': [
        'nombre', 'cedula_usuario', 'correo', 'rol', 'estado',
    ],
    'contrataciones': [
        'empresa_ganadora', 'tipo_contrato', 'modalidad', 'objeto',
        'fecha_registro_desde', 'fecha_registro_hasta', 'fecha_inicio_procedimiento_desde',
        'fecha_inicio_procedimiento_hasta', 'fecha_adjudicacion_desde', 'fecha_adjudicacion_hasta',
        'numero_contrato',
    ],
    'obras': [
        'titulo_obra', 'ubicacion_obra', 'fecha_inicio_desde', 'fecha_inicio_hasta',
        'fecha_fin_desde', 'fecha_fin_hasta', 'semaforo_estado', 'contratista',
        'criticidad', 'nivel_gravedad', 'gerente',
    ],
    'publicaciones': [
        'titulo_publicacion', 'nombre_responsable', 'tipo_publicacion',
        'fecha_publicacion_desde', 'fecha_publicacion_hasta',
    ],
    'solicitantes': [
        'nombre', 'apellido', 'cedula', 'correo', 'correo_dominio',
    ],
}


def _colectar_filtros_form(modulo='general'):
    campos_especificos = CAMPOS_POR_MODULO_PDF.get(modulo, [])
    campos = list(dict.fromkeys(CAMPOS_COMUNES + campos_especificos))
    filtros = {}
    for campo in campos:
        val = request.form.get(campo, '').strip()
        if val:
            filtros[campo] = val
    return filtros


def _limpiar_filtros_por_modulo(filtros, modulo_id):
    campos_validos = {
        'solicitudes': {
            'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'nombre_solicitante',
            'fecha_desde', 'fecha_hasta', 'municipio', 'parroquia', 'direccion', 'telefono', 'correo',
            'correo_dominio', 'sector', 'ambito',
        },
        'empleados': {
            'nombre_empleado', 'cargo', 'fecha_ingreso_desde', 'fecha_ingreso_hasta', 'estado_empleado',
            'cedula_persona', 'telefono', 'correo', 'direccion', 'parroquia', 'municipio', 'gerencia_asignada',
        },
        'usuarios': {'nombre', 'cedula_usuario', 'correo', 'rol', 'estado'},
        'contrataciones': {
            'empresa_ganadora', 'tipo_contrato', 'modalidad', 'objeto',
            'fecha_registro_desde', 'fecha_registro_hasta', 'fecha_inicio_procedimiento_desde',
            'fecha_inicio_procedimiento_hasta', 'fecha_adjudicacion_desde', 'fecha_adjudicacion_hasta',
            'numero_contrato',
        },
        'obras': {
            'titulo_obra', 'ubicacion_obra', 'fecha_inicio_desde', 'fecha_inicio_hasta',
            'fecha_fin_desde', 'fecha_fin_hasta', 'semaforo_estado', 'contratista',
            'criticidad', 'nivel_gravedad', 'gerente',
        },
        'publicaciones': {
            'titulo_publicacion', 'nombre_responsable', 'tipo_publicacion',
            'fecha_publicacion_desde', 'fecha_publicacion_hasta',
        },
        'solicitantes': {'nombre', 'apellido', 'cedula', 'correo', 'correo_dominio'},
    }
    validos = campos_validos.get(modulo_id, set())
    return {k: v for k, v in filtros.items() if k in validos}


@reporte_pdf_bp.route('/reporte-pdf', methods=['GET', 'POST'])
def generarReportePDF():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    if request.method == 'POST':
        modulo = request.form.get('modulo', '').strip().lower()
        filtros = _colectar_filtros_form(modulo)

        modulos_config = construir_modulos_config()
        if modulo and modulo != 'general':
            modulos_a_procesar = [m for m in modulos_config if m['id'] == modulo]
        else:
            modulos_a_procesar = modulos_config

        if not modulos_a_procesar:
            flash('No se encontró ningún módulo relacionado con el criterio ingresado.', 'info')
            return redirect(url_for('reporte_pdf_bp.generarReportePDF'))

        elementos = []

        es_contrataciones = any(mod['id'] == 'contrataciones' for mod in modulos_a_procesar)
        tamanio_pagina = landscape(letter) if es_contrataciones else letter

        for mod in modulos_a_procesar:
            mod_filtros = _limpiar_filtros_por_modulo(filtros, mod['id'])
            tipo_filtro = _detectar_tipo_filtro(mod_filtros, mod['id'])
            mod_config = _get_modulo_reconfigurado(mod, tipo_filtro)
            fetch_fn = mod_config['fetch']
            data = fetch_fn(mod_filtros if mod_filtros else None)
            if not data:
                continue
            elementos.append(Paragraph(f'<b>SECCIÓN: {mod_config["label"]}</b>', styles['Heading2']))
            elementos.append(Spacer(1, 28))

            encabezados = [Paragraph(str(h), estilo_celda) for h in mod_config['headers']]
            filas = [encabezados]
            for row in data:
                valores = []
                for field in mod_config['fields']:
                    val = row.get(field, '')
                    if val is None:
                        val = ''
                    elif isinstance(val, datetime):
                        val = val.strftime('%d/%m/%Y %I:%M:%S %p')
                    elif isinstance(val, date):
                        val = val.strftime('%d/%m/%Y')
                    else:
                        val = str(val)
                    if len(val) > 120:
                        val = val[:120] + '...'
                    valores.append(Paragraph(val, estilo_celda))
                filas.append(valores)

            col_w = (tamanio_pagina[0] - 144) / len(mod_config['headers'])
            tabla = Table(filas, colWidths=[col_w] * len(mod_config['headers']), repeatRows=1)
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC3545')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
            ]))
            elementos.append(tabla)
            elementos.append(Spacer(1, 24))
            elementos.append(PageBreak())

        if not elementos:
            flash('No hay registros disponibles para los criterios ingresados.', 'info')
            return redirect(url_for('reporte_pdf_bp.generarReportePDF'))

        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=tamanio_pagina,
            rightMargin=72,
            leftMargin=72,
            topMargin=125,
            bottomMargin=40
        )
        doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
        buffer.seek(0)
        BitacoraService.registrar_accion(
            session, 'Reportes', 'VER',
            f'Generó un reporte PDF de gestión'
        )
        return Response(
            buffer.read(),
            mimetype="application/pdf",
            headers={"Content-Disposition": "attachment; filename=Reporte_Invilara.pdf"}
        )

    publicaciones_previa = modelo_reporte.obtener_publicaciones_reporte()
    return render_template('reportes/reportePDF.html', publicaciones=publicaciones_previa)
