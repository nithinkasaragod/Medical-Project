# Quick Start Guide

## Overview
This guide will help you quickly set up and test the anesthesia delivery system.

## For Simulation (No Hardware Required)

### Prerequisites
- Python 3.6 or later
- No additional libraries required (uses only standard library)

### Running the Simulator

1. **Clone the repository**
   ```bash
   git clone https://github.com/nithinkasaragod/Medical-Project.git
   cd Medical-Project
   ```

2. **Run the live simulation** (60-second real-time simulation)
   ```bash
   python3 simulator.py
   ```
   
   This will show:
   - Real-time vital signs
   - PID controller output
   - Infusion rate adjustments
   - Alarm status

3. **Run automated tests**
   ```bash
   python3 simulator.py test
   ```
   
   This runs three quick validation tests:
   - Normal patient response
   - Safety alarm trigger
   - PID convergence

4. **Run comprehensive test suite**
   ```bash
   python3 test_system.py
   ```
   
   This runs 26 unit tests covering:
   - Patient simulator behavior
   - PID controller logic
   - Safety threshold monitoring
   - Integration scenarios

## For Hardware Implementation

### Prerequisites
- Arduino Uno R3 (or compatible board)
- Arduino IDE (version 1.8.x or later)
- Required sensors (see hardware requirements)
- Servo motor
- Buzzer and LED
- Buttons/switches

### Hardware Setup

1. **Assemble the circuit**
   
   Follow this pin configuration:
   
   ```
   Component               Arduino Pin    Connection Type
   ─────────────────────────────────────────────────────
   HR Sensor              A0             Analog input
   MAP Sensor             A1             Analog input
   RR Sensor              A2             Analog input
   SpO2 Sensor            A3             Analog input
   
   Servo Motor            9              PWM output
   Buzzer                 8              Digital output
   LED (Alarm)            13             Digital output
   
   Emergency Stop Button  2              Digital input (pullup)
   Manual Override Switch 3              Digital input (pullup)
   ```

2. **Connect power**
   - Arduino: USB or 7-12V DC to barrel jack
   - Servo: Separate 5V supply recommended (can share ground)
   - Sensors: 5V and GND from Arduino

3. **Load the firmware**
   ```
   a. Open Arduino IDE
   b. File → Open → anesthesia_controller.ino
   c. Tools → Board → Arduino Uno
   d. Tools → Port → Select your Arduino's port
   e. Click Upload button
   ```

4. **Open Serial Monitor**
   ```
   a. Tools → Serial Monitor
   b. Set baud rate to 9600
   c. Observe system initialization
   ```

### First-Time Calibration

1. **Test emergency stop**
   - Press emergency stop button
   - Verify servo moves to 0°
   - Verify alarm activates
   - Release button to resume

2. **Test manual override**
   - Flip manual override switch
   - Verify system enters manual mode
   - Flip back to resume automatic control

3. **Check sensor readings**
   - Observe vital signs in Serial Monitor
   - Verify values are reasonable
   - If values seem wrong, check sensor connections

4. **Calibrate sensors** (if using real sensors)
   - Compare readings to known standards
   - Adjust calibration in code if needed
   - See sensor datasheets for specific procedures

### Daily Operation Checklist

Before each session:

```
□ Visual inspection of all connections
□ Power on system
□ Wait for initialization (LED flash + beep)
□ Check Serial Monitor shows "System initialization complete"
□ Verify sensor readings are reasonable
□ Test emergency stop (press and release)
□ Test alarm (should trigger during E-stop)
□ Document baseline readings
```

### Monitoring During Operation

Watch the Serial Monitor output:

```
--- System Status ---
State: ACTIVE CONTROL
Vital Signs:
  HR:  72.3 bpm          ← Heart rate (target: 70)
  MAP: 87.1 mmHg         ← Blood pressure (target: 85)
  RR:  14.8 breaths/min  ← Respiratory rate
  SpO2: 97.2 %           ← Oxygen saturation (critical)

Control:
  PID Error: 0.033       ← Normalized error
  PID Output: 0.067      ← Controller output
  Infusion Rate: 45°     ← Current servo angle (0-120)
```

**Normal operation:**
- State cycles between MONITORING and ACTIVE CONTROL
- Vital signs stay within normal ranges
- Infusion rate adjusts gradually
- No alarms active

**Alarm condition:**
```
--- System Status ---
State: ALARM
...
  ⚠ ALARM ACTIVE
```

### Emergency Procedures

1. **Any alarm activates:**
   - Check patient immediately
   - Identify alarm cause from Serial Monitor
   - Verify appropriate system response
   - Do not silence until condition resolved

2. **Critical alarm (SpO2 < 88%):**
   - System automatically stops infusion
   - Maximum alarm level
   - Check airway, breathing, circulation
   - Provide supplemental oxygen/ventilation as needed
   - Do not restart until SpO2 > 95%

3. **Multiple alarms:**
   - Indicates serious condition
   - Press emergency stop if needed
   - Assess patient thoroughly
   - Call for assistance

4. **System malfunction:**
   - Press emergency stop immediately
   - Switch to manual IV control
   - Document the malfunction
   - Do not restart until issue diagnosed

### Shutdown Procedure

