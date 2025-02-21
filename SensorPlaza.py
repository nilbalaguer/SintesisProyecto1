import network
import time
import urequests
import machine
import json
import random

# Conexión Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect("Alumnes", "edu71243080")

while not wlan.isconnected():
    print("Conectando al Wi-Fi...")
    time.sleep(1)
print("Conexión Wi-Fi: " + str(wlan.isconnected()))

# Configuración del sensor
trigger = machine.Pin(4, machine.Pin.OUT)
echo = machine.Pin(35, machine.Pin.IN)
led = machine.Pin(2, machine.Pin.OUT)
distanciaDeteccion = 100
duracionDistancia = (distanciaDeteccion * 2) / 0.0343  # Microsegundos
placa = "25"

# URL del servidor
base_url = "http://172.16.3.139:8000/api/ocupar"

def detectar_objeto():
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    timeout = time.ticks_add(time.ticks_us(), 30000)  # 30ms de timeout
    while echo.value() == 0:
        if time.ticks_us() > timeout:
            return False
        start = time.ticks_us()

    timeout = time.ticks_add(time.ticks_us(), 30000)
    while echo.value() == 1:
        if time.ticks_us() > timeout:
            return False
        end = time.ticks_us()

    duracion = time.ticks_diff(end, start)
    return duracion < duracionDistancia

while True:
    if detectar_objeto():
        led.value(1)
        print("Sensor detecta")

        # Preparar datos
        data = {
            "accio": "ocupar",
            "placa": placa
        }
        
        print(data)

        # Enviar petición POST
        try:
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(base_url, json=data, headers=headers)
            print("Código Estado: ", response.status_code)
            if response.content:
                print("Respuesta: ", response.json())
            response.close()
        except Exception as e:
            print("Error en la petición:", e)
    else:
        # Preparar datos
        data = {
            "accio": "lliurar",
            "placa": placa
        }
        
        print(data)

        # Enviar petición POST
        try:
            headers = {'Content-Type': 'application/json'}
            response = urequests.post(base_url, json=data, headers=headers)
            print("Código Estado: ", response.status_code)
            if response.content:
                print("Respuesta: ", response.json())
            response.close()
        except Exception as e:
            print("Error en la petición:", e)

        led.value(0)
        print("Sensor no detecta")

    time.sleep(10 + random.randint(1, 5))
