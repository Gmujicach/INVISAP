# 🏛️ Arquitectura del Proyecto INVISAP

Este documento detalla todas las tecnologías, librerías y estructuras utilizadas para construir y desplegar el sistema INVISAP. Está redactado para que tanto el equipo de gestión como los ingenieros de desarrollo puedan comprender cómo encaja cada pieza del rompecabezas.

---

## 1. Visión General y Orquestación (El Entorno)

El sistema completo no corre como un solo programa en la computadora, sino que está dividido en piezas aisladas llamadas **Contenedores** mediante una herramienta llamada **Podman Compose** (100% compatible con Docker).

* **Explicación Sencilla:** Imagina que el sistema es un restaurante. En lugar de tener a una sola persona haciendo todo, contratamos a 3 especialistas encerrados en sus propias cocinas: uno hace la comida (La Aplicación), otro guarda el dinero y los registros (La Base de Datos), y otro es el contador que nos deja ver los números (phpMyAdmin). Trabajan juntos, pero no se mezclan.
* **Explicación Técnica:** El archivo `compose.yaml` levanta 3 servicios interconectados mediante una red interna virtual:
  1. **`app`**: Contenedor basado en `python:3.11-slim` donde corre el código de INVISAP (Expuesto en el puerto 5600).
  2. **`db`**: Contenedor oficial de `mysql:8.0` que gestiona el almacenamiento (Expuesto en 3307).
  3. **`phpmyadmin`**: Contenedor para administración gráfica de la base de datos (Expuesto en 8081).

---

## 2. El Cerebro Backend (Python y Flask)

El núcleo del sistema está escrito en Python usando el micro-framework Flask.

* **Explicación Sencilla:** Flask es como el jefe de operaciones. Recibe las peticiones del usuario (por ejemplo, "¡Quiero registrar una solicitud!"), le pregunta a la base de datos si todo está en orden, y luego le devuelve al usuario la pantalla HTML con su solicitud guardada.
* **Explicación Técnica:** Se eligió Flask (`Flask==2.3.2`) por su ligereza. La aplicación no es monolítica, sino que utiliza el patrón arquitectónico de **Blueprints** para dividir las rutas del sistema en submódulos (ej. `router_home.py`, `router_login.py`), permitiendo que el código sea escalable. Además, se separa la capa de acceso a datos (Modelos/Controladores) de la capa de presentación (Routers).

---

## 3. Librerías y Dependencias (Las Herramientas del Código)

El proyecto depende de ciertas "herramientas" prefabricadas listadas en el archivo `requirements.txt`. Para asegurar que el sistema funcione en lugares sin internet (despliegue offline), estas dependencias se instalan utilizando paquetes pre-descargados (*wheels*).

| Librería | ¿Para qué sirve? (Sencillo) | Detalles (Técnico) |
| :--- | :--- | :--- |
| **Flask (2.3.2)** | El motor del sitio web. | Micro-framework WSGI utilizado para el enrutamiento y ciclo de vida HTTP. |
| **Werkzeug (2.3.6)** | El guardia de seguridad de claves. | Librería criptográfica que genera y verifica los *hashes* (`generate_password_hash`) de las contraseñas para no guardarlas en texto plano. |
| **mysql-connector-python (8.1.0)** | El puente de comunicación. | El driver (conector) oficial de Oracle que permite a Python enviar sentencias SQL a la base de datos MySQL. |
| **Jinja2 (3.1.2)** | El pintor de páginas. | Motor de plantillas que inyecta los datos dinámicos de Python dentro del HTML mediante llaves `{{ dato }}`. |
| **openpyxl (3.1.2)** | El exportador de tablas. | Librería para leer y escribir archivos Excel (`.xlsx`), usada en el módulo de reportes. |
| **itsdangerous** | El creador de galletas (cookies) seguras. | Cifra la sesión del usuario para que nadie pueda falsificar su identidad. |

---

## 4. Base de Datos (El Archivo Central)

* **Explicación Sencilla:** Toda la información del Instituto (usuarios, solicitudes, mortadelas, comunidades) se guarda en cajones muy ordenados que se llaman "tablas". Usamos el gestor de bases de datos de MySQL para esto.
* **Explicación Técnica:** MySQL 8.0 almacena el esquema `invilara`. Se han aplicado correcciones y normalizaciones clave, como extender los campos criptográficos a `VARCHAR(255)` y corregir el *Double Encoding* eliminando caracteres especiales de los nombres de columnas (ej. `contrasena`). Los datos persisten en el disco de la computadora host mediante el volumen Docker `invisap_db_data`, asegurando que la información no se pierda al reiniciar el servidor.

---

## 5. El Frontend (La Interfaz del Usuario)

El sistema no utiliza tecnologías pesadas de un solo archivo (como React o Angular), sino que se apoya en renderizado tradicional potenciado con código ligero del lado del cliente.

* **Explicación Sencilla:** La cara que ve el usuario está hecha con HTML y el diseño bonito lo pone un sistema llamado Bootstrap. Para las cosas inteligentes, como cargar parroquias cuando eliges un municipio, le enseñamos a la página un poco de lenguaje "JavaScript" para que lo haga sin tener que molestar a la base de datos de nuevo.
* **Explicación Técnica:** 
  * **HTML/Jinja2:** Se utiliza un sistema de herencia de plantillas (`{% extends 'base_cpanel.html' %}`) para no repetir la barra lateral ni los encabezados en cada vista.
  * **CSS/Bootstrap:** Se utiliza Bootstrap 5 (clases como `card`, `shadow-sm`, `row`, `col`) para el diseño adaptativo (*responsive design*).
  * **Vanilla JS:** Los scripts del cliente (como la jerarquía dinámica de `form_solicitud.html`) están codificados en JavaScript puro, cargando diccionarios JSON en la memoria del navegador y modificando el DOM (Document Object Model) directamente a través del evento `onchange`.

---

## 6. Estructura de Directorios

Así están organizadas las carpetas del proyecto:

* `/BD/`: Contiene el respaldo inicial de la base de datos (`invilara.sql`).
* `/routers/`: Archivos `.py` que atrapan las URLs (Blueprints como `/empleados`, `/login`).
* `/controllers/`: Funciones en Python con la lógica de negocio y seguridad.
* `/models/`: Funciones de Python que hacen el trabajo sucio escribiendo sentencias `SELECT`, `INSERT` y `UPDATE` hacia la base de datos.
* `/static/`: Imágenes (como el logo oficial), CSS y JavaScript descargados.
* `/vista/`: Las plantillas HTML para dibujar las páginas.
* `/wheels/`: Las librerías de Python pre-empaquetadas para el despliegue militar/offline.
* `Containerfile` y `compose.yaml`: Los planos de construcción de los servidores virtuales.
