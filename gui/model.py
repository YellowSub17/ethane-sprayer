from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class TimingMode(str, Enum):
    VALVE = "Valve trigger (> 3 ms)"
    GATE_1 = "Gate 1 (0.3–3 ms)"
    PREDICTED = "Gate prediction (< 0.3 ms)"


class ShotState(str, Enum):
    '''
    Various states throughout a shot that the experiment can be in.
    '''
    IDLE = "IDLE"
    ARMED = "ARMED"
    CONDENSING = "CONDENSING"
    POSITIONING = "POSITIONING"
    SETTLING = "SETTLING"
    JET_TRIGGERED = "JET TRIGGERED"
    GATE_1_SEEN = "GATE 1 SEEN"
    GATE_2_SEEN = "GATE 2 SEEN"
    LASER_SCHEDULED = "LASER SCHEDULED"
    ARRIVAL_CHECKED = "ARRIVAL CHECKED"
    PLUNGING = "PLUNGING"
    COMPLETE = "COMPLETE"
    FAULT = "FAULT"


@dataclass(frozen=True)
class ExperimentConfig:
    '''
    ExperimentConfig: Configuration parameters for a ethane spray shot.

    requested_delay_us: Time (us) between pump laser activation and freezing.
    condensation_s: Time (s) for the sample to condensate on the grid.
    settle_ms: Time (ms)
    valve_pulse_us: Time (us) the ethane sprayer valve is open.
    gate_spacing_mm: Distance (mm) between GATE_1 and GATE_2 that measures the speed of the ethane.
    effective_distance_mm: Distance (mm) between GATE_2 and the sample grid.
    activation_temp_k: temprature (K) in which to activate (?).
    jetting_temp_k: temprature (K) of the liquid ethane.
    '''

    requested_delay_us: float = 107.0
    condensation_s: float = 60.0
    settle_ms: float = 200.0
    valve_pulse_us: float = 650.0
    gate_spacing_mm: float = 7.0
    effective_distance_mm: float = 0.92
    activation_temp_k: float = 290.0
    jetting_temp_k: float = 95.0

    def validate(self) -> None:
        positive = {
            "requested delay": self.requested_delay_us,
            "condensation time": self.condensation_s,
            "settling time": self.settle_ms,
            "valve pulse": self.valve_pulse_us,
            "gate spacing": self.gate_spacing_mm,
            "effective distance": self.effective_distance_mm,
            "activation temperature": self.activation_temp_k,
            "jetting temperature": self.jetting_temp_k,
        }
        for name, value in positive.items():
            if value <= 0:
                raise ValueError(f"{name} must be greater than zero")
        if self.settle_ms < 200.0:
            raise ValueError("settling time must be at least 200 ms")
        if self.effective_distance_mm >= self.gate_spacing_mm:
            raise ValueError("effective distance must be smaller than gate spacing")

    @property
    def timing_mode(self) -> TimingMode:
        if self.requested_delay_us > 3000.0:
            return TimingMode.VALVE
        if self.requested_delay_us >= 300.0:
            return TimingMode.GATE_1
        return TimingMode.PREDICTED

    def predicted_arrival_us(self, gate_1_us: float, gate_2_us: float) -> float:
        if gate_2_us <= gate_1_us:
            raise ValueError("Gate 2 timestamp must be later than Gate 1")
        transit_us = gate_2_us - gate_1_us
        return gate_2_us + transit_us * (
            self.effective_distance_mm / self.gate_spacing_mm
        )

    def laser_trigger_us(self, gate_1_us: float, gate_2_us: float) -> float:
        return self.predicted_arrival_us(gate_1_us, gate_2_us) - self.requested_delay_us


SIMULATION_SEQUENCE = (
    ShotState.ARMED,
    ShotState.CONDENSING,
    ShotState.POSITIONING,
    ShotState.SETTLING,
    ShotState.JET_TRIGGERED,
    ShotState.GATE_1_SEEN,
    ShotState.GATE_2_SEEN,
    ShotState.LASER_SCHEDULED,
    ShotState.ARRIVAL_CHECKED,
    ShotState.PLUNGING,
    ShotState.COMPLETE,
)

SEQUENCE_TT = {
        ShotState.ARMED:'''Arming equipment.''',
        ShotState.CONDENSING:'Condensing ethane.',
        ShotState.POSITIONING:'Positioning grid.',
        ShotState.SETTLING:'',
        ShotState.JET_TRIGGERED:'Spraying ethane jet.',
        ShotState.GATE_1_SEEN:'Jet passing through first gate.',
        ShotState.GATE_2_SEEN:'Jet passing through second gate.',
        ShotState.LASER_SCHEDULED:'Pump laser firing.',
        ShotState.ARRIVAL_CHECKED:'Ethane impacts grid.',
        ShotState.PLUNGING:'Plunging grid.',
        ShotState.COMPLETE:'Complete.',
        }



