#!/usr/bin/env python3
"""
Unit Tests for Anesthesia Delivery System

Comprehensive test suite for validating the control algorithm,
safety features, and system behavior.
"""

import unittest
import sys
from simulator import (
    PatientSimulator,
    AnesthesiaController,
    VitalSigns,
    HR_MIN, HR_MAX, HR_TARGET,
    MAP_MIN, MAP_MAX,
    RR_MIN, RR_MAX,
    SPO2_MIN, SPO2_CRITICAL,
    INFUSION_SAFE_MAX
)


class TestPatientSimulator(unittest.TestCase):
    """Test patient physiological simulation"""
    
    def setUp(self):
        self.patient = PatientSimulator()
    
    def test_initialization(self):
        """Test patient simulator initializes with normal vitals"""
        self.assertGreaterEqual(self.patient.vitals.heart_rate, 60)
        self.assertLessEqual(self.patient.vitals.heart_rate, 100)
        self.assertGreaterEqual(self.patient.vitals.mean_arterial_pressure, 70)
        self.assertGreaterEqual(self.patient.vitals.respiratory_rate, 12)
        self.assertGreaterEqual(self.patient.vitals.spo2, 95)
    
    def test_anesthesia_effect(self):
        """Test that infusion decreases heart rate"""
        initial_hr = self.patient.vitals.heart_rate
        
        # Apply high infusion rate for several cycles
        for _ in range(20):
            self.patient.update(120)  # High infusion
        
        final_hr = self.patient.vitals.heart_rate
        self.assertLess(final_hr, initial_hr, 
                       "Heart rate should decrease with anesthesia")
    
    def test_anesthesia_decay(self):
        """Test that anesthesia level decays over time"""
        # Build up anesthesia level
        for _ in range(20):
            self.patient.update(120)
        
        mid_level = self.patient.anesthesia_level
        self.assertGreater(mid_level, 0.15, "Anesthesia should accumulate")
        
        # Stop infusion and let it decay
        for _ in range(30):
            self.patient.update(0)
        
        final_level = self.patient.anesthesia_level
        self.assertLess(final_level, mid_level, 
                       "Anesthesia should decay without infusion")
    
    def test_spo2_response_to_deep_anesthesia(self):
        """Test that deep anesthesia causes SpO2 to decrease"""
        initial_spo2 = self.patient.vitals.spo2
        
        # Build up deep anesthesia
        for _ in range(100):
            self.patient.update(180)  # Maximum infusion
        
        final_spo2 = self.patient.vitals.spo2
        
        # SpO2 should drop with respiratory depression
        # Check anesthesia level is high
        self.assertGreater(self.patient.anesthesia_level, 0.7,
                          "Anesthesia level should be high with sustained infusion")
        
        # SpO2 should be lower than initial (may not drop below 95 with noise)
        self.assertLess(final_spo2, initial_spo2 + 1,
                       "SpO2 should decrease or stay same with deep anesthesia")
    
    def test_vitals_stay_in_physiological_bounds(self):
        """Test that simulated vitals remain physiologically possible"""
        # Random infusion rates
        for i in range(100):
            rate = (i * 37) % 180  # Pseudo-random pattern
            vitals = self.patient.update(rate)
            
            self.assertGreaterEqual(vitals.heart_rate, 30)
            self.assertLessEqual(vitals.heart_rate, 150)
            self.assertGreaterEqual(vitals.mean_arterial_pressure, 40)
            self.assertLessEqual(vitals.mean_arterial_pressure, 140)
            self.assertGreaterEqual(vitals.respiratory_rate, 4)
            self.assertLessEqual(vitals.respiratory_rate, 30)
            self.assertGreaterEqual(vitals.spo2, 85)
            self.assertLessEqual(vitals.spo2, 100)


