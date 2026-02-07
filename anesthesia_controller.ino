/*
 * Real-Time Closed-Loop Anesthesia Delivery System
 * 
 * This system monitors patient vitals (HR, MAP, RR, SpO2) and automatically
 * adjusts anesthesia drug infusion rate using a servo-controlled IV mechanism.
 * 
 * Features:
 * - PID control algorithm for stable drug delivery
 * - Real-time vital monitoring with multiple sensors
 * - Safety alarms with critical threshold monitoring
 * - Servo-actuated precision infusion control
 * - Emergency stop and manual override capabilities
 */

#include <Servo.h>
#include <Wire.h>

// Pin Definitions
#define SERVO_PIN 9
#define HR_SENSOR_PIN A0      // Heart Rate sensor (analog)
#define MAP_SENSOR_PIN A1     // Mean Arterial Pressure sensor (analog)
#define RR_SENSOR_PIN A2      // Respiratory Rate sensor (analog)
#define SPO2_SENSOR_PIN A3    // SpO2 sensor (analog)
#define ALARM_BUZZER_PIN 8
#define ALARM_LED_PIN 13
#define EMERGENCY_STOP_PIN 2
#define MANUAL_OVERRIDE_PIN 3

// Safety Thresholds
#define HR_MIN 40             // Minimum safe heart rate (bpm)
#define HR_MAX 120            // Maximum safe heart rate (bpm)
#define HR_TARGET 70          // Target heart rate (bpm)
#define MAP_MIN 60            // Minimum safe MAP (mmHg)
#define MAP_MAX 110           // Maximum safe MAP (mmHg)
#define MAP_TARGET 85         // Target MAP (mmHg)
#define RR_MIN 8              // Minimum safe respiratory rate (breaths/min)
#define RR_MAX 25             // Maximum safe respiratory rate (breaths/min)
#define SPO2_MIN 92           // Minimum safe SpO2 (%)
#define SPO2_CRITICAL 88      // Critical SpO2 threshold (%)

// PID Controller Parameters
#define KP 2.0                // Proportional gain
#define KI 0.5                // Integral gain
#define KD 1.0                // Derivative gain
#define PID_MIN 0             // Minimum PID output
#define PID_MAX 180           // Maximum PID output (servo angle)

// Infusion Control
#define INFUSION_MIN 0        // Minimum infusion rate (servo angle 0°)
#define INFUSION_MAX 180      // Maximum infusion rate (servo angle 180°)
#define INFUSION_SAFE_MAX 120 // Safe maximum infusion (servo angle 120°)

// System States
enum SystemState {
  INITIALIZING,
  MONITORING,
  ACTIVE_CONTROL,
  ALARM_STATE,
  EMERGENCY_STOP,
  MANUAL_MODE
};

// Global Variables
Servo infusionServo;
SystemState currentState = INITIALIZING;

// Vital Signs
float heartRate = 0.0;
float meanArterialPressure = 0.0;
float respiratoryRate = 0.0;
float spO2 = 0.0;

// PID Variables
float pidError = 0.0;
float pidIntegral = 0.0;
float pidDerivative = 0.0;
float pidLastError = 0.0;
float pidOutput = 0.0;

// Infusion Control
int currentInfusionRate = 0;
unsigned long lastUpdateTime = 0;
unsigned long lastAlarmCheck = 0;

// Alarm Flags
bool alarmActive = false;
bool emergencyStopActive = false;
bool manualOverride = false;

// Function Prototypes
void setup();
void loop();
void initializeSensors();
void readVitalSigns();
float readHeartRate();
float readMAP();
float readRespiratoryRate();
float readSpO2();
void computePIDControl();
void updateInfusionRate(int rate);
void checkSafetyThresholds();
void activateAlarm(String reason);
void deactivateAlarm();
void handleEmergencyStop();
void handleManualOverride();
void printStatus();

void setup() {
  Serial.begin(9600);
  Serial.println("=== Anesthesia Delivery System Initializing ===");
  
  // Initialize pins
  pinMode(ALARM_BUZZER_PIN, OUTPUT);
  pinMode(ALARM_LED_PIN, OUTPUT);
  pinMode(EMERGENCY_STOP_PIN, INPUT_PULLUP);
  pinMode(MANUAL_OVERRIDE_PIN, INPUT_PULLUP);
  
  // Initialize servo
  infusionServo.attach(SERVO_PIN);
  infusionServo.write(0); // Start at minimum infusion
  
  // Initialize sensors
  initializeSensors();
  
  // Perform system self-test
  Serial.println("Performing system self-test...");
  delay(1000);
  
  // Test alarm
  digitalWrite(ALARM_LED_PIN, HIGH);
  tone(ALARM_BUZZER_PIN, 1000, 200);
  delay(500);
  digitalWrite(ALARM_LED_PIN, LOW);
  
  Serial.println("System initialization complete");
  currentState = MONITORING;
  lastUpdateTime = millis();
  lastAlarmCheck = millis();
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check emergency stop
  if (digitalRead(EMERGENCY_STOP_PIN) == LOW) {
    handleEmergencyStop();
    return;
  }
  
  // Check manual override
  if (digitalRead(MANUAL_OVERRIDE_PIN) == LOW) {
    handleManualOverride();
    return;
  }
  
  // Read vital signs every cycle
  readVitalSigns();
  
  // Check safety thresholds every 500ms
  if (currentTime - lastAlarmCheck >= 500) {
    checkSafetyThresholds();
    lastAlarmCheck = currentTime;
  }
  
  // Update control system every 1000ms
  if (currentTime - lastUpdateTime >= 1000) {
    if (currentState == MONITORING || currentState == ACTIVE_CONTROL) {
      computePIDControl();
      printStatus();
    }
    lastUpdateTime = currentTime;
  }
  
  delay(100); // Small delay to prevent overwhelming the system
}

