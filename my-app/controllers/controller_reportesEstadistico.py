from flask import Blueprint, render_template, request, session, redirect, url_for, flash, Response, jsonify
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image, ImageDraw, ImageFont

from models.model_ReporteEstadistico import ReporteEstadisticoModel

reporte_estadistico_bp = Blueprint('reporte_estadistico_bp', __name__, template_folder='../vista')
modelo_estadistico = ReporteEstadisticoModel()

PAGE_W, PAGE_H = 612, 792
MARGIN = 72


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


def generar_pdf_estadistico(stats, filtro):
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
    draw.text((MARGIN, y), 'ANÁLISIS ESTADÍSTICO DE SOLICITUDES', fill='black', font=font_subtitulo)
    y += 28
    if filtro:
        draw.text((MARGIN, y), f'Filtro aplicado: {filtro}', fill='black', font=font_normal)
        y += 22

    graficos = []
    if stats.get('por_tipo'):
        graficos.append(generar_grafico_barras(
            [str(d['label']) for d in stats['por_tipo']],
            [int(d['valor']) for d in stats['por_tipo']],
            'Distribución por Tipo de Solicitud',
            '#0d6efd'
        ))

    if stats.get('por_estatus'):
        graficos.append(generar_grafico_barras(
            [str(d['label']) for d in stats['por_estatus']],
            [int(d['valor']) for d in stats['por_estatus']],
            'Distribución por Estatus de Solicitud',
            '#198754'
        ))

    if stats.get('por_fecha'):
        labels_fecha = []
        for d in stats['por_fecha']:
            lbl = d['label']
            if hasattr(lbl, 'strftime'):
                labels_fecha.append(lbl.strftime('%d/%m/%Y'))
            else:
                labels_fecha.append(str(lbl))
        graficos.append(generar_grafico_lineas(
            labels_fecha,
            [int(d['valor']) for d in stats['por_fecha']],
            'Tendencia de Solicitudes por Fecha',
            '#dc3545'
        ))

    grafico_h = 280
    grafico_w = 468

    for img in graficos:
        img.thumbnail((grafico_w, grafico_h))
        pos_x = (PAGE_W - grafico_w) // 2
        if y + grafico_h > PAGE_H - 80:
            draw.text((PAGE_W / 2, PAGE_H - 50), f'Página {pagina.info.get("page", 1)}', fill='black', font=font_pie, anchor='mt')
            yield pagina
            pagina = Image.new('RGB', (PAGE_W, PAGE_H), 'white')
            draw = ImageDraw.Draw(pagina)
            y = 80
            draw.text((MARGIN, y), 'ANÁLISIS ESTADÍSTICO DE SOLICITUDES', fill='black', font=font_subtitulo)
            y += 28
        pagina.paste(img, (pos_x, y))
        y += grafico_h + 20

    draw.text((PAGE_W / 2, PAGE_H - 50), 'Página 1', fill='black', font=font_pie, anchor='mt')
    yield pagina


@reporte_estadistico_bp.route('/reporte-estadistico', methods=['GET', 'POST'])
def generarReporteEstadistico():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    filtro = None
    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()

    stats = modelo_estadistico.obtener_estadisticas_solicitudes(filtro)
    paginas = list(generar_pdf_estadistico(stats, filtro))

    pdf_buffer = BytesIO()
    paginas[0].save(pdf_buffer, format='PDF', resolution=150.0, save_all=True, append_images=paginas[1:])
    pdf_buffer.seek(0)

    return Response(
        pdf_buffer.read(),
        mimetype="application/pdf",
        headers={"Content-Disposition": "attachment; filename=Reporte_Estadistico_Solicitudes.pdf"}
    )


@reporte_estadistico_bp.route('/reporte-estadistico/data')
def datosEstadisticos():
    if 'conectado' not in session:
        return jsonify({'error': 'No autorizado'}), 401

    filtro = request.args.get('filtro_busqueda', '').strip().lower()
    stats = modelo_estadistico.obtener_estadisticas_solicitudes(filtro if filtro else None)

    result = {}
    if stats.get('por_tipo'):
        result['por_tipo'] = [
            {'label': str(item['label']), 'valor': int(item['valor'])}
            for item in stats['por_tipo']
        ]
    if stats.get('por_estatus'):
        result['por_estatus'] = [
            {'label': str(item['label']), 'valor': int(item['valor'])}
            for item in stats['por_estatus']
        ]
    if stats.get('por_fecha'):
        result['por_fecha'] = []
        for item in stats['por_fecha']:
            lbl = item['label']
            if hasattr(lbl, 'strftime'):
                label_str = lbl.strftime('%d/%m/%Y')
            else:
                label_str = str(lbl)
            result['por_fecha'].append({'label': label_str, 'valor': int(item['valor'])})

    return jsonify(result)