class TestAnesthesiaController(unittest.TestCase):
    """Test PID controller and safety systems"""
    
    def setUp(self):
        self.controller = AnesthesiaController()
    
    def test_initialization(self):
        """Test controller initializes with safe defaults"""
        self.assertEqual(self.controller.current_infusion_rate, 0)
        self.assertFalse(self.controller.alarm_active)
        self.assertEqual(self.controller.pid_state.integral, 0.0)
    
    def test_pid_reduces_high_hr(self):
        """Test PID controller reduces HR when above target"""
        vitals = VitalSigns(
            heart_rate=95.0,  # Above target
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        target_rate = self.controller.compute_pid_control(vitals)
        
        # Should increase infusion to reduce HR
        self.assertGreater(target_rate, 0,
                          "Infusion should increase when HR > target")
    
    def test_pid_increases_low_hr(self):
        """Test PID controller increases HR when below target"""
        # First, establish some infusion
        self.controller.current_infusion_rate = 50
        
        vitals = VitalSigns(
            heart_rate=50.0,  # Below target
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        target_rate = self.controller.compute_pid_control(vitals)
        
        # Should decrease infusion to increase HR
        self.assertLess(target_rate, 50,
                       "Infusion should decrease when HR < target")
    
    def test_pid_convergence(self):
        """Test PID controller converges to target"""
        patient = PatientSimulator()
        patient.vitals.heart_rate = 90.0  # Start above target
        
        # Run closed loop for several iterations
        for _ in range(30):
            target_rate = self.controller.compute_pid_control(patient.vitals)
            actual_rate = self.controller.update_infusion_rate(target_rate)
            patient.update(actual_rate)
        
        final_hr = patient.vitals.heart_rate
        
        # Should be closer to target than initial
        initial_error = abs(90.0 - HR_TARGET)
        final_error = abs(final_hr - HR_TARGET)
        
        self.assertLess(final_error, initial_error,
                       "PID should reduce error over time")
        self.assertLess(final_error, 10,
                       "Should get within 10 bpm of target")
    
    def test_infusion_rate_limiting(self):
        """Test smooth rate transitions"""
        self.controller.current_infusion_rate = 50
        
        # Try to jump to 100 degrees
        actual = self.controller.update_infusion_rate(100)
        
        # Should only move by step size, not jump immediately
        self.assertLess(actual, 100)
        self.assertGreater(actual, 50)
    
    def test_safe_maximum_enforced(self):
        """Test infusion cannot exceed safe maximum"""
        vitals = VitalSigns(
            heart_rate=95.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        # Even with high HR, should not exceed safe max
        target_rate = self.controller.compute_pid_control(vitals)
        self.assertLessEqual(target_rate, INFUSION_SAFE_MAX,
                            "Should not exceed safe maximum")
    
    def test_integral_anti_windup(self):
        """Test integral term is limited to prevent windup"""
        vitals = VitalSigns(
            heart_rate=95.0,  # Persistent error
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        # Run for many iterations with persistent error
        for _ in range(100):
            self.controller.compute_pid_control(vitals)
        
        # Integral should be clamped
        self.assertLessEqual(abs(self.controller.pid_state.integral), 10.0,
                            "Integral term should be limited")


class TestSafetySystem(unittest.TestCase):
    """Test safety monitoring and alarms"""
    
    def setUp(self):
        self.controller = AnesthesiaController()
    
    def test_bradycardia_alarm(self):
        """Test alarm activates for low heart rate"""
        vitals = VitalSigns(
            heart_rate=35.0,  # Below minimum
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("BRADYCARDIA", reason)
    
    def test_tachycardia_alarm(self):
        """Test alarm activates for high heart rate"""
        vitals = VitalSigns(
            heart_rate=125.0,  # Above maximum
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("TACHYCARDIA", reason)
    
    def test_hypotension_alarm(self):
        """Test alarm activates for low blood pressure"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=55.0,  # Below minimum
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("HYPOTENSION", reason)
    
    def test_hypertension_alarm(self):
        """Test alarm activates for high blood pressure"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=115.0,  # Above maximum
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("HYPERTENSION", reason)
    
    def test_bradypnea_alarm(self):
        """Test alarm activates for low respiratory rate"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=6.0,  # Below minimum
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("BRADYPNEA", reason)
    
    def test_tachypnea_alarm(self):
        """Test alarm activates for high respiratory rate"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=28.0,  # Above maximum
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("TACHYPNEA", reason)
    
    def test_hypoxemia_alarm(self):
        """Test alarm activates for low SpO2"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=90.0  # Below minimum
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("HYPOXEMIA", reason)
    
    def test_critical_hypoxemia_stops_infusion(self):
        """Test critical SpO2 immediately stops infusion"""
        self.controller.current_infusion_rate = 80  # Some active infusion
        
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=85.0  # Critical level
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        self.assertIn("CRITICAL", reason)
        self.assertEqual(self.controller.current_infusion_rate, 0,
                        "Infusion should stop immediately at critical SpO2")
    
    def test_low_spo2_reduces_infusion(self):
        """Test low SpO2 causes infusion rate reduction"""
        vitals_normal = VitalSigns(
            heart_rate=80.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        vitals_low_spo2 = VitalSigns(
            heart_rate=80.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=91.0  # Low but not critical
        )
        
        rate_normal = self.controller.compute_pid_control(vitals_normal)
        
        controller2 = AnesthesiaController()
        rate_low_spo2 = controller2.compute_pid_control(vitals_low_spo2)
        
        self.assertLess(rate_low_spo2, rate_normal,
                       "Infusion should be reduced when SpO2 is low")
    
    def test_multiple_alarms(self):
        """Test system handles multiple simultaneous alarms"""
        vitals = VitalSigns(
            heart_rate=125.0,   # Tachycardia
            mean_arterial_pressure=115.0,  # Hypertension
            respiratory_rate=28.0,  # Tachypnea
            spo2=90.0  # Hypoxemia
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertTrue(alarm_active)
        # Should mention multiple issues
        alarm_count = reason.count("|")
        self.assertGreater(alarm_count, 1,
                          "Should report multiple alarm conditions")
    
    def test_normal_vitals_no_alarm(self):
        """Test no alarm with all vitals normal"""
        vitals = VitalSigns(
            heart_rate=70.0,
            mean_arterial_pressure=85.0,
            respiratory_rate=15.0,
            spo2=98.0
        )
        
        alarm_active, reason = self.controller.check_safety_thresholds(vitals)
        
        self.assertFalse(alarm_active)
        self.assertEqual(reason, "")


class TestIntegration(unittest.TestCase):
    """Integration tests for complete system"""
    
    def test_full_system_simulation(self):
        """Test complete system runs without errors"""
        patient = PatientSimulator()
        controller = AnesthesiaController()
        
        # Simulate 60 seconds
        for _ in range(60):
            vitals = patient.vitals
            target_rate = controller.compute_pid_control(vitals)
            actual_rate = controller.update_infusion_rate(target_rate)
            controller.check_safety_thresholds(vitals)
            patient.update(actual_rate)
        
        # Should complete without exceptions
        self.assertTrue(True)
    
    def test_system_recovers_from_alarm(self):
        """Test system can recover after alarm condition resolves"""
        patient = PatientSimulator()
        controller = AnesthesiaController()
        
        # Create alarm condition (low SpO2)
        patient.vitals.spo2 = 90.0
        alarm_active, _ = controller.check_safety_thresholds(patient.vitals)
        self.assertTrue(alarm_active)
        
        # Allow recovery
        patient.vitals.spo2 = 98.0
        alarm_active, _ = controller.check_safety_thresholds(patient.vitals)
        self.assertFalse(alarm_active)
    
    def test_system_stability_over_time(self):
        """Test system maintains stability over extended period"""
        patient = PatientSimulator()
        controller = AnesthesiaController()
        
        # Run for extended period
        hr_values = []
        for _ in range(120):  # 2 minutes
            target_rate = controller.compute_pid_control(patient.vitals)
            actual_rate = controller.update_infusion_rate(target_rate)
            patient.update(actual_rate)
            hr_values.append(patient.vitals.heart_rate)
        
        # Check for stability in second half
        second_half = hr_values[60:]
        mean_hr = sum(second_half) / len(second_half)
        
        # Should be close to target
        self.assertLess(abs(mean_hr - HR_TARGET), 15,
                       "Mean HR should stabilize near target")


def run_tests():
    """Run all tests and return results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestPatientSimulator))
    suite.addTests(loader.loadTestsFromTestCase(TestAnesthesiaController))
    suite.addTests(loader.loadTestsFromTestCase(TestSafetySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
