from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
import re
import openpyxl
from openpyxl.styles import PatternFill, Font, Border, Side, Alignment
from openpyxl.utils import get_column_letter
import os
import datetime
from models.model_reportesExcel import ReporteExcelModel

reporte_excel_bp = Blueprint('reporte_excel_bp', __name__, template_folder='../vista')
modelo_reporte = ReporteExcelModel()

header_fill = PatternFill(start_color='DC3545', end_color='DC3545', fill_type='solid')
header_font = Font(color='FFFFFF', bold=True, size=11)
border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)
header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
cell_alignment = Alignment(horizontal='left', vertical='center', wrap_text=True)


def construir_modulos_config_excel():
    return [
        {
            'id': 'solicitudes',
            'label': 'SOLICITUDES',
            'keywords': ['solicitudes', 'solicitud', 'solicitantes', 'solicitante'],
            'fetch': modelo_reporte.obtener_solicitudes_reporte,
            'headers': ['ID', 'Fecha', 'Tipo', 'Estatus', 'Problemática', 'Cédula', 'Prioridad'],
            'fields': ['id_solicitudes', 'fecha', 'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'prioridad']
        },
        {
            'id': 'empleados',
            'label': 'PERSONAL / EMPLEADOS',
            'keywords': ['empleados', 'empleado', 'personal', 'trabajadores', ' RRHH', 'recursos humanos'],
            'fetch': modelo_reporte.obtener_empleados_reporte,
            'headers': ['Nombre', 'Profesión', 'Gerencia', 'Ingreso', 'Email', 'Teléfono', 'Estado'],
            'fields': ['nombre_empleado', 'profesion_empleado', 'gerencia_asignada', 'fecha_ingreso', 'email_empleado', 'telefono_empleado', 'estado_empleado']
        },
        {
            'id': 'usuarios',
            'label': 'USUARIOS DEL SISTEMA',
            'keywords': ['usuarios', 'usuario', 'accesos', 'seguridad', 'roles'],
            'fetch': modelo_reporte.obtener_usuarios_reporte,
            'headers': ['Nombre', 'Cédula', 'Correo', 'Rol'],
            'fields': ['nombre', 'cedula_usuario', 'correo', 'rol']
        },
        {
            'id': 'contrataciones',
            'label': 'CONTRATACIONES',
            'keywords': ['contrataciones', 'contratacion', 'contratos', 'empresas'],
            'fetch': modelo_reporte.obtener_contrataciones_reporte,
            'headers': ['Empresa', 'RIF', 'Número Contrato', 'Monto', 'Tipo', 'Modalidad'],
            'fields': ['nombre_empresa', 'rif_empresa', 'numero_contrato', 'monto', 'tipo_contrato', 'modalidad']
        },
        {
            'id': 'obras',
            'label': 'OBRAS',
            'keywords': ['obras', 'obra', 'proyectos', 'construccion', 'construcción'],
            'fetch': modelo_reporte.obtener_obras_reporte,
            'headers': ['Nombre de Obra', 'Ubicación', '% Avance', 'Semáforo', 'Color', 'Contratista'],
            'fields': ['nombre_obra', 'ubicacion_obra', 'porcentaje_avance_obra', 'semaforo', 'color', 'contratista']
        },
        {
            'id': 'publicaciones',
            'label': 'PUBLICACIONES',
            'keywords': ['publicaciones', 'publicacion', 'noticias', 'avisos', 'comunicados'],
            'fetch': modelo_reporte.obtener_publicaciones_reporte,
            'headers': ['Título', 'Autor', 'Fecha', 'Tipo'],
            'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada', 'tipo_publicacion']
        }
    ]


def obtener_modulos_excel_por_filtro(filtro):
    modulos_config = construir_modulos_config_excel()
    if not filtro:
        return modulos_config
    texto = filtro.lower().strip()
    seleccionados = []
    for mod in modulos_config:
        if texto in mod['id'].lower() or any(texto in kw for kw in mod['keywords']) or texto in mod['label'].lower():
            seleccionados.append(mod)
    return seleccionados


@reporte_excel_bp.route('/reporte-excel', methods=['GET', 'POST'])
def generarReporteExcel():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()
        modulos_a_procesar = obtener_modulos_excel_por_filtro(filtro)

        if not modulos_a_procesar:
            flash('No se encontró ningún módulo relacionado con el criterio ingresado.', 'info')
            return redirect(url_for('reporte_excel_bp.generarReporteExcel'))

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        for mod in modulos_a_procesar:
            data = mod['fetch'](filtro if filtro else None)
            if not data:
                continue

            sheet_title = re.sub(r'[\\\/\?\*\[\]]', ' ', mod['label'])
            ws = wb.create_sheet(title=sheet_title)
            ws.sheet_view.showGridLines = True
            ws.freeze_panes = 'A2'

            start_row = 1
            ws.cell(row=start_row, column=1, value=sheet_title)
            ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=len(mod['headers']))
            title_cell = ws.cell(row=start_row, column=1)
            title_cell.font = Font(bold=True, size=13, color='FFFFFF')
            title_cell.fill = PatternFill(start_color='DC3545', end_color='DC3545', fill_type='solid')
            title_cell.alignment = Alignment(horizontal='center', vertical='center')
            start_row += 1

            column_widths = {i: len(str(h)) for i, h in enumerate(mod['headers'], 1)}

            for col_num, header in enumerate(mod['headers'], 1):
                cell = ws.cell(row=start_row, column=col_num, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = header_alignment
                column_widths[col_num] = max(column_widths[col_num], len(str(header)))
            start_row += 1

            date_fields = {'fecha', 'fecha_ingreso', 'fecha_formateada'}

            for reg in data:
                for col_num, field in enumerate(mod['fields'], 1):
                    val = reg.get(field, '')
                    if field in date_fields and val:
                        val = str(val)
                    elif isinstance(val, datetime.datetime):
                        val = val.strftime('%d/%m/%Y %H:%M')
                    elif isinstance(val, datetime.date):
                        val = val.strftime('%d/%m/%Y')
                    else:
                        val = str(val) if val is not None else ''

                    cell = ws.cell(row=start_row, column=col_num, value=val)
                    cell.border = border
                    cell.alignment = cell_alignment
                    column_widths[col_num] = max(column_widths[col_num], min(len(str(val)), 60))
                start_row += 1

            for col_num, width in column_widths.items():
                adjusted = min(max(width + 3, 12), 50)
                ws.column_dimensions[get_column_letter(col_num)].width = adjusted

        filename = f"Reporte_Invilara_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.normpath(os.path.join(base_dir, '..', 'static', 'downloads-excel'))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        ruta_archivo = os.path.join(folder_path, filename)
        wb.save(ruta_archivo)
        return send_file(ruta_archivo, as_attachment=True)

    publicaciones_previa = modelo_reporte.obtener_publicaciones_reporte()
    return render_template('reportes/reporteExcel.html', publicaciones=publicaciones_previa)
