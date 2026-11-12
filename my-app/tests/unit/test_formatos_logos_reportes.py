from types import SimpleNamespace
from unittest.mock import Mock

from PIL import Image

from controllers.controller_reportesExcel import (
    LOGO_GOBERNACION,
    LOGO_GOBERNACION_BOUNDS,
    LOGO_INVILARA,
    LOGO_INVILARA_BOUNDS,
    _crear_imagen_logo,
)
from controllers.controller_reportesPDF import (
    LOGO_GOBERNACION as LOGO_GOBERNACION_PDF,
    LOGO_INVILARA as LOGO_INVILARA_PDF,
    header_footer,
)


def test_logos_excel_conservan_proporciones_y_caben_en_sus_limites():
    for ruta, limites in (
        (LOGO_GOBERNACION, LOGO_GOBERNACION_BOUNDS),
        (LOGO_INVILARA, LOGO_INVILARA_BOUNDS),
    ):
        with Image.open(ruta) as original:
            proporcion_original = original.width / original.height

        logo = _crear_imagen_logo(ruta, limites)

        assert logo.width <= limites[0]
        assert logo.height <= limites[1]
        assert abs(logo.width / logo.height - proporcion_original) < 0.02


def test_encabezado_pdf_coloca_ambos_logos_con_proporcion_preservada():
    canvas = Mock()
    doc = SimpleNamespace(
        pagesize=(612, 792),
        height=612,
        topMargin=140,
        bottomMargin=40,
        leftMargin=72,
        rightMargin=72,
    )

    header_footer(canvas, doc)

    llamadas = canvas.drawImage.call_args_list
    assert [llamada.args[0] for llamada in llamadas] == [
        LOGO_GOBERNACION_PDF,
        LOGO_INVILARA_PDF,
    ]
    assert all(llamada.kwargs['preserveAspectRatio'] for llamada in llamadas)
