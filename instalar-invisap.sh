#!/usr/bin/env bash

# ============================================================
# INVISAP - INSTALADOR INTERACTIVO (MODO LOCAL / OFFLINE)
# Zorin OS 18.x / Ubuntu 24.04 LTS
# ============================================================
#
# Instala:
#   - Python 3 del sistema
#   - Entorno virtual Python
#   - requirements.txt
#   - MySQL Community Server 9.4.0 (Desde archivo local)
#   - Base de datos invilara
#   - Base de datos invilara_seguridad
#   - Usuario MySQL configurable
#   - Gunicorn
#   - Servicio systemd para INVISAP
#
# NO instala Nginx.
# NO abre puertos.
# MySQL escucha únicamente en localhost.
# Gunicorn escucha únicamente en localhost.
#
# ============================================================

set -Eeuo pipefail
set +H

# ============================================================
# COLORES
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================
# CONFIGURACIÓN GENERAL
# ============================================================

REPO_URL="https://github.com/Gmujicach/INVISAP.git"

INSTALL_ROOT=""
APP_ROOT=""
APP_DIR=""
VENV_DIR=""

APP_SERVICE="invisap"

# ============================================================
# MYSQL
# ============================================================

MYSQL_VERSION="9.4.0"

MYSQL_BASE="/usr/local/mysql"
MYSQL_INSTALL_DIR="/usr/local/mysql-${MYSQL_VERSION}"

MYSQL_DATA="/var/lib/mysql"

MYSQL_SYSTEM_USER="mysql"
MYSQL_SYSTEM_GROUP="mysql"

MYSQL_PORT="3306"

# ============================================================
# APLICACIÓN
# ============================================================

APP_SYSTEM_NAME="INVISAP"
APP_PORT="5600"

# ============================================================
# BASES DE DATOS
# ============================================================

DB_MAIN="invilara"
DB_SECURITY="invilara_seguridad"

DB_USER=""
DB_PASSWORD=""
MYSQL_ROOT_PASSWORD=""

# ============================================================
# CORREO
# ============================================================

MAIL_CONFIGURED="no"
MAIL_USERNAME=""
MAIL_PASSWORD=""

# ============================================================
# PYTHON
# ============================================================

PYTHON_BIN=""

# ============================================================
# FUNCIONES
# ============================================================

