#!/usr/bin/env python3
"""
Anesthesia Delivery System Simulator

This simulator tests the control algorithm logic without requiring physical hardware.
It simulates patient vital signs and the response to anesthesia infusion.
"""

import time
import random
import math
from dataclasses import dataclass
from typing import Tuple

# Safety Thresholds (matching Arduino constants)
HR_MIN = 40
HR_MAX = 120
HR_TARGET = 70
MAP_MIN = 60
MAP_MAX = 110
MAP_TARGET = 85
RR_MIN = 8
RR_MAX = 25
SPO2_MIN = 92
SPO2_CRITICAL = 88

# PID Parameters (matching Arduino constants)
KP = 2.0
KI = 0.5
KD = 1.0

# Infusion Control
INFUSION_MIN = 0
INFUSION_MAX = 180
INFUSION_SAFE_MAX = 120


@dataclass
class VitalSigns:
    """Patient vital signs"""
    heart_rate: float
    mean_arterial_pressure: float
    respiratory_rate: float
    spo2: float


@dataclass
class PIDState:
    """PID controller state"""
    error: float = 0.0
    integral: float = 0.0
    derivative: float = 0.0
    last_error: float = 0.0
    output: float = 0.0


class PatientSimulator:
    """Simulates patient physiological response to anesthesia"""
    
    def __init__(self):
        # Baseline vitals (awake patient)
        self.baseline_hr = 75.0
        self.baseline_map = 90.0
        self.baseline_rr = 16.0
        self.baseline_spo2 = 98.0
        
        # Current vitals
        self.vitals = VitalSigns(
            heart_rate=self.baseline_hr,
            mean_arterial_pressure=self.baseline_map,
            respiratory_rate=self.baseline_rr,
            spo2=self.baseline_spo2
        )
        
        # Anesthesia effect accumulation
        self.anesthesia_level = 0.0
        self.anesthesia_decay_rate = 0.05  # Per update cycle
    
    def update(self, infusion_rate: int) -> VitalSigns:
        """
        Update patient vitals based on infusion rate
        
        Args:
            infusion_rate: Servo angle (0-180) representing infusion rate
        
        Returns:
            Updated VitalSigns
        """
        # Convert servo angle to anesthesia dose (0-1 normalized)
        dose = infusion_rate / 180.0
        
        # Update anesthesia level with infusion and decay
        self.anesthesia_level += dose * 0.1
        self.anesthesia_level -= self.anesthesia_decay_rate
        self.anesthesia_level = max(0.0, min(1.0, self.anesthesia_level))
        
        # Simulate physiological response to anesthesia
        # Heart rate decreases with anesthesia
        hr_effect = -30 * self.anesthesia_level
        self.vitals.heart_rate = self.baseline_hr + hr_effect
        
        # Blood pressure decreases with anesthesia
        map_effect = -20 * self.anesthesia_level
        self.vitals.mean_arterial_pressure = self.baseline_map + map_effect
        
        # Respiratory rate decreases with anesthesia
        rr_effect = -6 * self.anesthesia_level
        self.vitals.respiratory_rate = self.baseline_rr + rr_effect
        
        # SpO2 might decrease slightly with deep anesthesia (respiratory depression)
        if self.anesthesia_level > 0.7:
            spo2_effect = -5 * (self.anesthesia_level - 0.7)
        else:
            spo2_effect = 0
        self.vitals.spo2 = self.baseline_spo2 + spo2_effect
        
        # Add realistic noise/variation
        self.vitals.heart_rate += random.uniform(-2, 2)
        self.vitals.mean_arterial_pressure += random.uniform(-3, 3)
        self.vitals.respiratory_rate += random.uniform(-1, 1)
        self.vitals.spo2 += random.uniform(-0.5, 0.5)
        
        # Ensure physiologically realistic bounds
        self.vitals.heart_rate = max(30, min(150, self.vitals.heart_rate))
        self.vitals.mean_arterial_pressure = max(40, min(140, self.vitals.mean_arterial_pressure))
        self.vitals.respiratory_rate = max(4, min(30, self.vitals.respiratory_rate))
        self.vitals.spo2 = max(85, min(100, self.vitals.spo2))
        
        return self.vitals


