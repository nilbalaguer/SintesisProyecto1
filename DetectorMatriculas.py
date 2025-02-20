
# OpenCV libs
import cv2
import numpy as np

# Configura la ruta de Tesseract si es necesario (solo en Windows)
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Extra Libs
import requests             # HTTP camera adquisition
import time                 # time.sleep

# recojemos la IP de la camara (1er parametro) y generamos la URL para capturar frames
import sys
if len(sys.argv) != 2:
    print("Uso: Falta el parametro de la IP de la camara")
    sys.exit(1)
ip_cam=sys.argv[1]
esp32_url = "http://" + ip_cam + "/capture"

def ordenar_puntos(puntos):
    # Ordenar los puntos en el orden: top-left, top-right, bottom-right, bottom-left
    puntos = puntos.reshape(4, 2)  # Asegúrate de que tenga forma (4, 2)
    suma = puntos.sum(axis=1)
    diferencia = np.diff(puntos, axis=1)
    top_left = puntos[np.argmin(suma)]
    bottom_right = puntos[np.argmax(suma)]
    top_right = puntos[np.argmin(diferencia)]
    bottom_left = puntos[np.argmax(diferencia)]
    return np.array([top_left, top_right, bottom_right, bottom_left], dtype="float32")

def enderezar_imagen(imagen, puntos):
    # Ordenar los puntos detectados
    puntos_ordenados = ordenar_puntos(puntos)

    # Calcular el ancho y alto de la nueva imagen
    (top_left, top_right, bottom_right, bottom_left) = puntos_ordenados

    ancho1 = np.linalg.norm(bottom_right - bottom_left)
    ancho2 = np.linalg.norm(top_right - top_left)
    max_ancho = max(int(ancho1), int(ancho2))

    alto1 = np.linalg.norm(top_right - bottom_right)
    alto2 = np.linalg.norm(top_left - bottom_left)
    max_alto = max(int(alto1), int(alto2))

    # Puntos de destino para la transformación
    destino = np.array( [
                        [0, 0],
                        [max_ancho - 1, 0],
                        [max_ancho - 1, max_alto - 1],
                        [0, max_alto - 1]
                        ],dtype="float32")

    # Calcular la matriz de transformación de perspectiva
    matriz = cv2.getPerspectiveTransform(puntos_ordenados, destino)

    # Aplicar la transformación de perspectiva
    imagen_enderezada = cv2.warpPerspective(imagen, matriz, (max_ancho, max_alto))

    return imagen_enderezada

