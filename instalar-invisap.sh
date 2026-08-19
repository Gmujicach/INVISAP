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
#   - MySQL Community Server 9.7.1 (Desde DEB Bundle local)
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

MYSQL_VERSION="9.7.1"
MYSQL_DATA="/var/lib/mysql"
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
# FUNCIONES BÁSICAS
# ============================================================

msg() { echo -e "${GREEN}[OK]${NC} $1"; }
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[AVISO]${NC} $1"; }
fail() { echo -e "${RED}[ERROR]${NC} $1"; }
die() { fail "$1"; exit 1; }
pause_installation() { echo; read -rp "Presiona ENTER para continuar..."; }

error_handler() {
    local code=$?
    echo
    fail "La instalación terminó con un error."
    echo
    echo "Código de error: ${code}"
    echo
    echo "Si el problema está relacionado con INVISAP:"
    echo "  sudo systemctl status invisap"
    echo "  sudo journalctl -u invisap -n 100 --no-pager"
    echo
    echo "Si el problema está relacionado con MySQL:"
    echo "  sudo systemctl status mysql"
    echo "  sudo journalctl -u mysql -n 100 --no-pager"
    echo
    exit "$code"
}

trap error_handler ERR

check_root() {
    if [[ "$EUID" -ne 0 ]]; then
        die "Este script debe ejecutarse con sudo."
    fi
}

check_architecture() {
    local architecture="$(uname -m)"
    if [[ "$architecture" != "x86_64" ]]; then
        die "Este instalador requiere arquitectura x86_64."
    fi
    msg "Arquitectura compatible: ${architecture}"
}

check_os() {
    if [[ ! -f /etc/os-release ]]; then
        die "No se encontró /etc/os-release."
    fi
    source /etc/os-release
    
    echo
    echo "Sistema operativo detectado: ${PRETTY_NAME:-desconocido}"
    echo

    if [[ "${ID:-}" != "zorin" ]] || [[ "${VERSION_ID:-}" != "18" ]]; then
        warn "Este instalador fue diseñado para Zorin OS 18.x."
        read -rp "¿Deseas continuar de todas formas? [s/N]: " answer
        if [[ ! "$answer" =~ ^[sS]$ ]]; then
            exit 0
        fi
    fi
    msg "Sistema operativo aceptado."
}

valid_mysql_name() {
    [[ "$1" =~ ^[a-zA-Z0-9_]+$ ]]
}

