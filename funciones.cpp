#include "funciones.h"

PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);

String tags[] = {"06 5C 87 4B", ""};  // Lista de tags autorizados
boolean autorizado = false;

void iniciarSistema() {
    pinMode(13, OUTPUT);
    Serial.begin(115200);
    nfc.begin();
    Serial.println("Sistema de registro medico NFC iniciado");
}

void verificarTag() {
    if (nfc.tagPresent()) {
        NfcTag tag = nfc.read();
        String uid = tag.getUidString();
        Serial.println("Tag detectado: " + uid);

        autorizado = false;
        for (int i = 0; i < sizeof(tags) / sizeof(tags[0]); i++) {
            if (uid == tags[i]) {
                autorizado = true;
                break;
            }
        }

        if (autorizado) {
            Serial.println("AUTORIZADO");
            digitalWrite(13, HIGH);
            Serial.print("REGISTRO:");
            Serial.println(uid);
            delay(1500);
            digitalWrite(13, LOW);
        } else {
            Serial.println("NO AUTORIZADO");
        }
    }
}