document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("formEditarProyecto");
      
    if (!formulario) return;

    const fechaPlan = document.getElementById("fecha_p") || document.getElementsByName("fecha_p")[0];
    const observaciones = document.getElementById("observaciones") || document.getElementsByName("observaciones")[0];
    const computos = document.getElementById("computos_p") || document.getElementsByName("computos_p")[0];
    const estimacion = document.getElementById("estimacion_p") || document.getElementsByName("estimacion_p")[0];


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
        if (feedback) {
            feedback.remove();
        }
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

      
        estimacion.addEventListener("focus", function() {
            if(estimacion.value === "0,00") {
                estimacion.value = "";
            }
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

    formulario.addEventListener("submit", function (e) {
        let tieneErrores = false;

       
        if (fechaPlan) {
            if (!fechaPlan.value) {
                marcarInvalido(fechaPlan, "Por favor, seleccione una fecha de planificación.");
                tieneErrores = true;
            } else {
                marcarValido(fechaPlan);
            }
        }

        
        if (observaciones) {
            if (observaciones.value.trim().length < 10) {
                marcarInvalido(observaciones, "La descripción técnica debe tener al menos 10 caracteres.");
                tieneErrores = true;
            } else {
                marcarValido(observaciones);
            }
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