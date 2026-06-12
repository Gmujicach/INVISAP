from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.contratacion import ContratacionModel

contrataciones_bp = Blueprint('contrataciones_bp', __name__)

# Esta es la ruta para ver el formulario
@contrataciones_bp.route('/form-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template('contrataciones/form_contratacion.html')
    return redirect(url_for('login_bp.inicio'))

# Esta es la ruta para ver la lista
@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        modelo = ContratacionModel()
        lista = modelo.obtener_todas_las_contrataciones()
        return render_template('contrataciones/lista_contrataciones.html', contrataciones=lista)
    return redirect(url_for('login_bp.inicio'))

# Esta es la ruta para procesar el post
@contrataciones_bp.route('/registrar-contratacion', methods=['POST'])
def procesar_registro():
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.registrar_contrataciones(request.form):
            flash('Registrado correctamente', 'success')
        else:
            flash('Error al guardar', 'error')
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
    return redirect(url_for('login_bp.inicio'))