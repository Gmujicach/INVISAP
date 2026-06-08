from flask import Blueprint, render_template, request, session, redirect, url_for, flash, send_file
import openpyxl
import os
import datetime
from models.model_reportesExcel import ReporteExcelModel

# Definimos el blueprint especificando la carpeta de vistas para que Flask encuentre reporteExcel.html
reporte_excel_bp = Blueprint('reporte_excel_bp', __name__, template_folder='../vista')
modelo_reporte = ReporteExcelModel()

@reporte_excel_bp.route('/reporte-excel', methods=['GET', 'POST'])
def generarReporteExcel():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    if request.method == 'POST':
        filtro = request.form.get('filtro_busqueda')
        data = modelo_reporte.obtener_empleados_reporte(filtro)

        if not data:
            flash('No hay información disponible para generar el reporte.', 'info')
            return redirect(url_for('reporte_excel_bp.generarReporteExcel'))

        wb = openpyxl.Workbook()
        hoja = wb.active
        hoja.title = "Reporte Empleados"

        cabecera = ("Nombre", "Apellido", "Sexo", "Telefono", "Email", "Profesión", "Salario", "Fecha de Ingreso")
        hoja.append(cabecera)

        for reg in data:
            hoja.append((
                reg['nombre_empleado'],
                reg['apellido_empleado'],
                reg['sexo_empleado'],
                reg['telefono_empleado'],
                reg['email_empleado'],
                reg['profesion_empleado'],
                reg['salario_empleado'],
                reg['fecha_registro']
            ))

        # Formato moneda para la columna de salario
        for fila in range(2, hoja.max_row + 1):
            hoja.cell(row=fila, column=7).number_format = '#,##0'

        filename = f"Reporte_Invilara_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Carpeta de descargas (usando ruta absoluta relativa a este archivo)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder_path = os.path.normpath(os.path.join(base_dir, '..', 'static', 'downloads-excel'))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        ruta_archivo = os.path.join(folder_path, filename)
        wb.save(ruta_archivo)

        return send_file(ruta_archivo, as_attachment=True)

    # Mostrar vista previa en GET
    empleados = modelo_reporte.obtener_empleados_reporte()
    return render_template('reportes/reporteExcel.html', empleados=empleados)

@reporte_excel_bp.route('/reportes-estadisticos', methods=['GET'])
def viewReportesEstadisticos():
    if 'conectado' not in session:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('login_bp.inicio'))

    data_stats = modelo_reporte.obtener_estadisticas_generales()
    return render_template('reportes/reporteEstadistico.html', estadisticas=data_stats)