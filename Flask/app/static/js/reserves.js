const form = document.getElementById("reservaform");
const inputs = form.getElementsByTagName("input");

function getURLParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}


const id = getURLParameter('id');


if (id != null) {
    document.getElementById("divCrearReserva").style.display = 'block';

    inputs[0].value = new Date();
    inputs[1].value = id;
}