
from app import app
from flask import request, session, redirect, url_for, jsonify


@app.errorhandler(404)
def page_not_found(error):
    accept = request.headers.get('Accept', '')
    content_type = request.headers.get('Content-Type', '')
    requested_with = request.headers.get('X-Requested-With', '')

    es_api = (
        request.path.startswith('/api/')
        or 'application/json' in accept
        or 'application/json' in content_type
        or requested_with == 'XMLHttpRequest'
    )

    if es_api:
        if 'conectado' not in session:
            return jsonify({'status': 'error', 'message': 'Sesión no válida.'}), 401
        return jsonify({'status': 'error', 'message': 'Recurso no encontrado.'}), 404

    if 'conectado' in session and request.method == 'GET':
        return redirect(url_for('login_bp.inicio'))
    else:
        return redirect(url_for('login_bp.inicio'))
