from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.model_gerencias import GerenciaModel

gerencia_bp = Blueprint('gerencia_bp', __name__)

@gerencia_bp.route('/registrar-gerencias', methods=['GET'])
def gestionar_gerencias():
    if 'conectado' in session:
        modelo = GerenciaModel()
        lista = modelo.obtener_todas_las_gerencias()
        return render_template('gerencias/lista_gerencias.html', gerencias=lista)
    return redirect(url_for('login_bp.inicio'))

@gerencia_bp.route('/form-registrar-gerencias', methods=['POST'])
def procesar_registro():
    print("ESTADO DE LA SESIÓN:", session) # Esto es vital
    
    if 'conectado' in session:
        print("¡USUARIO LOGUEADO! Intentando guardar...")
        datos = request.form
        modelo = GerenciaModel()
        if modelo.registrar_gerencias(datos):
            return "GUARDADO CON ÉXITO"
        else:
            return "ERROR EN EL MODELO"
    else:
        return "ERROR: ¡LA SESIÓN NO ESTÁ ACTIVA! No puedes registrar."