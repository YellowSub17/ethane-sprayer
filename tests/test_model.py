import unittest

from ethane_gui.model import ExperimentConfig, TimingMode
from ethane_gui.timeline import build_timeline_scenario


class ExperimentConfigTests(unittest.TestCase):
    def test_default_configuration_is_valid(self):
        ExperimentConfig().validate()

    def test_timing_mode_boundaries(self):
        self.assertEqual(ExperimentConfig(requested_delay_us=3000).timing_mode, TimingMode.GATE_1)
        self.assertEqual(ExperimentConfig(requested_delay_us=3001).timing_mode, TimingMode.VALVE)
        self.assertEqual(ExperimentConfig(requested_delay_us=300).timing_mode, TimingMode.GATE_1)
        self.assertEqual(ExperimentConfig(requested_delay_us=299).timing_mode, TimingMode.PREDICTED)

    def test_arrival_prediction(self):
        config = ExperimentConfig()
        predicted = config.predicted_arrival_us(10_000, 12_690)
        self.assertAlmostEqual(predicted, 13_043.542857, places=5)

    def test_laser_trigger_precedes_arrival_by_requested_delay(self):
        config = ExperimentConfig(requested_delay_us=107)
        arrival = config.predicted_arrival_us(10_000, 12_690)
        laser = config.laser_trigger_us(10_000, 12_690)
        self.assertAlmostEqual(arrival - laser, 107)

    def test_rejects_short_settle_time(self):
        with self.assertRaisesRegex(ValueError, "at least 200 ms"):
            ExperimentConfig(settle_ms=199).validate()

    def test_rejects_impossible_geometry(self):
        with self.assertRaisesRegex(ValueError, "smaller than gate spacing"):
            ExperimentConfig(effective_distance_mm=7.0).validate()

    def test_active_timeline_uses_requested_delay(self):
        config = ExperimentConfig(requested_delay_us=107)
        scenario = build_timeline_scenario(config, TimingMode.PREDICTED)
        self.assertAlmostEqual(scenario.actual_arrival_us - scenario.activation_us, 107)

    def test_inactive_timeline_uses_representative_delay(self):
        config = ExperimentConfig(requested_delay_us=107)
        scenario = build_timeline_scenario(config, TimingMode.GATE_1)
        self.assertEqual(scenario.requested_delay_us, 2000)
        self.assertAlmostEqual(scenario.actual_arrival_us - scenario.activation_us, 2000)


if __name__ == "__main__":
    unittest.main()
