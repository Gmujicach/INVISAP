const loaderOut = document.querySelector("#loader-out");
function fadeOut(element) {
  let opacity = 1;
  const timer = setInterval(function () {
    if (opacity <= 0.1) {
      clearInterval(timer);
      element.style.display = "none";
    }
    element.style.opacity = opacity;
    opacity -= opacity * 0.1;
  }, 50);
}
fadeOut(loaderOut);

function eliminarEmpleado(id_empleado, foto_empleado) {
  if (confirm("¿Estas seguro que deseas Eliminar el empleado?")) {
    fetch(`/borrar-empleado/${id_empleado}/${foto_empleado}`)
      .then(function(response) { return response.json(); })
      .then(function(data) {
        if (data && data.status === 'success') {
          // Se retira la fila afectada sin recargar la página.
          const fila = document.querySelector(
            `tr[data-id-empleado="${id_empleado}"], tr[data-id="${id_empleado}"]`
          );
          if (fila) {
            fila.style.transition = 'opacity 0.4s';
            fila.style.opacity = '0';
            setTimeout(function () { fila.remove(); }, 400);
          } else if (window.INVISAP_AJAX) {
            window.INVISAP_AJAX.refrescarListadoActual('tablaEmpleados', { origen: 'home' });
          } else {
            location.reload();
          }
        } else {
          alert(data && data.message ? data.message : 'Error al eliminar');
        }
      })
      .catch(function() {
        alert('Error de conexión');
      });
  }
}
