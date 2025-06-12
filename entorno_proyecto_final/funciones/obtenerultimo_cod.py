import os

def obtener_ultimo_codigo():
    try:
        if os.path.exists("ultimo_codigo.txt"):
            with open("ultimo_codigo.txt", "r") as f:
                return f.read().strip()
    except:
        pass
    return "aa0"

