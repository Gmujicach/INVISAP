from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
import openpyxl
import os
import datetime
from models.model_reportesExcel import ReporteExcelModel

reporte_excel_bp = Blueprint('reporte_excel_bp', __name__, template_folder='../vista')
modelo_reporte = ReporteExcelModel()

modulos_config_excel = [
    {
        'id': 'solicitudes',
        'label': 'SOLICITUDES',
        'fetch': modelo_reporte.obtener_solicitudes_reporte,
        'headers': ['ID', 'Fecha', 'Tipo', 'Estatus', 'Problemática', 'Cédula', 'Prioridad'],
        'fields': ['id_solicitudes', 'fecha', 'tipo_solicitud', 'estatus_solicitud', 'problematica', 'cedula', 'prioridad']
    },
    {
        'id': 'empleados',
        'label': 'PERSONAL / EMPLEADOS',
        'fetch': modelo_reporte.obtener_empleados_reporte,
        'headers': ['Nombre', 'Profesión', 'Gerencia', 'Ingreso', 'Email', 'Teléfono', 'Estado'],
        'fields': ['nombre_empleado', 'profesion_empleado', 'gerencia_asignada', 'fecha_ingreso', 'email_empleado', 'telefono_empleado', 'estado_empleado']
    },
    {
        'id': 'usuarios',
        'label': 'USUARIOS DEL SISTEMA',
        'fetch': modelo_reporte.obtener_usuarios_reporte,
        'headers': ['Nombre', 'Cédula', 'Correo', 'Rol'],
        'fields': ['nombre', 'cedula_usuario', 'correo', 'rol']
    },
    {
        'id': 'contrataciones',
        'label': 'CONTRATACIONES',
        'fetch': modelo_reporte.obtener_contrataciones_reporte,
        'headers': ['Empresa', 'RIF', 'Número Contrato', 'Monto', 'Tipo', 'Modalidad'],
        'fields': ['nombre_empresa', 'rif_empresa', 'numero_contrato', 'monto', 'tipo_contrato', 'modalidad']
    },
    {
        'id': 'obras',
        'label': 'OBRAS',
        'fetch': modelo_reporte.obtener_obras_reporte,
        'headers': ['Nombre de Obra', 'Ubicación', '% Avance', 'Semáforo', 'Color', 'Contratista'],
        'fields': ['nombre_obra', 'ubicacion_obra', 'porcentaje_avance_obra', 'semaforo', 'color', 'contratista']
    },
    {
        'id': 'publicaciones',
        'label': 'PUBLICACIONES',
        'fetch': modelo_reporte.obtener_publicaciones_reporte,
        'headers': ['Título', 'Autor', 'Fecha', 'Tipo'],
        'fields': ['titulo_publicacion', 'autor_publicacion', 'fecha_formateada', 'tipo_publicacion']
    }
]


@reporte_excel_bp.route('/reporte-excel', methods=['GET', 'POST'])
def generarReporteExcel():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda', '').strip().lower()
        modulos_a_procesar = []
        if not filtro:
            modulos_a_procesar = modulos_config_excel
        else:
            for mod in modulos_config_excel:
                if mod['id'] in filtro:
                    modulos_a_procesar.append(mod)

        if not modulos_a_procesar:
            flash('No hay información disponible para generar el reporte.', 'info')
            return redirect(url_for('reporte_excel_bp.generarReporteExcel'))

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Reporte General"

        header_fill = PatternFill(start_color='DC3545', end_color='DC3545', fill_type='solid')
        header_font = Font(color='FFFFFF', bold=True)
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

        start_row = 1
        for mod in modulos_a_procesar:
            data = mod['fetch'](filtro if filtro else None)
            if not data:
                continue

            ws.cell(row=start_row, column=1, value=mod['label'])
            ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=len(mod['headers']))
            ws.cell(row=start_row, column=1).font = Font(bold=True, size=12)
            ws.cell(row=start_row, column=1).alignment = Alignment(horizontal='center')
            start_row += 1

            for col_num, header in enumerate(mod['headers'], 1):
                cell = ws.cell(row=start_row, column=col_num, value=header)
                cell.fill = header_fill
                cell.font = header_font
                cell.border = border
                cell.alignment = Alignment(horizontal='center', vertical='center')
            start_row += 1

            for reg in data:
                for col_num, field in enumerate(mod['fields'], 1):
                    val = reg.get(field, '')
                    if isinstance(val, datetime.datetime):
                        val = val.strftime('%d/%m/%Y %H:%M')
                    elif isinstance(val, datetime.date):
                        val = val.strftime('%d/%m/%Y')
                    cell = ws.cell(row=start_row, column=col_num, value=val)
                    cell.border = border
                    cell.alignment = Alignment(vertical='center', wrap_text=True)
                start_row += 1
            start_row += 1

        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if cell.value:
                        max_length = max(max_length, len(str(cell.value)))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column].width = adjusted_width

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
