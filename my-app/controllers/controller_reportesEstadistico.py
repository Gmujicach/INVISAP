from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response, jsonify
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image, ImageDraw, ImageFont

from models.model_ReporteEstadistico import ReporteEstadisticoModel
from services.bitacora_service import BitacoraService

reporte_estadistico_bp = Blueprint('reporte_estadistico_bp', __name__, template_folder='../vista')
modelo_estadistico = ReporteEstadisticoModel()

PAGE_W, PAGE_H = 612, 792
MARGIN = 72

STAT_TITLES = {
    'por_tipo': 'Distribución por Tipo',
    'por_estatus': 'Distribución por Estatus',
    'por_fecha': 'Tendencia por Fecha',
    'por_municipio': 'Distribución por Municipio',
    'por_parroquia': 'Distribución por Parroquia',
    'por_estado': 'Distribución por Estado',
    'por_contratista': 'Distribución por Contratista',
    'por_ubicacion': 'Distribución por Ubicación',
    'por_semaforo_color': 'Distribución por Color de Semáforo',
    'por_avance': 'Distribución por Porcentaje de Avance',
    'por_cargo': 'Distribución por Cargo',
    'por_gerencia': 'Distribución por Gerencia',
    'por_fecha_ingreso': 'Tendencia por Fecha de Ingreso',
    'por_modalidad': 'Distribución por Modalidad',
    'por_objeto': 'Distribución por Objeto',
    'por_empresa': 'Distribución por Empresa',
    'por_autor': 'Distribución por Autor',
    'por_tipo_pub': 'Distribución por Tipo de Publicación',
}

STAT_COLORS = {
    'por_tipo': '#0d6efd',
    'por_estatus': '#198754',
    'por_fecha': '#dc3545',
    'por_municipio': '#0d6efd',
    'por_parroquia': '#6610f2',
    'por_estado': '#198754',
    'por_contratista': '#fd7e14',
    'por_ubicacion': '#20c997',
    'por_semaforo_color': '#dc3545',
    'por_avance': '#6610f2',
    'por_cargo': '#0d6efd',
    'por_gerencia': '#198754',
    'por_fecha_ingreso': '#dc3545',
    'por_modalidad': '#fd7e14',
    'por_objeto': '#20c997',
    'por_empresa': '#6610f2',
    'por_autor': '#0d6efd',
    'por_tipo_pub': '#dc3545',
}


def obtener_fuente(tamano):
    try:
        return ImageFont.truetype("arial.ttf", tamano)
    except Exception:
        return ImageFont.load_default()


def generar_grafico_barras(labels, valores, titulo, color_hex):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    colores = [color_hex] * len(labels)
    ax.bar(labels, valores, color=colores)
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    ax.set_ylabel('Cantidad')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer)


def generar_grafico_lineas(labels, valores, titulo, color_hex):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    fechas = []
    for lbl in labels:
        try:
            fechas.append(datetime.strptime(lbl, '%d/%m/%Y'))
        except Exception:
            fechas.append(lbl)

    ax.plot(fechas, valores, color=color_hex, marker='o')
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    ax.set_ylabel('Cantidad')
    ax.grid(axis='y', linestyle='--', alpha=0.4)
    if fechas and isinstance(fechas[0], datetime):
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m/%Y'))
        fig.autofmt_xdate(rotation=45)
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer)


def generar_grafico_circular(labels, valores, titulo, color_hex):
    fig, ax = plt.subplots(figsize=(8, 3.2))
    colores = []
    base_rgb = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
    for i in range(len(labels)):
        alpha = 0.7 + (i % 3) * 0.1
        r = max(0, min(255, base_rgb[0] + (i % 5) * 20 - 40))
        g = max(0, min(255, base_rgb[1] + (i % 5) * 15 - 30))
        b = max(0, min(255, base_rgb[2] + (i % 5) * 10 - 20))
        colores.append((r/255, g/255, b/255, alpha))
    
    ax.pie(valores, labels=labels, colors=colores, autopct='%1.0f%%', startangle=90)
    ax.set_title(titulo, fontsize=11, fontweight='bold')
    fig.tight_layout()

    buffer = BytesIO()
    fig.savefig(buffer, format='png', dpi=150)
    plt.close(fig)
    buffer.seek(0)
    return Image.open(buffer)


