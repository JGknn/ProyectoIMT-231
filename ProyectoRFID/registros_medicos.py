import serial
from datetime import datetime

equipos_registrados = {}

try:
    with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as ser, \
        open('registro_medico.log', 'a+') as log_file:
        
        print("Sistema de registro médico NFC - Esperando tags...")

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                
                if line.startswith('REGISTRO:'):
                    uid = line.split(':')[1]
                    timestamp = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
                    
                    registro = f"{timestamp} - Codigo de equipo : {uid} - ETIQUETA LEÍDA\n"
                    log_file.write(registro)
                    log_file.flush()
                    print(registro.strip())

                    # Alternar el estado del equipo (registrado/no registrado)
                    if uid in equipos_registrados:
                        del equipos_registrados[uid]
                    else:
                        equipos_registrados[uid] = timestamp

except KeyboardInterrupt:
    print("\nSistema cerrado correctamente")
except Exception as e:
    print(f"\nError: {str(e)}")