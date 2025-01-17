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

    inputs[2].value = date;
    inputs[3].value = id;

    inputs[2].addEventListener("keydown", function (event) {
        event.preventDefault();
    });
    
    inputs[3].addEventListener("keydown", function (event) {
        event.preventDefault();
    });
}

// Eliminar els parametres de la url
history.pushState({}, document.title, window.location.pathname);
