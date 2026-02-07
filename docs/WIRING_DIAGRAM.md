# Circuit Wiring Diagram

## Complete System Wiring

```
                          ┌───────────────────────────────────────┐
                          │      ANESTHESIA DELIVERY SYSTEM       │
                          │         Arduino Uno R3                │
                          └───────────────────────────────────────┘
                                          
                                   POWER SUPPLY
                          ┌──────────┐        ┌──────────┐
                          │  USB 5V  │        │ 7-12V DC │
                          │  or      │        │ (Optional)│
                          │  5V Ext  │        │          │
                          └─────┬────┘        └────┬─────┘
                                │                  │
                                └──────────┬───────┘
                                           │
        ╔══════════════════════════════════╧═══════════════════════════════════╗
        ║                         ARDUINO UNO R3                                ║
        ║                                                                       ║
        ║  ┌──────────────────────────────────────────────────────────────┐   ║
        ║  │ ANALOG INPUTS (Sensors)                                      │   ║
        ║  │                                                               │   ║
        ║  │  A0 ◄──────────┐  Heart Rate Sensor (HR)                    │   ║
        ║  │                 │  MAX30102 Pulse Oximeter                   │   ║
        ║  │                 │  VCC ──► 5V, GND ──► GND                   │   ║
        ║  │                 │  SIG ──► A0                                │   ║
        ║  │                 │                                             │   ║
        ║  │  A1 ◄──────────┐  Mean Arterial Pressure (MAP)              │   ║
        ║  │                 │  BP Monitor Module                         │   ║
        ║  │                 │  VCC ──► 5V, GND ──► GND                   │   ║
        ║  │                 │  SIG ──► A1                                │   ║
        ║  │                 │                                             │   ║
        ║  │  A2 ◄──────────┐  Respiratory Rate (RR)                     │   ║
        ║  │                 │  Piezo/Belt Sensor                         │   ║
        ║  │                 │  VCC ──► 5V, GND ──► GND                   │   ║
        ║  │                 │  SIG ──► A2                                │   ║
        ║  │                 │                                             │   ║
        ║  │  A3 ◄──────────┐  Oxygen Saturation (SpO2)                  │   ║
        ║  │                 │  MAX30102 (same as HR)                     │   ║
        ║  │                 │  SIG ──► A3 (or shared with A0)            │   ║
        ║  └───────────────────────────────────────────────────────────────┘   ║
        ║                                                                       ║
        ║  ┌──────────────────────────────────────────────────────────────┐   ║
        ║  │ DIGITAL I/O                                                   │   ║
        ║  │                                                               │   ║
        ║  │  D2 ◄──────────┐  Emergency Stop Button                      │   ║
        ║  │                 │  Normally Open, Momentary                  │   ║
        ║  │                 │  One side ──► D2                           │   ║
        ║  │                 │  Other side ──► GND                        │   ║
        ║  │                 │  (Internal pullup enabled)                 │   ║
        ║  │                 │                                             │   ║
        ║  │  D3 ◄──────────┐  Manual Override Switch                     │   ║
        ║  │                 │  SPST Toggle Switch                        │   ║
        ║  │                 │  One side ──► D3                           │   ║
        ║  │                 │  Other side ──► GND                        │   ║
        ║  │                 │  (Internal pullup enabled)                 │   ║
        ║  │                 │                                             │   ║
        ║  │  D8 ──►────────┐  Piezo Buzzer (Alarm)                      │   ║
        ║  │                 │  + ──► D8                                  │   ║
        ║  │                 │  - ──► GND                                 │   ║
        ║  │                 │  (Can add 100Ω resistor for volume)        │   ║
        ║  │                 │                                             │   ║
        ║  │  D9 ──►────────┐  Servo Motor (PWM)                         │   ║
        ║  │                 │  Signal (Orange) ──► D9                    │   ║
        ║  │                 │  VCC (Red) ──► 5V (external recommended)   │   ║
        ║  │                 │  GND (Brown) ──► GND                       │   ║
        ║  │                 │                                             │   ║
        ║  │  D13 ──►───────┐  LED (Alarm Indicator)                     │   ║
        ║  │                 │  Anode (+) ──► D13                         │   ║
        ║  │                 │  Cathode (-) ──► 220Ω ──► GND              │   ║
        ║  │                 │  (Built-in LED also available)             │   ║
        ║  └───────────────────────────────────────────────────────────────┘   ║
        ║                                                                       ║
        ║  ┌──────────────────────────────────────────────────────────────┐   ║
        ║  │ POWER PINS                                                    │   ║
        ║  │                                                               │   ║
        ║  │  5V  ──► Sensors VCC, LED (via resistor)                    │   ║
        ║  │  3.3V ──► Available if needed                                │   ║
        ║  │  GND  ──► All GND connections                                │   ║
        ║  │  VIN  ──► 7-12V external power (optional)                    │   ║
        ║  └───────────────────────────────────────────────────────────────┘   ║
        ╚═══════════════════════════════════════════════════════════════════════╝


## Component Details

### Emergency Stop Button (Large Red Mushroom Style)
```
     ╔════════╗
     ║  STOP  ║  ◄── Press to activate
     ╚════╤═══╝
          │
    ┌─────┴─────┐
    │  Normally │
    │    Open   │
    └─────┬─────┘
          │
     D2 ──┴── GND
     (with internal pullup)
