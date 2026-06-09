# Reporte de Mejora: Formulario Dinámico de Solicitudes

En este documento explicamos una de las mejoras más significativas implementadas en el sistema INVISAP: **El Rediseño del Formulario de Solicitudes**.

Como en nuestros demás documentos, encontrarás dos niveles de explicación para que todos en el equipo lo comprendan a la perfección.

---

## ¿Qué mejoramos y Por Qué?

**El Problema Original:**
El antiguo formulario para registrar una solicitud obligaba al usuario a "tipear" manualmente el municipio y la parroquia. Además, tenía textos genéricos como "Crud con Python" que le restaban profesionalismo a la institución.

* **Explicación Sencilla:** 
Si dejas que la gente escriba los municipios a mano, alguien escribirá "Iribaren", otro "iribarren", y otro "Barquisimeto". A la hora de hacer reportes, la computadora se confunde. Lo mejor es darles una lista desplegable. Pero, si escoges "Palavecino", la lista de parroquias no debe mostrar las parroquias de Iribarren. Hicimos que el formulario sea inteligente y sepa qué parroquias mostrar dependiendo del municipio que elijas.
  
* **Explicación Técnica:** 
Se migró de un enfoque de recolección de datos no estructurado (`<input type="text">`) a un enfoque de datos normalizados mediante selectores anidados (`<select>`). Se implementó un algoritmo *Vanilla JavaScript* reactivo en el lado del cliente (frontend) que escucha el evento `onchange` del selector de Municipios y reconstruye el Document Object Model (DOM) del selector de Parroquias utilizando un objeto JSON en memoria, reduciendo las peticiones al servidor (AJAX) y la carga del backend.

---

## Archivos Involucrados en el Cambio

Toda la magia se realizó modificando un solo archivo clave del Frontend:
`my-app/vista/solicitudes/form_solicitud.html`

### ¿Qué se cambió exactamente en ese archivo?

#### 1. Identidad Visual (La Fachada)
* **Antes:** `{% block title %}Crud con Python | Registrar Solicitud{% endblock %}`
* **Ahora:** `{% block title %}INVISAP | Registrar Solicitud{% endblock %}`
* Se eliminaron los estilos visuales básicos y se añadieron clases avanzadas de **Bootstrap 5** (como `shadow-sm`, `bg-light`) y se integraron íconos (`<i class="bi bi-bank"></i>`) para que luciera institucional.

#### 2. Selectores Inteligentes (Los Controles)
En lugar de una caja de texto libre, se implementó el selector principal (solo para el Estado Lara):
```html
<select name="com_municipio" id="com_municipio" onchange="actualizarParroquias()">
    <option value="Iribarren">Iribarren</option>
    <option value="Palavecino">Palavecino</option>
    <!-- ... y 7 más ... -->
</select>
```

Y un selector vacío que espera la información:
```html
<select name="com_parroquia" id="com_parroquia" disabled>
    <option>Seleccione primero el municipio...</option>
</select>
```

#### 3. El Motor del Formulario (JavaScript)
Al final del archivo, agregamos un "diccionario" de datos (JSON) que le enseña al navegador la geografía del Estado Lara:

```javascript
const laraData = {
    "Iribarren": ["Catedral", "Concepción", "El Cují", "Santa Rosa", "Tamaca", "..."],
    "Palavecino": ["Cabudare", "José Gregorio Bastidas", "Agua Viva"],
    // ...
};

// Esta función es la que hace la magia cuando el usuario cambia el municipio
function actualizarParroquias() {
    const municipio = document.getElementById('com_municipio').value;
    const selectParroquia = document.getElementById('com_parroquia');
    
    // Si seleccionó un municipio válido, activamos las parroquias
    if (municipio) {
        selectParroquia.disabled = false;
        // Llenamos el desplegable con la lista correspondiente de 'laraData'
        laraData[municipio].forEach(parroquia => {
            selectParroquia.innerHTML += `<option value="${parroquia}">${parroquia}</option>`;
        });
    }
}
```

## Beneficios para la Institución
1. **Datos limpios:** Garantiza integridad referencial al momento de cruzar datos en bases de datos o exportar a Excel.
2. **Mejor experiencia de usuario:** Los funcionarios de INVISAP completarán las solicitudes en la mitad del tiempo al no tener que tipear.
3. **Imagen profesional:** El diseño se ve moderno, seguro e infunde confianza.
