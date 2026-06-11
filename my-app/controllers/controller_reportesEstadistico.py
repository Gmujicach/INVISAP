from flask import render_template, request, jsonify
from models.model_ReporteEstadistico import ReporteEstadisticoModel

class ReporteController:
    @staticmethod
    def generar_reporte(db_connection):
        # Capturamos el filtro enviado por el formulario
        modulo = request.form.get('filtro_busqueda', 'solicitudes') # 'solicitudes' por defecto
        
        modelo = ReporteEstadisticoModel(db_connection)
        datos = modelo.obtener_estadisticas_por_modulo(modulo)
        
        # Procesamiento para Chart.js
        labels = [d['label'] for d in datos]
        valores = [d['valor'] for d in datos]
        
        return render_template('reporteEstadistico.html', 
                               labels=labels, 
                               valores=valores)