async function buscadorTable(tableId) {
  let input, busqueda, url;
  url = "/buscando-empleado";

  input = document.getElementById("search");
  busqueda = input.value.toUpperCase();

  const dataPeticion = { busqueda };

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dataPeticion)
    });
    if (!response.ok) {
      console.log(`HTTP error! status: ${response.status} 😭`);
    }

    const data = await response.json();
    if (data.fin === 0) {
      $(`#${tableId} tbody`).html("");
      $(`#${tableId} tbody`).html(`
      <tr>
        <td colspan="6" style="text-align:center;color: red;font-weight: bold;">No resultados para la busqueda: <strong style="text-align:center;color: #222;">${busqueda}</strong></td>
      </tr>`);
      return false;
    }

    if (data) {
      $(`#${tableId} tbody`).html("");
      let miData = data;
      $(`#${tableId} tbody`).append(miData);
    }
  } catch (error) {
    console.error(error);
  }
}
