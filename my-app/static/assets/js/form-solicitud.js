document.addEventListener('DOMContentLoaded', function() {
    const selectorTipo = document.getElementById('tipo_solicitud');
    
    // Objeto que mapea el valor del select con el ID del contenedor
    const secciones = {
      'Comunidad': 'seccion_comunidad',
      'Institucion': 'seccion_institucion',
      'Particular': 'seccion_particular'
    };

    selectorTipo.addEventListener('change', function() {
      // 1. Ocultamos todas las secciones y deshabilitamos sus inputs
      Object.values(secciones).forEach(idSeccion => {
        const div = document.getElementById(idSeccion);
        div.style.display = 'none';
        
        // Seleccionamos todos los inputs, selects y textareas dentro del div oculto
        const elementos = div.querySelectorAll('input, select, textarea');
        elementos.forEach(el => {
          el.disabled = true; // Al deshabilitar, el navegador no valida el "required" oculto ni envía datos basura
        });
      });

      // 2. Mostramos solo la sección seleccionada y habilitamos sus inputs
      const seleccionActual = selectorTipo.value;
      if (secciones[seleccionActual]) {
        const divActivo = document.getElementById(secciones[seleccionActual]);
        divActivo.style.display = 'block';
        
        const elementosActivos = divActivo.querySelectorAll('input, select, textarea');
        elementosActivos.forEach(el => {
          el.disabled = false; // Rehabilitamos los campos para que el usuario pueda escribir y validarse
        });
      }
    });
  });