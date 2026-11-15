# Formatos de planificación y especificación

Estos archivos son plantillas editables para completar con los responsables
del proyecto y conservar como evidencia. La ejecución automatizada y los
resultados comprobados se documentan aparte en
[`CAPITULO_IV_INVISAP.md`](../../CAPITULO_IV_INVISAP.md).

## Descargas

- [Planificación y bitácora de pruebas de Unidad, Integración y Sistema](Plantilla_Plan_Pruebas_Unidad_Integracion_Sistema.xlsx)
- [Especificación de Pruebas de Requerimientos Funcionales](Plantilla_Especificacion_Pruebas_RF.xlsx)
- [Matriz de Trazabilidad de Pruebas de INVISAP](Matriz_Trazabilidad_Pruebas_INVISAP.docx)

La matriz de INVISAP conserva las seis columnas del formato institucional y
traza los RF/RNF del SRS (borrador) con las suites automatizadas disponibles.
Los IDs de caso son provisionales; las filas pendientes señalan brechas, no
resultados aprobados. Para regenerarla con la plantilla original:

```powershell
python tests\documentation\generate_traceability_matrix.py `
  --template "ruta\Matriz de Trazabilidad de Pruebas.docx"
```

## Uso

1. En el plan, completar el ambiente autorizado, fecha programada, lugar,
   responsables, criterios de entrada/salida y observaciones.
2. En la especificación, crear un registro por caso e indicar ID del requisito
   aprobado. Los códigos `UT-GRA-001` e `IT-CON-01` del capítulo son IDs de
   seguimiento de ejemplo; no sustituyen IDs del documento de requisitos.
3. Registrar entradas/pasos, resultado esperado y resultado observado por
   separado. Guardar evidencia con una ruta estable.
4. Si aparece un error, asignar un ID de incidencia, describir la corrección
   aplicada y guardar el resultado del retest. Si se simuló intencionalmente
   un error, identificarlo como tal; no registrarlo como defecto abierto.
5. Dejar la evaluación de conformidad, nombre y firma al validador funcional.
   Las pruebas automatizadas no reemplazan la aceptación del tutor o usuarios.

Las fechas y nombres de responsables no disponibles se dejan pendientes de
confirmación: no se completan con valores supuestos.

## Contratos de backend en Postman

Las solicitudes de
[`postman/collections/INVISAP - Pruebas de Contrato HTTP`](../../postman/collections/INVISAP%20-%20Pruebas%20de%20Contrato%20HTTP)
son complementarias a `tests/api`, que se ejecuta con el cliente de prueba
Flask y modelos simulados. Las solicitudes Postman hacen peticiones HTTP al
servidor configurado y no sustituyen las pruebas unitarias ni los casos de
integración simulados.

- Configura `baseUrl` y, para los contratos autenticados, `session_cookie` con
  el encabezado completo `session=<cookie>` de una cuenta de pruebas en el
  entorno local de Postman. También configura IDs de registros que existan
  para empresa, evidencia, informe, usuario, rol y proyecto.
- `Login.request.yaml` usa `login_username`, `login_password` y
  `recaptcha_token`, sin valores de acceso guardados en el repositorio. La
  verificación de login exige que la respuesta deje de mostrar el formulario.
- Ejecuta primero `Acceso API sin sesión.request.yaml`: debe responder HTTP
  401 y no divulgar solicitudes. Después inicia sesión y ejecuta los contratos
  GET de módulos.
- Los contratos actuales comprueban principalmente estado HTTP, tipo de
  contenido y que el cuerpo sea JSON o HTML. Agrega aserciones de esquema,
  campos y resultados esperados específicos para cada endpoint antes de
  considerar completa la validación funcional.
- No guardes contraseñas, tokens de reCAPTCHA ni cookies en el entorno
  compartido/commiteado ni en capturas o bitácoras. No ejecutes operaciones
  modificadoras contra producción.

La presencia de los archivos de solicitudes no demuestra que la colección se
haya ejecutado. Registra como resultado Postman únicamente una ejecución
realizada contra el servidor y los datos de prueba autorizados, con resumen y
fecha; no se debe inferir el resultado positivo de API desde pytest.
