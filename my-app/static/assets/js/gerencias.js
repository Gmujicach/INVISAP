// Gerencia script

document.getElementById('btn-agregar-telefono').addEventListener('click', function() {
    // 1. Seleccionamos el contenedor
    const contenedor = document.getElementById('contenedor-telefonos');
    
    // 2. Creamos un nuevo grupo de input con su botón de eliminar
    const nuevoGrupo = document.createElement('div');
    nuevoGrupo.className = 'input-group mb-2';
    
    nuevoGrupo.innerHTML = `
        <input
            type="text"
            name="telefono_gerente[]"
            class="form-control"
            maxlength="20"
            required />
        <button class="btn btn-outline-danger btn-eliminar-telefono" type="button">
            ×
        </button>
    `;
    
    // 3. Lo metemos en el contenedor
    contenedor.appendChild(nuevoGrupo);
    
    // 4. Lógica para que el botón de eliminar (×) funcione si lo presionan
    nuevoGrupo.querySelector('.btn-eliminar-telefono').addEventListener('click', function() {
        nuevoGrupo.remove();
    });
});