/* =========================================
   BÚSQUEDA RÁPIDA EN LA PÁGINA ACTUAL
   ========================================= */
document.addEventListener('DOMContentLoaded', function() {
    const busquedaRapida = document.getElementById('buscarBitacora');
    const tbody = document.querySelector('#tabla-bitacora tbody');

    if (!tbody) return;

    const filas = Array.from(tbody.querySelectorAll('tr.fila-registro'));

    function aplicarBusqueda() {
        if (!busquedaRapida) return;

        const filtro = busquedaRapida.value.trim().toLowerCase();

        filas.forEach(fila => {
            const coincide = !filtro || fila.textContent.toLowerCase().includes(filtro);
            fila.style.display = coincide ? '' : 'none';
        });
    }

    if (busquedaRapida) {
        busquedaRapida.addEventListener('keyup', aplicarBusqueda);
    }

    aplicarBusqueda();
});