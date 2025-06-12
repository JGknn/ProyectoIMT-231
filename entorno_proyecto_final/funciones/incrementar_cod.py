def incrementar_codigo(codigo_actual):
    letras = codigo_actual[:2]
    numero = codigo_actual[2:]
    num = int(numero) + 1
    if num > 9:
        num = 1
        letras_list = list(letras)
        for i in range(1, -1, -1):
            if letras_list[i] < 'z':
                letras_list[i] = chr(ord(letras_list[i]) + 1)
                break
            else:
                letras_list[i] = 'a'
                if i == 0:
                    letras_list = ['a', 'a']
        letras = ''.join(letras_list)
    return f"{letras}{num}"

