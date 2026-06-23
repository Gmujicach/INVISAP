"""
Servicio de Email para el Sistema Invilara
con manejo de envío de correos electrónicos con OTP
aplicando principios de POO y encapsulamiento.
"""

from flask_mail import Mail, Message
from flask import render_template_string
import random
import string
from datetime import datetime, timedelta
from conexion.conexionBD import connectionBD_seguridad

class EmailService:
    """
    Clase para gestionar el envío de correos electrónicos
    Implementa encapsulamiento y responsabilidad única (POO)
    """
    
    def __init__(self, mail_instance):
        self.__mail = mail_instance  # Atributo privado
        self.__otp_expiry_minutes = 15  # OTP válido por 15 minutos
        self.__max_attempts = 5  # Máximo 5 intentos
    
    # Getters y Setters (Encapsulamiento)
    def get_otp_expiry_minutes(self):
        return self.__otp_expiry_minutes
    
    def set_otp_expiry_minutes(self, minutes):
        if minutes > 0 and minutes <= 30:
            self.__otp_expiry_minutes = minutes
        else:
            raise ValueError("Los minutos deben estar entre 1 y 30")
    
    def __generate_otp(self):
        """
        Método privado para generar código OTP de 6 dígitos
        Aplicando encapsulamiento según Prof. Escalona
        """
        return ''.join(random.choices(string.digits, k=6))
    
    def __get_email_template(self, otp_code, nombre_usuario):
        """
        Método privado para obtener la plantilla HTML del email
        Sin dependencias de CDN - Todo local
        """
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Recuperación de Contraseña - INVILARA</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
                    padding: 20px;
                }}
                .email-container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background: #ffffff;
                    border-radius: 16px;
                    overflow: hidden;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                }}
                .header {{
                    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                    padding: 40px 20px;
                    text-align: center;
                    color: white;
                }}
                .header h1 {{
                    font-size: 28px;
                    margin-bottom: 10px;
                }}
                .header p {{
                    font-size: 14px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #2c3e50;
                    margin-bottom: 20px;
                }}
                .message {{
                    color: #555;
                    line-height: 1.6;
                    margin-bottom: 30px;
                }}
                .otp-container {{
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                    border: 2px dashed #2ecc71;
                    border-radius: 12px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .otp-label {{
                    font-size: 14px;
                    color: #666;
                    margin-bottom: 15px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .otp-code {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #2ecc71;
                    letter-spacing: 8px;
                    font-family: 'Courier New', monospace;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .warning {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    margin: 20px 0;
                    border-radius: 4px;
                }}
                .warning-icon {{
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    background: #ffc107;
                    border-radius: 50%;
                    text-align: center;
                    line-height: 20px;
                    color: white;
                    font-weight: bold;
                    margin-right: 10px;
                }}
                .warning-text {{
                    color: #856404;
                    font-size: 14px;
                }}
                .expiry-info {{
                    text-align: center;
                    color: #e74c3c;
                    font-weight: bold;
                    margin: 20px 0;
                    font-size: 16px;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #dee2e6;
                }}
                .footer-text {{
                    color: #6c757d;
                    font-size: 13px;
                    line-height: 1.6;
                }}
                .logo {{
                    font-size: 36px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .security-tips {{
                    background: #e8f5e9;
                    border-radius: 8px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .security-tips h3 {{
                    color: #2ecc71;
                    font-size: 16px;
                    margin-bottom: 15px;
                }}
                .security-tips ul {{
                    list-style: none;
                    padding: 0;
                }}
                .security-tips li {{
                    color: #555;
                    font-size: 13px;
                    padding: 8px 0;
                    padding-left: 25px;
                    position: relative;
                }}
                .security-tips li:before {{
                    content: "✓";
                    position: absolute;
                    left: 0;
                    color: #2ecc71;
                    font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    <div class="logo">INVILARA</div>
                    <h1>Recuperación de Contraseña</h1>
                    <p>Sistema de Gestión - Gobernación de Lara</p>
                </div>
                
                <div class="content">
                    <div class="greeting">
                        Hola, <strong>{nombre_usuario}</strong>
                    </div>
                    
                    <div class="message">
                        Hemos recibido una solicitud para restablecer la contraseña de tu cuenta en el Sistema INVILARA.
                        Para continuar con el proceso, utiliza el siguiente código de verificación:
                    </div>
                    
                    <div class="otp-container">
                        <div class="otp-label">Tu Código de Verificación</div>
                        <div class="otp-code">{otp_code}</div>
                    </div>
                    
                    <div class="expiry-info">
                        Este código expira en {self.__otp_expiry_minutes} minutos
                    </div>
                    
                    <div class="warning">
                        <span class="warning-icon">!</span>
                        <span class="warning-text">
                            <strong>Importante:</strong> Si no solicitaste este cambio, ignora este correo. 
                            Tu contraseña permanecerá segura.
                        </span>
                    </div>
                    
                    <div class="security-tips">
                        <h3>Consejos de Seguridad</h3>
                        <ul>
                            <li>Nunca compartas este código con nadie</li>
                            <li>El personal de INVILARA nunca te pedirá este código</li>
                            <li>Usa una contraseña fuerte y única</li>
                            <li>Cambia tu contraseña regularmente</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="footer-text">
                        <strong>Sistema INVILARA</strong><br>
                        Gobernación del Estado Lara - Venezuela<br>
                        Barquisimeto, Estado Lara<br><br>
                        Este es un correo automático, por favor no responder.<br>
                        © 2025 INVILARA. Todos los derechos reservados.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
    
    def __save_otp_to_database(self, correo, otp_code):
        """
        Método privado para guardar el OTP en la base de datos
        Aplicando validaciones según Prof. Escalona
        """
        try:
            conexion = connectionBD_seguridad()
            cursor = conexion.cursor()
            
            expiry_time = datetime.now() + timedelta(minutes=self.__otp_expiry_minutes)
            
            sql = """
                UPDATE usuarios 
                SET otp_code = %s, 
                    otp_expiry = %s,
                    otp_attempts = 0
                WHERE correo = %s AND estado = 1
            """
            cursor.execute(sql, (otp_code, expiry_time, correo))
            conexion.commit()
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error al guardar OTP: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()
    
    def send_otp_email(self, correo, nombre_usuario):
        """
        Método público para enviar email con OTP
        Retorna: (success: bool, otp_code: str, message: str)
        """
        try:
            # Generar OTP
            otp_code = self.__generate_otp()
            
            # Guardar en BD
            if not self.__save_otp_to_database(correo, otp_code):
                return False, None, "Error al guardar el código de verificación"
            
            # Preparar email
            msg = Message(
                subject="Código de Recuperación - Sistema INVILARA",
                recipients=[correo],
                html=self.__get_email_template(otp_code, nombre_usuario)
            )
            
            # Enviar email
            self.__mail.send(msg)
            
            return True, otp_code, "Código enviado exitosamente"
            
        except Exception as e:
            print(f"Error al enviar email: {e}")
            return False, None, f"Error al enviar el correo: {str(e)}"
    
    def verify_otp(self, correo, otp_ingresado):
        """
        Método público para verificar el OTP ingresado
        Retorna: (valid: bool, message: str)
        """
        try:
            conexion = connectionBD_seguridad()
            cursor = conexion.cursor(dictionary=True)
            
            sql = """
                SELECT otp_code, otp_expiry, otp_attempts 
                FROM usuarios 
                WHERE correo = %s AND estado = 1
            """
            cursor.execute(sql, (correo,))
            user = cursor.fetchone()
            
            if not user:
                return False, "Usuario no encontrado"
            
            # Verificar intentos
            if user['otp_attempts'] >= self.__max_attempts:
                return False, f"Máximo de intentos alcanzado. Solicita un nuevo código."
            
            # Verificar expiración
            if not user['otp_expiry'] or datetime.now() > user['otp_expiry']:
                return False, "El código ha expirado. Solicita uno nuevo."
            
            # Verificar código
            if user['otp_code'] != otp_ingresado:
                # Incrementar intentos fallidos
                cursor.execute(
                    "UPDATE usuarios SET otp_attempts = otp_attempts + 1 WHERE correo = %s",
                    (correo,)
                )
                conexion.commit()
                intentos_restantes = self.__max_attempts - (user['otp_attempts'] + 1)
                return False, f"Código incorrecto. Te quedan {intentos_restantes} intentos."
            
            # Código válido - limpiar OTP
            cursor.execute(
                """UPDATE usuarios 
                   SET otp_code = NULL, otp_expiry = NULL, otp_attempts = 0 
                   WHERE correo = %s""",
                (correo,)
            )
            conexion.commit()
            
            return True, "Código verificado correctamente"
            
        except Exception as e:
            print(f"Error al verificar OTP: {e}")
            return False, "Error al verificar el código"
        finally:
            if cursor:
                cursor.close()
            if conexion:
                conexion.close()