class AnesthesiaController:
    """Closed-loop anesthesia controller using PID"""
    
    def __init__(self):
        self.pid_state = PIDState()
        self.current_infusion_rate = 0
        self.alarm_active = False
    
    def compute_pid_control(self, vitals: VitalSigns) -> int:
        """
        Compute PID control output based on vital signs
        
        Args:
            vitals: Current patient vital signs
        
        Returns:
            Target infusion rate (servo angle 0-180)
        """
        # Calculate error based on heart rate (primary indicator)
        hr_error = HR_TARGET - vitals.heart_rate
        normalized_error = hr_error / HR_TARGET
        
        # PID calculation
        self.pid_state.error = normalized_error
        self.pid_state.integral += self.pid_state.error * 1.0  # dt = 1 second
        self.pid_state.derivative = self.pid_state.error - self.pid_state.last_error
        
        # Anti-windup: Limit integral term
        self.pid_state.integral = max(-10.0, min(10.0, self.pid_state.integral))
        
        # Calculate PID output
        self.pid_state.output = (
            KP * self.pid_state.error +
            KI * self.pid_state.integral +
            KD * self.pid_state.derivative
        )
        
        # Convert PID output to servo angle (infusion rate)
        # Inverse relationship: higher HR means reduce infusion
        target_rate = self.current_infusion_rate - int(self.pid_state.output * 10)
        
        # Constrain to safe limits
        target_rate = max(INFUSION_MIN, min(INFUSION_SAFE_MAX, target_rate))
        
        # Additional safety: Reduce infusion if SpO2 is low
        if vitals.spo2 < SPO2_MIN:
            target_rate = target_rate // 2
        
        # Store error for next iteration
        self.pid_state.last_error = self.pid_state.error
        
        return target_rate
    
    def update_infusion_rate(self, target_rate: int) -> int:
        """
        Smoothly update infusion rate
        
        Args:
            target_rate: Desired infusion rate
        
        Returns:
            Actual infusion rate after smooth transition
        """
        step_size = 5
        
        if target_rate > self.current_infusion_rate:
            self.current_infusion_rate = min(
                self.current_infusion_rate + step_size,
                target_rate
            )
        elif target_rate < self.current_infusion_rate:
            self.current_infusion_rate = max(
                self.current_infusion_rate - step_size,
                target_rate
            )
        
        return self.current_infusion_rate
    
    def check_safety_thresholds(self, vitals: VitalSigns) -> Tuple[bool, str]:
        """
        Check if vitals are within safe thresholds
        
        Args:
            vitals: Current patient vital signs
        
        Returns:
            Tuple of (alarm_active, alarm_reason)
        """
        alarm_reasons = []
        
        # Check Heart Rate
        if vitals.heart_rate < HR_MIN:
            alarm_reasons.append(f"BRADYCARDIA: HR={vitals.heart_rate:.1f} < {HR_MIN}")
        elif vitals.heart_rate > HR_MAX:
            alarm_reasons.append(f"TACHYCARDIA: HR={vitals.heart_rate:.1f} > {HR_MAX}")
        
        # Check Mean Arterial Pressure
        if vitals.mean_arterial_pressure < MAP_MIN:
            alarm_reasons.append(f"HYPOTENSION: MAP={vitals.mean_arterial_pressure:.1f} < {MAP_MIN}")
        elif vitals.mean_arterial_pressure > MAP_MAX:
            alarm_reasons.append(f"HYPERTENSION: MAP={vitals.mean_arterial_pressure:.1f} > {MAP_MAX}")
        
        # Check Respiratory Rate
        if vitals.respiratory_rate < RR_MIN:
            alarm_reasons.append(f"BRADYPNEA: RR={vitals.respiratory_rate:.1f} < {RR_MIN}")
        elif vitals.respiratory_rate > RR_MAX:
            alarm_reasons.append(f"TACHYPNEA: RR={vitals.respiratory_rate:.1f} > {RR_MAX}")
        
        # Check SpO2 - Critical Parameter
        if vitals.spo2 < SPO2_CRITICAL:
            alarm_reasons.append(f"CRITICAL HYPOXEMIA: SpO2={vitals.spo2:.1f} < {SPO2_CRITICAL}")
            # Emergency action: Stop infusion
            self.current_infusion_rate = 0
        elif vitals.spo2 < SPO2_MIN:
            alarm_reasons.append(f"HYPOXEMIA: SpO2={vitals.spo2:.1f} < {SPO2_MIN}")
        
        alarm_active = len(alarm_reasons) > 0
        alarm_reason = " | ".join(alarm_reasons) if alarm_active else ""
        
        return alarm_active, alarm_reason