ask_configuration() {
    clear
    echo -e "${CYAN}============================================================${NC}"
    echo "          CONFIGURACIÓN DE INVISAP"
    echo -e "${CYAN}============================================================${NC}"
    echo

    read -rp "Ruta base de instalación [/var/www]: " value
    INSTALL_ROOT="${value:-/var/www}"
    APP_ROOT="${INSTALL_ROOT}/invisap"
    APP_DIR="${APP_ROOT}/my-app"
    VENV_DIR="${APP_DIR}/venv"

    read -rp "Nombre del sistema [INVISAP]: " value
    APP_SYSTEM_NAME="${value:-INVISAP}"

    while true; do
        read -rp "Usuario MySQL [invisap]: " value
        DB_USER="${value:-invisap}"
        if valid_mysql_name "$DB_USER"; then break; fi
        warn "El usuario solamente puede contener letras, números y _."
    done

    while true; do
        read -rsp "Contraseña del usuario MySQL: " DB_PASSWORD
        echo
        read -rsp "Repite la contraseña: " DB_PASSWORD_CONFIRM
        echo
        if [[ -z "$DB_PASSWORD" ]]; then
            warn "La contraseña no puede estar vacía."
        elif [[ "$DB_PASSWORD" != "$DB_PASSWORD_CONFIRM" ]]; then
            warn "Las contraseñas no coinciden."
        else
            break
        fi
    done

    while true; do
        read -rp "Base de datos principal [invilara]: " value
        DB_MAIN="${value:-invilara}"
        if valid_mysql_name "$DB_MAIN"; then break; fi
        warn "El nombre de la BD solamente puede contener letras, números y _."
    done

    while true; do
        read -rp "Base de datos de seguridad [invilara_seguridad]: " value
        DB_SECURITY="${value:-invilara_seguridad}"
        if valid_mysql_name "$DB_SECURITY"; then break; fi
        warn "El nombre de la BD solamente puede contener letras, números y _."
    done

    while true; do
        read -rp "Puerto local de Flask/Gunicorn [5600]: " value
        APP_PORT="${value:-5600}"
        if [[ "$APP_PORT" =~ ^[0-9]+$ ]] && (( APP_PORT >= 1024 && APP_PORT <= 65535 )); then break; fi
        warn "Introduce un puerto entre 1024 y 65535."
    done

    echo
    read -rp "¿Deseas configurar el correo ahora? [s/N]: " answer
    if [[ "$answer" =~ ^[sS]$ ]]; then
        MAIL_CONFIGURED="yes"
        while [[ -z "$MAIL_USERNAME" ]]; do
            read -rp "Correo Gmail: " MAIL_USERNAME
        done
        read -rsp "Contraseña de aplicación Gmail: " MAIL_PASSWORD
        echo
        [[ -n "$MAIL_PASSWORD" ]] || die "La contraseña no puede estar vacía."
    fi

    echo
    echo "¿La configuración es correcta?"
    read -rp "[S/n]: " answer
    if [[ "$answer" =~ ^[nN]$ ]]; then
        ask_configuration
    fi
}

install_system_packages() {
    info "Actualizando repositorios y dependencias base..."
    apt-get update

    DEBIAN_FRONTEND=noninteractive apt-get install -y         git curl wget ca-certificates gnupg xz-utils build-essential         python3 python3-venv python3-dev python3-pip         libaio1t64 libncurses6 libnuma1 libssl3t64 pkg-config openssl         libmecab2

    if [[ -f /usr/lib/x86_64-linux-gnu/libaio.so.1t64 ]] && [[ ! -f /usr/lib/x86_64-linux-gnu/libaio.so.1 ]]; then
        ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
    fi

    PYTHON_BIN="$(command -v python3)"
    msg "Python detectado: $($PYTHON_BIN --version)"
}

