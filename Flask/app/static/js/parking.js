const botoReservarPlaca = document.getElementById("botoReservarPlaca");
const indicadorOcupacio = document.getElementById("indicadorOcupacio");
const DataReservaInput = document.getElementById("datareservainput");
botoReservarPlaca.textContent = "Reservar";

DataReservaInput.addEventListener("change", async function() {
    const parkingDivs = document.querySelectorAll(".parkings div[class^='div']");
    const parkingArray = Array.from(parkingDivs);

    parkingArray.forEach((div) => {
        div.classList.remove("estat_reservat");
        div.classList.remove("estat_ocupat");

        div.classList.add("estat_lliure");
    })

    let temps = DataReservaInput.value;

    //Fetch per obtindre dades del parking
    fetch('/apireserves')
    .then(response => response.json())
    .then(data => {
        let contadorlliures = 0;

        for (let i = 0; i < data.length; i++) {
            if (data[i].data == temps) {
                console.log(data[i].id_parking);
                parkingArray[data[i].id_parking-1].classList.remove("estat_lliure");
                parkingArray[data[i].id_parking-1].classList.add("estat_reservat");
            }


            /*
            if (data[i].estat == "lliure") {
                parkingArray[i].classList.add("estat_lliure");
                contadorlliures += 1;
            } else if (data[i].estat == "reservat") {
                parkingArray[i].classList.add("estat_reservat");
            } else if (data[i].estat == "ocupat"){
                parkingArray[i].classList.add("estat_ocupat");
            }
            */
            
        }

        indicadorOcupacio.innerHTML = "Ocupacio: " + Math.round(contadorlliures*100/42) + " %<br>Plaçes lliures: " + contadorlliures;
    })
    .catch(error => console.error('Error al obtindre les plaçes del parking:', error));

    parkingArray.forEach((div, index) => {
        div.textContent = `P ${index + 1}`;
        div.addEventListener("click", () => {seleccionarPlaca(index, parkingArray)});
    });

    cancelaSeleccio();
});

let seleccio = -1;

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

function cancelaSeleccio(parking) {
    parking.forEach((div) => {
        div.classList.remove("selectedPlaca");
        seleccio = -1;
    })
}

function enviarReserva(id) {
    window.location.href = `/reservas?id=${id+1}`;
}
