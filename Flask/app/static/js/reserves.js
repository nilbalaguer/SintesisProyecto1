const form = document.getElementById("reservaform");
const inputs = form.getElementsByTagName("input");
const llistareserves = document.getElementById("llistareserves");
const usuari_id = llistareserves.textContent;

llistareserves.innerHTML = "";

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}


const id = getURLParameter('id');
const date = getURLParameter('date');


if (id != null) {
    document.getElementById("divCrearReserva").style.display = 'block';

    inputs[2].value = date;
    inputs[3].value = id;

    inputs[2].readOnly = true;
    inputs[3].readOnly = true;
}

fetch('/apireserves')
        .then(response => response.json())
        .then(data => {
            for (let i = 0; i < data.length; i++) {
                if (usuari_id == data[i].id_usuari) {
                    llistareserves.innerHTML += "<p>Plaça: <b>"+data[i].id_parking+"</b> | Data: <b>"+data[i].data+"</b> | <a href='/cancelarReserva?id="+ data[i].id +"&user="+ data[i].id_usuari +"'>Cancelar Reserva</a></p>";
                }
            }
        })
        .catch(error => console.error('Error al obtindre les plaçes del parking: ', error));


// Eliminar els parametres de la url
history.pushState({}, document.title, window.location.pathname);
