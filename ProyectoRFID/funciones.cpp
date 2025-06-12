#include "funciones.h"
// Lista de tags autorizados (termina con string vacio para futuros registros)
String tags[] = {"06 5C 87 4B", "A6 59 07 52", " "};
// Funcion: Inicializa el sistema
void inicializarSistema() {
    pinMode(LED, OUTPUT);   // Configura LED como salida
    Serial.begin(BAUDRATE);   // Inicia comunicacion serial
    nfc.begin();    // Inicia lector NFC
    Serial.println("Sistema de registro medico NFC iniciado"); // Mensaje inicio
}

void verificarTag() {
    if (nfc.tagPresent()) {   // Si hay tag presente
        NfcTag tag = nfc.read();   // Lee tag
        String uid = tag.getUidString();    // Obtiene UID como string
        Serial.println("Tag detectado: " + uid);  
        
        if(verificarAutorizacion(uid)) {  // Verifica autorizacion
            Serial.println("AUTORIZADO");   
            digitalWrite(LED, HIGH);     // Enciende LED
            
            Serial.print("REGISTRO:");    // Log registro
            Serial.println(uid);
            
            delay(1500);   // Espera 1.5 seg
            digitalWrite(LED, LOW);   // Apaga LED
        } else {
            Serial.println("NO AUTORIZADO");   // Mensaje no autorizado
        }
    }
}
// Funcion: Compara UID con lista de tags autorizados
bool verificarAutorizacion(String uid) {   
    for(int i = 0; i < sizeof(tags)/sizeof(tags[0]); i++) {    // Recorre array de tags
        if(uid == tags[i]) {
            return true;
        }
    }
    return false;
}