msg() {
    echo -e "${GREEN}[OK]${NC} $1"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

fail() {
    echo -e "${RED}[ERROR]${NC} $1"
}

die() {
    fail "$1"
    exit 1
}

pause_installation() {
    echo
    read -rp "Presiona ENTER para continuar..."
}

error_handler() {

    local code=$?

    echo
    fail "La instalación terminó con un error."
    echo
    echo "Código de error: ${code}"
    echo
    echo "Si el problema está relacionado con INVISAP:"
    echo
    echo "  sudo systemctl status invisap"
    echo
    echo "  sudo journalctl -u invisap -n 100 --no-pager"
    echo
    echo "Si el problema está relacionado con MySQL:"
    echo
    echo "  sudo systemctl status mysql-invisap"
    echo
    echo "  sudo journalctl -u mysql-invisap -n 100 --no-pager"
    echo

    exit "$code"
}

trap error_handler ERR

# ============================================================
# COMPROBAR ROOT
# ============================================================

check_root() {

    if [[ "$EUID" -ne 0 ]]; then

        die "Este script debe ejecutarse con sudo."

    fi

}

# ============================================================
# COMPROBAR ARQUITECTURA
# ============================================================

check_architecture() {

    local architecture

    architecture="$(uname -m)"

    if [[ "$architecture" != "x86_64" ]]; then

        die "Este instalador requiere arquitectura x86_64."

    fi

    msg "Arquitectura compatible: ${architecture}"

}

# ============================================================
# COMPROBAR ZORIN OS
# ============================================================

check_os() {

    if [[ ! -f /etc/os-release ]]; then

        die "No se encontró /etc/os-release."

    fi

    # shellcheck disable=SC1091
    source /etc/os-release

    echo
    echo "Sistema operativo detectado:"
    echo
    echo "  ${PRETTY_NAME:-desconocido}"
    echo

    if [[ "${ID:-}" != "zorin" ]]; then

        warn "El sistema detectado no es Zorin OS."

        read -rp \
            "¿Deseas continuar de todas formas? [s/N]: " answer

        if [[ ! "$answer" =~ ^[sS]$ ]]; then
            exit 0
        fi

    fi

    if [[ "${VERSION_ID:-}" != "18" ]]; then

        warn "Este instalador fue diseñado para Zorin OS 18.x."

        read -rp \
            "¿Deseas continuar? [s/N]: " answer

        if [[ ! "$answer" =~ ^[sS]$ ]]; then
            exit 0
        fi

    fi

    msg "Sistema operativo aceptado."

}

# ============================================================
# COMPROBAR MYSQL EXISTENTE
# ============================================================

check_existing_mysql() {

    if command -v mysqld >/dev/null 2>&1; then

        local version

        version="$(mysqld --version || true)"

        warn "Se encontró una instalación existente de MySQL:"
        echo
        echo "  ${version}"
        echo

        if systemctl list-unit-files 2>/dev/null |
            grep -q '^mysql.service'; then

            warn "También existe un servicio mysql.service."

            die \
                "No se modificará una instalación MySQL existente automáticamente."

        fi

    fi

}

# ============================================================
# VALIDACIONES DE NOMBRES
# ============================================================

valid_mysql_name() {

    [[ "$1" =~ ^[a-zA-Z0-9_]+$ ]]

}

# ============================================================
# CONFIGURACIÓN INTERACTIVA
# ============================================================

ask_configuration() {

    clear

    echo -e "${CYAN}"
    echo "============================================================"
    echo "          CONFIGURACIÓN DE INVISAP"
    echo "============================================================"
    echo -e "${NC}"

    echo
    echo "Introduce los parámetros que utilizará el sistema."
    echo

    # --------------------------------------------------------
    # RUTA DE INSTALACIÓN
    # --------------------------------------------------------

    read -rp \
        "Ruta base de instalación [/var/www]: " value

    INSTALL_ROOT="${value:-/var/www}"
    APP_ROOT="${INSTALL_ROOT}/invisap"
    APP_DIR="${APP_ROOT}/my-app"
    VENV_DIR="${APP_DIR}/venv"

    # --------------------------------------------------------
    # NOMBRE DEL SISTEMA
    # --------------------------------------------------------

    read -rp \
        "Nombre del sistema [INVISAP]: " value

    APP_SYSTEM_NAME="${value:-INVISAP}"

    # --------------------------------------------------------
    # USUARIO MYSQL
    # --------------------------------------------------------

    while true; do

        read -rp \
            "Usuario MySQL [invisap]: " value

        DB_USER="${value:-invisap}"

        if valid_mysql_name "$DB_USER"; then
            break
        fi

        warn \
            "El usuario solamente puede contener letras, números y _."

    done

    # --------------------------------------------------------
    # CONTRASEÑA MYSQL
    # --------------------------------------------------------

    while true; do

        read -rsp \
            "Contraseña del usuario MySQL: " DB_PASSWORD

        echo

        read -rsp \
            "Repite la contraseña: " DB_PASSWORD_CONFIRM

        echo

        if [[ -z "$DB_PASSWORD" ]]; then

            warn "La contraseña no puede estar vacía."

        elif [[ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]]; then

            warn "Las contraseñas no coinciden."

        else

            break

        fi

    done

    # --------------------------------------------------------
    # BASE DE DATOS PRINCIPAL
    # --------------------------------------------------------

    while true; do

        read -rp \
            "Base de datos principal [invilara]: " value

        DB_MAIN="${value:-invilara}"

        if valid_mysql_name "$DB_MAIN"; then
            break
        fi

        warn \
            "El nombre de la BD solamente puede contener letras, números y _."

    done

    # --------------------------------------------------------
    # BASE DE DATOS DE SEGURIDAD
    # --------------------------------------------------------

    while true; do

        read -rp \
            "Base de datos de seguridad [invilara_seguridad]: " value

        DB_SECURITY="${value:-invilara_seguridad}"

        if valid_mysql_name "$DB_SECURITY"; then
            break
        fi

        warn \
            "El nombre de la BD solamente puede contener letras, números y _."

    done

    # --------------------------------------------------------
    # PUERTO
    # --------------------------------------------------------

    while true; do

        read -rp \
            "Puerto local de Flask/Gunicorn [5600]: " value

        APP_PORT="${value:-5600}"

        if [[ "$APP_PORT" =~ ^[0-9]+$ ]] &&
            (( APP_PORT >= 1024 && APP_PORT <= 65535 )); then

            break

        fi

        warn \
            "Introduce un puerto entre 1024 y 65535."

    done

    # --------------------------------------------------------
    # CORREO
    # --------------------------------------------------------

    echo
    echo "Configuración opcional de correo."
    echo
    echo "Esto se utiliza para funciones que necesiten enviar"
    echo "correos desde INVISAP."
    echo

    read -rp \
        "¿Deseas configurar el correo ahora? [s/N]: " answer

    if [[ "$answer" =~ ^[sS]$ ]]; then

        MAIL_CONFIGURED="yes"

        while [[ -z "$MAIL_USERNAME" ]]; do

            read -rp \
                "Correo Gmail: " MAIL_USERNAME

            if [[ -z "$MAIL_USERNAME" ]]; then
                warn "El correo no puede estar vacío."
            fi

        done

        read -rsp \
            "Contraseña de aplicación Gmail: " MAIL_PASSWORD

        echo

        [[ -n "$MAIL_PASSWORD" ]] || \
            die "La contraseña de aplicación no puede estar vacía."

    fi

    # --------------------------------------------------------
    # RESUMEN
    # --------------------------------------------------------

    echo
    echo -e "${CYAN}"
    echo "============================================================"
    echo "                 RESUMEN DE CONFIGURACIÓN"
    echo "============================================================"
    echo -e "${NC}"

    echo
    echo "Sistema:"
    echo "  Nombre               : ${APP_SYSTEM_NAME}"
    echo "  Directorio           : ${APP_DIR}"

    echo
    echo "MySQL:"
    echo "  Versión              : ${MYSQL_VERSION}"
    echo "  Usuario              : ${DB_USER}"
    echo "  BD principal         : ${DB_MAIN}"
    echo "  BD seguridad         : ${DB_SECURITY}"
    echo "  Puerto               : ${MYSQL_PORT}"

    echo
    echo "Aplicación:"
    echo "  Puerto local         : ${APP_PORT}"

    echo
    echo "Correo:"
    echo "  Configurado          : ${MAIL_CONFIGURED}"

    echo

    read -rp \
        "¿La configuración es correcta? [S/n]: " answer

    if [[ "$answer" =~ ^[nN]$ ]]; then

        ask_configuration

    fi

}

# ============================================================
# INSTALAR PAQUETES
# ============================================================

install_system_packages() {

    info "Actualizando repositorios APT..."

    apt-get update

    info "Instalando herramientas necesarias..."

    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git \
        curl \
        wget \
        ca-certificates \
        gnupg \
        xz-utils \
        build-essential \
        python3 \
        python3-venv \
        python3-dev \
        python3-pip \
        libaio1t64 \
        libncurses6 \
        libnuma1 \
        libssl3t64 \
        pkg-config \
        openssl

    # Crear enlace simbólico de compatibilidad para libaio.so.1 en Ubuntu 24.04 / Zorin OS 18
    if [[ -f /usr/lib/x86_64-linux-gnu/libaio.so.1t64 ]] && [[ ! -f /usr/lib/x86_64-linux-gnu/libaio.so.1 ]]; then
        ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
    fi

    PYTHON_BIN="$(command -v python3)"

    msg \
        "Python detectado: $($PYTHON_BIN --version)"

}

# ============================================================
# INSTALAR MYSQL 9.4.0 (DESDE ARCHIVO LOCAL)
# ============================================================

install_mysql() {

    info "Instalando MySQL Community Server ${MYSQL_VERSION} (modo local)..."

    # Si el servicio no está activo, limpiar restos anteriores para garantizar instalación limpia
    if ! systemctl is-active --quiet mysql-invisap.service 2>/dev/null; then
        rm -rf "$MYSQL_BASE" "$MYSQL_INSTALL_DIR" "$MYSQL_DATA"
    fi

    if [[ -x "${MYSQL_BASE}/bin/mysqld" ]]; then

        local current_version

        current_version="$(
            "${MYSQL_BASE}/bin/mysqld" --version || true
        )"

        if grep -q "${MYSQL_VERSION}" <<< "$current_version"; then

            msg "MySQL ${MYSQL_VERSION} ya está instalado."
            systemctl start mysql-invisap.service || true
            return

        fi

        die \
            "Existe ${MYSQL_BASE}, pero no corresponde a MySQL ${MYSQL_VERSION}."

    fi

    check_existing_mysql

    # Buscar el archivo .tar.xz de MySQL localmente (en la carpeta del script o en la ruta actual)
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    local archive_name="mysql-${MYSQL_VERSION}-linux-glibc2.28-x86_64.tar.xz"
    local archive=""

    if [[ -f "${script_dir}/${archive_name}" ]]; then
        archive="${script_dir}/${archive_name}"
    elif [[ -f "./${archive_name}" ]]; then
        archive="./${archive_name}"
    else
        die "No se encontró el archivo local '${archive_name}' en la carpeta del script (${script_dir}) ni en el directorio actual."
    fi

    info "Usando archivo local de MySQL encontrado en: ${archive}"

    info "Extrayendo MySQL..."

    rm -rf "$MYSQL_INSTALL_DIR"

    tar \
        -xJf "$archive" \
        -C /usr/local

    # Desactivar temporalmente pipefail para evitar errores de tubería al listar el tar
    local extracted_folder
    set +o pipefail
    extracted_folder="$(tar -tf "$archive" | head -1 | cut -f1 -d"/")"
    set -o pipefail

    if [[ -n "$extracted_folder" ]] && [[ -d "/usr/local/${extracted_folder}" ]] && [[ "/usr/local/${extracted_folder}" != "$MYSQL_INSTALL_DIR" ]]; then
        rm -rf "$MYSQL_INSTALL_DIR"
        mv "/usr/local/${extracted_folder}" "$MYSQL_INSTALL_DIR"
    fi

    [[ -d "$MYSQL_INSTALL_DIR" ]] || \
        die "No se encontró ${MYSQL_INSTALL_DIR}."

    # --------------------------------------------------------
    # Usuario mysql
    # --------------------------------------------------------

    if ! getent group "$MYSQL_SYSTEM_GROUP" >/dev/null; then

        groupadd \
            --system \
            "$MYSQL_SYSTEM_GROUP"

    fi

    if ! id "$MYSQL_SYSTEM_USER" >/dev/null 2>&1; then

        useradd \
            --system \
            --gid "$MYSQL_SYSTEM_GROUP" \
            --home-dir /nonexistent \
            --shell /usr/sbin/nologin \
            "$MYSQL_SYSTEM_USER"

    fi

    ln -sfn \
        "$MYSQL_INSTALL_DIR" \
        "$MYSQL_BASE"

    # --------------------------------------------------------
    # Directorios
    # --------------------------------------------------------

    mkdir -p "$MYSQL_DATA"
    mkdir -p /var/log/mysql
    mkdir -p /var/lib/mysql-files
    mkdir -p /run/mysqld

    chown -R \
        "${MYSQL_SYSTEM_USER}:${MYSQL_SYSTEM_GROUP}" \
        "$MYSQL_DATA"

    chown -R \
        "${MYSQL_SYSTEM_USER}:${MYSQL_SYSTEM_GROUP}" \
        /var/log/mysql

    chown \
        "${MYSQL_SYSTEM_USER}:${MYSQL_SYSTEM_GROUP}" \
        /var/lib/mysql-files

    chown \
        "${MYSQL_SYSTEM_USER}:${MYSQL_SYSTEM_GROUP}" \
        /run/mysqld

    chmod 750 "$MYSQL_DATA"
    chmod 750 /var/log/mysql
    chmod 750 /var/lib/mysql-files
    chmod 755 /run/mysqld

    ldconfig

    # --------------------------------------------------------
    # Configuración MySQL
    # --------------------------------------------------------

    cat > /etc/mysql-invisap.cnf <<EOF
[mysqld]

basedir=${MYSQL_BASE}
datadir=${MYSQL_DATA}

socket=/run/mysqld/mysqld.sock
pid-file=/run/mysqld/mysqld.pid

port=${MYSQL_PORT}

bind-address=127.0.0.1

character-set-server=utf8mb4
collation-server=utf8mb4_0900_ai_ci

skip-name-resolve

log-error=/var/log/mysql/error.log

secure-file-priv=/var/lib/mysql-files

local-infile=0
EOF

    chmod 644 /etc/mysql-invisap.cnf

    # --------------------------------------------------------
    # Inicializar MySQL
    # --------------------------------------------------------

    info "Inicializando la base de datos interna de MySQL..."

    set +e
    "$MYSQL_BASE/bin/mysqld" \
        --initialize \
        --user="$MYSQL_SYSTEM_USER" \
        --basedir="$MYSQL_BASE" \
        --datadir="$MYSQL_DATA" \
        > /tmp/invisap-mysql-init.log 2>&1
    local init_status=$?
    set -e

    if [[ $init_status -ne 0 ]]; then
        echo
        echo -e "${RED}============================================================${NC}"
        echo -e "${RED} ERROR CRÍTICO AL INICIALIZAR MYSQL (Código: $init_status)${NC}"
        echo -e "${RED}============================================================${NC}"
        cat /tmp/invisap-mysql-init.log
        echo -e "${RED}============================================================${NC}"
        die "La inicialización de MySQL falló. Revisa el registro superior."
    fi

    # --------------------------------------------------------
    # Obtener contraseña temporal
    # --------------------------------------------------------

    MYSQL_TEMP_PASSWORD="$(
        grep \
            "A temporary password is generated" \
            /tmp/invisap-mysql-init.log |
            sed 's/.*: //' |
            tail -1
    )"

    if [[ -z "$MYSQL_TEMP_PASSWORD" ]]; then

        cat /tmp/invisap-mysql-init.log

        die \
            "No se pudo obtener la contraseña temporal de MySQL."

    fi

    # --------------------------------------------------------
    # Servicio systemd
    # --------------------------------------------------------

    cat > /etc/systemd/system/mysql-invisap.service <<EOF
