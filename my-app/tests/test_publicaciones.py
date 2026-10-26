from unittest.mock import MagicMock, patch

from models.model_publicaciones import PublicacionModel


def test_obtener_publicacion_consulta_por_id_con_parametro():
    modelo = PublicacionModel()
    conexion = MagicMock()
    conexion.cursor.return_value.fetchone.return_value = {'id_publicacion': 7}

    with patch.object(modelo, 'obtener_conexion', return_value=conexion):
        resultado = modelo.obtener_publicacion_por_id(7)

    assert resultado == {'id_publicacion': 7}
    conexion.cursor.return_value.execute.assert_called_once_with(
        'SELECT *, cuerpo_publicacion FROM publicacion WHERE id_publicacion = %s', (7,)
    )
