import os

import pytest


def test_formulario_de_acceso_se_muestra_en_el_navegador(tmp_path):
    base_url = os.getenv("INVISAP_TEST_URL")
    if not base_url:
        pytest.skip("Define INVISAP_TEST_URL para probar la interfaz con Playwright.")

    playwright_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Instala Playwright y Chromium para ejecutar la prueba visual.",
    )

    with playwright_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            response = page.goto(f"{base_url.rstrip('/')}/login", wait_until="networkidle")
            page.locator("#loader-out").wait_for(state="hidden", timeout=10000)
            forms = page.locator("form").count()
            inputs = page.locator("input").count()
            assert response is not None and response.status == 200, (
                f"GET /login debía responder HTTP 200; "
                f"respuesta={response.status if response else 'sin respuesta'}"
            )
            assert forms > 0, "La página de acceso debe contener un formulario."
            assert inputs >= 2, f"Se esperaban al menos 2 campos; encontrados: {inputs}."
            assert page.get_by_text(
                "Primero debes iniciar sesión.", exact=True
            ).count() == 0, "No debe aparecer un aviso de sesión incorrecto."
            page.screenshot(path=str(tmp_path / "playwright_login.png"), full_page=True)
        finally:
            browser.close()
