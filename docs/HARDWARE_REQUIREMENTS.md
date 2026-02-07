# Hardware Requirements

## Overview
This document specifies the hardware components required for the real-time closed-loop anesthesia delivery system.

## Core Components

### 1. Microcontroller
- **Arduino Uno R3** (or compatible)
  - ATmega328P microcontroller
  - 16 MHz clock speed
  - 32 KB Flash memory
  - 14 digital I/O pins
  - 6 analog input pins
  - USB connection for programming and serial communication

### 2. Servo Motor
- **Standard Servo Motor** (e.g., TowerPro SG90 or similar)
  - Operating voltage: 4.8V - 6V
  - Rotation range: 0° to 180°
  - Torque: Minimum 1.8 kg·cm
  - Purpose: Controls IV drip rate via mechanical valve adjustment
  - Connection: Digital Pin 9 (PWM)

### 3. Sensors

#### 3.1 Heart Rate (HR) Sensor
- **Pulse Oximeter Sensor** (e.g., MAX30102 or MAX30100)
  - Communication: I2C or Analog output
  - Range: 30-240 BPM
  - Accuracy: ±2 BPM
  - Connection: Analog Pin A0 or I2C (SDA/SCL)

#### 3.2 Mean Arterial Pressure (MAP) Sensor
- **Non-invasive Blood Pressure Sensor Module**
  - Automatic oscillometric measurement
  - Range: 0-300 mmHg
  - Interface: UART or Analog
  - Connection: Analog Pin A1 or Serial
  - Update rate: Every 30-60 seconds (typical for NIBP)

#### 3.3 Respiratory Rate (RR) Sensor
- **Respiration Belt Sensor** or **Piezoelectric Sensor**
  - Measures chest expansion/contraction
  - Range: 0-60 breaths/min
  - Output: Analog voltage
  - Connection: Analog Pin A2

#### 3.4 Oxygen Saturation (SpO₂) Sensor
- **Pulse Oximeter** (same as HR sensor - typically integrated)
  - Range: 70-100%
  - Accuracy: ±2%
  - Connection: Analog Pin A3 or shared with HR sensor

### 4. Alarm System

#### 4.1 Visual Alarm
- **LED Indicator**
  - Color: Red
  - Connection: Digital Pin 13
  - Purpose: Visual alarm indicator

#### 4.2 Audible Alarm
- **Piezo Buzzer**
  - Operating voltage: 3-5V
  - Frequency range: 1000-4000 Hz
  - Connection: Digital Pin 8
  - Purpose: Audible alarm for safety violations

### 5. Safety Controls

#### 5.1 Emergency Stop Button
- **Momentary Push Button** (Normally Open)
  - Large red mushroom-style button recommended
  - Connection: Digital Pin 2 (with internal pull-up)
  - Function: Immediately halts all infusion

#### 5.2 Manual Override Switch
- **Toggle Switch** (SPST)
  - Connection: Digital Pin 3 (with internal pull-up)
  - Function: Switches system to manual control mode

### 6. Power Supply
- **5V DC Power Supply**
  - Current capacity: Minimum 2A
  - USB power for Arduino
  - Separate power for servo motor (recommended)
  
- **Optional: Battery Backup**
  - 9V battery or Li-Po battery pack
  - For uninterrupted operation during power outages

### 7. Additional Components

#### 7.1 Display (Optional)
- **16x2 LCD Display** or **OLED Display**
  - Purpose: Real-time vital sign display
  - Connection: I2C or parallel interface
  - Not included in basic implementation

#### 7.2 Data Logging (Optional)
- **SD Card Module**
  - Purpose: Log vital signs and system events
  - Connection: SPI interface
  - Not included in basic implementation

## Wiring Diagram

