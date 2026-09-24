"""
Unit Test Suite for Smart Fitness Session Analyzer.

Tests domain classes, validation logic, recovery detection, baseline calculations,
and session classification across all required scenarios.
"""

import unittest
from data_generator import available_scenarios, generate_fitness_data
from main import (
    Metric,
    FitnessObservation,
    Participant,
    FitnessSession,
    SessionAnalyzer,
    validate_observation_data,
    calculate_summary_statistics,
    detect_recovery_pattern,
)


class TestSmartFitnessAnalyzer(unittest.TestCase):

    def setUp(self):
        self.profile = {
            "participant_id": "TEST_01",
            "baseline_heart_rate": 70,
            "baseline_skin_response": 1.5,
            "baseline_temperature": 32.0,
        }
        self.participant = Participant.from_dict(self.profile)

    def test_participant_encapsulation(self):
        """Verify getter properties and private attribute encapsulation."""
        self.assertEqual(self.participant.participant_id, "TEST_01")
        self.assertEqual(self.participant.baseline_hr, 70)
        self.assertEqual(self.participant.baseline_skin, 1.5)
        self.assertEqual(self.participant.baseline_temp, 32.0)

        # Private attribute privacy verification
        with self.assertRaises(AttributeError):
            _ = self.participant.__baseline_hr

    def test_fitness_observation_validation(self):
        """Test observation validation for valid, missing, and out-of-bound sensor data."""
        # Valid observation
        valid_obs = FitnessObservation(0, 110, 2.0, 33.0, 0.5, 0.95)
        self.assertTrue(valid_obs.is_valid())

        # Invalid: missing heart rate
        missing_hr = FitnessObservation(0, None, 2.0, 33.0, 0.5, 0.95)
        self.assertFalse(missing_hr.is_valid())

        # Invalid: heart rate out of range (> 205)
        high_hr = FitnessObservation(0, 250, 2.0, 33.0, 0.5, 0.95)
        self.assertFalse(high_hr.is_valid())

        # Invalid: activity level negative
        neg_act = FitnessObservation(0, 110, 2.0, 33.0, -0.2, 0.95)
        self.assertFalse(neg_act.is_valid())

        # Invalid: low signal quality (< 0.60)
        poor_signal = FitnessObservation(0, 110, 2.0, 33.0, 0.5, 0.35)
        self.assertFalse(poor_signal.is_valid())

    def test_standalone_functions(self):
        """Test standalone calculation and validation helper functions."""
        # 1. Validation function
        valid_dict = {
            "timestamp": 1,
            "heart_rate": 80,
            "skin_response": 1.2,
            "temperature": 32.5,
            "activity_level": 0.2,
            "signal_quality": 0.90,
        }
        self.assertTrue(validate_observation_data(valid_dict))

        # 2. Summary stats function
        stats = calculate_summary_statistics([10, 20, 30])
        self.assertEqual(stats["mean"], 20.0)
        self.assertEqual(stats["min"], 10.0)
        self.assertEqual(stats["max"], 30.0)

    def test_scenarios_classification(self):
        """Verify analyzer results across all 5 generated scenarios."""
        expected_classifications = {
            "resting": "resting",
            "moderate_activity": "moderate activity",
            "high_activity": "high activity",
            "recovery": "recovering",
            "poor_quality": "insufficient data",
        }

        for scenario in available_scenarios():
            profile, raw_obs = generate_fitness_data("P_TEST", scenario=scenario, seed=42, number_of_windows=12)
            part = Participant.from_dict(profile)
            session = FitnessSession(part)

            for o in raw_obs:
                session.add_observation(FitnessObservation(
                    timestamp=o["timestamp"],
                    heart_rate=o["heart_rate"],
                    skin_response=o["skin_response"],
                    temperature=o["temperature"],
                    activity_level=o["activity_level"],
                    signal_quality=o["signal_quality"],
                ))

            res = SessionAnalyzer(session).analyze()
            self.assertEqual(res["classification"], expected_classifications[scenario])


if __name__ == "__main__":
    unittest.main()