```

### Manual Override Switch (SPST Toggle)
```
         ON
      ┌──┴──┐
      │  ●──┤ ◄── Flip to activate manual mode
      └─────┘
         OFF
      
      D3 ──┬── Switch ──┬── GND
     (with pullup)
```

### Servo Motor (TowerPro SG90 or similar)
```
      ┌─────────────┐
      │             │
      │   SERVO     │ ◄── Mechanical connection to IV valve
      │             │
      └──┬──┬──┬───┘
         │  │  │
       Brown│Orange
         │  │  │
       Red  │  │
         │  │  │
       GND 5V D9 (PWM)
```

### HR/SpO2 Sensor (MAX30102)
```
      ┌─────────────┐
      │   ┌───┐     │
      │   │ ● │     │ ◄── Finger clip/probe
      │   └───┘     │
      │  MAX30102   │
      └──┬──┬──┬───┘
         │  │  │
       VCC GND SDA/SCL or Analog
         │  │  │
        5V GND A0/A3
```

### Piezo Buzzer
```
         ┌─┐
         │+│ ◄── Audible alarm
         └┬┘
          │
       ┌──┴──┐
       │  -  │
       └─────┘
       
       + ──► D8
       - ──► GND
```

### LED Indicator
```
         ┌─┐
         │●│ ◄── Red LED (visual alarm)
         └┬┘
          │
       ┌──┴──┐
       │ 220Ω│ ◄── Current limiting resistor
       └──┬──┘
          │
       D13 ──┴── GND
```

## Physical Layout Recommendation

```
┌───────────────────────────────────────────────────────────────┐
│                     ENCLOSURE TOP VIEW                        │
│                                                               │
│  ┌─────────┐                                ┌──────────────┐ │
│  │ SENSORS │                                │  EMERGENCY   │ │
│  │  HR/SpO2│                                │     STOP     │ │
│  │  MAP    │                                │   [  ●  ]    │ │
│  │  RR     │                                └──────────────┘ │
│  └─────────┘                                                  │
│                                                               │
│              ┌──────────────────┐                            │
│              │                  │             ┌────────────┐ │
│              │  ARDUINO UNO R3  │             │  MANUAL    │ │
│              │                  │             │  OVERRIDE  │ │
│              └──────────────────┘             │   [ ─  ]   │ │
│                                               └────────────┘ │
│                                                               │
│  ┌──────────┐                                 ┌────┐         │
│  │  BUZZER  │                                 │LED │         │
│  │   ♪♪♪    │                                 │ ●  │         │
│  └──────────┘                                 └────┘         │
│                                                               │
│                       ┌─────────────┐                        │
│                       │    SERVO    │                        │
│                       │   MOTOR     │ ──►  To IV Mechanism   │
│                       └─────────────┘                        │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

## Wiring Best Practices

### 1. Power Distribution
- Use breadboard or terminal blocks for power distribution
- Keep power and signal wires separated
- Use appropriate wire gauge (22-24 AWG for signals, 18-20 AWG for power)

### 2. Servo Power
**Recommended:** Separate 5V power supply for servo
```
Arduino 5V ──► Sensors only
External 5V ──► Servo motor
Common GND ──► All components
```

**Why?** Servo draws high current that can cause voltage drops affecting Arduino/sensors.

### 3. Button/Switch Wiring
- Use internal pullup resistors (enabled in code)
- Connect button between pin and GND
- No external resistors needed

### 4. Sensor Connections
- Keep sensor wires short (<1 meter if possible)
- Use shielded cable for long runs
- Twist signal and ground wires together

### 5. Grounding
- Star grounding: All grounds meet at one point (Arduino GND)
- Avoid ground loops
- Ensure solid connections

## Breadboard Layout Example