def run_simulation(duration_seconds: int = 60, update_interval: float = 1.0):
    """
    Run the anesthesia delivery system simulation
    
    Args:
        duration_seconds: Total simulation duration
        update_interval: Time between updates in seconds
    """
    print("=" * 70)
    print("Anesthesia Delivery System Simulator")
    print("=" * 70)
    print()
    
    # Initialize components
    patient = PatientSimulator()
    controller = AnesthesiaController()
    
    # Simulation loop
    num_updates = int(duration_seconds / update_interval)
    
    for iteration in range(num_updates):
        print(f"\n--- Update {iteration + 1}/{num_updates} (t={iteration * update_interval:.1f}s) ---")
        
        # Read current vitals
        vitals = patient.vitals
        
        # Compute control output
        target_rate = controller.compute_pid_control(vitals)
        actual_rate = controller.update_infusion_rate(target_rate)
        
        # Check safety
        alarm_active, alarm_reason = controller.check_safety_thresholds(vitals)
        
        # Print status
        print(f"Vital Signs:")
        print(f"  HR:  {vitals.heart_rate:6.1f} bpm")
        print(f"  MAP: {vitals.mean_arterial_pressure:6.1f} mmHg")
        print(f"  RR:  {vitals.respiratory_rate:6.1f} breaths/min")
        print(f"  SpO2: {vitals.spo2:5.1f} %")
        
        print(f"Control:")
        print(f"  PID Error:      {controller.pid_state.error:7.3f}")
        print(f"  PID Output:     {controller.pid_state.output:7.3f}")
        print(f"  Infusion Rate:  {actual_rate:3d}° (servo angle)")
        print(f"  Anesthesia Lvl: {patient.anesthesia_level:5.2f}")
        
        if alarm_active:
            print(f"\n⚠️  ALARM: {alarm_reason}")
        else:
            print(f"\n✓  Status: Normal")
        
        # Update patient state based on infusion
        patient.update(actual_rate)
        
        # Wait for next update
        time.sleep(update_interval)
    
    print("\n" + "=" * 70)
    print("Simulation Complete")
    print("=" * 70)


def run_test_scenarios():
    """Run predefined test scenarios"""
    print("=" * 70)
    print("Running Test Scenarios")
    print("=" * 70)
    
    # Test 1: Normal operation
    print("\nTest 1: Normal Patient Response")
    print("-" * 50)
    patient = PatientSimulator()
    controller = AnesthesiaController()
    
    for i in range(30):
        vitals = patient.vitals
        target_rate = controller.compute_pid_control(vitals)
        actual_rate = controller.update_infusion_rate(target_rate)
        patient.update(actual_rate)
        
        if i % 10 == 0:
            print(f"t={i}s: HR={vitals.heart_rate:.1f}, "
                  f"MAP={vitals.mean_arterial_pressure:.1f}, "
                  f"Rate={actual_rate}°")
    
    # Test 2: Safety alarm
    print("\nTest 2: Safety Alarm (Simulated Hypoxemia)")
    print("-" * 50)
    patient2 = PatientSimulator()
    controller2 = AnesthesiaController()
    patient2.vitals.spo2 = 90.0  # Below threshold
    
    vitals = patient2.vitals
    alarm_active, alarm_reason = controller2.check_safety_thresholds(vitals)
    
    if alarm_active:
        print(f"✓ Alarm correctly triggered: {alarm_reason}")
    else:
        print("✗ Alarm should have triggered")
    
    # Test 3: PID response
    print("\nTest 3: PID Controller Response")
    print("-" * 50)
    patient3 = PatientSimulator()
    controller3 = AnesthesiaController()
    patient3.vitals.heart_rate = 95.0  # Above target
    
    initial_hr = patient3.vitals.heart_rate
    for i in range(20):
        vitals = patient3.vitals
        target_rate = controller3.compute_pid_control(vitals)
        actual_rate = controller3.update_infusion_rate(target_rate)
        patient3.update(actual_rate)
    
    final_hr = patient3.vitals.heart_rate
    print(f"Initial HR: {initial_hr:.1f} bpm")
    print(f"Final HR:   {final_hr:.1f} bpm")
    print(f"Target HR:  {HR_TARGET} bpm")
    
    if abs(final_hr - HR_TARGET) < abs(initial_hr - HR_TARGET):
        print("✓ PID controller successfully reduced HR toward target")
    else:
        print("✗ PID controller did not improve HR")
    
    print("\n" + "=" * 70)
    print("All tests complete")
    print("=" * 70)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_test_scenarios()
    else:
        # Run live simulation
        run_simulation(duration_seconds=60, update_interval=1.0)
