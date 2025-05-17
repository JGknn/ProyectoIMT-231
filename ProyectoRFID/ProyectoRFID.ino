#include <SPI.h>
#include <MFRC522.h>
#include "funciones.h"
void setup() {
  Serial.begin(9600);
  SPI.begin();
  inicializarRFID();
  inicializarLED();
  Serial.println("Sistema RFID iniciado...");
}

void loop() {
   detectarYMostrarRFID();
}
