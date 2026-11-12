@echo off
REM Evita mostrar cada comando mientras se ejecuta el archivo.
REM Activa la expansion retardada para leer variables actualizadas dentro de bloques.
setlocal EnableDelayedExpansion

REM ============================================================
REM CONFIGURACION PARA CADA COMPUTADORA
REM Cambia la siguiente ruta por la carpeta donde esta el proyecto
REM en tu computadora. Debe ser la carpeta que contiene run.py,
REM requirements-actualizado.txt y donde se creara o ya existe .venv.
REM Ejemplo: set "project_dir=C:\mis-proyectos\INVISAP\my-app"
REM Este archivo .bat puede estar en otra carpeta, como el Escritorio.
REM ============================================================
set "project_dir=D:\laragon\www\INVISAP\my-app"

REM Comprueba que la ruta configurada sea correcta antes de continuar.
if not exist "%project_dir%\run.py" (
    echo ERROR: No se encontro run.py en "%project_dir%".
    pause
    exit /b 1
)

REM Cambia la carpeta de trabajo al proyecto (tambien funciona si cambia de unidad).
cd /d "%project_dir%"

REM Recuerda si este script tuvo que crear el entorno virtual.
REM Solo en ese caso se instalaran las dependencias desde el archivo de requirements.
set "venv_created=0"
if not exist ".venv\Scripts\activate.bat" (
    echo No se encontro el entorno virtual. Creandolo en:
    echo %CD%\.venv
    REM Crea .venv dentro de la carpeta del proyecto; requiere Python instalado y disponible en PATH.
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual. Verifica que Python este instalado.
        pause
        exit /b 1
    )
    set "venv_created=1"
)

REM Confirma que el entorno exista y tenga el archivo necesario para activarlo.
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: No se encontro el activador del entorno virtual despues de crearlo.
    pause
    exit /b 1
)

REM Activa el entorno virtual del proyecto para usar sus paquetes y su interprete de Python.
call ".venv\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

REM Instala las dependencias solamente cuando .venv se acaba de crear.
if "!venv_created!"=="1" (
    if not exist "requirements-actualizado.txt" (
        echo ERROR: No se encontro requirements-actualizado.txt para instalar las dependencias.
        pause
        exit /b 1
    )

    echo Instalando las dependencias del proyecto. Esto puede tardar unos minutos...
    REM requirements-actualizado.txt esta guardado en UTF-16.
    REM Se convierte temporalmente a UTF-8 para que pip pueda leerlo sin modificar el original.
    set "requirements_file=%TEMP%\invisap-requirements-%RANDOM%-%RANDOM%.txt"
    powershell -NoProfile -Command "$content = [IO.File]::ReadAllText('requirements-actualizado.txt', [Text.Encoding]::Unicode); [IO.File]::WriteAllText('!requirements_file!', $content, [Text.UTF8Encoding]::new($false))"
    if errorlevel 1 (
        echo ERROR: No se pudo preparar requirements-actualizado.txt para pip.
        pause
        exit /b 1
    )

    REM Instala los paquetes enumerados en el archivo temporal dentro del entorno virtual.
    python -m pip install -r "!requirements_file!"
    set "install_exit_code=!ERRORLEVEL!"
    REM Borra el archivo temporal y muestra un error si pip no pudo instalar los paquetes.
    del "!requirements_file!" >nul 2>&1
    if not "!install_exit_code!"=="0" (
        echo ERROR: No se pudieron instalar las dependencias del proyecto.
        pause
        exit /b !install_exit_code!
    )
)

REM Inicia la aplicacion Flask; la salida sin buffer permite ver los logs inmediatamente.
echo Iniciando el servidor Flask desde:
echo %CD%
echo.
set "FLASK_DEBUG=1" && python -u run.py

REM Conserva el codigo de salida del servidor para informar si termino con error.
set "exit_code=%ERRORLEVEL%"
if not "%exit_code%"=="0" (
    echo.
    echo El servidor termino con un error (codigo %exit_code%).
)
REM Espera una tecla para que la ventana no se cierre y se puedan leer los mensajes.
pause
exit /b %exit_code%
