import qrcode
import os

def incrementar_codigo(codigo_actual):
    letras = codigo_actual[:2]      # se separan las letras ej. ab1 → letras = ab
    numero = codigo_actual[2]       # se separa el numero
    num = int(numero) + 1           # se incrementa el numero
    
    if num > 9:
        num = 1
        letras_list = list(letras) # convierte ab en lista ['a','b']

        for i in range(1, -1, -1):  # recorre la lista desde el final hasta el inicio
            if letras_list[i] < 'z':
                letras_list[i] = chr(ord(letras_list[i]) + 1)
                break
            else:
                letras_list[i] = 'a'
                if i == 0:
                    letras_list = ['a','a']

        letras = ''.join(letras_list)
    return f"{letras}{num}"

def generar_qr(texto, archivo_salida):
    try:
        qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
        qr.add_data(texto)
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color="white")
        img.save(archivo_salida)
        return True
        
    except Exception as e:
        print(f"Error al generar QR: {e}")
        return False

def obtener_ultimo_codigo():
    try:
        if os.path.exists("ultimo_codigo.txt"):
            with open("ultimo_codigo.txt", "r") as f:
                return f.read().strip()
    except:
        pass
    return "aa0"  # Valor inicial

def guardar_ultimo_codigo(codigo):
    with open("ultimo_codigo.txt", "w") as f:
        f.write(codigo)

if __name__ == "__main__":
    ultimo_codigo = obtener_ultimo_codigo()
    nuevo_codigo = incrementar_codigo(ultimo_codigo)
    nombre_archivo = f"{nuevo_codigo}.png"

    if generar_qr(nuevo_codigo, nombre_archivo):
        guardar_ultimo_codigo(nuevo_codigo)
        print(f"\nCódigo QR generado con éxito: {nombre_archivo}")
        print(f"Contenido: {nuevo_codigo}")
    else:
        print("Error al generar el código QR")
