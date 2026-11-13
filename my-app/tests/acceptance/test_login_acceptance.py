from routers import router_home, router_login
from models.model_seguridad import RolPermisoModel


def test_usuario_inicia_sesion_y_consulta_solicitudes_autorizadas(
    client,
    authenticated_permissions,
    monkeypatch,
):
    solicitudes = [{'id_solicitudes': 7, 'problematica': 'Caso de aceptación'}]
    monkeypatch.setattr(
        router_login,
        'verificar_recaptcha',
        lambda token: (True, 'válido'),
    )
    monkeypatch.setattr(
        router_login.auth_context,
        'login',
        lambda username, password: {
            'id_usuarios': 12,
            'nombre': 'Usuario de aceptación',
            'correo': 'aceptacion@example.test',
            'rol': 'Usuario',
        },
    )
    monkeypatch.setattr(
        RolPermisoModel,
        'obtener_nombres_modulos_por_rol',
        lambda self, rol: ['solicitudes'],
    )
    monkeypatch.setattr(router_login, 'info_perfil_session', lambda: [])
    monkeypatch.setattr(
        router_login.BitacoraService,
        'registrar_accion',
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(router_home, 'obtener_solicitudes', lambda: solicitudes)

    formulario = client.get('/login')
    assert formulario.status_code == 200

    login = client.post(
        '/login',
        data={
            'nombre': 'usuario-prueba',
            'pass_user': 'clave-de-prueba',
            'g-recaptcha-response': 'token-de-prueba',
        },
    )
    assert login.status_code == 302
    with client.session_transaction() as session:
        assert session['conectado'] is True
        assert session['name_surname'] == 'Usuario de aceptación'

    respuesta = client.get('/api/obtener-solicitudes-json')
    assert respuesta.status_code == 200
    assert respuesta.get_json() == solicitudes
