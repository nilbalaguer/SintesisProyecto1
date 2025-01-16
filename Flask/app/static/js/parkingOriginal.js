const botoReservarPlaca = document.getElementById("botoReservarPlaca");
const indicadorOcupacio = document.getElementById("indicadorOcupacio");
botoReservarPlaca.textContent = "Reservar";

document.addEventListener("DOMContentLoaded", async function() {
    const parkingDivs = document.querySelectorAll(".parkings div[class^='div']");
    const parkingArray = Array.from(parkingDivs);

    //Fetch per obtindre dades del parking
    fetch('/apiparking')
    .then(response => response.json())
    .then(data => {
        console.log(data);
        let contadorlliures = 0;

        for (let i = 0; i < data.length; i++) {
            if (data[i].estat == "lliure") {
                parkingArray[i].classList.add("estat_lliure");
                contadorlliures += 1;
            } else if (data[i].estat == "reservat") {
                parkingArray[i].classList.add("estat_reservat");
            } else if (data[i].estat == "ocupat"){
                parkingArray[i].classList.add("estat_ocupat");
            }
            
        }

        indicadorOcupacio.innerHTML = "Ocupacio: " + Math.round(contadorlliures*100/42) + " %<br>Plaçes lliures: " + contadorlliures;
    })
    .catch(error => console.error('Error al obtindre les plaçes del parking:', error));

    parkingArray.forEach((div, index) => {
        div.textContent = `P ${index + 1}`;
        div.addEventListener("click", () => {seleccionarPlaca(index, parkingArray)});
    });
});

let seleccio = 0;

botoReservarPlaca.addEventListener("click", () => {enviarReserva(seleccio)});

function seleccionarPlaca(id, parking) {
    seleccio = id;
    if (parking[id].classList.contains("estat_lliure")) {
        parking.forEach((div) => {
            div.classList.remove("selectedPlaca");
        });
        parking[id].classList.add("selectedPlaca");
        botoReservarPlaca.textContent = `Reservar plaça: ${id + 1}`;
        botoReservarPlaca.classList.add("selectedButon");
    } else {
        parking[id].classList.add('tremolar');

        setTimeout(() => {
            parking[id].classList.remove('tremolar');
        }, 500);
    }
}

function enviarReserva(id) {
    window.location.href = `/reservas?id=${id+1}`;
}