def generar_pagina_pdf(tipo_reporte, stats):
    pagina = Image.new('RGB', (PAGE_W, PAGE_H), 'white')
    draw = ImageDraw.Draw(pagina)

    font_titulo = obtener_fuente(18)
    font_subtitulo = obtener_fuente(13)
    font_encabezado = obtener_fuente(10)
    font_normal = obtener_fuente(11)
    font_pie = obtener_fuente(9)

    draw.text((PAGE_W / 2, 50), 'GOBERNACIÓN DEL ESTADO LARA - INVILARA', fill='black', font=font_titulo, anchor='mt')
    draw.text((PAGE_W / 2, 78), 'REPORTE ESTADÍSTICO', fill='black', font=font_subtitulo, anchor='mt')
    draw.text((PAGE_W - MARGIN, 98), f'Fecha de Emisión: {datetime.now().strftime("%d/%m/%Y %H:%M")}', fill='black', font=font_encabezado, anchor='rt')
    draw.line((MARGIN, 115, PAGE_W - MARGIN, 115), fill='black', width=1)

    y = 130
    draw.text((MARGIN, y), f'ANÁLISIS ESTADÍSTICO DE {tipo_reporte}', fill='black', font=font_subtitulo)
    y += 28

    graficos = []
    for key, items in stats.items():
        if not items:
            continue
        labels = [str(d['label']) for d in items]
        valores = [int(d['valor']) for d in items]
        titulo = STAT_TITLES.get(key, key.replace('_', ' ').title())
        color = STAT_COLORS.get(key, '#0d6efd')

        if key in ('por_fecha', 'por_fecha_ingreso'):
            graficos.append(generar_grafico_lineas(labels, valores, titulo, color))
        elif key in ('por_tipo', 'por_estatus', 'por_municipio', 'por_parroquia', 'por_estado',
                     'por_contratista', 'por_ubicacion', 'por_semaforo_color', 'por_avance',
                     'por_cargo', 'por_gerencia', 'por_modalidad', 'por_objeto', 'por_empresa',
                     'por_autor', 'por_tipo_pub', 'por_tipo_pub'):
            if len(labels) <= 2:
                graficos.append(generar_grafico_circular(labels, valores, titulo, color))
            else:
                graficos.append(generar_grafico_barras(labels, valores, titulo, color))
        else:
            graficos.append(generar_grafico_barras(labels, valores, titulo, color))

    grafico_h = 280
    grafico_w = 468
    pagina_num = 1

    for img in graficos:
        img.thumbnail((grafico_w, grafico_h))
        pos_x = (PAGE_W - grafico_w) // 2
        if y + grafico_h > PAGE_H - 80:
            draw.text((PAGE_W / 2, PAGE_H - 50), f'Página {pagina_num}', fill='black', font=font_pie, anchor='mt')
            yield pagina
            pagina_num += 1
            pagina = Image.new('RGB', (PAGE_W, PAGE_H), 'white')
            draw = ImageDraw.Draw(pagina)
            y = 80
            draw.text((MARGIN, y), f'ANÁLISIS ESTADÍSTICO DE {tipo_reporte}', fill='black', font=font_subtitulo)
            y += 28
        pagina.paste(img, (pos_x, y))
        y += grafico_h + 20

    draw.text((PAGE_W / 2, PAGE_H - 50), f'Página {pagina_num}', fill='black', font=font_pie, anchor='mt')
    yield pagina


TIPO_REPORTE_LABELS = {
    'solicitudes': 'SOLICITUDES',
    'obras': 'OBRAS',
    'empleados': 'PERSONAL / EMPLEADOS',
    'contrataciones': 'CONTRATACIONES',
    'publicaciones': 'PUBLICACIONES',
}


def _obtener_stats_por_tipo(tipo_reporte, filtros, agrupacion='dia'):
    if tipo_reporte == 'solicitudes':
        return modelo_estadistico.obtener_estadisticas_solicitudes(filtros, agrupacion)
    elif tipo_reporte == 'obras':
        return modelo_estadistico.obtener_estadisticas_obras(filtros, agrupacion)
    elif tipo_reporte == 'empleados':
        return modelo_estadistico.obtener_estadisticas_empleados(filtros, agrupacion)
    elif tipo_reporte == 'contrataciones':
        return modelo_estadistico.obtener_estadisticas_contrataciones(filtros, agrupacion)
    elif tipo_reporte == 'publicaciones':
        return modelo_estadistico.obtener_estadisticas_publicaciones(filtros, agrupacion)
    return modelo_estadistico.obtener_estadisticas_solicitudes(filtros, agrupacion)


