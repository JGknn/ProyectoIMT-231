import cv2

def procesar_qr(ruta_imagen):
    try:
        imagen = cv2.imread(ruta_imagen)
        detector = cv2.QRCodeDetector()
        datos_qr, _, _ = detector.detectAndDecode(imagen)
        return datos_qr if datos_qr else "QR no detectado."
    except Exception as e:
        return f"Error al leer QR: {e}"

