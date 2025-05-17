#include <MFRC522.h>
#include <Arduino.h>

#define SS_PIN 10
#define RST_PIN 9
#define LED_PIN 7

MFRC522 rfid(SS_PIN, RST_PIN);

void inicializarRFID() {
  rfid.PCD_Init();
}

void inicializarLED() {
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
}

void detectarYMostrarRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) {
    digitalWrite(LED_PIN, LOW);
    return;
  }

  Serial.print("ID detectado: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
    Serial.print(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  digitalWrite(LED_PIN, HIGH);
  delay(1000); // Mantiene el LED encendido un momento
  rfid.PICC_HaltA();
}