[Unit]
Description=MySQL Community Server ${MYSQL_VERSION} - INVISAP
After=network.target

[Service]

Type=notify

User=${MYSQL_SYSTEM_USER}
Group=${MYSQL_SYSTEM_GROUP}

ExecStart=${MYSQL_BASE}/bin/mysqld \
    --defaults-file=/etc/mysql-invisap.cnf

LimitNOFILE=65535

Restart=on-failure
RestartSec=5

[Install]

WantedBy=multi-user.target
EOF

    systemctl daemon-reload

    systemctl enable mysql-invisap.service

    systemctl start mysql-invisap.service

    info "Esperando a que MySQL inicie..."

    local ready="no"

    for i in {1..30}; do

        if "$MYSQL_BASE/bin/mysqladmin" \
            --socket=/run/mysqld/mysqld.sock \
            ping >/dev/null 2>&1; then

            ready="yes"
            break

        fi

        sleep 1

    done

    if [[ "$ready" != "yes" ]]; then

        journalctl \
            -u mysql-invisap \
            -n 80 \
            --no-pager || true

        die "MySQL no pudo iniciar."

    fi

    # --------------------------------------------------------
    # Configurar root
    # --------------------------------------------------------

    configure_mysql_root

    # --------------------------------------------------------
    # Verificar versión
    # --------------------------------------------------------

    local installed_version

    installed_version="$(
        "$MYSQL_BASE/bin/mysql" \
            --protocol=socket \
            --socket=/run/mysqld/mysqld.sock \
            -uroot \
            -p"$MYSQL_ROOT_PASSWORD" \
            -Nse "SELECT VERSION();"
    )"

    if [[ "$installed_version" != "$MYSQL_VERSION" ]]; then

        die \
            "Se esperaba MySQL ${MYSQL_VERSION}, pero se encontró ${installed_version}."

    fi

    rm -f /tmp/invisap-mysql-init.log

    msg \
        "MySQL ${installed_version} instalado correctamente desde archivo local."

}

