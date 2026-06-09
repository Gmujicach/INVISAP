# Reporte Pedagógico de Fallas y Soluciones — Sistema INVISAP

Este documento está diseñado para ser comprendido por cualquier persona del equipo. 
* Si eres **nuevo en la programación**, lee las secciones de *"Explicación Sencilla"*.
* Si eres un **desarrollador experimentado**, encontrarás los detalles técnicos en la *"Explicación Técnica"*.

---

## 1. La Base de Datos no iniciaba correctamente
**¿Qué pasaba?** Al arrancar la aplicación, el sistema decía que las tablas (como "usuarios") no existían.

* **Explicación Sencilla:** Imagina que tienes una carpeta para guardar facturas. Le dices al sistema "Si la carpeta no existe, créala y mete estas 5 facturas de ejemplo". El problema es que la carpeta ya existía de una prueba anterior, pero estaba vacía. Como ya existía, el sistema nunca metió las facturas de ejemplo.
* **Explicación Técnica:** El contenedor de MySQL en Podman/Docker mapeó un volumen (`invisap_db_data`) que ya había sido creado. El script de inicialización (`initdb.d`) de MySQL solo se ejecuta si el directorio de datos está completamente vacío y virgen. Como el volumen tenía metadatos, se omitió el script `invilara.sql`.
* **Solución:** Importamos la base de datos de manera manual "inyectando" el código SQL directamente al cerebro del contenedor usando la terminal: `podman exec -i invisap_db mysql ... < invilara.sql`.

---

## 2. Imposibilidad de iniciar sesión y contraseñas truncadas
**¿Qué pasaba?** No se podía iniciar sesión. El sistema decía que la clave era incorrecta aunque estuviera bien escrita.

* **Explicación Sencilla:** Piensa en un formulario del gobierno donde el cuadro para tu nombre solo tiene 8 cuadritos. Si te llamas "Alejandro", la "o" se queda por fuera y te registran como "Alejandr". En nuestro sistema, la seguridad transforma las contraseñas en códigos secretos larguísimos (ej. `$2b$12$R9h...`), pero la base de datos solo permitía guardar 8 letras. Al guardar, el código se cortaba y se rompía. Además, la base de datos no entendía la letra "ñ" en la palabra "contraseña".
* **Explicación Técnica:** La columna `contraseña` estaba tipada como `VARCHAR(8)`. El algoritmo de Werkzeug usado en Flask (`generate_password_hash`) devuelve una cadena que supera los 100 caracteres. Además, nombrar una columna con caracteres no-ASCII ("ñ") causó un fallo de *Double Encoding*, impidiendo que las consultas en Python la referenciaran.
* **Solución:** 
  1. Se cambió el tipo de dato en SQL a `VARCHAR(255)`.
  2. Se renombró la columna eliminando la eñe: de `contraseña` a `contrasena`.
  3. Se actualizaron los modelos en Python (`model_usuarios.py`, `funciones_login.py`) para reflejar este nuevo nombre.

---

## 3. Error 500 al renderizar el Menú (Pantalla rota)
**¿Qué pasaba?** Al entrar al sistema, la pantalla mostraba un error "Internal Server Error" o "BuildError".

* **Explicación Sencilla:** La barra de menú lateral intentaba buscar la dirección de las distintas páginas del sistema preguntando "Oye, ¿dónde queda la página de Solicitudes?". Pero el sistema acababa de ser organizado en "departamentos" (Blueprints), y la barra de menú no especificaba a qué departamento preguntar.
* **Explicación Técnica:** La aplicación fue reestructurada modularmente utilizando *Blueprints* en Flask. Las plantillas HTML del menú (`menu_sidebar.html`) usaban `url_for('viewFormSolicitud')` buscando un endpoint global, el cual ya no existía porque había sido movido dentro del blueprint `home_bp`.
* **Solución:** Se actualizaron todas las rutas en el HTML añadiendo el prefijo del departamento correcto, quedando así: `url_for('home_bp.viewFormSolicitud')`.

