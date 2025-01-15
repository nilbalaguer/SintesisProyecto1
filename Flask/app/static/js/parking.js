const botoReservarPlaca = document.getElementById("botoReservarPlaca");
botoReservarPlaca.textContent = "Reservar";

document.addEventListener("DOMContentLoaded", async function() {
    const parkingDivs = document.querySelectorAll(".parkings div[class^='div']");
    const parkingArray = Array.from(parkingDivs);

    //Fetch per obtindre dades del parking
    fetch('/apiparking')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        for (let i = 0; i < data.length; i++) {
            if (data[i].estat == "lliure") {
                parkingArray[i].classList.add("estat_lliure");
            } else if (data[i].estat == "reservat") {
                parkingArray[i].classList.add("estat_reservat");
            } else if (data[i].estat == "ocupat"){
                parkingArray[i].classList.add("estat_ocupat");
            }
            
        }
    })
    .catch(error => console.error('Error al obtindre les plaçes del parking:', error));

    parkingArray.forEach((div, index) => {
        div.textContent = `A ${index + 1}`;
        div.addEventListener("click", () => {seleccionarPlaca(index, parkingArray)});
    });
});

let seleccio = 0;

function seleccionarPlaca(id, parking) {
    seleccio = (id + 1);
    parking.forEach((div) => {
        div.classList.remove("selectedPlaca");
    })
    parking[id].classList.add("selectedPlaca");
    botoReservarPlaca.textContent = `Reservar plaça: ${id + 1}`;
    botoReservarPlaca.classList.add("selectedButon");
    botoReservarPlaca.addEventListener("click", () => {enviarReserva(id)})
}

function enviarReserva(id) {
    console.log("Reserva: " + (id+1));
}