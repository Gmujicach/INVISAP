document.addEventListener("DOMContentLoaded", () => {
    const formGravedad = document.getElementById("formGravedad");
    const selectNivel = document.getElementById("selectNivel");

    // Validación de Existencia (Req. Prof. Escalona)
    selectNivel.addEventListener("change", async (e) => {
        const nivelSeleccionado = e.target.value;
        try {
            // Simulamos consulta dinámica al backend para verificar estado=1
            const response = await fetch(`/api/gravedad/validar?nivel=${nivelSeleccionado}`);
            const data = await response.json();
            
            if (!data.activo) {
                alert("Atención: Este nivel de gravedad ha sido desactivado en el catálogo.");
                e.target.value = ""; // Resetea el campo
            }
        } catch (error) {
            console.error("Error validando el catálogo:", error);
        }
    });

    // Envío del formulario mediante Fetch API para evitar recarga
    formGravedad.addEventListener("submit", async (e) => {
        e.preventDefault(); // Previene la recarga tradicional de la página

        const formData = new FormData(formGravedad);
        
        try {
            const response = await fetch("/api/gravedad/registrar", {
                method: "POST",
                body: formData
            });

            if (response.ok) {
                alert("Nivel de gravedad registrado exitosamente.");
                formGravedad.reset();
            } else {
                alert("Error en el servidor al procesar la solicitud.");
            }
        } catch (error) {
            console.error("Error en la transacción Ajax:", error);
            alert("Error de conexión con el backend.");
        }
    });
});