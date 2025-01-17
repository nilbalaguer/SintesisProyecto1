const form = document.getElementById("reservaform");
const inputs = form.getElementsByTagName("input");

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}


const id = getURLParameter('id');
const date = getURLParameter('date');


if (id != null) {
    document.getElementById("divCrearReserva").style.display = 'block';

    inputs[0].value = date;
    inputs[1].value = id;
}

// Eliminar els parametres de la url
history.pushState({}, document.title, window.location.pathname);
