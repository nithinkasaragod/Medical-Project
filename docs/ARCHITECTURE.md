# System Architecture

## Overview
The closed-loop anesthesia delivery system is designed as a real-time embedded control system that monitors patient vitals and automatically adjusts drug infusion rates using feedback control.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     ANESTHESIA DELIVERY SYSTEM                      │
└─────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┴──────────────────────────┐
        │                                                       │
        ▼                                                       ▼
┌───────────────┐                                     ┌────────────────┐
│  SENSOR LAYER │                                     │  ACTUATION     │
└───────────────┘                                     │     LAYER      │
        │                                             └────────────────┘
        │  ┌─────────────┐                                    │
        ├──┤ HR Sensor   │                            ┌───────┴────────┐
        │  └─────────────┘                            │  Servo Motor   │
        │  ┌─────────────┐                            │  (0° - 180°)   │
        ├──┤ MAP Sensor  │                            └────────────────┘
        │  └─────────────┘                                    │
        │  ┌─────────────┐                            ┌───────┴────────┐
        ├──┤ RR Sensor   │                            │  IV Mechanism  │
        │  └─────────────┘                            │  Flow Control  │
        │  ┌─────────────┐                            └────────────────┘
        └──┤ SpO2 Sensor │
           └─────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  DATA ACQUISITION│
        │  & CONDITIONING  │
        └─────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTROL LAYER (Arduino)                          │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐    ┌───────────────┐ │
│  │  Safety Monitor  │───▶│  PID Controller  │───▶│  Infusion     │ │
│  │  - Thresholds    │    │  - Target: HR=70 │    │  Rate Manager │ │
│  │  - Alarms        │    │  - Kp, Ki, Kd    │    │  - Smooth     │ │
│  │  - Emergency     │    │  - Anti-windup   │    │    Transitions│ │
│  └──────────────────┘    └──────────────────┘    └───────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │   ALARM LAYER   │
        ├─────────────────┤
        │  ┌────────────┐ │
        │  │ Visual LED │ │
        │  └────────────┘ │
        │  ┌────────────┐ │
        │  │ Buzzer     │ │
        │  └────────────┘ │
        └─────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  USER INTERFACE │
        ├─────────────────┤
        │  ┌────────────┐ │
        │  │ Emergency  │ │
        │  │ Stop Button│ │
        │  └────────────┘ │
        │  ┌────────────┐ │
        │  │ Manual     │ │
        │  │ Override   │ │
        │  └────────────┘ │
        │  ┌────────────┐ │
        │  │ Serial     │ │
        │  │ Monitor    │ │
        │  └────────────┘ │
        └─────────────────┘
```

## System Components

### 1. Sensor Layer
**Purpose:** Continuous monitoring of patient physiological parameters

**Components:**
- Heart Rate (HR) sensor - Primary indicator of anesthetic depth
- Mean Arterial Pressure (MAP) sensor - Cardiovascular stability
- Respiratory Rate (RR) sensor - Respiratory function
- SpO₂ sensor - Oxygenation status

**Sampling Rate:** 1-10 Hz depending on sensor
**Data Type:** Analog voltage signals

### 2. Data Acquisition & Conditioning
**Purpose:** Convert sensor signals to usable digital values

**Functions:**
- Analog-to-Digital Conversion (10-bit ADC)
- Signal filtering and noise reduction
- Calibration curve application
- Unit conversion to clinical values

### 3. Control Layer
**Purpose:** Core decision-making and control logic

#### 3.1 Safety Monitor
**Functions:**
- Continuous threshold checking
- Multi-parameter alarm logic
- Emergency stop handling
- System state management

**Safety Thresholds:**
```
HR:  40-120 bpm    (Target: 70 bpm)
MAP: 60-110 mmHg   (Target: 85 mmHg)
RR:  8-25 br/min
SpO₂: >92%         (Critical: <88%)
```

#### 3.2 PID Controller
**Functions:**
- Error calculation (Target - Measured)
- Proportional, Integral, Derivative computation
- Output scaling to infusion rate
- Anti-windup protection

**Parameters:**
```
Kp = 2.0   (Proportional gain)
Ki = 0.5   (Integral gain)
Kd = 1.0   (Derivative gain)
```

**Control Equation:**
```
u(t) = Kp·e(t) + Ki·∫e(τ)dτ + Kd·de(t)/dt