def _colectar_filtros_form():
    campos_posibles = [
        'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'nombre_solicitante',
        'fecha_desde', 'fecha_hasta', 'municipio', 'parroquia', 'direccion', 'telefono', 'correo',
        'sector', 'ambito',
        'nombre_empleado', 'cargo', 'fecha_ingreso_desde', 'fecha_ingreso_hasta', 'estado_empleado',
        'cedula_persona', 'gerencia_asignada', 'tipo_contrato', 'modalidad', 'objeto',
        'fecha_registro_desde', 'fecha_registro_hasta', 'fecha_inicio_procedimiento_desde',
        'fecha_inicio_procedimiento_hasta', 'fecha_adjudicacion_desde', 'fecha_adjudicacion_hasta',
        'numero_contrato',
        'titulo_obra', 'ubicacion_obra', 'fecha_inicio_desde', 'fecha_inicio_hasta',
        'fecha_fin_desde', 'fecha_fin_hasta', 'semaforo_estado', 'contratista',
        'titulo_publicacion', 'nombre_responsable', 'tipo_publicacion',
        'fecha_publicacion_desde', 'fecha_publicacion_hasta',
        'apellido', 'nombre', 'rol',
    ]
    filtros = {}
    for campo in campos_posibles:
        val = request.form.get(campo, '').strip()
        if val:
            filtros[campo] = val
    return filtros


@reporte_estadistico_bp.route('/reporte-estadistico', methods=['GET', 'POST'])
def generarReporteEstadistico():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    tipo_reporte = 'solicitudes'
    filtros = None
    agrupacion = 'dia'
    if request.method == 'POST':
        tipo_reporte = request.form.get('tipo_reporte', 'solicitudes').strip().lower()
        agrupacion = request.form.get('agrupacion', 'dia').strip().lower()
        filtros = _colectar_filtros_form()
        tipo_reporte_label = TIPO_REPORTE_LABELS.get(tipo_reporte, 'SOLICITUDES')

    stats = _obtener_stats_por_tipo(tipo_reporte, filtros, agrupacion)
    paginas = list(generar_pagina_pdf(tipo_reporte_label, stats))

    pdf_buffer = BytesIO()
    paginas[0].save(pdf_buffer, format='PDF', resolution=150.0, save_all=True, append_images=paginas[1:])
    pdf_buffer.seek(0)

    BitacoraService.registrar_accion(
        session, 'Reportes', 'VER',
        f'Generó un reporte estadístico de {tipo_reporte_label}'
    )
    return Response(
        pdf_buffer.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=Reporte_Estadistico_{tipo_reporte}.pdf"}
    )


@reporte_estadistico_bp.route('/reporte-estadistico/data')
def datosEstadisticos():
    if 'conectado' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    tipo_reporte = request.args.get('tipo_reporte', 'solicitudes').strip().lower()
    agrupacion = request.args.get('agrupacion', 'dia').strip().lower()
    filtros = {}
    campos_posibles = [
        'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'nombre_solicitante',
        'fecha_desde', 'fecha_hasta', 'municipio', 'parroquia', 'direccion', 'telefono', 'correo',
        'sector', 'ambito',
        'nombre_empleado', 'cargo', 'fecha_ingreso_desde', 'fecha_ingreso_hasta', 'estado_empleado',
        'cedula_persona', 'gerencia_asignada', 'tipo_contrato', 'modalidad', 'objeto',
        'fecha_registro_desde', 'fecha_registro_hasta', 'fecha_inicio_procedimiento_desde',
        'fecha_inicio_procedimiento_hasta', 'fecha_adjudicacion_desde', 'fecha_adjudicacion_hasta',
        'numero_contrato',
        'titulo_obra', 'ubicacion_obra', 'fecha_inicio_desde', 'fecha_inicio_hasta',
        'fecha_fin_desde', 'fecha_fin_hasta', 'semaforo_estado', 'contratista',
        'titulo_publicacion', 'nombre_responsable', 'tipo_publicacion',
        'fecha_publicacion_desde', 'fecha_publicacion_hasta',
        'apellido', 'nombre', 'rol',
    ]
    for campo in campos_posibles:
        val = request.args.get(campo, '').strip()
        if val:
            filtros[campo] = val

    stats = _obtener_stats_por_tipo(tipo_reporte, filtros, agrupacion)

    result = {}
    for key, items in stats.items():
        if items:
            result[key] = [
                {'label': str(item['label']), 'valor': int(item['valor'])}
                for item in items
            ]

    return jsonify(result)