install_mysql() {
    info "Instalando MySQL Community Server ${MYSQL_VERSION} (DEB Bundle local)..."

    local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local archive_name="mysql-server_${MYSQL_VERSION}-1ubuntu24.04_amd64.deb-bundle.tar"
    local archive="${script_dir}/${archive_name}"

    if [[ ! -f "$archive" ]]; then
        archive="./${archive_name}"
        if [[ ! -f "$archive" ]]; then
            die "No se encontró el archivo local '${archive_name}'."
        fi
    fi

    local extract_dir="/tmp/mysql_bundle_extract"
    rm -rf "$extract_dir"
    mkdir -p "$extract_dir"

    info "Extrayendo el paquete Bundle..."
    tar -xf "$archive" -C "$extract_dir"

    info "Instalando paquetes .deb de MySQL..."
    
    # Preconfigurar debconf para instalación desatendida (sin prompt de contraseña root)
    export DEBIAN_FRONTEND=noninteractive
    debconf-set-selections <<< "mysql-community-server mysql-community-server/root-pass password "
    debconf-set-selections <<< "mysql-community-server mysql-community-server/re-root-pass password "

    # Instalar paquetes con dpkg y forzar dependencias con apt-get
    dpkg -i "$extract_dir"/*.deb || true
    apt-get install -f -y

    rm -rf "$extract_dir"

    systemctl enable mysql
    systemctl restart mysql

    info "Esperando a que MySQL inicie..."
    sleep 5

    configure_mysql_root

    local installed_version="$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -Nse "SELECT VERSION();")"
    msg "MySQL ${installed_version} instalado correctamente desde DEB Bundle."
}

configure_mysql_root() {
    echo
    echo -e "${CYAN}============================================================${NC}"
    echo "          CONFIGURACIÓN DE ROOT MYSQL"
    echo -e "${CYAN}============================================================${NC}"

    while true; do
        read -rsp "Contraseña root de MySQL: " MYSQL_ROOT_PASSWORD
        echo
        read -rsp "Repite la contraseña root: " MYSQL_ROOT_PASSWORD_CONFIRM
        echo
        if [[ -z "$MYSQL_ROOT_PASSWORD" ]]; then
            warn "La contraseña no puede estar vacía."
        elif [[ "$MYSQL_ROOT_PASSWORD" != "$MYSQL_ROOT_PASSWORD_CONFIRM" ]]; then
            warn "Las contraseñas no coinciden."
        else
            break
        fi
    done

    info "Aplicando contraseña root..."

    # En Ubuntu/Zorin, root puede entrar sin clave inicialmente gracias a auth_socket
    mysql -u root <<SQL
ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY '${MYSQL_ROOT_PASSWORD}';
FLUSH PRIVILEGES;
SQL

    msg "Contraseña root configurada."
}

create_databases() {
    info "Creando bases de datos y usuario de la aplicación..."

    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<SQL
DROP DATABASE IF EXISTS \`${DB_MAIN}\`;
DROP DATABASE IF EXISTS \`${DB_SECURITY}\`;

CREATE DATABASE \`${DB_MAIN}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE \`${DB_SECURITY}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED WITH caching_sha2_password BY '${DB_PASSWORD}';
CREATE USER IF NOT EXISTS '${DB_USER}'@'127.0.0.1' IDENTIFIED WITH caching_sha2_password BY '${DB_PASSWORD}';

ALTER USER '${DB_USER}'@'localhost' IDENTIFIED WITH caching_sha2_password BY '${DB_PASSWORD}';
ALTER USER '${DB_USER}'@'127.0.0.1' IDENTIFIED WITH caching_sha2_password BY '${DB_PASSWORD}';

GRANT ALL PRIVILEGES ON \`${DB_MAIN}\`.* TO '${DB_USER}'@'localhost';
GRANT ALL PRIVILEGES ON \`${DB_MAIN}\`.* TO '${DB_USER}'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \`${DB_SECURITY}\`.* TO '${DB_USER}'@'localhost';
GRANT ALL PRIVILEGES ON \`${DB_SECURITY}\`.* TO '${DB_USER}'@'127.0.0.1';

FLUSH PRIVILEGES;
SQL

    msg "Bases de datos y usuario creados."
}

install_application() {
    info "Preparando directorio de la aplicación..."
    mkdir -p "$INSTALL_ROOT"

    if [[ -d "$APP_ROOT/.git" ]]; then
        git -C "$APP_ROOT" pull --ff-only
    else
        if [[ -d "$APP_ROOT" ]]; then
            mv "$APP_ROOT" "${APP_ROOT}.backup.$(date +%Y%m%d_%H%M%S)"
        fi
        git clone "$REPO_URL" "$APP_ROOT"
    fi
}

install_python_environment() {
    info "Creando entorno virtual Python..."
    rm -rf "$VENV_DIR"
    "$PYTHON_BIN" -m venv "$VENV_DIR"

    "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
    "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    "$VENV_DIR/bin/pip" install "gunicorn>=23,<24"
    msg "Entorno Python preparado."
}

import_databases() {
    info "Importando tablas a las bases de datos..."

    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "$DB_MAIN" < "$APP_DIR/BD/invilara.sql"
    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "$DB_SECURITY" < "$APP_DIR/BD/invilara_seguridad.sql"

    msg "Archivos SQL importados correctamente."
}

create_environment_file() {
    info "Generando archivo .env..."

    cat > "$APP_DIR/.env" <<EOF
DB_HOST=127.0.0.1
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_MAIN}
DB_NAME_SEGURIDAD=${DB_SECURITY}
DB_AUTH_PLUGIN=caching_sha2_password
MAIL_USERNAME=${MAIL_USERNAME}
MAIL_PASSWORD=${MAIL_PASSWORD}
EOF
    chmod 640 "$APP_DIR/.env"

    local clave_file="$APP_DIR/claveApi.py"
    if [[ ! -f "$clave_file" ]]; then
        local secret_key=$(openssl rand -hex 16)
        cat > "$clave_file" <<EOF
SECRET_KEY = "${secret_key}"
EOF
        chmod 640 "$clave_file"
    fi
}

configure_permissions() {
    info "Configurando permisos del proyecto..."
    local admin_user="${SUDO_USER:-root}"

    chown -R "${admin_user}:www-data" "$APP_ROOT"
    find "$APP_ROOT" -type d -exec chmod 750 {} \;
    find "$APP_ROOT" -type f -exec chmod 640 {} \;

    if [[ -d "$VENV_DIR/bin" ]]; then
        find "$VENV_DIR/bin" -type f -exec chmod 750 {} \;
    fi
    chmod 640 "$APP_DIR/.env"
    [[ -f "$APP_DIR/claveApi.py" ]] && chmod 640 "$APP_DIR/claveApi.py"
    [[ -d "$APP_DIR/static" ]] && chmod -R g+rX "$APP_DIR/static"
    [[ -d "$APP_DIR/vista" ]] && chmod -R g+rX "$APP_DIR/vista"
}

configure_application_service() {
    info "Configurando servicio de INVISAP..."

    cat > "/etc/systemd/system/${APP_SERVICE}.service" <<EOF
[Unit]
Description=${APP_SYSTEM_NAME} - Flask/Gunicorn
After=network.target mysql.service
Requires=mysql.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=${APP_DIR}
EnvironmentFile=${APP_DIR}/.env
ExecStart=${VENV_DIR}/bin/gunicorn --workers 2 --bind 127.0.0.1:${APP_PORT} --timeout 120 --access-logfile - --error-logfile - app:application
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

    chmod 644 "/etc/systemd/system/${APP_SERVICE}.service"
    systemctl daemon-reload
    systemctl enable "$APP_SERVICE"
    systemctl restart "$APP_SERVICE"

    sleep 3
    if ! systemctl is-active --quiet "$APP_SERVICE"; then
        die "El servicio de INVISAP no inició correctamente."
    fi
    msg "Servicio INVISAP activo."
}

test_mysql() {
    local version="$(mysql -u"$DB_USER" -p"$DB_PASSWORD" -Nse "SELECT VERSION();" "$DB_MAIN")"
    msg "Conexión MySQL correcta. Versión: ${version}"
}

test_python_application() {
    cd "$APP_DIR"
    "$VENV_DIR/bin/python" <<'PY'
import flask, mysql.connector, app
if not hasattr(app, "application"): raise RuntimeError("No application object found.")
PY
    msg "La aplicación Python se cargó correctamente."
}

test_http() {
    local code
    if code="$(curl -sS --max-time 15 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${APP_PORT}/")"; then
        if [[ "$code" =~ ^[2345][0-9][0-9]$ ]]; then
            msg "Gunicorn responde correctamente (HTTP ${code})."
        fi
    fi
}

show_final_information() {
    echo -e "${GREEN}============================================================${NC}"
    echo "             INSTALACIÓN COMPLETADA"
    echo -e "${GREEN}============================================================${NC}"
    echo
    echo "INVISAP está corriendo en http://127.0.0.1:${APP_PORT}/"
    echo "Servicio de la app : sudo systemctl status invisap"
    echo "Servicio de MySQL  : sudo systemctl status mysql"
    echo -e "${YELLOW}NOTA: No se instaló Nginx ni se expusieron puertos.${NC}"
}

main() {
    clear
    check_root
    check_architecture
    check_os

    ask_configuration
    pause_installation
    clear

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

main "$@"
