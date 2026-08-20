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
          location.reload();
        } else {
          alert(data && data.message ? data.message : 'Error al eliminar');
        }
      })
      .catch(function() {
        alert('Error de conexión');
      });
  }
}
