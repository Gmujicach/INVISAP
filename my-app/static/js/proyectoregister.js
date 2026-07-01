document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("formRegistrarProyecto");
    if (!formulario) return;

    const solicitudId = document.getElementById("solicitud_id_p");
    const errorSolicitudDiv = document.getElementById("solicitud_error_message");
    const fechaPlan = document.getElementById("fecha_p");
    const observaciones = document.getElementById("observaciones");
    const computos = document.getElementById("computos_p");
    const estimacion = document.getElementById("estimacion_p");
    const codigoProyecto = document.getElementById("Codigo_p");


    function marcarInvalido(input, mensaje) {
        if (!input) return;
        input.classList.remove("is-valid");
        input.classList.add("is-invalid");

        let contenedorPadre = input.parentElement;
        if (contenedorPadre.classList.contains("input-group")) {
            contenedorPadre = contenedorPadre.parentElement;
        }

        let feedback = contenedorPadre.querySelector(".invalid-feedback");
        if (!feedback) {
            feedback = document.createElement("div");
            feedback.className = "invalid-feedback d-block";
            contenedorPadre.appendChild(feedback);
        }
        feedback.innerText = mensaje;
    }

    function marcarValido(input) {
        if (!input) return;
        input.classList.remove("is-invalid");
        input.classList.add("is-valid");

        let contenedorPadre = input.parentElement;
        if (contenedorPadre.classList.contains("input-group")) {
            contenedorPadre = contenedorPadre.parentElement;
        }

        const feedback = contenedorPadre.querySelector(".invalid-feedback");
        if (feedback) feedback.remove();
    }

    
    if (estimacion) {
        estimacion.addEventListener("input", function () {
            let valor = estimacion.value.replace(/\D/g, "");
            if (valor === "") {
                estimacion.value = "";
                return;
            }
            let entero = parseInt(valor, 10);
            if (isNaN(entero)) {
                estimacion.value = "";
                return;
            }
            let opciones = { minimumFractionDigits: 2, maximumFractionDigits: 2 };
            estimacion.value = (entero / 100).toLocaleString("de-DE", opciones);
            marcarValido(estimacion);
        });
    }

    
    if (observaciones) {
        observaciones.addEventListener("input", function () {
            if (observaciones.value.trim().length >= 10) {
                marcarValido(observaciones);
            } else {
                marcarInvalido(observaciones, "La descripción técnica debe tener al menos 10 caracteres.");
            }
        });
    }
    if (codigoProyecto) {
        codigoProyecto.addEventListener("input", function () {
          
            let valor = codigoProyecto.value.toUpperCase().replace(/[^A-Z0-9]/g, "");
           
            if (valor.length > 3) {
                valor = valor.slice(0, 3) + "-" + valor.slice(3);
            }
            
          
            codigoProyecto.value = valor;

         
            if (codigoProyecto.value.trim().length >= 5) {
                marcarValido(codigoProyecto);
            } else {
           
                marcarInvalido(codigoProyecto, "El formato debe comenzar con 3 letras seguido de un guion y el número (Ej: PRY-001).");
            }
        });
        codigoProyecto.addEventListener("keydown", function (e) {
            if (e.key === "Backspace" && codigoProyecto.value.length === 5) {
                
                codigoProyecto.value = codigoProyecto.value.replace("-", "");
            }
        });
    }

    formulario.addEventListener("submit", function (e) {
        let tieneErrores = false;


        if (solicitudId && !solicitudId.value) {
            if (errorSolicitudDiv) errorSolicitudDiv.classList.remove("d-none");
            tieneErrores = true;
        } else {
            if (errorSolicitudDiv) errorSolicitudDiv.classList.add("d-none");
        }

        
        if (fechaPlan && !fechaPlan.value) {
            marcarInvalido(fechaPlan, "Debe seleccionar una fecha de planificación.");
            tieneErrores = true;
        } else if (fechaPlan) {
            marcarValido(fechaPlan);
        }


        if (observaciones && observaciones.value.trim().length < 10) {
            marcarInvalido(observaciones, "La descripción técnica debe tener al menos 10 caracteres.");
            tieneErrores = true;
        }

       
        if (codigoProyecto && codigoProyecto.value.trim() === "") {
            marcarInvalido(codigoProyecto, "El código del proyecto es obligatorio (Ej: PRY-001).");
            tieneErrores = true;
        }

      
        if (tieneErrores) {
            e.preventDefault(); 
            const primerError = formulario.querySelector(".is-invalid");
            if (primerError) primerError.focus();
        } else {
        
            if (estimacion && estimacion.value.trim() !== "") {
                estimacion.value = estimacion.value.replace(/\./g, "").replace(",", ".");
            }
        }
    });
});

function confirmarEliminacion(elemento) {
    const url = elemento.getAttribute('data-delete-url');
    
    Swal.fire({
        title: '¿Estás seguro?',
        text: "¡No podrás revertir esta acción!",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Sí, eliminar',
        cancelButtonText: 'Cancelar'
    }).then((result) => {
        if (result.isConfirmed) {
           
            window.location.href = url;
        }
    });
}
