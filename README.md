<p align="center">
  <img src="my-app/static/assets/img/INVILARA%20LOGO%20OFICIAL%20HORIZONTAL.png" alt="INVILARA" width="340">
</p>

<h1 align="center">INVISAP</h1>

<p align="center">
  Sistema de gestión del Instituto de Vialidad del Estado Lara
  <br>
  Una plataforma para organizar solicitudes, proyectos, obras y procesos institucionales.
</p>

<p align="center">
  <img alt="Python 3.11" src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="Flask 2.3" src="https://img.shields.io/badge/Flask-2.3-000000?style=flat-square&logo=flask&logoColor=white">
  <img alt="MySQL 8" src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat-square&logo=mysql&logoColor=white">
  <img alt="Interfaz en español" src="https://img.shields.io/badge/Idioma-Espa%C3%B1ol-087A24?style=flat-square">
</p>

---

## Presentación

**INVISAP** es una aplicación web desarrollada para apoyar la gestión del Instituto de Vialidad del Estado Lara (INVILARA). Reúne en una sola plataforma información y herramientas para el seguimiento de solicitudes, proyectos, obras y actividades relacionadas.

La interfaz pública presenta al instituto y sus capacidades; el sistema de gestión permite a los usuarios autorizados trabajar con los módulos que corresponden a sus roles y permisos.

## Vista previa

La siguiente demostración recorre la página de INVILARA. También puedes [abrir el archivo de video en el repositorio](my-app/static/video/landing%20page%20Invilara.mp4).

<p align="center">
  <video controls width="100%" preload="metadata">
    <source src="https://raw.githubusercontent.com/Gmujicach/INVISAP/main/my-app/static/video/landing%20page%20Invilara.mp4" type="video/mp4">
    Tu navegador no puede reproducir este video. Usa el enlace al archivo de video anterior.
  </video>
</p>

## Funcionalidades

- Gestión de solicitudes y proyectos.
- Registro y seguimiento de obras, maquinaria y contrataciones.
- Administración de empresas y empleados.
- Gestión de inspecciones, evidencias e informes de avance.
- Administración de usuarios, roles, permisos y bitácora.
- Publicaciones y notificaciones.
- Panel de control y reportes estadísticos.
- Exportación de reportes a PDF y Excel.
- Administración de respaldos y manual del sistema.

## Tecnologías

| Componente | Tecnología |
| --- | --- |
| Backend | Python 3.11 y Flask |
| Vistas | HTML, Jinja2, CSS, Bootstrap y JavaScript |
| Base de datos | MySQL 8 |
| Reportes | ReportLab y openpyxl |
| Servidor de desarrollo | Flask, puerto `5600` |

## Requisitos

- Python 3.11.
- MySQL 8.0.
- Git.
- Un navegador web actualizado.

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/Gmujicach/INVISAP.git
cd INVISAP
```

### 2. Crear y activar un entorno virtual

**Windows (PowerShell):**

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux o macOS:**

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar dependencias

```bash
python -m pip install --upgrade pip
pip install -r my-app/requirements.txt
```

### 4. Crear las bases de datos

El sistema utiliza dos bases de datos. Importa los scripts SQL incluidos en `my-app/BD/` con MySQL o una herramienta de administración:

```bash
mysql -u root -p < my-app/BD/invilara.sql
mysql -u root -p < my-app/BD/invilara_seguridad.sql
```

Los scripts crean las bases `invilara` e `invilara_seguridad`. Asegúrate de que el usuario de MySQL configurado para la aplicación tenga acceso a ambas.

### 5. Configurar el entorno

Copia `my-app/.env.example` como `my-app/.env` y configura los datos de conexión a MySQL, las claves de la aplicación y los datos de correo necesarios para la recuperación de contraseña. Por ejemplo:

```dotenv
DB_HOST=localhost
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=invilara
DB_NAME_SEGURIDAD=invilara_seguridad
DB_AUTH_PLUGIN=mysql_native_password

FLASK_SECRET_KEY=una_clave_secreta_propia
RECAPTCHA_SECRET_KEY=tu_clave_secreta_de_recaptcha
SESSION_COOKIE_SECURE=false
```

Genera valores propios para las claves y completa `MAIL_USERNAME` y `MAIL_PASSWORD` si vas a utilizar el envío de correos. No publiques credenciales reales ni secretos en el repositorio.

### 6. Iniciar la aplicación

```bash
cd my-app
python run.py
```

Abre [http://127.0.0.1:5600](http://127.0.0.1:5600) en tu navegador.

## Estructura del proyecto

```text
INVISAP/
├── my-app/
│   ├── BD/             # Esquemas SQL de INVILARA y seguridad
│   ├── conexion/       # Conexiones a MySQL
│   ├── controllers/    # Lógica de aplicación
│   ├── models/         # Acceso y operaciones de datos
│   ├── routers/        # Rutas y blueprints
│   ├── services/       # Servicios de la aplicación
│   ├── static/         # CSS, JavaScript, imágenes y video
│   ├── vista/          # Plantillas HTML de Jinja2
│   ├── app.py          # Configuración de Flask
│   ├── run.py          # Punto de entrada
│   └── requirements.txt
├── ARQUITECTURA_DEL_PROYECTO.md
├── CAPITULO_IV_INVISAP.md
├── Containerfile
├── compose.yaml
└── README.md
```

## Despliegue con contenedores

El repositorio incluye `compose.yaml` y `Containerfile`, pero antes de iniciar el sistema con contenedores hay que alinear la configuración de compilación con los archivos actuales: el `Containerfile` busca `requirements.txt` y una carpeta `wheels/` en la raíz, mientras que las dependencias están en `my-app/requirements.txt` y no hay una carpeta `wheels/` en la raíz. Además, cambia las credenciales de ejemplo de Compose antes de cualquier despliegue.

Hasta ajustar esos archivos, sigue los pasos de instalación local indicados arriba.

## Documentación adicional

- [Arquitectura del proyecto](ARQUITECTURA_DEL_PROYECTO.md)
- [Recomendaciones y evolución del sistema](CAPITULO_IV_INVISAP.md)

## Seguridad

- Usa claves y contraseñas propias; no reutilices valores de ejemplo.
- Mantén el archivo `.env` y las credenciales fuera del control de versiones.
- En producción, sirve la aplicación mediante HTTPS y configura las cookies seguras.
- Concede acceso a cada usuario según sus responsabilidades y permisos.
- Restringe el acceso a MySQL y a las herramientas de administración.

## Uso y contribuciones

Este sistema está orientado a los procesos institucionales de INVILARA. Para información sobre licencia, distribución o contribuciones, consulta con el equipo responsable del proyecto.
