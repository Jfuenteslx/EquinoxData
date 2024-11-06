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
