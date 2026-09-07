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
#   - Scripts manuales para iniciar/detener INVISAP
#
# NO crea un servicio systemd para INVISAP.
# NO deja MySQL habilitado para arrancar automáticamente con el sistema.
# NO abre puertos.
# MySQL escucha únicamente en localhost.
# Gunicorn escucha únicamente en localhost.
#
# Después de instalar:
#   sudo /usr/local/bin/invisap-start
#   sudo /usr/local/bin/invisap-stop
#   sudo /usr/local/bin/invisap-status
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
START_SCRIPT="/usr/local/bin/invisap-start"
STOP_SCRIPT="/usr/local/bin/invisap-stop"
STATUS_SCRIPT="/usr/local/bin/invisap-status"
RUNNER_SCRIPT=""
PID_FILE=""
LOG_FILE=""

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
    echo "  sudo /usr/local/bin/invisap-status"
    echo "  sudo tail -n 100 ${APP_ROOT:-/var/www/invisap}/invisap.log"
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

    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        git curl wget ca-certificates gnupg xz-utils build-essential sudo \
        python3 python3-venv python3-dev python3-pip \
        libaio1t64 libncurses6 libnuma1 libssl3t64 pkg-config openssl \
        libmecab2

    if [[ -f /usr/lib/x86_64-linux-gnu/libaio.so.1t64 ]] && [[ ! -f /usr/lib/x86_64-linux-gnu/libaio.so.1 ]]; then
        ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1
    fi

    PYTHON_BIN="$(command -v python3)"
    msg "Python detectado: $($PYTHON_BIN --version)"
}

