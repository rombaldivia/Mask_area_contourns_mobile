import cv2
import numpy as np

def process_video(hsv_values):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Could not open video device")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Convertir el frame de la cámara a HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lower_bound = np.array([hsv_values[0] , hsv_values[1] - 20, hsv_values[2] - 40])
            upper_bound = np.array([hsv_values[0] , hsv_values[1] + 20, hsv_values[2] + 40])

            # Crear la máscara usando el rango HSV
            mask = cv2.inRange(hsv, lower_bound, upper_bound)

            # Aplicar dilatación a la máscara
            kernel = np.ones((8, 8), np.uint8)  # Define el tamaño del kernel para la dilatación
            dilated_mask = cv2.dilate(mask, kernel, iterations=58)  # Puedes ajustar el número de iteraciones

            # Mostrar la máscara dilatada
            cv2.imshow('Dilated Mask', dilated_mask)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()

# Suponiendo que se ejecuta el código con valores HSV específicos
process_video((30, 100, 100))  # Ejemplo de valores HSV
