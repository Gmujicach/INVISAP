/* =========================================
   LÓGICA DE PAGINACIÓN Y BÚSQUEDA DEL CLIENTE
   ========================================= */
document.addEventListener('DOMContentLoaded', function() {
    const busquedaRapida = document.getElementById('buscarBitacora');
    const tbody = document.querySelector('#tabla-bitacora tbody');
    
    // Verificamos si existe el tbody (por si hay un error en la carga HTML)
    if (!tbody) return;

    // Convertimos la lista de nodos (tr) a un Array. Ignoramos la fila vacía de aviso.
    const filas = Array.from(tbody.querySelectorAll('tr.fila-registro'));
    
    // Variables de Estado de la Paginación
    const filasPorPagina = 5;
    let paginaActual = 1;
    let filasVisibles = [];

    /**
     * Paso 1: Configurar el estado base y el total de páginas.
     * Esta función se llama al inicio y cada vez que el usuario hace una búsqueda rápida.
     */
    function inicializarPaginacion() {
        // Obtenemos solo las filas que NO tienen la clase oculta (Las que coinciden con la búsqueda)
        filasVisibles = filas.filter(fila => !fila.classList.contains('oculto-por-busqueda'));

        // Si no se encuentra ningún registro, limpiamos los botones
        if (filasVisibles.length === 0) {
            document.getElementById('paginacion-container').innerHTML = '';
            filas.forEach(f => f.style.display = 'none');
            return;
        }

        const totalPaginas = Math.ceil(filasVisibles.length / filasPorPagina);
        
        // Prevención de errores de índice al realizar búsquedas fuertes
        if (paginaActual > totalPaginas) paginaActual = totalPaginas;
        if (paginaActual < 1) paginaActual = 1;

        mostrarFilasActuales();
        renderizarBotonesPaginacion(totalPaginas);
    }

    /**
     * Paso 2: Iterar sobre los registros y mostrar solo los 10 que tocan en la página actual.
     */
    function mostrarFilasActuales() {
        // Restablecemos el display en none para todos los registros del Array original
        filas.forEach(fila => fila.style.display = 'none');

        // Calculamos los offsets
        const inicio = (paginaActual - 1) * filasPorPagina;
        const fin = inicio + filasPorPagina;

        // Visualizamos el segmento correspondiente
        for (let i = inicio; i < fin && i < filasVisibles.length; i++) {
            filasVisibles[i].style.display = '';
        }
    }

    /**
     * Paso 3: Renderizar la estructura HTML de la botonera dinámica de Bootstrap.
     */
    function renderizarBotonesPaginacion(totalPaginas) {
        const contenedor = document.getElementById('paginacion-container');
        
        if (totalPaginas <= 1) {
            contenedor.innerHTML = '';
            return;
        }

        let html = '<ul class="pagination pagination-sm">';

        // Configuración de Botón "Anterior"
        html += `<li class="page-item ${paginaActual === 1 ? 'disabled' : ''}">
                    <a class="page-link shadow-none" href="#" data-page="${paginaActual - 1}">Anterior</a>
                 </li>`;

        // Lógica para limitar a 5 botones numerados como máximo y no saturar la vista
        let paginaInicio = Math.max(1, paginaActual - 2);
        let paginaFin = Math.min(totalPaginas, paginaActual + 2);

        if (paginaActual <= 3 && totalPaginas >= 5) { paginaFin = 5; }
        if (paginaActual >= totalPaginas - 2 && totalPaginas >= 5) { paginaInicio = totalPaginas - 4; }

        for (let i = paginaInicio; i <= paginaFin; i++) {
            html += `<li class="page-item ${i === paginaActual ? 'active' : ''}">
                        <a class="page-link shadow-none" href="#" data-page="${i}">${i}</a>
                     </li>`;
        }

        // Configuración de Botón "Siguiente"
        html += `<li class="page-item ${paginaActual === totalPaginas ? 'disabled' : ''}">
                    <a class="page-link shadow-none" href="#" data-page="${paginaActual + 1}">Siguiente</a>
                 </li>`;

        html += '</ul>';
        contenedor.innerHTML = html;

        // Escucha de eventos de clic sobre los botones creados
        contenedor.querySelectorAll('.page-link').forEach(boton => {
            boton.addEventListener('click', function(e) {
                e.preventDefault();
                const nuevaPagina = parseInt(this.getAttribute('data-page'));
                
                if (!isNaN(nuevaPagina) && nuevaPagina >= 1 && nuevaPagina <= totalPaginas) {
                    paginaActual = nuevaPagina;
                    mostrarFilasActuales();
                    renderizarBotonesPaginacion(totalPaginas);
                }
            });
        });
    }

    /**
     * Paso 4: Lógica combinada entre Paginación y Barra de Búsqueda Rápida Frontend
     */
    if (busquedaRapida) {
        busquedaRapida.addEventListener('keyup', function () {
            const filtro = this.value.toLowerCase();
            
            filas.forEach(fila => {
                // Comparamos los caracteres tipeados con todo el string de la tabla
                if(fila.textContent.toLowerCase().includes(filtro)) {
                    fila.classList.remove('oculto-por-busqueda');
                } else {
                    fila.classList.add('oculto-por-busqueda');
                }
            });

            // Forzamos la tabla a retornar a la página 1 cuando cambia el set de datos
            paginaActual = 1; 
            inicializarPaginacion();
        });
    }

    // Arranque inicial cuando la página carga los registros de tu base de datos Flask
    if (filas.length > 0) {
        inicializarPaginacion();
    }
});