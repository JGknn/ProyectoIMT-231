#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>
#include "funciones.h"

PN532_I2C pn532_i2c(Wire);
NfcAdapter nfc = NfcAdapter(pn532_i2c);
boolean autorizado = false;

void setup() {
    inicializarSistema();
}

void loop(void) {
    verificarTag();
    delay(500);
}