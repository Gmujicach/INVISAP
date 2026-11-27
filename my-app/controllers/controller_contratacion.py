from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from models.model_contratacion import ContratacionModel

contrataciones_bp = Blueprint('contrataciones_bp', __name__)

@contrataciones_bp.route('/form-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template('contratacion/form_contratacion.html')
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        modelo = ContratacionModel()
        lista = modelo.obtener_todas()
        return render_template('contratacion/form_contratacion.html', contrataciones=lista)
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/editar-contratacion/<int:id>', methods=['GET'])
def vista_editar(id):
    if 'conectado' in session:
        modelo = ContratacionModel()
        contratacion_data = modelo.obtener_por_id(id)
        
        if contratacion_data:
            campos_fecha = ['fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro']
            for campo in campos_fecha:
                if contratacion_data.get(campo):
                    if hasattr(contratacion_data[campo], 'strftime'):
                        contratacion_data[campo] = contratacion_data[campo].strftime('%Y-%m-%d')
                    else:
                        contratacion_data[campo] = str(contratacion_data[campo])[:10]
            
            return render_template('contratacion/form_contratacionM.html', contratacion=contratacion_data)
        
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
    return redirect(url_for('login_bp.inicio'))

@contrataciones_bp.route('/api/obtener-empresas-json', methods=['GET'])
def obtener_empresas_json():
    if 'conectado' in session:
        modelo = ContratacionModel()
        empresas = modelo.obtener_empresas()
        return jsonify(empresas)
    return jsonify([]), 401

@contrataciones_bp.route('/registrar-contratacion', methods=['POST'])
def procesar_registro():
    if 'conectado' in session:
        modelo = ContratacionModel()
        exito, mensaje = modelo.registrar(request.form)
        if exito:
            return jsonify({'status': 'success', 'message': mensaje})
        return jsonify({'status': 'error', 'message': mensaje})
    return jsonify({'status': 'error', 'message': 'Sesión expirada.'}), 401

@contrataciones_bp.route('/procesar-actualizacion', methods=['POST'])
def procesar_actualizacion():
    if 'conectado' in session:
        modelo = ContratacionModel()
        exito, mensaje = modelo.actualizar(request.form) 
        if exito:
            return jsonify({'status': 'success', 'message': mensaje, 'redirect': url_for('contrataciones_bp.gestionar_contrataciones')})
        return jsonify({'status': 'error', 'message': mensaje})
    return jsonify({'status': 'error', 'message': 'Sesión expirada.'}), 401

@contrataciones_bp.route('/eliminar-contratacion/<int:id>', methods=['POST'])
def eliminar_contratacion(id):
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.eliminar(id):
            return jsonify({'exito': True, 'mensaje': 'Contratación eliminada correctamente.'})
        return jsonify({'exito': False, 'mensaje': 'Error al intentar eliminar el registro.'})
    return jsonify({'exito': False, 'mensaje': 'Sesión expirada.'}), 401