void initializeSensors() {
  Serial.println("Initializing sensors...");
  // Configure analog sensors
  pinMode(HR_SENSOR_PIN, INPUT);
  pinMode(MAP_SENSOR_PIN, INPUT);
  pinMode(RR_SENSOR_PIN, INPUT);
  pinMode(SPO2_SENSOR_PIN, INPUT);
  Serial.println("Sensors initialized");
}

void readVitalSigns() {
  heartRate = readHeartRate();
  meanArterialPressure = readMAP();
  respiratoryRate = readRespiratoryRate();
  spO2 = readSpO2();
}

float readHeartRate() {
  // Read heart rate from sensor
  // In real implementation, this would interface with a pulse oximeter or ECG
  int rawValue = analogRead(HR_SENSOR_PIN);
  // Convert to BPM (simulated conversion)
  // Real sensor would have specific calibration
  float hr = map(rawValue, 0, 1023, 50, 100);
  return hr;
}

float readMAP() {
  // Read Mean Arterial Pressure from sensor
  // In real implementation, this would interface with a blood pressure monitor
  int rawValue = analogRead(MAP_SENSOR_PIN);
  // Convert to mmHg (simulated conversion)
  float map_value = map(rawValue, 0, 1023, 70, 100);
  return map_value;
}

float readRespiratoryRate() {
  // Read Respiratory Rate from sensor
  // In real implementation, this would use a respiration belt or capnography
  int rawValue = analogRead(RR_SENSOR_PIN);
  // Convert to breaths/min (simulated conversion)
  float rr = map(rawValue, 0, 1023, 10, 20);
  return rr;
}

float readSpO2() {
  // Read SpO2 from sensor
  // In real implementation, this would interface with a pulse oximeter
  int rawValue = analogRead(SPO2_SENSOR_PIN);
  // Convert to percentage (simulated conversion)
  float spo2 = map(rawValue, 0, 1023, 90, 100);
  return spo2;
}

void computePIDControl() {
  // Multi-parameter control algorithm
  // Primary control based on depth of anesthesia indicators
  
  // Calculate error based on heart rate (primary indicator)
  float hrError = HR_TARGET - heartRate;
  
  // Normalize error to -1.0 to 1.0 range
  float normalizedError = hrError / HR_TARGET;
  
  // PID calculation
  pidError = normalizedError;
  pidIntegral += pidError * 1.0; // dt = 1 second
  pidDerivative = pidError - pidLastError;
  
  // Anti-windup: Limit integral term
  if (pidIntegral > 10.0) pidIntegral = 10.0;
  if (pidIntegral < -10.0) pidIntegral = -10.0;
  
  // Calculate PID output
  pidOutput = (KP * pidError) + (KI * pidIntegral) + (KD * pidDerivative);
  
  // Convert PID output to servo angle (infusion rate)
  // Inverse relationship: higher HR means reduce infusion
  int targetRate = currentInfusionRate - (int)(pidOutput * 10);
  
  // Constrain to safe limits
  targetRate = constrain(targetRate, INFUSION_MIN, INFUSION_SAFE_MAX);
  
  // Additional safety: Reduce infusion if SpO2 is low
  if (spO2 < SPO2_MIN) {
    targetRate = targetRate / 2;
  }
  
  // Update infusion rate
  updateInfusionRate(targetRate);
  
  // Store error for next iteration
  pidLastError = pidError;
  
  // Update system state
  if (targetRate > 0) {
    currentState = ACTIVE_CONTROL;
  } else {
    currentState = MONITORING;
  }
}

void updateInfusionRate(int rate) {
  // Smooth transition: Change rate gradually
  int stepSize = 5;
  
  if (rate > currentInfusionRate) {
    currentInfusionRate = min(currentInfusionRate + stepSize, rate);
  } else if (rate < currentInfusionRate) {
    currentInfusionRate = max(currentInfusionRate - stepSize, rate);
  }
  
  // Apply to servo
  infusionServo.write(currentInfusionRate);
}

