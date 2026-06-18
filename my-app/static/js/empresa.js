document.addEventListener('DOMContentLoaded', function() {
    document.body.addEventListener('click', function(e) {
        // Buscamos si el clic fue en el botón con la clase .btn-eliminar
        const boton = e.target.closest('.btn-eliminar');
        
        if (boton) {
            e.preventDefault(); // Evita que la página salte arriba por el '#'
            
            const urlEliminar = boton.getAttribute('data-url');
            const nombreObjeto = boton.getAttribute('data-nombre') || 'este registro';

            // Lanzamos la alerta estilizada
            Swal.fire({
                title: '¿Estás seguro?',
                text: `Deseas eliminar la Empresa: ${nombreObjeto}. ¡Esta acción no se puede deshacer!`,
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Si acepta, Flask se encarga del resto
                    window.location.href = urlEliminar;
                }
            });
        }
    });
});