from flask import render_template, request, redirect, url_for, flash, session
from app import app
from models.model_usuarios import UsuarioModel

# Instanciamos el modelo una sola vez
modelo_usuario = UsuarioModel()

@app.route('/lista-de-usuarios', methods=['GET'])
def listar_usuarios():
    if 'conectado' not in session:
        return redirect(url_for('login_bp.inicio'))
    
    # El Controlador pide datos al Modelo
    usuarios = modelo_usuario.listar_todos()
    # El Controlador entrega los datos a la Vista
    return render_template('usuarios/lista_usuarios.html', resp_usuariosBD=usuarios)

@app.route('/saved-register', methods=['POST'])
def registrar_usuario():
    if request.method == 'POST':
        resultado = modelo_usuario.incluir(request.form)
        if resultado:
            flash('Usuario creado con éxito', 'success')
        else:
            flash('Error al crear usuario', 'error')
    return redirect(url_for('listar_usuarios'))

@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def eliminar_usuario(id):
    if 'conectado' in session:
        modelo_usuario.eliminar(id)
        flash('Usuario eliminado', 'success')
    return redirect(url_for('listar_usuarios'))