install_mysql() {
    info "Instalando/verificando MySQL Community Server ${MYSQL_VERSION} (DEB Bundle local)..."

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local archive_name="mysql-server_${MYSQL_VERSION}-1ubuntu24.04_amd64.deb-bundle.tar"
    local archive="${script_dir}/${archive_name}"

    if [[ ! -f "$archive" ]]; then
        archive="./${archive_name}"
        if [[ ! -f "$archive" ]]; then
            die "No se encontró el archivo local '${archive_name}'."
        fi
    fi

    if command -v mysql >/dev/null 2>&1 && systemctl cat mysql.service >/dev/null 2>&1; then
        local current_version=""
        current_version="$(mysql --version 2>/dev/null || true)"

        if [[ "$current_version" == *"Ver 9.7.1"* ]]; then
            msg "MySQL ${MYSQL_VERSION} ya está instalado. Se conservará la instalación existente."
        else
            info "Se detectó MySQL instalado, pero no se pudo confirmar la versión ${MYSQL_VERSION}."
            info "Se utilizará el Bundle ${MYSQL_VERSION} para completar/verificar la instalación."
        fi
    fi

    if ! command -v mysql >/dev/null 2>&1 || ! systemctl cat mysql.service >/dev/null 2>&1; then
        local extract_dir="/tmp/mysql_bundle_extract"
        rm -rf "$extract_dir"
        install -d -m 700 "$extract_dir"

        info "Extrayendo el paquete Bundle..."
        tar -xf "$archive" -C "$extract_dir"

        info "Instalando paquetes .deb de MySQL..."
        export DEBIAN_FRONTEND=noninteractive

        debconf-set-selections <<< "mysql-community-server mysql-community-server/root-pass password "
        debconf-set-selections <<< "mysql-community-server mysql-community-server/re-root-pass password "

        dpkg -i "$extract_dir"/*.deb || true
        apt-get install -f -y

        rm -rf "$extract_dir"
    fi

    command -v mysql >/dev/null 2>&1 || die "El cliente mysql no quedó instalado."
    systemctl cat mysql.service >/dev/null 2>&1 || die "No se encontró mysql.service."

    configure_mysql_persistence
    systemctl daemon-reload

    # MySQL se inicia únicamente durante la instalación para poder crear
    # usuarios y bases de datos. No se habilita para el arranque del sistema.
    if ! systemctl is-active --quiet mysql; then
        info "Iniciando MySQL temporalmente para completar la instalación..."
        systemctl start mysql
    else
        msg "MySQL ya estaba activo."
    fi

    wait_for_mysql
    configure_mysql_root

    local installed_version
    installed_version="$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -Nse "SELECT VERSION();")"

    if [[ "$installed_version" != 9.7.1* ]]; then
        die "Se esperaba MySQL 9.7.1, pero se detectó ${installed_version}."
    fi

    # No se desinstala MySQL ni se modifica su almacenamiento.
    # Solo se desactiva su arranque automático.
    systemctl disable mysql >/dev/null 2>&1 || true

    msg "MySQL ${installed_version} instalado/configurado correctamente."
    msg "MySQL quedó instalado pero NO habilitado para arrancar automáticamente."
}

configure_mysql_persistence() {
    info "Configurando persistencia de los datos de MySQL..."

    install -d -o mysql -g mysql -m 750 "$MYSQL_DATA"

    local conf="/etc/mysql/mysql.conf.d/99-invisap-recovery.cnf"

    cat > "$conf" <<EOF
[mysqld]
datadir=${MYSQL_DATA}

# Durabilidad frente a apagados inesperados.
innodb_flush_log_at_trx_commit=1
sync_binlog=1
innodb_doublewrite=ON

# Recuperación conservadora después de un cierre inesperado.
innodb_fast_shutdown=1
EOF

    chmod 644 "$conf"
    chown root:root "$conf"

    # Elimina cualquier override creado por una versión anterior del instalador.
    # De esta forma MySQL utiliza únicamente su servicio nativo.
    rm -f /etc/systemd/system/mysql.service.d/override.conf
    rmdir /etc/systemd/system/mysql.service.d 2>/dev/null || true
    systemctl daemon-reload

    if command -v mysqld >/dev/null 2>&1; then
        if ! mysqld --validate-config >/dev/null 2>&1; then
            warn "La validación de la configuración de MySQL falló."
            rm -f "$conf"
            systemctl daemon-reload
            die "Se detectó una configuración MySQL inválida. No se continuará."
        fi
    fi

    msg "Persistencia de los datos de MySQL configurada."
}

wait_for_mysql() {
    info "Esperando a que MySQL esté disponible..."

    local attempts=60
    local i=1

    while (( i <= attempts )); do
        if mysqladmin ping --silent >/dev/null 2>&1; then
            msg "MySQL está respondiendo correctamente."
            return 0
        fi

        sleep 2
        ((i++))
    done

    systemctl status mysql --no-pager || true
    journalctl -u mysql -n 100 --no-pager || true

    die "MySQL no respondió después de esperar $((attempts * 2)) segundos."
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
    info "Creando/verificando bases de datos y usuario de la aplicación..."

    mysql -u root -p"${MYSQL_ROOT_PASSWORD}" <<SQL
CREATE DATABASE IF NOT EXISTS \`${DB_MAIN}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE DATABASE IF NOT EXISTS \`${DB_SECURITY}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;

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

    msg "Bases de datos y usuario verificados/creados sin eliminar datos existentes."
}

database_has_tables() {
    local db="$1"
    local count

    count="$(mysql -u root -p"${MYSQL_ROOT_PASSWORD}" -Nse \
        "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${db}';")"

    [[ "$count" =~ ^[0-9]+$ ]] && (( count > 0 ))
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
    info "Preparando entorno virtual Python..."

    if [[ -x "$VENV_DIR/bin/python" && -x "$VENV_DIR/bin/pip" ]]; then
        msg "El entorno virtual ya existe y será conservado."
    else
        if [[ -d "$VENV_DIR" ]]; then
            local broken_dir="${VENV_DIR}.broken.$(date +%Y%m%d_%H%M%S)"
            warn "El entorno virtual existe pero está incompleto."
            warn "Se conservará como respaldo en: ${broken_dir}"
            mv "$VENV_DIR" "$broken_dir"
        fi

        "$PYTHON_BIN" -m venv "$VENV_DIR"
    fi

    "$VENV_DIR/bin/python" -m pip install --upgrade pip setuptools wheel
    "$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt"
    "$VENV_DIR/bin/pip" install "gunicorn>=23,<24"
    "$VENV_DIR/bin/pip" install "python-dotenv>=1,<2"

    # Comprobación de que el entorno quedó realmente ejecutable.
    "$VENV_DIR/bin/python" -c "import flask, mysql.connector" || \
        die "El entorno Python no pudo cargar Flask/mysql.connector."

    "$VENV_DIR/bin/gunicorn" --version >/dev/null || \
        die "Gunicorn no quedó disponible en el entorno virtual."

    msg "Entorno Python preparado y persistente."
}


import_databases() {
    info "Verificando/importando tablas de las bases de datos..."

    if database_has_tables "$DB_MAIN"; then
        warn "La base ${DB_MAIN} ya contiene tablas. NO se importará el SQL para proteger los datos existentes."
    else
        # CORRECCIÓN AQUÍ: Se agrupan los comandos para desactivar/activar llaves foráneas
        # antes y después de inyectar el contenido del archivo SQL, mitigando el ERROR 1452.
        {
            echo "SET FOREIGN_KEY_CHECKS=0;"
            cat "$APP_DIR/BD/invilara.sql"
            echo "SET FOREIGN_KEY_CHECKS=1;"
        } | mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "$DB_MAIN"
        msg "SQL de ${DB_MAIN} importado."
    fi

    if database_has_tables "$DB_SECURITY"; then
        warn "La base ${DB_SECURITY} ya contiene tablas. NO se importará el SQL para proteger los datos existentes."
    else
        # CORRECCIÓN AQUÍ: Se aplica la misma lógica para la base de datos de seguridad.
        {
            echo "SET FOREIGN_KEY_CHECKS=0;"
            cat "$APP_DIR/BD/invilara_seguridad.sql"
            echo "SET FOREIGN_KEY_CHECKS=1;"
        } | mysql -u root -p"${MYSQL_ROOT_PASSWORD}" "$DB_SECURITY"
        msg "SQL de ${DB_SECURITY} importado."
    fi

    msg "Importación/verificación de bases de datos completada sin destruir datos existentes."
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
    info "Configurando control manual de INVISAP (sin servicio systemd)..."

    RUNNER_SCRIPT="${APP_DIR}/invisap_runner.py"
    PID_FILE="${APP_ROOT}/.invisap.pid"
    LOG_FILE="${APP_ROOT}/invisap.log"

    # Limpia cualquier servicio invisap creado por una instalación anterior.
    if systemctl cat "${APP_SERVICE}.service" >/dev/null 2>&1; then
        systemctl disable --now "${APP_SERVICE}.service" >/dev/null 2>&1 || true
        rm -f "/etc/systemd/system/${APP_SERVICE}.service"
        systemctl daemon-reload
    fi

    # Carga .env con python-dotenv y ejecuta Gunicorn.
    cat > "$RUNNER_SCRIPT" <<EOF
#!/usr/bin/env python3
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: python-dotenv no está instalado.", file=sys.stderr)
    sys.exit(1)

APP_DIR = ${APP_DIR@Q}
ENV_FILE = os.path.join(APP_DIR, ".env")
GUNICORN = os.path.join(${VENV_DIR@Q}, "bin", "gunicorn")

load_dotenv(ENV_FILE)
os.chdir(APP_DIR)

os.execv(
    GUNICORN,
    [
        GUNICORN,
        "--workers", "2",
        "--bind", "127.0.0.1:${APP_PORT}",
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
        "app:application",
    ],
)
EOF

    chmod 750 "$RUNNER_SCRIPT"
    chown "${SUDO_USER:-root}:www-data" "$RUNNER_SCRIPT"

    cat > "$START_SCRIPT" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

APP_ROOT=${APP_ROOT@Q}
VENV_DIR=${VENV_DIR@Q}
RUNNER_SCRIPT=${RUNNER_SCRIPT@Q}
PID_FILE=${PID_FILE@Q}
LOG_FILE=${LOG_FILE@Q}
APP_PORT=${APP_PORT@Q}

if [[ "\$EUID" -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

if [[ -f "\$PID_FILE" ]]; then
    old_pid="\$(cat "\$PID_FILE" 2>/dev/null || true)"
    if [[ "\$old_pid" =~ ^[0-9]+$ ]] && \$SUDO kill -0 "\$old_pid" 2>/dev/null; then
        echo "[INFO] INVISAP ya está ejecutándose (PID \$old_pid)."
        echo "[INFO] http://127.0.0.1:\${APP_PORT}/"
        exit 0
    fi
    rm -f "\$PID_FILE"
fi

echo "[INFO] Iniciando MySQL..."
\$SUDO systemctl start mysql

echo "[INFO] Esperando a que MySQL responda..."
for i in {1..60}; do
    if \$SUDO mysqladmin ping --silent >/dev/null 2>&1; then
        break
    fi
    sleep 2
done

if ! \$SUDO mysqladmin ping --silent >/dev/null 2>&1; then
    echo "[ERROR] MySQL no respondió."
    echo "[ERROR] Revisa: sudo systemctl status mysql"
    echo "[ERROR] Revisa: sudo journalctl -u mysql -n 100 --no-pager"
    exit 1
fi

if [[ ! -x "\$VENV_DIR/bin/python" || ! -x "\$VENV_DIR/bin/gunicorn" ]]; then
    echo "[ERROR] El entorno Python/Gunicorn no está disponible."
    exit 1
fi

touch "\$LOG_FILE"
echo "[INFO] Iniciando Gunicorn..."
nohup \$SUDO -u www-data "\$VENV_DIR/bin/python" "\$RUNNER_SCRIPT" >> "\$LOG_FILE" 2>&1 &
pid=\$!
echo "\$pid" > "\$PID_FILE"

sleep 3

if ! \$SUDO kill -0 "\$pid" 2>/dev/null; then
    echo "[ERROR] INVISAP no pudo iniciar."
    tail -n 50 "\$LOG_FILE" 2>/dev/null || true
    rm -f "\$PID_FILE"
    exit 1
fi

echo "[OK] INVISAP está ejecutándose."
echo "[OK] URL: http://127.0.0.1:\${APP_PORT}/"
echo "[OK] PID: \$pid"
echo "[OK] Log: \$LOG_FILE"
echo
echo "[INFO] Para detenerlo: sudo /usr/local/bin/invisap-stop"
EOF

    cat > "$STOP_SCRIPT" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

PID_FILE=${PID_FILE@Q}

if [[ "\$EUID" -eq 0 ]]; then
    SUDO=""
else
    SUDO="sudo"
fi

if [[ -f "\$PID_FILE" ]]; then
    pid="\$(cat "\$PID_FILE" 2>/dev/null || true)"

    if [[ "\$pid" =~ ^[0-9]+$ ]] && \$SUDO kill -0 "\$pid" 2>/dev/null; then
        echo "[INFO] Deteniendo INVISAP (PID \$pid)..."
        \$SUDO kill "\$pid" 2>/dev/null || true

        for i in {1..15}; do
            if ! \$SUDO kill -0 "\$pid" 2>/dev/null; then
                break
            fi
            sleep 1
        done

        if \$SUDO kill -0 "\$pid" 2>/dev/null; then
            \$SUDO kill -9 "\$pid" 2>/dev/null || true
        fi
    fi

    rm -f "\$PID_FILE"
else
    echo "[INFO] INVISAP no tiene un PID registrado."
fi

echo "[INFO] Deteniendo MySQL..."
\$SUDO systemctl stop mysql || true

echo "[OK] INVISAP y MySQL están detenidos."
EOF

    cat > "$STATUS_SCRIPT" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail

PID_FILE=${PID_FILE@Q}
APP_PORT=${APP_PORT@Q}

if [[ -f "\$PID_FILE" ]]; then
    pid="\$(cat "\$PID_FILE" 2>/dev/null || true)"
    if [[ "\$pid" =~ ^[0-9]+$ ]] && kill -0 "\$pid" 2>/dev/null; then
        echo "[OK] INVISAP está ejecutándose (PID \$pid)."
    else
        echo "[INFO] INVISAP está detenido."
    fi
else
    echo "[INFO] INVISAP está detenido."
fi

if systemctl is-active --quiet mysql; then
    echo "[OK] MySQL está ejecutándose."
else
    echo "[INFO] MySQL está detenido."
fi

echo "[INFO] URL: http://127.0.0.1:\${APP_PORT}/"
EOF

    chmod 755 "$START_SCRIPT" "$STOP_SCRIPT" "$STATUS_SCRIPT"
    chown root:root "$START_SCRIPT" "$STOP_SCRIPT" "$STATUS_SCRIPT"

    systemctl disable mysql >/dev/null 2>&1 || true

    msg "Control manual configurado:"
    msg "  ${START_SCRIPT}"
    msg "  ${STOP_SCRIPT}"
    msg "  ${STATUS_SCRIPT}"
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
    info "Probando INVISAP mediante el iniciador manual..."

    "$START_SCRIPT"

    local code=""
    for _ in {1..15}; do
        if code="$(curl -sS --max-time 5 -o /dev/null -w "%{http_code}" "http://127.0.0.1:${APP_PORT}/" 2>/dev/null)"; then
            if [[ "$code" =~ ^[2345][0-9][0-9]$ ]]; then
                msg "Gunicorn responde correctamente (HTTP ${code})."
                "$STOP_SCRIPT"
                return 0
            fi
        fi
        sleep 1
    done

    warn "No se pudo confirmar la respuesta HTTP de INVISAP."
    tail -n 50 "$LOG_FILE" 2>/dev/null || true
    "$STOP_SCRIPT" || true
    die "La prueba HTTP de INVISAP falló."
}


validate_persistence() {
    info "Validando que NO existan arranques automáticos..."

    systemctl cat mysql.service >/dev/null || die "mysql.service no está disponible."

    if systemctl is-enabled --quiet mysql; then
        die "mysql.service sigue habilitado para arrancar automáticamente."
    fi

    if [[ -f "/etc/systemd/system/${APP_SERVICE}.service" ]]; then
        die "Todavía existe el servicio systemd personalizado de INVISAP."
    fi

    if systemctl is-enabled --quiet "$APP_SERVICE" 2>/dev/null; then
        die "El servicio ${APP_SERVICE} sigue habilitado."
    fi

    [[ -d "$MYSQL_DATA" ]] || die "No existe el directorio persistente de MySQL: ${MYSQL_DATA}"
    [[ -x "$VENV_DIR/bin/python" ]] || die "No existe el Python del entorno virtual."
    [[ -x "$VENV_DIR/bin/gunicorn" ]] || die "No existe Gunicorn en el entorno virtual."
    [[ -f "/etc/mysql/mysql.conf.d/99-invisap-recovery.cnf" ]] || die "Falta la configuración persistente de MySQL."
    [[ ! -f "/etc/systemd/system/mysql.service.d/override.conf" ]] || die "Existe un override personalizado de MySQL."
    [[ -x "$START_SCRIPT" ]] || die "Falta el iniciador manual de INVISAP."
    [[ -x "$STOP_SCRIPT" ]] || die "Falta el detenedor manual de INVISAP."
    [[ -x "$STATUS_SCRIPT" ]] || die "Falta el comprobador de estado de INVISAP."

    msg "Validación correcta: MySQL y Python NO arrancarán automáticamente."
}

show_final_information() {
    echo -e "${GREEN}============================================================${NC}"
    echo "             INSTALACIÓN COMPLETADA"
    echo -e "${GREEN}============================================================${NC}"
    echo
    echo "INVISAP quedó instalado pero detenido."
    echo
    echo "Para iniciar el sistema manualmente:"
    echo "  sudo ${START_SCRIPT}"
    echo
    echo "Para detener INVISAP y MySQL:"
    echo "  sudo ${STOP_SCRIPT}"
    echo
    echo "Para consultar el estado:"
    echo "  sudo ${STATUS_SCRIPT}"
    echo
    echo "URL cuando esté iniciado: http://127.0.0.1:${APP_PORT}/"
    echo -e "${YELLOW}NOTA: No se instaló Nginx, no se expusieron puertos y no se creó un servicio systemd para INVISAP.${NC}"
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
    validate_persistence
    show_final_information
}

main "$@"