where:
  u(t) = control output
  e(t) = error signal = target - measured
  t = time
```

#### 3.3 Infusion Rate Manager
**Functions:**
- Rate limiting (smooth transitions)
- Safety bounds enforcement
- Servo angle calculation
- Emergency shutoff capability

### 4. Actuation Layer
**Purpose:** Physical control of drug delivery

**Components:**
- Servo motor (180° rotation)
- Mechanical linkage
- IV flow control mechanism

**Mapping:**
```
0°   = No infusion
90°  = Medium infusion
180° = Maximum infusion (limited to 120° for safety)
```

### 5. Alarm Layer
**Purpose:** Alert medical staff to critical conditions

**Visual Alarms:**
- LED indicator (steady/flashing patterns)

**Audible Alarms:**
- Buzzer with variable frequency/pattern
- Critical alarms: Continuous high-frequency
- Warning alarms: Pulsing medium-frequency

**Alarm Priorities:**
1. Critical (SpO₂ < 88%) - Immediate infusion stop
2. High (HR/MAP/RR outside limits) - Controlled adjustment
3. Medium (Parameter trending toward limits) - Monitoring

### 6. User Interface Layer
**Purpose:** Human interaction and override capabilities

**Components:**
- Emergency Stop button (hardware interrupt)
- Manual Override switch
- Serial Monitor (status display)

## Control Flow

### Main Loop Sequence

```
1. Initialize System
   ├─ Configure pins
   ├─ Initialize sensors
   ├─ Test alarms
   └─ Set initial state

2. Main Loop (every 100ms)
   ├─ Check Emergency Stop
   │  └─ If pressed: Halt system
   │
   ├─ Check Manual Override
   │  └─ If enabled: Enter manual mode
   │
   ├─ Read Vital Signs (continuous)
   │  ├─ HR from analog pin
   │  ├─ MAP from analog pin
   │  ├─ RR from analog pin
   │  └─ SpO₂ from analog pin
   │
   ├─ Check Safety Thresholds (every 500ms)
   │  ├─ Compare each vital to limits
   │  ├─ Activate alarms if violated
   │  └─ Emergency stop if critical
   │
   └─ Update Control (every 1000ms)
      ├─ Compute PID error
      ├─ Calculate control output
      ├─ Update infusion rate
      └─ Print status to serial
```

### State Machine

```
                  ┌──────────────┐
                  │ INITIALIZING │
                  └──────┬───────┘
                         │
                         ▼
                  ┌──────────────┐
         ┌────────│  MONITORING  │◀────────┐
         │        └──────┬───────┘         │
         │               │                 │
         │               │ Infusion > 0    │
         │               ▼                 │
         │        ┌──────────────┐         │
         │        │    ACTIVE    │─────────┘
         │        │   CONTROL    │
         │        └──────┬───────┘
         │               │
         │               │ Threshold violated
         │               ▼
         │        ┌──────────────┐
         └────────│ ALARM STATE  │
                  └──────┬───────┘
                         │
         ┌───────────────┼────────────────┐
         │               │                │
Emergency│               │           Manual│
  Stop   │               │          Override│
         ▼               ▼                ▼
  ┌──────────────┐  ┌────────┐   ┌────────────┐
  │  EMERGENCY   │  │ Resume │   │   MANUAL   │
  │     STOP     │  │        │   │    MODE    │
  └──────────────┘  └────────┘   └────────────┘
```

## Data Flow

### Sensor to Actuator Pipeline

```
1. Sensor Reading
   Raw Analog Value (0-1023)
   ↓

