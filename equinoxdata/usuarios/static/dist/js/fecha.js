let cardElement = document.querySelector(".card");

function startTime() {
  var weekday = new Array();
  weekday[0] = "Domingo";
  weekday[1] = "Lunes";
  weekday[2] = "Martes";
  weekday[3] = "Miercoles";
  weekday[4] = "Jueves";
  weekday[5] = "Viernes";
  weekday[6] = "Sabado";
  var month = new Array();
  month[0] = "January";
  month[1] = "February";
  month[2] = "March";
  month[3] = "April";
  month[4] = "May";
  month[5] = "June";
  month[6] = "July";
  month[7] = "August";
  month[8] = "September";
  month[9] = "Octubre";
  month[10] = "November";
  month[11] = "December";
  var today = new Date();
  var d = today.getDate();
  var y = today.getFullYear();
  var wd = weekday[today.getDay()];
  var mt = month[today.getMonth()];

  document.getElementById("date").innerHTML = d;
  document.getElementById("day").innerHTML = wd;
  document.getElementById("month").innerHTML = mt + "/" + y;

  var t = setTimeout(startTime, 500);
}
function checkTime(i) {
  if (i < 10) {
    i = "0" + i;
  }
  return i;
}

// js para manejar modals productos


  // Modal de creación
  $('#crearProductoBaseModal').on('show.bs.modal', function () {
    // Aquí podrías reiniciar el formulario si fuera necesario
    $('#crearProductoBaseForm')[0].reset();
  });

  // Modal de edición
  $('#editarProductoBaseModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Botón que activó el modal
    var productoId = button.data('id'); // Extraer información del atributo data-id

    // Llenar el formulario de edición con los datos correspondientes
    $.ajax({
      url: "{% url 'productos:producto_base_editar' 0 %}".replace('0', productoId),
      method: "GET",
      success: function (response) {
        // Asumimos que el formulario se encuentra dentro del modal y que es reemplazado con los datos del producto
        $('#editarProductoBaseModal .modal-body').html(response.html);
      }
    });
  });

  // Modal de eliminación
  $('#confirmDeleteModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget); // Botón que activó el modal
    var productoId = button.data('id'); // Extraer el id del producto a eliminar

    $('#confirmDeleteBtn').on('click', function () {
      // Realizar la eliminación con AJAX o redirigir a la URL de eliminación
      $.ajax({
        url: "{% url 'productos:producto_base_eliminar' 0 %}".replace('0', productoId),
        method: "DELETE",
        success: function (response) {
          // Cerrar el modal
          $('#confirmDeleteModal').modal('hide');
          // Actualizar la tabla o hacer algo más
          location.reload();
        }
      });
    });
  });

