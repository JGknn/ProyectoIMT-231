import cv2

def leer_qr(ruta_imagen):
    try:
        imagen = cv2.imread(ruta_imagen)
        detector = cv2.QRCodeDetector()
        datos, puntos, _ = detector.detectAndDecode(imagen)

        if datos:
            return datos
        else:
            print("No se detectó ningún código QR.")
            return None

    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    ruta = input("Introduce la ruta de la imagen con el QR: ")
    resultado = leer_qr(ruta)
    
    if resultado:
        print("\nContenido del código QR:")
        print(resultado)
