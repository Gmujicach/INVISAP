from unittest.mock import Mock

from mysql.connector import Error as MySQLConnectorError

from app import app
from conexion.conexionBD import get_db_config
from routers import router_login


def test_db_config_uses_configured_port_and_does_not_supply_a_password(monkeypatch):
    monkeypatch.setenv('DB_USER', 'invisap_test')
    monkeypatch.setenv('DB_PASSWORD', '')
    monkeypatch.setenv('DB_PORT', '3307')
    monkeypatch.setenv('DB_CONNECT_TIMEOUT', '7')

    config = get_db_config()

    assert config['user'] == 'invisap_test'
    assert config['password'] == ''
    assert config['port'] == 3307
    assert config['connection_timeout'] == 7


def test_login_returns_service_unavailable_when_mysql_rejects_connection(monkeypatch):
    monkeypatch.setitem(app.config, 'TESTING', True)
    monkeypatch.setattr(router_login, 'verificar_recaptcha', lambda _token: (True, ''))
    monkeypatch.setattr(
        router_login.auth_context,
        'login',
        Mock(side_effect=MySQLConnectorError(
            errno=1045,
            msg='Access denied for test account',
            sqlstate='28000',
        )),
    )

    response = app.test_client().post(
        '/login',
        data={
            'nombre': 'usuario_de_prueba',
            'pass_user': 'clave-de-prueba',
            'g-recaptcha-response': 'token-de-prueba',
        },
    )

    assert response.status_code == 503
    assert b'Verifica la configuraci' in response.data
    assert b'Access denied' not in response.data
