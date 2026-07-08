from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from models.model_contratacion import ContratacionModel
from controllers.funciones_maquinaria import *
from services.bitacora_service import BitacoraService
import re

contrataciones_bp = Blueprint('contrataciones_bp', __name__)

# Ruta para ver el formulario
@contrataciones_bp.route('/form-contratacion', methods=['GET'])
def viewFormContratacion():
    if 'conectado' in session:
        return render_template('contrataciones/form_contratacion.html')
    return redirect(url_for('login_bp.inicio'))

# Ruta para ver la lista
@contrataciones_bp.route('/contrataciones', methods=['GET'])
def gestionar_contrataciones():
    if 'conectado' in session:
        modelo = ContratacionModel()
        lista = modelo.obtener_todas_las_contrataciones()
        return render_template('contrataciones/lista_contrataciones.html', contrataciones=lista)
    return redirect(url_for('login_bp.inicio'))

# Ruta para procesar el post
@contrataciones_bp.route('/registrar-contratacion', methods=['POST'])
def procesar_registro():
    if 'conectado' in session:
        modelo = ContratacionModel()
        if modelo.registrar_contrataciones(request.form):
            BitacoraService.registrar_accion(
                session, 'Contrataciones', 'CREAR',
                f'Registró la contratación N°: {request.form.get("numero_contrato")}'
            )
            flash('Contratacion Registrada correctamente', 'success')
        else:
            flash('Error al guardar', 'error')
        return redirect(url_for('contrataciones_bp.gestionar_contrataciones'))
    return redirect(url_for('login_bp.inicio'))


def validar_datos_contratacion(datos):
    campos_requeridos = [
        'empresa_ganadora', 'empresa_rif', 'descripcion', 'numero_contrato',
        'monto', 'tipo_contrato', 'modalidad', 'objeto', 'observacion',
        'fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro'
    ]
    
    for campo in campos_requeridos:
        valor = datos.get(campo, '').strip()
        if not valor:
            nombre_legible = campo.replace('_', ' ').capitalize()
            return False, f"El campo '{nombre_legible}' es obligatorio."

    descripcion = datos.get('descripcion').strip()
    if len(descripcion) < 5 or len(descripcion) > 100:
        return False, "La descripción debe tener entre 5 y 100 caracteres."

    num_contrato = datos.get('numero_contrato').strip()
    if len(num_contrato) < 3 or len(num_contrato) > 12:
        return False, "El número de contrato debe tener entre 3 y 12 caracteres."
        
    monto = datos.get('monto').strip()
    if len(monto) < 3 or len(monto) > 20:
        return False, "El monto debe tener entre 3 y 20 caracteres."

    tipos_validos = ['Contrato de Obra', 'Contrato de Servicio', 'Contrato de Bienes']
    if datos.get('tipo_contrato') not in tipos_validos:
        return False, "El tipo de contrato seleccionado no es válido."

    modalidades_validas = ['Concurso Abierto', 'Concurso Cerrado', 'Consulta de Precios', 'Adjudicación Directa']
    if datos.get('modalidad') not in modalidades_validas:
        return False, "La modalidad seleccionada no es válida."

    objetos_validos = ['Ejecución de Obras', 'Prestación de Servicios', 'Suministro de Bienes']
    if datos.get('objeto') not in objetos_validos:
        return False, "El objeto seleccionado no es válido."

    patron_fecha = r'^\d{4}-\d{2}-\d{2}$'
    campos_fecha = ['fecha_inicio_procedimiento', 'fecha_adjudicacion', 'fecha_registro']
    for campo in campos_fecha:
        if not re.match(patron_fecha, datos.get(campo)):
            return False, "Una de las fechas enviadas tiene un formato inválido."

    return True, "Validación exitosa."