2. Signal Conditioning
   Apply calibration: clinical_value = f(raw_value)
   ↓

3. Safety Check
   if value < min OR value > max:
      TRIGGER ALARM
   ↓

4. Control Calculation
   error = target - measured
   pid_output = Kp*error + Ki*integral + Kd*derivative
   ↓

5. Rate Adjustment
   target_rate = current_rate - (pid_output * gain)
   constrain(target_rate, 0, 120)
   ↓

6. Smooth Transition
   if |target - current| > step_size:
      current += step_size * sign(target - current)
   ↓

7. Servo Actuation
   servo.write(current_rate)
   ↓

8. Physical Infusion
   Drug flows at rate proportional to servo angle
```

## Timing Specifications

| Operation | Frequency | Period | Priority |
|-----------|-----------|--------|----------|
| Main Loop | 10 Hz | 100 ms | High |
| Sensor Reading | 10 Hz | 100 ms | High |
| Safety Check | 2 Hz | 500 ms | Critical |
| Control Update | 1 Hz | 1000 ms | Medium |
| Status Display | 1 Hz | 1000 ms | Low |
| Emergency Stop | Event-driven | <50 ms | Critical |

## Safety Architecture

### Fail-Safe Principles

1. **Default to Safe State**
   - Power loss → Servo returns to 0° (no infusion)
   - Sensor failure → Stop infusion
   - Controller crash → Watchdog reset → Stop infusion

2. **Redundant Monitoring**
   - Multiple vital signs monitored
   - Cross-checking between parameters
   - Alarm redundancy (visual + audible)

3. **Hardware Override**
   - Emergency stop is hardware interrupt
   - Does not depend on software state
   - Immediate response (<50ms)

4. **Graduated Response**
   - Minor deviation → Gradual adjustment
   - Moderate deviation → Faster adjustment + warning
   - Critical deviation → Immediate stop + alarm

### Error Handling

```cpp
Error Conditions:
├─ Sensor disconnected → Stop infusion, alarm
├─ Invalid reading → Use last valid value, alarm after timeout
├─ Communication failure → Stop infusion, alarm
├─ Servo malfunction → Stop infusion, alarm
├─ Power fluctuation → Maintain state if brief, stop if sustained
└─ Memory overflow → Reset controller, alarm
```

## Performance Specifications

### Response Times
- Sensor reading to control output: <1 second
- Alarm detection to activation: <500 ms
- Emergency stop to infusion halt: <50 ms
- Manual override recognition: <100 ms

### Accuracy Requirements
- HR measurement: ±2 bpm
- MAP measurement: ±5 mmHg
- RR measurement: ±2 breaths/min
- SpO₂ measurement: ±2%
- Infusion rate control: ±5% of target

### Stability Criteria
- Steady-state error: <5% of target
- Overshoot: <10% of step change
- Settling time: <30 seconds
- No sustained oscillations

## Scalability and Extensibility

### Future Enhancements

1. **Additional Sensors**
   - EEG for consciousness monitoring
   - Capnography for CO₂ monitoring
   - Temperature monitoring
   - Additional drug channels

2. **Advanced Control**
   - Model Predictive Control (MPC)
   - Adaptive PID tuning
   - Multi-variable optimization
   - Machine learning integration

3. **Connectivity**
   - WiFi/Bluetooth for remote monitoring
   - Integration with hospital EMR systems
   - Data analytics and reporting
   - Cloud backup and analysis

4. **User Interface**
   - Touchscreen display
   - Graphical trend display
   - Configuration interface
   - Alarm acknowledgment

## References

- PID Control Theory: Åström & Murray, "Feedback Systems"
- Medical Device Standards: IEC 60601-1
- Anesthesia Monitoring: "Clinical Anesthesia" by Barash et al.
- Embedded Systems: "Real-Time Systems Design and Analysis" by Phillip A. Laplante
