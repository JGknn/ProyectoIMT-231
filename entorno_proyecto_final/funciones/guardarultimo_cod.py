def guardar_ultimo_codigo(codigo):
    with open("ultimo_codigo.txt", "w") as f:
        f.write(codigo)