```
Breadboard View (simplified):

     +5V Rail ═══════════════════════════════════════
        ║
        ╠══► HR Sensor VCC
        ╠══► MAP Sensor VCC  
        ╠══► RR Sensor VCC
        ╠══► SpO2 Sensor VCC
        ╠══► Servo VCC (if sharing)
        
     Arduino 5V ──►║

     GND Rail ═══════════════════════════════════════
        ║
        ╠══► HR Sensor GND
        ╠══► MAP Sensor GND
        ╠══► RR Sensor GND
        ╠══► SpO2 Sensor GND
        ╠══► Servo GND
        ╠══► Buzzer (-)
        ╠══► LED Cathode (via 220Ω)
        ╠══► E-Stop Button
        ╠══► Manual Override Switch
        
     Arduino GND ──►║

Signal Connections (direct to Arduino):
     HR Sensor SIG     ──► A0
     MAP Sensor SIG    ──► A1
     RR Sensor SIG     ──► A2
     SpO2 Sensor SIG   ──► A3
     Servo Signal      ──► D9
     Buzzer (+)        ──► D8
     LED Anode         ──► D13 (via 220Ω)
     E-Stop            ──► D2
     Manual Override   ──► D3
```

## Safety Considerations

### 1. Electrical Safety
- [ ] All connections properly insulated
- [ ] No exposed conductors
- [ ] Proper wire strain relief
- [ ] Fuse protection on power supply
- [ ] Enclosure properly grounded (if metal)

### 2. Mechanical Safety
- [ ] Servo securely mounted
- [ ] IV mechanism has physical stops
- [ ] Cannot over-rotate and damage equipment
- [ ] Emergency stop easily accessible
- [ ] Components secured against vibration

### 3. Environmental
- [ ] Keep away from water/liquids
- [ ] Adequate ventilation
- [ ] Operating temperature: 0-40°C
- [ ] Avoid direct sunlight
- [ ] Protected from dust/debris

## Testing Procedure

### Continuity Test (Power Off)
1. Check each connection with multimeter
2. Verify no shorts between power and ground
3. Check button/switch operation

### Power-On Test (No Load)
1. Connect only Arduino (no sensors/servo)
2. Check 5V rail voltage (should be 4.8-5.2V)
3. Upload test sketch that flashes LED
4. Verify Serial Monitor communication

### Component Test (Individual)
Test each component separately:
1. Connect sensor → Read value → Verify reasonable
2. Connect servo → Sweep 0-180° → Verify smooth motion
3. Connect buzzer → Play tone → Verify audible
4. Connect LED → Turn on/off → Verify visible
5. Connect buttons → Press → Verify digital read

### Integration Test (Full System)
1. Connect all components
2. Upload firmware
3. Verify system initialization
4. Check all sensors reporting
5. Test emergency stop
6. Test manual override
7. Observe servo response to sensor changes

## Troubleshooting

| Problem | Check | Solution |
|---------|-------|----------|
| No power | Power supply | Verify voltage, connections |
| Sensors not working | 5V rail | Check voltage, connections |
| Servo jittery | Power supply | Use separate 5V for servo |
| Random resets | Power/GND | Check all ground connections |
| Buttons not responding | Pullup | Verify INPUT_PULLUP in code |
| Buzzer silent | Polarity | Check +/- orientation |
| LED not lighting | Resistor | Check 220Ω resistor present |

## Bill of Materials (BOM)

| Qty | Component | Specification | Notes |
|-----|-----------|---------------|-------|
| 1 | Arduino Uno R3 | ATmega328P | Or compatible |
| 1 | Servo Motor | SG90 or similar | 180° rotation |
| 1 | HR Sensor | MAX30102 | Pulse oximeter |
| 1 | MAP Sensor | BP module | UART or analog |
| 1 | RR Sensor | Piezo/belt | Analog output |
| 1 | SpO2 Sensor | MAX30102 | Same as HR |
| 1 | Buzzer | Piezo, 5V | Audible alarm |
| 1 | LED | Red, 5mm | Visual alarm |
| 1 | Emergency Button | NO, momentary | Large red |
| 1 | Toggle Switch | SPST | Manual override |
| 1 | Resistor | 220Ω, 1/4W | For LED |
| 1 | Power Supply | 5V, 2A+ | USB or DC |
| 1 | Breadboard | Half-size | Or PCB |
| 1 | Jumper Wires | M-M, M-F | Various lengths |
| 1 | Enclosure | ABS/PC | Sized appropriately |

---

**Document Version:** 1.0  
**Last Updated:** February 2026  
**Review Before Assembly:** Ensure all components match specifications