```
1. Activate manual override
2. Observe infusion rate gradually decrease
3. Once rate is 0°, disconnect IV
4. Power off Arduino
5. Save/document session data from Serial Monitor
6. Clean and sanitize sensors
```

## Interpreting Results

### Vital Sign Ranges

| Parameter | Normal | Warning | Critical |
|-----------|--------|---------|----------|
| HR (bpm) | 60-80 | 40-60 or 80-120 | <40 or >120 |
| MAP (mmHg) | 70-100 | 60-70 or 100-110 | <60 or >110 |
| RR (br/min) | 10-20 | 8-10 or 20-25 | <8 or >25 |
| SpO2 (%) | 95-100 | 92-95 | <92 |

### PID Controller Behavior

- **PID Error > 0:** HR below target → System may increase infusion
- **PID Error < 0:** HR above target → System will increase infusion
- **PID Error ≈ 0:** At target → Minimal adjustments

The controller uses an *inverse* relationship:
- High HR indicates light anesthesia → Increase drug
- Low HR indicates deep anesthesia → Decrease drug

### System States

| State | Meaning | Infusion |
|-------|---------|----------|
| INITIALIZING | Starting up | 0° |
| MONITORING | Watching vitals | 0° |
| ACTIVE CONTROL | PID controlling | Variable |
| ALARM STATE | Threshold violated | Reduced/Stopped |
| EMERGENCY STOP | E-stop pressed | 0° (forced) |
| MANUAL MODE | Manual override | Maintained |

## Troubleshooting

### Problem: Sensors show unrealistic values

**Solutions:**
- Check sensor connections (loose wires)
- Verify sensor power (5V and GND)
- Check sensor is not damaged
- Review calibration settings in code

### Problem: Servo not moving

**Solutions:**
- Check servo connection to pin 9
- Verify servo power supply
- Test servo with basic Arduino sketch
- Check mechanical linkage is not stuck

### Problem: No Serial Monitor output

**Solutions:**
- Verify baud rate is 9600
- Check USB connection
- Try different USB port
- Check Arduino has power

### Problem: Alarm constantly active

**Solutions:**
- Check if vitals are actually abnormal
- Verify sensor accuracy
- Review threshold settings in code
- May need recalibration

### Problem: System not responding to emergency stop

**Solutions:**
- This indicates a serious hardware issue
- Disconnect power immediately
- Check button wiring
- Check button is normally-open type
- Do not use until repaired

## Best Practices

### For Development/Testing

1. **Always test with simulator first**
   - Verify control logic works
   - Test safety features
   - Validate alarm thresholds

2. **Use Serial Monitor extensively**
   - Monitor all system activity
   - Log data for analysis
   - Identify issues early

3. **Test emergency procedures**
   - Practice emergency stop
   - Verify alarm responses
   - Time response latencies

4. **Document everything**
   - Record calibrations
   - Log test results
   - Note any anomalies

### For Safety

1. **Never bypass safety features**
   - Keep emergency stop functional
   - Don't disable alarms
   - Maintain threshold monitoring

2. **Always have backup**
   - Manual control capability
   - Alternative infusion method
   - Emergency medications ready

3. **Stay vigilant**
   - Continuous monitoring required
   - Quick response to alarms
   - Don't leave system unattended

4. **Know your limits**
   - This is a prototype
   - Not for clinical use
   - Seek expert help when needed

## Example Session

Here's what a typical 5-minute test session looks like:

```bash
$ python3 simulator.py test

======================================================================
Running Test Scenarios
======================================================================

Test 1: Normal Patient Response
--------------------------------------------------
t=0s: HR=75.0, MAP=90.0, Rate=0°
t=10s: HR=74.1, MAP=92.5, Rate=34°
t=20s: HR=74.7, MAP=91.0, Rate=84°

✓ System maintains stable control

Test 2: Safety Alarm (Simulated Hypoxemia)
--------------------------------------------------
✓ Alarm correctly triggered: HYPOXEMIA: SpO2=90.0 < 92

Test 3: PID Controller Response
--------------------------------------------------
Initial HR: 95.0 bpm
Final HR:   73.6 bpm
Target HR:  70 bpm
✓ PID controller successfully reduced HR toward target

======================================================================
All tests complete
======================================================================
```

## Next Steps

1. **Learn the system**
   - Read all documentation
   - Understand control algorithm
   - Practice with simulator

2. **Assemble hardware**
   - Order components
   - Build circuit
   - Test each component

3. **Calibrate and test**
   - Sensor calibration
   - Servo calibration
   - Safety feature validation

4. **Advanced features**
   - Experiment with PID parameters
   - Add data logging
   - Implement additional sensors

## Support Resources

- **Documentation:** See `docs/` folder
  - HARDWARE_REQUIREMENTS.md
  - ARCHITECTURE.md
  - SAFETY_PROTOCOLS.md

- **Code Examples:**
  - anesthesia_controller.ino
  - simulator.py
  - test_system.py

- **Community:**
  - GitHub Issues: Report bugs or ask questions
  - Discussions: Share improvements and ideas

## Important Reminders

⚠️ **This is a prototype for educational/research purposes only**

- NOT FDA approved
- NOT for clinical use on humans
- Requires extensive validation before medical use
- Always follow safety protocols
- Keep medical professionals informed

---

**Document Version:** 1.0  
**Last Updated:** February 2026
