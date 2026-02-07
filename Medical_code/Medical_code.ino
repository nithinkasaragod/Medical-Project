#include <Servo.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

/* ---------- OLED ---------- */
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

/* ---------- HARDWARE ---------- */
Servo dripServo;
#define SERVO_PIN 9
#define BUZZER_PIN 8

/* ---------- VITALS ---------- */
float HR = 80, MAP = 70, RR = 14, SPO2 = 98;

/* ---------- TIMING ---------- */
unsigned long lastUpdate = 0;
const unsigned long interval = 2000;

void setup() {
  Serial.begin(9600);
  Serial.setTimeout(1000);

  dripServo.attach(SERVO_PIN);
  pinMode(BUZZER_PIN, OUTPUT);

  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);

  Serial.println("Send: HR MAP RR SPO2");
}

void loop() {

  /* ===== SERIAL INPUT ===== */
  if (Serial.available()) {
    float h = Serial.parseFloat();
    float m = Serial.parseFloat();
    float r = Serial.parseFloat();
    float s = Serial.parseFloat();

    if (h > 0 && m > 0 && r > 0 && s > 0) {
      HR = h;
      MAP = m;
      RR = r;
      SPO2 = s;

      Serial.print("UPDATED -> ");
      Serial.print(HR); Serial.print(" ");
      Serial.print(MAP); Serial.print(" ");
      Serial.print(RR); Serial.print(" ");
      Serial.println(SPO2);
    }

    while (Serial.available()) Serial.read();
  }

  /* ===== CONTROL LOOP ===== */
  if (millis() - lastUpdate >= interval) {
    lastUpdate = millis();

    int servoAngle;
    bool danger = false;
    bool warning = false;

    /* ===== SERVO PRIORITY LOGIC ===== */
    if (SPO2 < 92) {                 // 🚨 LOW SpO2
      servoAngle = 47;
      danger = true;
    }
    else if (MAP < 60) {             // ⚠️ LOW BP
      servoAngle = 55;
      warning = true;
    }
    else if (HR > 85) {              // ⬆️ HR HIGH
      servoAngle = 75;
    }
    else {                           // ✅ NORMAL
      servoAngle = 65;
    }

    dripServo.write(servoAngle);

    /* ===== BUZZER ===== */
    if (danger) {
      digitalWrite(BUZZER_PIN, HIGH);               // continuous
    }
    else if (warning) {
      digitalWrite(BUZZER_PIN, (millis() / 300) % 2); // beep
    }
    else {
      digitalWrite(BUZZER_PIN, LOW);
    }

    /* ===== OLED ===== */
    display.clearDisplay();
    display.setCursor(0,0);
    display.print("HR:"); display.print(HR);
    display.print(" MAP:"); display.print(MAP);

    display.setCursor(0,12);
    display.print("RR:"); display.print(RR);
    display.print(" SpO2:"); display.print(SPO2);

    display.setCursor(0,24);
    display.print("Servo:");
    display.print(servoAngle);
    display.print(" deg");

    display.display();

    /* ===== LOG ===== */
    Serial.print("HR="); Serial.print(HR);
    Serial.print(" MAP="); Serial.print(MAP);
    Serial.print(" RR="); Serial.print(RR);
    Serial.print(" SpO2="); Serial.print(SPO2);
    Serial.print(" Servo=");
    Serial.println(servoAngle);
  }
}