void checkSafetyThresholds() {
  bool safetyViolation = false;
  String alarmReason = "";
  
  // Check Heart Rate
  if (heartRate < HR_MIN) {
    safetyViolation = true;
    alarmReason = "BRADYCARDIA: HR < " + String(HR_MIN);
  } else if (heartRate > HR_MAX) {
    safetyViolation = true;
    alarmReason = "TACHYCARDIA: HR > " + String(HR_MAX);
  }
  
  // Check Mean Arterial Pressure
  if (meanArterialPressure < MAP_MIN) {
    safetyViolation = true;
    alarmReason += " | HYPOTENSION: MAP < " + String(MAP_MIN);
  } else if (meanArterialPressure > MAP_MAX) {
    safetyViolation = true;
    alarmReason += " | HYPERTENSION: MAP > " + String(MAP_MAX);
  }
  
  // Check Respiratory Rate
  if (respiratoryRate < RR_MIN) {
    safetyViolation = true;
    alarmReason += " | BRADYPNEA: RR < " + String(RR_MIN);
  } else if (respiratoryRate > RR_MAX) {
    safetyViolation = true;
    alarmReason += " | TACHYPNEA: RR > " + String(RR_MAX);
  }
  
  // Check SpO2 - Critical Parameter
  if (spO2 < SPO2_CRITICAL) {
    safetyViolation = true;
    alarmReason += " | CRITICAL HYPOXEMIA: SpO2 < " + String(SPO2_CRITICAL);
    // Emergency action: Stop infusion immediately
    updateInfusionRate(0);
    currentState = ALARM_STATE;
  } else if (spO2 < SPO2_MIN) {
    safetyViolation = true;
    alarmReason += " | HYPOXEMIA: SpO2 < " + String(SPO2_MIN);
  }
  
  // Activate or deactivate alarm
  if (safetyViolation) {
    activateAlarm(alarmReason);
  } else {
    deactivateAlarm();
  }
}

void activateAlarm(String reason) {
  if (!alarmActive) {
    alarmActive = true;
    Serial.println("\n!!! ALARM ACTIVATED !!!");
    Serial.println("Reason: " + reason);
  }
  
  // Visual alarm
  digitalWrite(ALARM_LED_PIN, HIGH);
  
  // Audible alarm (pulsing pattern)
  if (millis() % 1000 < 500) {
    tone(ALARM_BUZZER_PIN, 2000);
  } else {
    noTone(ALARM_BUZZER_PIN);
  }
  
  currentState = ALARM_STATE;
}

void deactivateAlarm() {
  if (alarmActive) {
    alarmActive = false;
    Serial.println("Alarm deactivated - vitals within normal range");
  }
  digitalWrite(ALARM_LED_PIN, LOW);
  noTone(ALARM_BUZZER_PIN);
  
  if (currentState == ALARM_STATE) {
    currentState = MONITORING;
  }
}

void handleEmergencyStop() {
  if (!emergencyStopActive) {
    emergencyStopActive = true;
    Serial.println("\n!!! EMERGENCY STOP ACTIVATED !!!");
    currentState = EMERGENCY_STOP;
  }
  
  // Stop all infusion immediately
  infusionServo.write(0);
  currentInfusionRate = 0;
  
  // Activate alarm
  digitalWrite(ALARM_LED_PIN, HIGH);
  tone(ALARM_BUZZER_PIN, 3000);
  
  // Reset PID controller
  pidIntegral = 0.0;
  pidLastError = 0.0;
  
  Serial.println("System halted - Release emergency stop to resume");
  delay(500);
}

void handleManualOverride() {
  if (!manualOverride) {
    manualOverride = true;
    Serial.println("\n*** MANUAL OVERRIDE ACTIVE ***");
    currentState = MANUAL_MODE;
  }
  
  // In manual mode, maintain current infusion rate
  // In a real system, this would allow manual control via a dial or buttons
  
  Serial.println("Manual control enabled - Automatic control suspended");
  delay(500);
}

void printStatus() {
  Serial.println("\n--- System Status ---");
  Serial.print("State: ");
  
  switch(currentState) {
    case INITIALIZING:
      Serial.println("INITIALIZING");
      break;
    case MONITORING:
      Serial.println("MONITORING");
      break;
    case ACTIVE_CONTROL:
      Serial.println("ACTIVE CONTROL");
      break;
    case ALARM_STATE:
      Serial.println("ALARM");
      break;
    case EMERGENCY_STOP:
      Serial.println("EMERGENCY STOP");
      break;
    case MANUAL_MODE:
      Serial.println("MANUAL MODE");
      break;
  }
  
  Serial.println("Vital Signs:");
  Serial.print("  HR:  "); Serial.print(heartRate, 1); Serial.println(" bpm");
  Serial.print("  MAP: "); Serial.print(meanArterialPressure, 1); Serial.println(" mmHg");
  Serial.print("  RR:  "); Serial.print(respiratoryRate, 1); Serial.println(" breaths/min");
  Serial.print("  SpO2: "); Serial.print(spO2, 1); Serial.println(" %");
  
  Serial.println("Control:");
  Serial.print("  PID Error: "); Serial.println(pidError, 3);
  Serial.print("  PID Output: "); Serial.println(pidOutput, 3);
  Serial.print("  Infusion Rate: "); Serial.print(currentInfusionRate); Serial.println("° (servo angle)");
  
  if (alarmActive) {
    Serial.println("  ⚠ ALARM ACTIVE");
  }
  
  Serial.println("--------------------");
}
