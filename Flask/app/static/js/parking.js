const botoReservarPlaca = document.getElementById("botoReservarPlaca");
botoReservarPlaca.textContent = "Reservar";

document.addEventListener("DOMContentLoaded", function() {
    const parkingDivs = document.querySelectorAll(".parkings div[class^='div']");
    const parkingArray = Array.from(parkingDivs);

    parkingArray.forEach((div, index) => {
        div.textContent = `A ${index + 1}`;

        div.addEventListener("click", () => {seleccionarPlaca(index + 1)});
    });
});

//Fetch per obtindre dades del parking
fetch('/api/parking')
        .then(response => response.json())
        .then(data => {
            data.forEach(reserva => {
                console.log(reserva);
            });
        })
        .catch(error => console.error('Error al obtener las reservas:', error));


let seleccio = 0;

function seleccionarPlaca(id) {
    seleccio = id;
    botoReservarPlaca.textContent = `Reservar plaça: ${id}`;
}