# ============================================================
# CONFIGURAR ROOT MYSQL
# ============================================================

configure_mysql_root() {

    echo
    echo -e "${CYAN}"
    echo "============================================================"
    echo "          CONFIGURACIÓN DE ROOT MYSQL"
    echo "============================================================"
    echo -e "${NC}"

    while true; do

        read -rsp \
            "Contraseña root de MySQL: " MYSQL_ROOT_PASSWORD

        echo

        read -rsp \
            "Repite la contraseña root: " MYSQL_ROOT_PASSWORD_CONFIRM

        echo

        if [[ -z "$MYSQL_ROOT_PASSWORD" ]]; then

            warn "La contraseña no puede estar vacía."

        elif [[ "$MYSQL_ROOT_PASSWORD" != "$MYSQL_ROOT_PASSWORD_CONFIRM" ]]; then

            warn "Las contraseñas no coinciden."

        else

            break

        fi

    done

    info "Configurando contraseña root..."

    "$MYSQL_BASE/bin/mysql" \
        --protocol=socket \
        --socket=/run/mysqld/mysqld.sock \
        -uroot \
        -p"$MYSQL_TEMP_PASSWORD" \
        --connect-expired-password <<SQL

ALTER USER 'root'@'localhost'
IDENTIFIED WITH caching_sha2_password
BY '${MYSQL_ROOT_PASSWORD}';

FLUSH PRIVILEGES;

SQL

    msg "Contraseña root configurada."

}

