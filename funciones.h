#ifndef FUNCIONES_H
#define FUNCIONES_H

#include <Wire.h>
#include <PN532_I2C.h>
#include <PN532.h>
#include <NfcAdapter.h>

extern PN532_I2C pn532_i2c;
extern NfcAdapter nfc;
extern String tags[];
extern boolean autorizado;

void iniciarSistema();
void verificarTag();

#endif
