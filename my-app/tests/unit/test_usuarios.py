from unittest.mock import MagicMock, patch

from models.model_usuarios import DEFAULT_AVATAR, UsuarioModel


def test_listar_usuarios_asigna_avatar_por_defecto():
    usuario = UsuarioModel()
    conexion = MagicMock()
    conexion.cursor.return_value.fetchall.return_value = [
        {'id_usuarios': 1, 'avatar': None},
        {'id_usuarios': 2, 'avatar': 'assets/avatar.png'},
    ]

    with patch.object(usuario, 'obtener_conexion_seguridad', return_value=conexion):
        usuarios = usuario.listar_todos()

    assert usuarios[0]['avatar'] == DEFAULT_AVATAR
    assert usuarios[1]['avatar'] == 'assets/avatar.png'
