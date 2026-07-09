from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from models.model_obra import ObraModel
from models.model_bitacora import BitacoraModel

obra_bp = Blueprint('obra_bp', __name__)

@obra_bp.route('/gestionar-obras', methods=['GET'])
def vista_gestionar_obras():
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))
        
    modelo = ObraModel()
    obras = modelo.obtener_todas()
    
    return render_template('obras/form_gestionar_obras.html', obras=obras)

@obra_bp.route('/form-registrar-obra', methods=['POST'])
def registrar_obra():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'Sesión caducada.'}), 401
    
    try:
        data = request.form
        modelo = ObraModel()
        
        # Mapeo actualizado de las claves exactas de la tabla
        datos_insertar = {
            'titulo_obra': data.get('titulo_obra'),
            'ubicacion_obra': data.get('ubicacion_obra'),
            'periodo_ejecucion': data.get('periodo_ejecucion'),
            'fecha_inicio': data.get('fecha_inicio'),
            'fecha_fin': data.get('fecha_fin'),
            'mediciones_obra': data.get('mediciones_obra'),
            'valuaciones': data.get('valuaciones'),
            'modificaciones_contrato': data.get('modificaciones_contrato'),
            'certificaciones_obras_ejecutadas': data.get('certificaciones_obras_ejecutadas'),
            'numero_contrato': data.get('numero_contrato'),
            'porcentaje_avance_obra': data.get('porcentaje_avance_obra'),
            'semaforo_id_semaforo': data.get('semaforo_id_semaforo'),
            'contratacion_id_contratacion': data.get('contratacion_id_contratacion'),
            'gestionar_proyectos_codigo_proyecto': data.get('gestionar_proyectos_codigo_proyecto')
        }
        
        if modelo.registrar_obra(datos_insertar):
            BitacoraModel().registrar(
                usuario=session.get('usuario', 'Sistema'),
                id_usuario=session.get('id_usuario', 1),
                modulo='Obras',
                accion='CREAR',
                descripcion=f"Registró la obra: {datos_insertar['titulo_obra']}"
            )
            return jsonify({'status': 'success', 'message': 'Obra registrada exitosamente.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Rechazado por Base de Datos. Revisa referencias.'}), 400
            
    except Exception as e:
        print(f"Error en controlador: {e}")
        return jsonify({'status': 'error', 'message': 'Excepción interna.'}), 500