# Loop principal (se sale con tecla Q)
while True:

    # frecuencia Loop
    time.sleep(1.0)
    
    try:
        
        # Solicita una imagen a la ESP32-CAM
        response = requests.get(esp32_url, stream=True)
        if response.status_code == 200:
            
            # recojemos los datos como buffer de bytes (Numpy) que nos han enviado de la peticion HTTP GET
            data        = np.frombuffer(response.content, np.uint8)
            
            # convertimos el buffer de bytes a imagen valida para OpenCV
            image       = cv2.imdecode(data, cv2.IMREAD_COLOR)
            
            # posibilidad de GaussianBlur para eviar rudio si lo hay
            #gb_image = cv2.GaussianBlur(image, (21, 21), 0)  # Reduce el ruido
                    
            # imagen a escala de grises, no necesitamos color, simpificamos memoria de calculos
            gray_image  = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Usamos Canny para dejar toda la imagen en negro y en blanco todos los contornos que encuentre
            edges1 = cv2.Canny(gray_image, 100, 200)
            
            # Generamos una lista con todos lo contornos
            contours, _     = cv2.findContours(edges1 , cv2.RETR_EXTERNAL , cv2.CHAIN_APPROX_SIMPLE)            # solo externos (los internos dentro de un contorno superior se eliminan)
            #contours, _     = cv2.findContours(edges1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)                 # todos
         
            # creamos un buffer B/W todo negro como mascara, compatible imagen OpenCV para pintar encima (solo grises)
            mask            = np.zeros_like(gray_image)                # Crear una nueva imagen en blanco del tamaño de la captura vacia para poder dibujar
            
            # una copia de la imagen para dibujar encima el resultado
            mask_resultado  = image.copy()
            
            # Trabajamos con los contornos que hemos encontrado (primera vuelta) (eliminamos estrella No es convexos)
            contornos_candidatos = []
            for contour in contours:
                
                if cv2.contourArea(contour) > 150:          # Filtrar áreas pequeñas
                    
                    # Aproximar el contorno
                    #epsilon = 0.1 * cv2.arcLength(contour, True)                   # mayor el 0.1 mas aproximacion hace, menos puntos de contorno
                    epsilon = 0.025 * cv2.arcLength(contour, True)                  # con este valor la estrella da 7 u 8 , pero triangulo 4
                    #epsilon = 0.1 * cv2.arcLength(contour, True)                   # con este valor me discrimina el triangulo 3 vertices, cuadrado 4 y la estrella 4
                    #epsilon = 0.05 * cv2.arcLength(contour, True)                  # con este valor me discrimina el triangulo 3 vertices, cuadrado 4 y la estrella 4
                    aproximacion = cv2.approxPolyDP(contour, epsilon, True)
                    
                    x, y, w, h = cv2.boundingRect(aproximacion)
                    
                    # Adicional: opcional si quieres contornos convexos
                    if cv2.isContourConvex(aproximacion):
                        contornos_candidatos.append(contour)
                        #cv2.rectangle(mask_resultado, (x-4, y-4), (x + w + 4, y + h + 4), color=(0, 255, 0), thickness=1)           # COLOR VERDE
                        pass
                    else:
                        cv2.drawContours(mask, [contour], -1, 255, thickness=1)     # Dibuja en blanco sobre la máscara
                    
                    pass
                else:
                    #print( cv2.contourArea(contour) )                              # el valor del Area
                    cv2.drawContours(mask, [contour], -1, 128, thickness=1)         # Dibuja en blanco sobre la máscara
            
            # Trabajamos con los contornos que hemos encontrado (SEGUNDA vuelta)
            contornos_candidatos2 = []
            for contour in contornos_candidatos:
                    
                    # Aproximar el contorno
                    #epsilon = 0.05 * cv2.arcLength(contour, True)                   # con este valor me discrimina el triangulo 3 vertices, cuadrado 4 y la estrella 4 (podemos provar entre 0.25 y 0.01)
                    epsilon = 0.07 * cv2.arcLength(contour, True)                   # con este valor me discrimina el triangulo 3 vertices, cuadrado 4 y la estrella 4
                    aproximacion = cv2.approxPolyDP(contour, epsilon, True)
                    
                    x, y, w, h = cv2.boundingRect(aproximacion)
                    
                    # Calcular el centro del bounding box
                    centro_x = x + w // 2
                    centro_y = y + h // 2
                    
                    # Verificar si tiene forma rectangular
                    if len(aproximacion) == 4:
                        
                        cv2.rectangle(mask_resultado, (x-8, y-8), (x + w + 8, y + h + 8), color=(0, 0, 255), thickness=1)           # COLOR ROJO
                        cv2.putText(mask_resultado , str(len(aproximacion)), (centro_x, centro_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        contornos_candidatos2.append(contour)
                        
                        # Hacer crop de la region
                        cropped_rect = gray_image[y:y+h, x:x+w]
                        cropped_edges = cv2.Canny(cropped_rect, 100, 200)
                        contornosinteriores, _ = cv2.findContours(cropped_edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                        
                        # si hay cosas dentro puede ser una matricula
                        if len(contornosinteriores) > 10:
                        
                            # Enderezar la imagen usando la transformación de perspectiva
                            rectangulo_enderezado = enderezar_imagen(image, aproximacion)
                            
                            # Le quitamos el borde del rectangulo (10 pixels)
                            alto, ancho, canales = rectangulo_enderezado.shape
                            pixelsreduccion=5
                            rectangulo_sinborde = rectangulo_enderezado[pixelsreduccion:alto-pixelsreduccion, pixelsreduccion:ancho-pixelsreduccion]
                            
                            cv2.imshow('Recorte de matricula', rectangulo_sinborde)
                            
                            # aplicamos OCR
                            _, thresh = cv2.threshold(rectangulo_sinborde, 100, 150, cv2.THRESH_BINARY)
                            texto = pytesseract.image_to_string(rectangulo_sinborde, lang='eng')
                            print("Texto detectado:")
                            print(texto)

                            #Peticion a la API para abrir la puerta
                            import requests

                            #URL API WEB, para abrir la puerta
                            url = "http://127.0.0.1:5000/api/checkMatricula"
                            payload = {
                                "matricula": texto.strip(),
                                "accio": "entrada",
                            }

                            response = requests.post(url, json=payload)

                            if response.status_code == 200:
                                data = response.json()
                                print("Respuesta:", data)
                            else:
                                print(f"Error: {response.status_code}")
                            
                        pass
                        
                    elif len(aproximacion) == 3:             # Verificar si tiene forma triangular
                        cv2.rectangle(mask_resultado, (x-4, y-4), (x + w + 4, y + h + 4), color=(0, 255, 0), thickness=1)           # COLOR VERDE
                        cv2.putText(mask_resultado , str(len(aproximacion)), (centro_x, centro_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        contornos_candidatos2.append(contour)
                        pass
                        
                    else:
                        cv2.putText(mask_resultado , str(len(aproximacion)), (centro_x, centro_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    
                    # Si queremos ver en pantalla la consola cuantos vertices tiene
                    #print( len(aproximacion) )
                    
                    pass
           
            # Dibujar los contornos cerrados en la imagen original
            imagen_resultado = image.copy()
            cv2.drawContours(imagen_resultado, contornos_candidatos2 , -1, (0, 255, 0), 2)        
            
            # Muestra la imagen
            #cv2.imshow("Original grises", gray_image)
            cv2.imshow("Canny 1", edges1)
            cv2.imshow("Contornos Externos Cerrados", mask)
            cv2.imshow("Debug", mask_resultado)
            cv2.imshow("Resultado final", imagen_resultado)
            
            # Salir con la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print("Error al obtener la imagen.")
        
    except Exception as e:
        print(f"Error: {e}")

cv2.destroyAllWindows()