# ============================================================
# CREAR BASES DE DATOS (Con limpieza previa Error 1050 y host local 127.0.0.1)
# ============================================================

create_databases() {

    info "Creando bases de datos..."

    "$MYSQL_BASE/bin/mysql" \
        --protocol=socket \
        --socket=/run/mysqld/mysqld.sock \
        -uroot \
        -p"$MYSQL_ROOT_PASSWORD" <<SQL

DROP DATABASE IF EXISTS \`${DB_MAIN}\`;
DROP DATABASE IF EXISTS \`${DB_SECURITY}\`;

CREATE DATABASE \`${DB_MAIN}\`
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

CREATE DATABASE \`${DB_SECURITY}\`
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;

CREATE USER IF NOT EXISTS
'${DB_USER}'@'localhost'
IDENTIFIED WITH caching_sha2_password
BY '${DB_PASSWORD}';

CREATE USER IF NOT EXISTS
'${DB_USER}'@'127.0.0.1'
IDENTIFIED WITH caching_sha2_password
BY '${DB_PASSWORD}';

ALTER USER
'${DB_USER}'@'localhost'
IDENTIFIED WITH caching_sha2_password
BY '${DB_PASSWORD}';

ALTER USER
'${DB_USER}'@'127.0.0.1'
IDENTIFIED WITH caching_sha2_password
BY '${DB_PASSWORD}';

GRANT ALL PRIVILEGES
ON \`${DB_MAIN}\`.*
TO '${DB_USER}'@'localhost';

GRANT ALL PRIVILEGES
ON \`${DB_MAIN}\`.*
TO '${DB_USER}'@'127.0.0.1';

GRANT ALL PRIVILEGES
ON \`${DB_SECURITY}\`.*
TO '${DB_USER}'@'localhost';

GRANT ALL PRIVILEGES
ON \`${DB_SECURITY}\`.*
TO '${DB_USER}'@'127.0.0.1';

FLUSH PRIVILEGES;

SQL

    msg "Bases de datos y usuario creados."

}

# ============================================================
# CLONAR / ACTUALIZAR PROYECTO
# ============================================================

install_application() {

    info "Preparando directorio de la aplicación..."

    mkdir -p "$INSTALL_ROOT"

    if [[ -d "$APP_ROOT/.git" ]]; then

        warn "Ya existe una copia del repositorio."

        read -rp \
            "¿Deseas actualizarla con git pull? [S/n]: " answer

        if [[ ! "$answer" =~ ^[nN]$ ]]; then

            git \
                -C "$APP_ROOT" \
                pull \
                --ff-only

        fi

    else

        if [[ -d "$APP_ROOT" ]]; then

            local backup

            backup="${APP_ROOT}.backup.$(date +%Y%m%d_%H%M%S)"

            mv \
                "$APP_ROOT" \
                "$backup"

            info \
                "Instalación anterior respaldada en: ${backup}"

        fi

        info "Clonando INVISAP desde GitHub..."

        git clone \
            "$REPO_URL" \
            "$APP_ROOT"

    fi

    # --------------------------------------------------------
    # Comprobaciones
    # --------------------------------------------------------

    [[ -d "$APP_DIR" ]] || \
        die "No existe ${APP_DIR}."

    [[ -f "$APP_DIR/app.py" ]] || \
        die "No existe app.py."

    [[ -f "$APP_DIR/requirements.txt" ]] || \
        die "No existe requirements.txt."

    [[ -d "$APP_DIR/BD" ]] || \
        die "No existe la carpeta BD."

    [[ -f "$APP_DIR/BD/invilara.sql" ]] || \
        die "No existe BD/invilara.sql."

    [[ -f "$APP_DIR/BD/invilara_seguridad.sql" ]] || \
        die "No existe BD/invilara_seguridad.sql."

    msg "Estructura de INVISAP comprobada."

}

# ============================================================
# ENTORNO VIRTUAL
# ============================================================

install_python_environment() {

    info "Creando entorno virtual Python..."

    rm -rf "$VENV_DIR"

    "$PYTHON_BIN" \
        -m venv \
        "$VENV_DIR"

    info "Actualizando herramientas de Python..."

    "$VENV_DIR/bin/python" \
        -m pip install \
        --upgrade \
        pip \
        setuptools \
        wheel

    info "Instalando requirements.txt..."

    "$VENV_DIR/bin/pip" \
        install \
        -r "$APP_DIR/requirements.txt"

    info "Instalando Gunicorn..."

    "$VENV_DIR/bin/pip" \
        install \
        "gunicorn>=23,<24"

    msg "Entorno Python preparado."

}

# ============================================================
# IMPORTAR BASES DE DATOS
# ============================================================

import_databases() {

    info "Importando invilara.sql..."

    "$MYSQL_BASE/bin/mysql" \
        --protocol=socket \
        --socket=/run/mysqld/mysqld.sock \
        -uroot \
        -p"$MYSQL_ROOT_PASSWORD" \
        "$DB_MAIN" \
        < "$APP_DIR/BD/invilara.sql"

    msg "invilara.sql importado."

    info "Importando invilara_seguridad.sql..."

    "$MYSQL_BASE/bin/mysql" \
        --protocol=socket \
        --socket=/run/mysqld/mysqld.sock \
        -uroot \
        -p"$MYSQL_ROOT_PASSWORD" \
        "$DB_SECURITY" \
        < "$APP_DIR/BD/invilara_seguridad.sql"

    msg "invilara_seguridad.sql importado."

    # --------------------------------------------------------
    # Verificar tablas
    # --------------------------------------------------------

    local main_tables
    local security_tables

    main_tables="$(
        "$MYSQL_BASE/bin/mysql" \
            --protocol=socket \
            --socket=/run/mysqld/mysqld.sock \
            -uroot \
            -p"$MYSQL_ROOT_PASSWORD" \
            -Nse "
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema='${DB_MAIN}';
            "
    )"

    security_tables="$(
        "$MYSQL_BASE/bin/mysql" \
            --protocol=socket \
            --socket=/run/mysqld/mysqld.sock \
            -uroot \
            -p"$MYSQL_ROOT_PASSWORD" \
            -Nse "
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema='${DB_SECURITY}';
            "
    )"

    echo
    echo "Tablas detectadas:"
    echo
    echo "  ${DB_MAIN}:          ${main_tables}"
    echo "  ${DB_SECURITY}:      ${security_tables}"
    echo

    (( main_tables > 0 )) || \
        die "La BD ${DB_MAIN} no contiene tablas."

    (( security_tables > 0 )) || \
        die "La BD ${DB_SECURITY} no contiene tablas."

    msg "Bases de datos verificadas."

}

# ============================================================
# CREAR ARCHIVOS DE ENTORNO Y SEGURIDAD
# ============================================================

create_environment_file() {

    info "Generando archivo .env..."

    local env_file="$APP_DIR/.env"
    local temporary_file="${env_file}.tmp"

    cat > "$temporary_file" <<EOF
# ============================================================
# CONFIGURACIÓN DE INVISAP
# Generado automáticamente
# ============================================================

DB_HOST=127.0.0.1
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

DB_NAME=${DB_MAIN}
DB_NAME_SEGURIDAD=${DB_SECURITY}

DB_AUTH_PLUGIN=caching_sha2_password

MAIL_USERNAME=${MAIL_USERNAME}
MAIL_PASSWORD=${MAIL_PASSWORD}
EOF

    mv \
        "$temporary_file" \
        "$env_file"

    chmod 640 "$env_file"

    msg ".env creado correctamente."

    # --------------------------------------------------------
    # Verificar o generar claveApi.py (Respeta el archivo si ya existe)
    # --------------------------------------------------------

    local clave_file="$APP_DIR/claveApi.py"

    if [[ ! -f "$clave_file" ]]; then

        info "Generando archivo claveApi.py por defecto..."
        
        local secret_key
        secret_key=$(openssl rand -hex 16)

        cat > "$clave_file" <<EOF
# ============================================================
# CLAVES DE SEGURIDAD
# Generado automáticamente por el instalador
# ============================================================

SECRET_KEY = "${secret_key}"
EOF

        chmod 640 "$clave_file"
        msg "claveApi.py creado correctamente."

    else

        msg "El archivo claveApi.py ya existe. Se deja tal cual sin modificar."

    fi

}

# ============================================================
# CONFIGURAR PERMISOS
# ============================================================

configure_permissions() {

    info "Configurando permisos del proyecto..."

    local admin_user

    admin_user="${SUDO_USER:-root}"

    chown \
        -R \
        "${admin_user}:www-data" \
        "$APP_ROOT"

    find "$APP_ROOT" \
        -type d \
        -exec chmod 750 {} \;

    find "$APP_ROOT" \
        -type f \
        -exec chmod 640 {} \;

    if [[ -d "$VENV_DIR/bin" ]]; then

        find "$VENV_DIR/bin" \
            -type f \
            -exec chmod 750 {} \;

    fi

    chmod 640 "$APP_DIR/.env"
    
    if [[ -f "$APP_DIR/claveApi.py" ]]; then
        chmod 640 "$APP_DIR/claveApi.py"
    fi

    if [[ -d "$APP_DIR/static" ]]; then

        chmod -R g+rX "$APP_DIR/static"

    fi

    if [[ -d "$APP_DIR/vista" ]]; then

        chmod -R g+rX "$APP_DIR/vista"

    fi

    msg "Permisos configurados."

}

# ============================================================
# SERVICIO SYSTEMD
# ============================================================

configure_application_service() {

    info "Configurando servicio de INVISAP..."

    cat > "/etc/systemd/system/${APP_SERVICE}.service" <<EOF
[Unit]
Description=${APP_SYSTEM_NAME} - Flask/Gunicorn
After=network.target mysql-invisap.service
Requires=mysql-invisap.service

[Service]

Type=simple

User=www-data
Group=www-data

WorkingDirectory=${APP_DIR}

EnvironmentFile=${APP_DIR}/.env

ExecStart=${VENV_DIR}/bin/gunicorn \
    --workers 2 \
    --bind 127.0.0.1:${APP_PORT} \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    app:application

Restart=always
RestartSec=5

[Install]

WantedBy=multi-user.target
EOF

    chmod 644 \
        "/etc/systemd/system/${APP_SERVICE}.service"

    systemctl daemon-reload

    systemctl enable "$APP_SERVICE"
    systemctl enable mysql-invisap.service

    systemctl restart "$APP_SERVICE"

    sleep 3

    if ! systemctl is-active --quiet "$APP_SERVICE"; then

        echo
        fail "INVISAP no pudo iniciar."
        echo

        journalctl \
            -u "$APP_SERVICE" \
            -n 100 \
            --no-pager

        die "El servicio de INVISAP no inició correctamente."

    fi

    msg "Servicio INVISAP activo."

}

# ============================================================
# PRUEBA MYSQL
# ============================================================

test_mysql() {

    info "Probando conexión con MySQL..."

    local version

    version="$(
        "$MYSQL_BASE/bin/mysql" \
            --protocol=socket \
            --socket=/run/mysqld/mysqld.sock \
            -u"$DB_USER" \
            -p"$DB_PASSWORD" \
            -Nse "SELECT VERSION();" \
            "$DB_MAIN"
    )"

    echo
    echo "Versión MySQL detectada:"
    echo "  ${version}"
    echo

    msg "Conexión MySQL correcta."

}

# ============================================================
# PRUEBA PYTHON / FLASK
# ============================================================

test_python_application() {

    info "Probando importación de la aplicación..."

    cd "$APP_DIR"

    "$VENV_DIR/bin/python" <<'PY'
import flask
import mysql.connector
import app

print("Flask:", flask.__version__)
print("mysql-connector:", mysql.connector.__version__)

if not hasattr(app, "application"):
    raise RuntimeError(
        "No se encontró el objeto 'application' en app.py."
    )

print("Objeto Flask 'application': OK")
PY

    msg "La aplicación Python puede cargarse correctamente."

}

# ============================================================
# PRUEBA HTTP
# ============================================================

test_http() {

    info "Probando servidor Flask/Gunicorn..."

    local code

    if code="$(
        curl \
            -sS \
            --max-time 15 \
            -o /tmp/invisap_response.html \
            -w "%{http_code}" \
            "http://127.0.0.1:${APP_PORT}/"
    )"; then

        echo
        echo "Código HTTP recibido: ${code}"
        echo

        if [[ "$code" =~ ^[2345][0-9][0-9]$ ]]; then

            msg \
                "Gunicorn está respondiendo correctamente."

        else

            warn \
                "Se recibió un código HTTP inesperado: ${code}"

        fi

    else

        warn \
            "No fue posible realizar la prueba HTTP."

        warn \
            "Revisa los logs de INVISAP."

    fi

    rm -f /tmp/invisap_response.html

}

# ============================================================
# INFORMACIÓN FINAL
# ============================================================

show_final_information() {

    echo

    echo -e "${GREEN}"
    echo "============================================================"
    echo "             INSTALACIÓN COMPLETADA"
    echo "============================================================"
    echo -e "${NC}"

    echo
    echo "INVISAP"
    echo "------------------------------------------------------------"
    echo "Nombre             : ${APP_SYSTEM_NAME}"
    echo "Directorio         : ${APP_DIR}"
    echo "Python             : $($PYTHON_BIN --version)"
    echo "Entorno virtual    : ${VENV_DIR}"

    echo
    echo "MySQL"
    echo "------------------------------------------------------------"
    echo "Versión            : ${MYSQL_VERSION}"
    echo "Puerto             : ${MYSQL_PORT}"
    echo "Host               : 127.0.0.1"
    echo "BD principal       : ${DB_MAIN}"
    echo "BD seguridad       : ${DB_SECURITY}"
    echo "Usuario             : ${DB_USER}"

    echo
    echo "Aplicación"
    echo "------------------------------------------------------------"
    echo "Gunicorn           : 127.0.0.1:${APP_PORT}"
    echo "Servicio           : ${APP_SERVICE}.service"

    echo
    echo "Acceso local"
    echo "------------------------------------------------------------"
    echo "http://127.0.0.1:${APP_PORT}/"

    echo
    echo "Comandos útiles"
    echo "------------------------------------------------------------"
    echo
    echo "Estado de INVISAP:"
    echo "  sudo systemctl status invisap"
    echo
    echo "Reiniciar INVISAP:"
    echo "  sudo systemctl restart invisap"
    echo
    echo "Logs de INVISAP:"
    echo "  sudo journalctl -u invisap -f"
    echo
    echo "Estado de MySQL:"
    echo "  sudo systemctl status mysql-invisap"
    echo
    echo "Logs de MySQL:"
    echo "  sudo journalctl -u mysql-invisap -f"

    echo
    echo -e "${YELLOW}"
    echo "IMPORTANTE"
    echo "------------------------------------------------------------"
    echo "MySQL y Gunicorn están configurados únicamente para"
    echo "escuchar en localhost."
    echo
    echo "No se instaló Nginx."
    echo "No se abrió ningún puerto del firewall."
    echo
    echo "Esta configuración está pensada para la prueba local"
    echo "de INVISAP en el servidor."
    echo -e "${NC}"

}

# ============================================================
# MAIN
# ============================================================

main() {

    clear

    echo -e "${CYAN}"
    echo "============================================================"
    echo "             INSTALADOR DE INVISAP (MODO LOCAL)"
    echo "============================================================"
    echo "        Zorin OS 18.x / Ubuntu 24.04 LTS"
    echo "============================================================"
    echo -e "${NC}"

    echo
    echo "Este instalador configurará automáticamente:"
    echo
    echo "  - Python"
    echo "  - Entorno virtual"
    echo "  - requirements.txt"
    echo "  - MySQL ${MYSQL_VERSION} (Desde archivo local)"
    echo "  - invilara"
    echo "  - invilara_seguridad"
    echo "  - Gunicorn"
    echo "  - systemd"
    echo
    echo "No se instalará Nginx."
    echo

    read -rp \
        "Presiona ENTER para comenzar..."

    check_root

    check_architecture

    check_os

    check_existing_mysql

    ask_configuration

    pause_installation

    clear

    echo -e "${CYAN}"
    echo "============================================================"
    echo "             INICIANDO INSTALACIÓN"
    echo "============================================================"
    echo -e "${NC}"

    echo

    install_system_packages

    install_mysql

    create_databases

    install_application

    install_python_environment

    import_databases

    create_environment_file

    configure_permissions

    configure_application_service

    test_mysql

    test_python_application

    test_http

    show_final_information

}

# ============================================================
# EJECUTAR
# ============================================================

main "$@"