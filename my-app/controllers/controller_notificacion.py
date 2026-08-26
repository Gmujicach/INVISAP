"""
Controller de Notificaciones — Expone las rutas API para el "campanita"
del panel: listar, contar no leídas, marcar como leída y marcar todas.

El usuario solo puede ver/marcar SUS propias notificaciones (filtrado por
session['id']).
"""
from flask import Blueprint, jsonify, session, request

from models.model_notificacion import NotificacionModel

notificacion_bp = Blueprint('notificacion_bp', __name__, url_prefix='/notificaciones')


def _id_usuario_actual():
    uid = session.get('id')
    try:
        return int(uid)
    except (TypeError, ValueError):
        return 0


@notificacion_bp.route('/lista', methods=['GET'])
def lista():
    """Devuelve las notificaciones del usuario y el conteo de no leídas."""
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    modelo = NotificacionModel()
    uid = _id_usuario_actual()
    notificaciones = modelo.listar(uid, limit=20)
    no_leidas = modelo.contar_no_leidas(uid)

    datos = []
    for n in notificaciones:
        fecha = n.get('fecha')
        if isinstance(fecha, str):
            fecha_str = fecha
        elif fecha is not None:
            fecha_str = fecha.strftime('%Y-%m-%d %H:%M')
        else:
            fecha_str = ''
        avatar = n.get('creado_por_avatar') or ''
        if not avatar and n.get('creado_por_id'):
            try:
                from models.model_usuarios import UsuarioModel, DEFAULT_AVATAR
                usuario = UsuarioModel().buscar_por_id(n['creado_por_id'])
                if usuario:
                    avatar = usuario.get('avatar') or DEFAULT_AVATAR
            except Exception:
                pass
        if avatar and not avatar.startswith('/'):
            avatar = '/static/' + avatar
        datos.append({
            'id_notificacion': n.get('id_notificacion'),
            'modulo': n.get('modulo'),
            'titulo': n.get('titulo'),
            'mensaje': n.get('mensaje'),
            'enlace': n.get('enlace') or '',
            'leida': int(n.get('leida') or 0),
            'creado_por': n.get('creado_por') or '',
            'creado_por_id': n.get('creado_por_id'),
            'creado_por_avatar': avatar,
            'fecha': fecha_str
        })

    return jsonify({
        'status': 'success',
        'notificaciones': datos,
        'no_leidas': no_leidas
    })


@notificacion_bp.route('/marcar-leida/<int:id_notificacion>', methods=['POST'])
def marcar_leida(id_notificacion):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    modelo = NotificacionModel()
    ok = modelo.marcar_leida(id_notificacion, _id_usuario_actual())
    return jsonify({'status': 'success' if ok else 'error', 'no_leidas': modelo.contar_no_leidas(_id_usuario_actual())})


@notificacion_bp.route('/marcar-todas', methods=['POST'])
def marcar_todas():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    modelo = NotificacionModel()
    modelo.marcar_todas(_id_usuario_actual())
    return jsonify({'status': 'success', 'no_leidas': 0})


@notificacion_bp.route('/eliminar/<int:id_notificacion>', methods=['POST'])
def eliminar(id_notificacion):
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    modelo = NotificacionModel()
    ok = modelo.eliminar(id_notificacion, _id_usuario_actual())
    return jsonify({'status': 'success' if ok else 'error', 'no_leidas': modelo.contar_no_leidas(_id_usuario_actual())})


@notificacion_bp.route('/eliminar-todas', methods=['POST'])
def eliminar_todas():
    if 'conectado' not in session:
        return jsonify({'status': 'error', 'message': 'No autorizado'}), 401

    modelo = NotificacionModel()
    modelo.eliminar_todas(_id_usuario_actual())
    return jsonify({'status': 'success', 'no_leidas': 0})
