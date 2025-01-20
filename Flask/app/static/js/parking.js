const botoReservarPlaca = document.getElementById("botoReservarPlaca");
const indicadorOcupacio = document.getElementById("indicadorOcupacio");
const DataReservaInput = document.getElementById("datareservainput");
botoReservarPlaca.textContent = "Reservar";

//Data actual per ficar el minim en el formulari
const hoy = new Date();
const yyyy = hoy.getFullYear();
const mm = String(hoy.getMonth() + 1).padStart(2, '0');
const dd = String(hoy.getDate()).padStart(2, '0');
const dataActual = `${yyyy}-${mm}-${dd}`;
DataReservaInput.setAttribute('min', dataActual);

//Boton de dia millorat
DataReservaInput.addEventListener("keydown", function (event) {
    event.preventDefault();
});

DataReservaInput.addEventListener("click", function () {
    this.showPicker();
});

//Detectar quan canvii el input de la data
alert("Introdueix la data de reserva");

DataReservaInput.addEventListener("change", async function() {
    const parkingDivs = document.querySelectorAll(".parkings div[class^='div']");
    const parkingArray = Array.from(parkingDivs);

    cancelaSeleccio(parkingArray);

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
        let contadorlliures = 42;

        for (let i = 0; i < data.length; i++) {
            if (data[i].data == temps) {
                parkingArray[data[i].id_parking-1].classList.remove("estat_lliure");
                parkingArray[data[i].id_parking-1].classList.add("estat_reservat");
                contadorlliures -= 1;
            }
            
        }

        indicadorOcupacio.innerHTML = "Ocupacio: " + Math.round(((42-contadorlliures)/42)*100) + " %<br>Plaçes lliures: " + contadorlliures;
    })
    .catch(error => console.error('Error al obtindre les plaçes del parking:', error));

    if (temps == dataActual) {
        fetch('/apiocupacions')
        .then(response => response.json())
        .then(data => {
            for (let i = 0; i < data.length; i++) {
                parkingArray[data[i].placa-1].classList.remove("estat_lliure");
                parkingArray[data[i].placa-1].classList.remove("estat_reservat");
                parkingArray[data[i].placa-1].classList.add("estat_ocupat");
            }
        })
        .catch(error => console.error('Error al obtindre les plaçes del parking: ', error));
    }

    parkingArray.forEach((div, index) => {
        div.textContent = `${index + 1}`;
        div.addEventListener("click", () => {seleccionarPlaca(index, parkingArray)});
    });
});

let seleccio = -1;

botoReservarPlaca.addEventListener("click", () => {enviarReserva(seleccio, DataReservaInput.value)});

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
    })

    seleccio = -1;

    botoReservarPlaca.textContent = "Reserva";
    botoReservarPlaca.classList.remove("selectedButon");
}

function enviarReserva(id, date) {
    window.location.href = `/reservas?id=${id+1}&date=${date}`;
}
