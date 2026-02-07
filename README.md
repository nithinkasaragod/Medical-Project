# Medical-Project
A closed-loop anesthesia delivery prototype using real-time physiological feedback (HR, MAP, RR, SpO₂) to automatically control drug infusion via a servo-driven IV mechanism with safety alarms.

# Googel Drive link
https://drive.google.com/drive/folders/11GEpnO9BKzEJP7l6zyrreYiuH9esYToA

# Closed-Loop Anesthesia Delivery System

A hardware-based closed-loop anesthesia delivery prototype that continuously monitors physiological parameters and automatically adjusts anesthetic infusion using embedded control logic.

This project was developed as part of a **24-hour TinkerHub Hackathon (Jan 31 – Feb 1)**.

---

## 🧠 Problem Statement

Conventional anesthesia delivery relies on manual adjustment by clinicians based on intermittent observation of patient vitals. This approach can lead to:

- Delayed response to physiological changes  
- Increased dependence on operator experience  
- Higher risk during long surgical procedures  

The goal of this project is to demonstrate a **closed-loop control system** that automates anesthetic drug delivery using real-time feedback while enforcing strict safety constraints.

---

## 🎯 Objectives

- Monitor key physiological parameters:
  - Heart Rate (HR)
  - Mean Arterial Pressure (MAP)
  - Respiratory Rate (RR)
  - Oxygen Saturation (SpO₂)
- Implement a real-time closed-loop control algorithm
- Automatically adjust infusion rate
- Provide visual and audible safety alerts
- Demonstrate a low-cost academic prototype

---

## ⚙️ System Architecture

---

## 🔧 Servo & Safety Logic

| Condition | Servo Angle | Alarm |
|---------|------------|-------|
| Normal | 65° | OFF |
| Low BP (MAP < 60) | 55° | Beep |
| Low SpO₂ (< 92%) | 47° | Continuous |

Safety overrides always take priority over control output.

---

## 🧩 Hardware Components

- Arduino microcontroller  
- Servo motor (IV clamp control)  
- OLED display (SSD1306)  
- Buzzer (audible alarms)  
- Power supply  
- Simulated IV drip setup  

---

## 💻 Software Implementation

- Language: Embedded C (Arduino)
- Features:
  - Priority-based control logic
  - Real-time OLED visualization
  - Audible alarm system
  - Serial input for vitals simulation

---

## 🧪 Results

- Stable closed-loop operation
- Correct servo response to changing vitals
- Immediate alarm triggering under unsafe conditions
- Suitable for academic and hackathon demonstration

---

## 🚀 Future Scope

- Integration of real biomedical sensors
- PID / adaptive control algorithms
- Wireless monitoring dashboard
- AI-based patient-specific models
- Digital twin simulation

---



## 👥 Team

- **Nithin B** – PG Diploma in ROS, I Hub School of Learning  
- **Hashim** – AI & Robotics, I Hub School of Learning  
- **Rahil** – AI & Robotics, I Hub School of Learning  
- **Anugraha** – Medical Student  

---

## 🏆 Event

**TinkerHub 24-Hour Hackathon**  
📅 January 31 – February 1
