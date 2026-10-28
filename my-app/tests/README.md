# Pruebas de INVISAP con pytest

Desde PowerShell, ejecuta los comandos en `my-app`. Pytest muestra cada caso
con su nombre y el porcentaje de avance; el resumen final indica cuántos
pasaron, fallaron o fueron omitidos.

```powershell
python -m pytest
```

## Carpetas

- `unit`: validaciones y lógica de un módulo aislado.
- `integration`: colaboración entre componentes, como rutas, controladores,
  modelos y bitácora.
- `api`: pruebas de endpoints HTTP del backend.
- `smoke`: comprobaciones rápidas de que una parte esencial de la aplicación
  responde.
- `ui`: pruebas del navegador con Playwright.
- `performance`: reservado para pruebas de carga con Locust. Locust es una
  herramienta aparte y estas pruebas no se ejecutan con pytest.
- `acceptance`: reservado para recorridos completos según criterios de
  aceptación definidos por el negocio.

## Ejecutar una categoría

```powershell
python -m pytest tests\unit
python -m pytest tests\integration
python -m pytest tests\api
python -m pytest tests\smoke
python -m pytest tests\ui
```

Para un módulo, indica su archivo. Por ejemplo:

```powershell
python -m pytest tests\unit\test_gravedad_obra.py
python -m pytest tests\unit\test_prioridad.py
python -m pytest tests\unit\test_proyectos.py
```

`tests\performance` y `tests\acceptance` documentan categorías que todavía
necesitan escenarios ejecutables. No son pruebas aprobadas mientras no haya
casos implementados en esas carpetas.

## Prueba de interfaz con Playwright

Inicia la aplicación y configura su URL antes de ejecutar la prueba:

```powershell
$env:INVISAP_TEST_URL = "http://127.0.0.1:5600"
python -m pytest tests\ui
```

Si no se define la URL, o Playwright/Chromium no está instalado, pytest marcará
la prueba visual como omitida. No contará como una prueba aprobada.
