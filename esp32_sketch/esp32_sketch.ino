/*
 * Smart Security Tag System — ESP32 Sketch
 * 
 * Hardware:
 *   - Servo Motor (SG90) on GPIO 18
 *   - Passive Buzzer on GPIO 5
 *   - Tamper Wire Loop on GPIO 4 (INPUT_PULLUP)
 *   - Common GND rail
 *   - Servo power from VIN
 * 
 * Serial: 115200 baud
 * Commands: "unlock\n" — unlock tag for 5 seconds
 */

#include <ESP32Servo.h>

#define BUZZER_PIN   5    // D5 LEFT
#define TAMPER_PIN   4    // D4 LEFT
#define SERVO_PIN    18   // D18 LEFT

Servo tagServo;

bool isUnlocked = false;
bool tamperActive = false;

void setup() {
  Serial.begin(115200);
  delay(500);

  // Buzzer setup
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  // Tamper wire — INPUT_PULLUP: wire intact = LOW, wire broken = HIGH
  pinMode(TAMPER_PIN, INPUT_PULLUP);

  // Servo — lock position (0°)
  tagServo.attach(SERVO_PIN);
  tagServo.write(0);
  delay(1000);

  Serial.println("[ESP32] Smart Security Tag System ready");
  Serial.println("[ESP32] Servo LOCKED at 0 degrees");
  Serial.println("[ESP32] Tamper sensor active");
}

void loop() {
  // --- Tamper Detection ---
  int tamperState = digitalRead(TAMPER_PIN);

  if (tamperState == HIGH && !isUnlocked) {
    // Wire is broken — ALARM
    if (!tamperActive) {
      Serial.println("[ALERT] Tamper Detected! Buzzer ON");
      tamperActive = true;
    }
    digitalWrite(BUZZER_PIN, HIGH);
  } else if (tamperState == LOW && !isUnlocked) {
    // Wire is intact — safe
    if (tamperActive) {
      Serial.println("[ESP32] Tamper wire restored. Buzzer OFF");
      tamperActive = false;
    }
    digitalWrite(BUZZER_PIN, LOW);
  }

  // --- Serial Command Handling ---
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    Serial.print("[ESP32] Received command: '");
    Serial.print(command);
    Serial.print("' (length: ");
    Serial.print(command.length());
    Serial.println(")");

    if (command == "unlock") {
      // Silence buzzer immediately
      digitalWrite(BUZZER_PIN, LOW);
      tamperActive = false;
      isUnlocked = true;

      Serial.println("[ESP32] Payment Verified. Unlocking...");

      // Detach and re-attach servo for fresh PWM signal
      tagServo.detach();
      delay(100);
      tagServo.attach(SERVO_PIN);
      delay(100);

      // Rotate to 90° — UNLOCKED
      tagServo.write(90);
      delay(1000);  // Let servo physically rotate
      Serial.println("[ESP32] Tag UNLOCKED ✓");

      // Hold unlocked for 5 seconds
      delay(5000);

      // Rotate back to 0° — RE-LOCKED
      tagServo.write(0);
      delay(1000);  // Let servo physically rotate
      Serial.println("[ESP32] Tag RE-LOCKED. Ready for next payment.");

      isUnlocked = false;
    }
  }

  delay(100);  // Avoid serial flooding
}