---

## 4. Error interno al guardar una Nueva Solicitud
**¿Qué pasaba?** Al darle al botón "Registrar" en el formulario, fallaba el guardado.

* **Explicación Sencilla:** Imagina que mandas un paquete a la "Avenida Los Leones", pero en el mapa oficial de la ciudad, esa avenida fue registrada como "Avenida Leones". El repartidor (el código Python) se pierde y devuelve el paquete.
* **Explicación Técnica:** En el archivo `model_solicitudes.py`, la sentencia SQL `INSERT` estaba intentando guardar el ID del usuario en una columna que creía que se llamaba `solicitante_id_solicitante`. Pero al inspeccionar el esquema físico de la base de datos, el nombre real de la columna era `solicitante_id_comunidad`.
* **Solución:** Se reemplazó el nombre incorrecto por `solicitante_id_comunidad` en todos los queries (INSERT y SELECT) de los archivos controladores.

---

## 5. Página en Blanco tras guardar una solicitud exitosamente
**¿Qué pasaba?** La solicitud se guardaba bien, pero al final salía un error rojo diciendo `TemplateNotFound: solicitudes/lista_solicitudes.html`.

* **Explicación Sencilla:** Al guardar tu información, el código está programado para enviarte a la página donde se ven todas las solicitudes en forma de tabla. Sin embargo, el archivo físico que dibuja esa tabla literalmente no existía en los archivos del proyecto.
* **Explicación Técnica:** El controlador de Flask instruía un `render_template` hacia `lista_solicitudes.html`. Este archivo `.html` faltaba en el repositorio. Al no encontrarlo, Jinja2 lanza una excepción `TemplateNotFound`.
* **Solución:** Se programó el archivo faltante `lista_solicitudes.html` desde cero, creando la tabla dinámica, los colores para los estatus y un buscador en tiempo real.

---

## 6. No había cómo navegar a la Lista de Solicitudes
**¿Qué pasaba?** El usuario no tenía ningún botón para ver sus solicitudes guardadas.

* **Explicación Sencilla:** La página existía, pero se les olvidó ponerle un botón en el menú de la izquierda para que la gente pudiera hacer clic y entrar a verla.
* **Explicación Técnica:** El archivo `menu_sidebar.html` no tenía la etiqueta `<li>` ni el hipervínculo correspondiente al endpoint de la lista de solicitudes.
* **Solución:** Se editó el archivo base del menú, agregando el elemento `Lista de Solicitudes` debajo de `Registrar Solicitud`.

---

## 7. Ceguera ante la Base de Datos
**¿Qué pasaba?** Administrar la información de los usuarios y solicitudes era muy difícil porque no había una interfaz gráfica.

* **Explicación Sencilla:** Estábamos manejando los datos a ciegas usando comandos de texto puros en una pantalla negra de computadora de los años 80.
* **Explicación Técnica:** La arquitectura de contenedores Docker/Podman solo incluía la App de Flask y el motor de MySQL desnudo, sin gestores de bases de datos como DBeaver o phpMyAdmin.
* **Solución:** Se agregó el servicio oficial de `phpMyAdmin` en el archivo de orquestación `compose.yaml`. Ahora el equipo puede entrar por el puerto 8081 y administrar las bases de datos cómodamente desde el navegador.

---

## 8. TemplateNotFound al ver los detalles de una Solicitud
**¿Qué pasaba?** Al hacer clic en el botón azul "Ver" en la lista de solicitudes, daba error.

* **Explicación Sencilla:** Exactamente el mismo problema que en el paso 5. El archivo que pinta los detalles bonitos en pantalla no existía.
* **Explicación Técnica:** El endpoint `/detalles-solicitud/<id>` intentaba cargar la plantilla `detalles_solicitud.html`, la cual fue omitida en el desarrollo inicial de las vistas del sistema.
* **Solución:** Se desarrolló desde cero esta vista integrando *Bootstrap Cards*, organizando la información en columnas legibles (Información del Solicitante, Ubicación y Problemática).
