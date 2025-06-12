import qrcode
from PIL import Image, ImageTk

def generar_qr(texto, archivo_salida):
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
        qr.add_data(texto)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="white")
        img.save(archivo_salida)
        return True
    except Exception as e:
        print(f"Error al generar QR: {e}")
        return False

