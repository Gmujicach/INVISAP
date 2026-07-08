"""
Genera el Manual del Sistema de INVILARA en formato PDF.
Uso:  python generar_manual.py
Salida: static/manuals/Manual_del_Sistema_INVILARA.pdf
"""
import os
import sys

# Poner lib_pdf (fpdf2 + Pillow) en el path de importacion
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, "lib_pdf"))

from fpdf import FPDF

FONT_REG = r"C:\Windows\Fonts\arial.ttf"
FONT_BOLD = r"C:\Windows\Fonts\arialbd.ttf"

VERDE = (8, 122, 36)      # #087A24
AMARILLO = (255, 193, 7)  # #FFC107
NEGRO = (33, 37, 41)      # #212529
GRIS = (108, 122, 141)    # #6C7A8D
BLANCO = (255, 255, 255)


class ManualINVILARA(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Arial", "B", 9)
        self.set_text_color(*VERDE)
        self.cell(0, 8, "Manual del Sistema - INVILARA", align="L")
        self.set_font("Arial", "", 9)
        self.set_text_color(*GRIS)
        self.cell(0, 8, "Comunidad INVILARA - Barquisimeto, Edo. Lara", align="R")
        self.ln(10)
        self.set_draw_color(*AMARILLO)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-13)
        self.set_font("Arial", "", 8)
        self.set_text_color(*GRIS)
        self.cell(0, 8, "Pagina %d" % self.page_no(), align="C")

    def titulo_seccion(self, numero, titulo):
        self.ln(2)
        self.set_fill_color(*VERDE)
        self.set_text_color(*BLANCO)
        self.set_font("Arial", "B", 13)
        self.cell(0, 9, "  %s. %s" % (numero, titulo), new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(3)
        self.set_text_color(*NEGRO)

    def parrafo(self, texto):
        self.set_font("Arial", "", 11)
        self.set_text_color(*NEGRO)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, texto, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def subitem(self, texto):
        self.set_font("Arial", "B", 11)
        self.set_text_color(*VERDE)
        self.set_x(self.l_margin)
        self.multi_cell(0, 6, texto, new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*NEGRO)

    def lista(self, items):
        self.set_font("Arial", "", 11)
        self.set_text_color(*NEGRO)
        for it in items:
            self.set_x(self.l_margin)
            self.cell(5, 6, "-")
            self.multi_cell(0, 6, it, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)


def portada(pdf):
    pdf.add_page()
    pdf.ln(38)
    pdf.set_fill_color(*VERDE)
    pdf.rect(0, pdf.get_y(), pdf.w, 46, style="F")
    pdf.set_y(pdf.get_y() + 9)
    pdf.set_font("Arial", "B", 30)
    pdf.set_text_color(*BLANCO)
    pdf.cell(0, 14, "MANUAL DEL SISTEMA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "INVILARA", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(20)
    pdf.set_text_color(*NEGRO)
    pdf.set_font("Arial", "", 13)
    pdf.cell(0, 8, "Gestion Comunitaria de Solicitudes, Obras e Informes de Avance", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(*GRIS)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, "Proyecto Socio-Tecnologico III - Barquisimeto, Estado Lara, Venezuela", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(24)
    pdf.set_draw_color(*AMARILLO)
    pdf.set_line_width(1.2)
    pdf.line(55, pdf.get_y(), pdf.w - 55, pdf.get_y())
    pdf.ln(8)
    pdf.set_text_color(*NEGRO)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Version 1.0 - Documento de Usuario Interactivo", align="C", new_x="LMARGIN", new_y="NEXT")


def main():
    pdf = ManualINVILARA(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_font("Arial", "", FONT_REG)
    pdf.add_font("Arial", "B", FONT_BOLD)
    pdf.set_title("Manual del Sistema INVILARA")

    portada(pdf)

    # Tabla de contenido
    pdf.add_page()
    pdf.titulo_seccion("", "Indice de Contenidos")
    pdf.lista([
        "1. Introduccion y Objetivo del Sistema",
        "2. Acceso e Inicio de Sesion (Modulo de Seguridad)",
        "3. Navegacion y Menu Lateral",
        "4. Gestion de Usuarios, Roles y Perfiles",
        "5. Modulo de Solicitudes",
        "6. Modulo de Contratacion",
        "7. Gravedad y Prioridad de Obras",
        "8. Empleados y Empresas",
        "9. Maquinaria y Evidencias",
        "10. Proyectos, Obras e Inspecciones",
        "11. Informe de Avance de Obra",
        "12. Publicaciones",
        "13. Respaldos y Restauracion (Mantenimiento)",
        "14. Bitacora del Sistema",
        "15. Reportes (Excel, PDF y Estadisticos)",
        "16. Recomendaciones de Uso y Soporte",
    ])

    # 1. Introduccion
    pdf.add_page()
    pdf.titulo_seccion("1", "Introduccion y Objetivo del Sistema")
    pdf.parrafo(
        "El Sistema INVILARA es una aplicacion web desarrollada para la comunidad INVILARA de "
        "Barquisimeto, Estado Lara (Venezuela). Su objetivo es gestionar de forma integral las "
        "solicitudes ciudadanas, las obras publicas, las inspecciones tecnicas, los informes de "
        "avance y la publicacion de informacion institucional, apoyando la toma de decisiones y la "
        "transparencia de la gestion comunitaria."
    )
    pdf.parrafo(
        "El sistema sigue una arquitectura de software basada en el patron MVC (Modelo - Vista - "
        "Controlador) e implementa buenas practicas de Programacion Orientada a Objetos, validacion "
        "de datos en el servidor y seguridad en el acceso mediante autenticacion, cifrado de "
        "contrasenas y bitacora de eventos."
    )
    pdf.subitem("Principales beneficios:")
    pdf.lista([
        "Centraliza la atencion de solicitudes ciudadanas por tipo y estatus.",
        "Permite el seguimiento del ciclo de vida de obras (semaforo verde/amarillo/rojo).",
        "Genera reportes estadisticos para la toma de decisiones.",
        "Mantiene una auditoria (bitacora) de todas las acciones criticas.",
        "Cuenta con respaldo y restauracion de la base de datos.",
    ])

    # 2. Acceso
    pdf.add_page()
    pdf.titulo_seccion("2", "Acceso e Inicio de Sesion")
    pdf.parrafo(
        "El Modulo de Seguridad protege el acceso al sistema. Para ingresar, el usuario debe "
        "dirigirse a la pantalla de inicio de sesion e introducir su correo y contrasena."
    )
    pdf.subitem("Autenticacion de dos factores (OTP):")
    pdf.parrafo(
        "Por seguridad, despues de validar las credenciales se solicita un codigo OTP de 4 digitos "
        "enviado al correo electronico registrado. El codigo tiene un tiempo de expiracion y un "
        "numero limitado de intentos."
    )
    pdf.subitem("Recuperacion de clave:")
    pdf.parrafo(
        "Si el usuario olvida su contrasena, dispone de la opcion 'Olvide mi contrasena' que envia "
        "un enlace de restablecimiento seguro a su correo. Las contrasenas se almacenan con "
        "cifrado (PBKDF2-SHA256) y nunca se guardan en texto plano."
    )
    pdf.subitem("Captcha / Verificacion:")
    pdf.parrafo(
        "El formulario de acceso incluye verificacion para detectar que no es un robot, protegiendo "
        "el sistema contra accesos automaticos no deseados."
    )

    # 3. Navegacion
    pdf.add_page()
    pdf.titulo_seccion("3", "Navegacion y Menu Lateral")
    pdf.parrafo(
        "Una vez autenticado, el usuario accede al panel principal. El menu lateral (sidebar) agrupa "
        "los modulos por funcionalidad y permite una navegacion intuitiva. El sistema es responsive y "
        "cuenta con modo oscuro/claro para adaptarse a las preferencias del usuario."
    )
    pdf.subitem("Recomendaciones de navegacion:")
    pdf.lista([
        "Use el alternador de tema (sol/luna) para activar el modo oscuro.",
        "Los submenus se despliegan al hacer clic en un modulo con flecha.",
        "El modulo actual queda resaltado en el menu.",
        "La opcion 'Manual del Sistema' abre este documento en una nueva ventana.",
    ])

    # 4. Usuarios
    pdf.add_page()
    pdf.titulo_seccion("4", "Gestion de Usuarios, Roles y Perfiles")
    pdf.parrafo(
        "El sistema maneja perfiles de usuario con roles jerarquicos (Super Usuario, Administrador, "
        "Presidente, Gerente, Recepcionista, Asistente, entre otros). Cada rol determina los permisos "
        "disponibles en los distintos modulos."
    )
    pdf.subitem("Funciones disponibles:")
    pdf.lista([
        "Registrar nuevos usuarios asignando rol y estado (activo/inactivo).",
        "Listar y buscar usuarios existentes.",
        "Editar la informacion y el rol de un usuario.",
        "Activar o desactivar usuarios (borrado logico, sin perder trazabilidad).",
        "Gestionar la foto de perfil (avatar) desde su cuenta.",
    ])
    pdf.parrafo(
        "El cambio de rol permite transferir responsabilidades ante ascensos o reasignaciones de "
        "departamento, manteniendo el historial de acciones en la bitacora."
    )

    # 5. Solicitudes
    pdf.add_page()
    pdf.titulo_seccion("5", "Modulo de Solicitudes")
    pdf.parrafo(
        "Permite registrar las solicitudes de la ciudadania (Particular, Comunidad o Institucion), "
        "clasificarlas por problematica y darles seguimiento."
    )
    pdf.subitem("Operaciones:")
    pdf.lista([
        "Registrar Solicitud: tipo, estatus, problematica y solicitante.",
        "Lista de Solicitudes: busqueda, filtros y paginacion.",
        "Ver detalles y editar una solicitud.",
        "Borrado logico (desactivacion) manteniendo el registro.",
        "Al vincularse una primera inspeccion, el estatus pasa a 'En Proceso' automaticamente.",
    ])
    pdf.parrafo(
        "Todos los campos cuentan con validaciones en el servidor (expresiones regulares, longitud y "
        "formato) y con textos guia (placeholders) para facilitar el llenado."
    )

    # 6. Contratacion
    pdf.add_page()
    pdf.titulo_seccion("6", "Modulo de Contratacion")
    pdf.parrafo(
        "Gestiona los procedimientos de contratacion de obras: empresa ganadora, numero de contrato, "
        "monto, fechas, tipo, modalidad, objeto y observaciones."
    )
    pdf.subitem("Operaciones:")
    pdf.lista([
        "Registrar contrataciones vinculadas a una empresa (catologo).",
        "Listar y editar contrataciones.",
        "Desactivar (borrado logico) contrataciones.",
    ])

    # 7. Gravedad y Prioridad
    pdf.add_page()
    pdf.titulo_seccion("7", "Gravedad y Prioridad de Obras")
    pdf.parrafo(
        "Estos modulos parametrizan el nivel de gravedad/critcidad de una obra y el rango de prioridad "
        "de atencion. La prioridad puede ajustarse indicando responsable y justificacion del cambio."
    )

    # 8. Empleados y Empresas
    pdf.add_page()
    pdf.titulo_seccion("8", "Empleados y Empresas")
    pdf.parrafo(
        "El modulo de Empleados registra el personal (nombre, cargo, fecha de ingreso, gerencia) y lo "
        "vincula a una persona. El modulo de Empresas administra el catologo de contratistas (RIF, "
        "nombre, telefono, domicilio fiscal)."
    )
    pdf.subitem("Nota:")
    pdf.parrafo(
        "Al crear una Inspeccion o Informe, el campo 'Inspector' se obtiene de los empleados con rol "
        "de inspector, garantizando integridad referencial."
    )

    # 9. Maquinaria y Evidencias
    pdf.add_page()
    pdf.titulo_seccion("9", "Maquinaria y Evidencias")
    pdf.parrafo(
        "Maquinaria: catologo de equipos (nombre, tipo) que pueden asignarse a proyectos. Evidencias: "
        "registro fotografico de obras en las etapas antes, durante y despues."
    )
    pdf.subitem("Recomendaciones de almacenamiento:")
    pdf.lista([
        "En la base de datos solo se guarda la URL de la imagen, no el archivo.",
        "Limite de 3 a 5 fotos por informe para no sobrecargar el servidor.",
        "Las imagenes se comprimen para reducir el tamano sin perder calidad.",
    ])

    # 10. Proyectos Obras Inspecciones
    pdf.add_page()
    pdf.titulo_seccion("10", "Proyectos, Obras e Inspecciones")
    pdf.parrafo(
        "Proyectos: planifica y asigna maquinaria y solicitudes a codigos de proyecto. Obras: registra "
        "las obras publicas con su semaforo, contratacion y proyecto asociado. Inspecciones: registra "
        "la inspeccion tecnica vinculada a una obra y su evidencia."
    )
    pdf.subitem("Ciclo de vida (Semaforo):")
    pdf.lista([
        "Verde: obra activa / culminada al alcanzar el 100% de avance.",
        "Amarillo: en ejecucion / advertencia.",
        "Rojo: paralizada por detencion del avance.",
    ])

    # 11. Informe Avance
    pdf.add_page()
    pdf.titulo_seccion("11", "Informe de Avance de Obra")
    pdf.parrafo(
        "Registra el avance porcentual de una obra, su estatus, poblacion beneficiada, tipo de informe "
        "y evidencias (antes, durante, despues). Al actualizarse el porcentaje, el sistema ajusta el "
        "semaforo de la obra automaticamente mediante reglas de negocio."
    )

    # 12. Publicaciones
    pdf.add_page()
    pdf.titulo_seccion("12", "Publicaciones")
    pdf.parrafo(
        "Permite crear y listar publicaciones institucionales vinculadas a un informe de avance, con "
        "titulo, responsable, tipo y cuerpo. Incluye vista de detalles y borrado logico."
    )

    # 13. Respaldos
    pdf.add_page()
    pdf.titulo_seccion("13", "Respaldos y Restauracion (Mantenimiento)")
    pdf.parrafo(
        "El Modulo de Mantenimiento genera respaldos de la base de datos de forma automatica (la fecha "
        "se captura en el instante de la accion) y permite restaurar un respaldo previo. Los respaldos "
        "se listan con su tamano y descripcion."
    )

    # 14. Bitacora
    pdf.add_page()
    pdf.titulo_seccion("14", "Bitacora del Sistema")
    pdf.parrafo(
        "La bitacora registra automaticamente los eventos criticos (inicio de sesion, creacion, "
        "edicion, eliminacion, consulta) con usuario, modulo, accion y fecha/hora. Permite filtrar por "
        "usuario, modulo y accion, y cuenta con paginacion para su analisis."
    )

    # 15. Reportes
    pdf.add_page()
    pdf.titulo_seccion("15", "Reportes (Excel, PDF y Estadisticos)")
    pdf.parrafo(
        "El sistema genera reportes para la toma de decisiones en distintos formatos:"
    )
    pdf.lista([
        "Reportes Excel: exportacion de datos por modulo.",
        "Reportes PDF: documentos consolidados para impresion y archivo.",
        "Reportes Estadisticos: graficos de solicitudes por tipo, estatus y parroquia.",
    ])

    # 16. Recomendaciones
    pdf.add_page()
    pdf.titulo_seccion("16", "Recomendaciones de Uso y Soporte")
    pdf.lista([
        "Cierre sesion al terminar, especialmente en equipos compartidos.",
        "Revise los placeholders de cada formulario antes de llenarlo.",
        "Use los filtros y la busqueda para trabajar con grandes volumenes de datos.",
        "Consulte la bitacora para auditoria de eventos.",
        "Realice respaldos periodicos de la base de datos.",
        "Ante dudas, contacte al administrador del sistema.",
    ])
    pdf.ln(4)
    pdf.set_font("Arial", "B", 11)
    pdf.set_text_color(*VERDE)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 6, "INVILARA - Gestion comunitaria transparente y eficiente. Barquisimeto, Estado Lara, Venezuela.", new_x="LMARGIN", new_y="NEXT")

    out_dir = os.path.join(BASE_DIR, "static", "manuals")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "Manual_del_Sistema_INVILARA.pdf")
    pdf.output(out_path)
    print("PDF generado en:", out_path)


if __name__ == "__main__":
    main()