```
Arduino Connections:
┌─────────────────────────────────────────┐
│         Arduino Uno R3                  │
├─────────────────────────────────────────┤
│ Digital Pin 2  ← Emergency Stop Button  │
│ Digital Pin 3  ← Manual Override Switch │
│ Digital Pin 8  → Buzzer (Alarm)        │
│ Digital Pin 9  → Servo Motor (PWM)     │
│ Digital Pin 13 → LED (Alarm)           │
│                                         │
│ Analog Pin A0  ← HR Sensor             │
│ Analog Pin A1  ← MAP Sensor            │
│ Analog Pin A2  ← RR Sensor             │
│ Analog Pin A3  ← SpO2 Sensor           │
│                                         │
│ 5V             → Sensor VCC             │
│ GND            → Sensor GND, Button GND │
└─────────────────────────────────────────┘
```

## Physical Setup Requirements

### 1. IV Mechanism
- Standard IV drip chamber
- Servo-controlled roller clamp or valve
- Mechanical linkage between servo and flow control
- Calibration required: Map servo angle to flow rate (mL/hr)

### 2. Patient Interface
- Standard medical-grade sensors with appropriate connectors
- Proper electrode/sensor placement per manufacturer guidelines
- Secure attachment to prevent motion artifacts

### 3. Mounting and Enclosure
- Protective enclosure for electronics
- Medical-grade materials (cleanable, non-reactive)
- Secure mounting near patient bed
- Cable management for safety

## Calibration Requirements

### 1. Sensor Calibration
- Each sensor must be calibrated against known standards
- Record calibration curves in software
- Regular recalibration per maintenance schedule

### 2. Servo-to-Flow Rate Mapping
- Establish relationship between servo angle and drug flow rate
- Test with actual IV setup using graduated cylinder
- Document: 0° = no flow, 180° = maximum safe flow

### 3. Alarm Threshold Verification
- Test alarm triggers at each threshold
- Verify appropriate response times
- Document alarm delays and response

## Safety Considerations

### 1. Redundancy
- **Recommended:** Dual sensor configuration for critical vitals
- **Recommended:** Backup power supply
- **Recommended:** Watchdog timer for system monitoring

### 2. Fail-Safe Design
- System defaults to STOP on any error
- Loss of sensor signal triggers immediate stop
- Emergency stop is hardware-based (not software-only)

### 3. Medical Standards Compliance
- This is a **PROTOTYPE** system for educational/research purposes
- **NOT FDA approved** for clinical use
- Requires extensive validation and regulatory approval before clinical deployment
- Must comply with IEC 60601 medical electrical equipment standards for production use

## Cost Estimate

| Component | Quantity | Estimated Cost (USD) |
|-----------|----------|---------------------|
| Arduino Uno R3 | 1 | $25 |
| Servo Motor | 1 | $10 |
| Pulse Oximeter Module | 1 | $15 |
| Blood Pressure Module | 1 | $50 |
| Respiration Sensor | 1 | $20 |
| Buzzer | 1 | $2 |
| LED | 1 | $1 |
| Buttons/Switches | 2 | $5 |
| Miscellaneous (wires, resistors, etc.) | - | $10 |
| **Total** | | **~$138** |

*Note: Costs are approximate and vary by supplier and location.*

## Procurement Sources

### Educational/Hobbyist Suppliers
- Adafruit Industries
- SparkFun Electronics
- Arduino Store
- AliExpress (bulk orders)

### Medical-Grade Sensors (for production)
- Nonin Medical
- Masimo Corporation
- Philips Healthcare
- GE Healthcare

## Next Steps

1. **Prototype Phase:** Use development boards and breakout modules
2. **Validation Phase:** Upgrade to medical-grade sensors
3. **Production Phase:** Custom PCB with integrated components
4. **Certification Phase:** Regulatory testing and approval

## Maintenance Schedule

- **Daily:** Visual inspection, alarm test
- **Weekly:** Sensor calibration check
- **Monthly:** Full system calibration
- **Annually:** Component replacement (as needed)

## References

- Arduino Hardware Documentation: https://www.arduino.cc/
- Medical Device Standards: IEC 60601 series
- Sensor Datasheets: Consult manufacturer documentation
