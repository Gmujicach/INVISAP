import unittest
from unittest.mock import patch

from controllers import funciones_login


class RecaptchaSecurityTestCase(unittest.TestCase):
    def test_no_acepta_verificacion_si_no_hay_secreto_configurado(self):
        with patch.object(funciones_login, 'RECAPTCHA_SECRET_KEY', ''):
            with patch.object(funciones_login.urllib.request, 'urlopen') as urlopen:
                valido, mensaje = funciones_login.verificar_recaptcha('token-de-prueba')

        self.assertFalse(valido)
        self.assertIn('no está configurada', mensaje)
        urlopen.assert_not_called()

    def test_no_acepta_verificacion_si_google_no_responde(self):
        with patch.object(funciones_login, 'RECAPTCHA_SECRET_KEY', 'secreto-de-prueba'):
            with patch.object(
                funciones_login.urllib.request,
                'urlopen',
                side_effect=OSError('sin red'),
            ):
                valido, mensaje = funciones_login.verificar_recaptcha('token-de-prueba')

        self.assertFalse(valido)
        self.assertIn('No se pudo validar', mensaje)


if __name__ == '__main__':
    unittest.main()