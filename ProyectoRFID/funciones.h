#ifndef FUNCIONES_H
#define FUNCIONES_H

#include <Arduino.h>   // Funciones basicas de Arduino
#include <PN532_I2C.h>  // Controlador PN532 via I2C
#include <PN532.h>   // Funcionalidades PN532
#include <NfcAdapter.h>  // Adaptador NFC

// Definiciones de constantes
#define LED 13 // Pin del LED integrado
#define BAUDRATE 115200  // Velocidad comunicacion serial


// Declaracion de variables externas (definidas en .cpp)
extern PN532_I2C pn532_i2c;   // Objeto PN532
extern NfcAdapter nfc;   // Objeto NFC
extern String tags[];    // Array de tags autorizados
extern boolean autorizado;   // Estado de autorizacion

void inicializarSistema();
void verificarTag();
bool verificarAutorizacion(String uid); // Valida UID

#endif
