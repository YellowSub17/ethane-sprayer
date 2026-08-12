from __future__ import annotations

from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk

from .model import ExperimentConfig, TimingMode


BG = "#101820"
PANEL = "#17232d"
TEXT = "#e8f0f2"
MUTED = "#8fa5b2"
GREEN = "#47d18c"
AMBER = "#f1b84b"
ORANGE = "#f07a3f"
MAGENTA = "#ef4da8"
BLUE = "#72a7e8"


@dataclass(frozen=True)
class TimelineScenario:
    mode: TimingMode
    requested_delay_us: float
    valve_us: float
    gate_1_us: float
    gate_2_us: float
    predicted_arrival_us: float
    activation_us: float
    actual_arrival_us: float


def build_timeline_scenario(config: ExperimentConfig, mode: TimingMode) -> TimelineScenario:
    """Create idealized events for a Figure S3/S4/S5-style display."""
    representative_delays = {
        TimingMode.VALVE: 5000.0,
        TimingMode.GATE_1: 2000.0,
        TimingMode.PREDICTED: 100.0,
    }
    delay_us = config.requested_delay_us if config.timing_mode == mode else representative_delays[mode]
    valve_us = 0.0
    gate_1_us = 10_000.0
    gate_2_us = 12_690.0
    predicted_us = config.predicted_arrival_us(gate_1_us, gate_2_us)
    activation_us = predicted_us - delay_us
    return TimelineScenario(
        mode=mode,
        requested_delay_us=delay_us,
        valve_us=valve_us,
        gate_1_us=gate_1_us,
        gate_2_us=gate_2_us,
        predicted_arrival_us=predicted_us,
        activation_us=activation_us,
        actual_arrival_us=predicted_us,
    )


class TimelineWindow(tk.Toplevel):
    """Live, idealized timing diagrams based on supplementary Figures S3-S5."""

    def __init__(self, parent: tk.Misc, config: ExperimentConfig) -> None:
        super().__init__(parent)
        self.title("Ethane Sprayer — Timing Diagrams")
        self.geometry("1080x700")
        self.minsize(820, 560)
        self.configure(bg=BG)
        self.transient(parent)
        self._config = config
        self._active_state = "IDLE"
        self._canvases: dict[TimingMode, tk.Canvas] = {}

        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(header, text="EXPERIMENT TIMELINES", bg=BG, fg=TEXT, font=("Arial", 18, "bold")).pack(side="left")
        self.mode_badge = tk.Label(
            header, bg="#21333f", fg=AMBER, font=("Arial", 10, "bold"), padx=12, pady=6
        )
        self.mode_badge.pack(side="right")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=8)
        tab_names = {
            TimingMode.VALVE: "> 3 ms  ·  valve reference",
            TimingMode.GATE_1: "0.3–3 ms  ·  Gate 1 reference",
            TimingMode.PREDICTED: "< 300 µs  ·  two-gate prediction",
        }
        for mode, title in tab_names.items():
            frame = tk.Frame(self.notebook, bg=PANEL)
            canvas = tk.Canvas(frame, bg=PANEL, highlightthickness=0)
            canvas.pack(fill="both", expand=True)
            canvas.bind("<Configure>", lambda _event, m=mode: self._draw(m))
            self.notebook.add(frame, text=title)
            self._canvases[mode] = canvas

        note = (
            "Idealized simulated signals based on Supplementary Figures S3–S5. "
            "The traces update from the GUI parameters; they are not measured data."
        )
        tk.Label(self, text=note, bg=BG, fg=MUTED, font=("Arial", 9)).pack(
            anchor="w", padx=22, pady=(2, 14)
        )
        self.update_config(config, select_active=True)

    def update_config(self, config: ExperimentConfig, select_active: bool = False) -> None:
        self._config = config
        self.mode_badge.configure(
            text=f"CURRENT: {config.requested_delay_us:g} µs  •  {config.timing_mode.value}"
        )
        if select_active:
            order = [TimingMode.VALVE, TimingMode.GATE_1, TimingMode.PREDICTED]
            self.notebook.select(order.index(config.timing_mode))
        for mode in self._canvases:
            self._draw(mode)

    def set_state(self, state: str) -> None:
        self._active_state = state
        for mode in self._canvases:
            self._draw(mode)

    def _draw(self, mode: TimingMode) -> None:
        canvas = self._canvases.get(mode)
        if canvas is None or not canvas.winfo_exists():
            return
        canvas.delete("all")
        width = max(canvas.winfo_width(), 760)
        height = max(canvas.winfo_height(), 440)
        scenario = build_timeline_scenario(self._config, mode)

        title = {
            TimingMode.VALVE: "Long delay: activation timed from the nitrogen-valve trigger",
            TimingMode.GATE_1: "Intermediate delay: activation timed from Gate 1",
            TimingMode.PREDICTED: "Short delay: arrival predicted from both laser gates",
        }[mode]
        canvas.create_text(28, 28, anchor="w", text=title, fill=TEXT, font=("Arial", 14, "bold"))

        rows = {
            TimingMode.VALVE: [
                ("N₂ valve trigger", "pulse", scenario.valve_us, AMBER),
                ("Activation laser", "pulse", scenario.activation_us, MAGENTA),
                ("Arrival-time laser", "drop", scenario.actual_arrival_us, BLUE),
            ],
            TimingMode.GATE_1: [
                ("1st laser gate", "drop", scenario.gate_1_us, ORANGE),
                ("Activation laser", "pulse", scenario.activation_us, MAGENTA),
                ("Arrival-time laser", "drop", scenario.actual_arrival_us, BLUE),
            ],
            TimingMode.PREDICTED: [
                ("1st laser gate", "drop", scenario.gate_1_us, ORANGE),
                ("2nd laser gate", "drop", scenario.gate_2_us, MAGENTA),
                ("Arrival prediction", "rise", scenario.predicted_arrival_us, GREEN),
                ("Activation laser", "pulse", scenario.activation_us, AMBER),
                ("Arrival-time laser", "drop", scenario.actual_arrival_us, BLUE),
            ],
        }[mode]

        events = [event for _, _, event, _ in rows]
        span = max(events) - min(events)
        margin = max(span * 0.10, 300.0 if mode != TimingMode.PREDICTED else 80.0)
        t_min = min(events) - margin
        t_max = max(events) + margin
        x_left, x_right = 170.0, width - 42.0
        y_top, y_bottom = 88.0, height - 92.0

        def xpos(time_us: float) -> float:
            return x_left + (time_us - t_min) / (t_max - t_min) * (x_right - x_left)

        row_gap = (y_bottom - y_top) / max(len(rows), 1)
        for index, (label, shape, event_us, color) in enumerate(rows):
            center = y_top + (index + 0.5) * row_gap
            high, low = center - 16, center + 16
            x_event = xpos(event_us)
            canvas.create_text(x_left - 14, center, anchor="e", text=label, fill=color, font=("Arial", 10, "bold"))
            canvas.create_line(x_left, low, x_right, low, fill="#35505f", width=1)
            if shape == "drop":
                canvas.create_line(x_left, high, x_event - 6, high, x_event + 6, low, x_right, low, fill=color, width=3, smooth=True)
            elif shape == "rise":
                pulse_width = max(10, (x_right - x_left) * 0.015)
                canvas.create_line(x_left, low, x_event, low, x_event, high, x_event + pulse_width, high, x_event + pulse_width, low, x_right, low, fill=color, width=3)
            else:
                pulse_width = max(10, (x_right - x_left) * 0.012)
                canvas.create_line(x_left, low, x_event - pulse_width, low, x_event, high, x_event + pulse_width, low, x_right, low, fill=color, width=3)
            canvas.create_line(x_event, y_top - 15, x_event, y_bottom + 8, fill=color, dash=(2, 5))

        x_activation = xpos(scenario.activation_us)
        x_arrival = xpos(scenario.actual_arrival_us)
        arrow_y = y_bottom + 34
        canvas.create_line(x_activation, arrow_y, x_arrival, arrow_y, fill=TEXT, arrow="both", width=2)
        canvas.create_text(
            (x_activation + x_arrival) / 2,
            arrow_y - 13,
            text=f"requested delay  {self._format_delay(scenario.requested_delay_us)}",
            fill=TEXT,
            font=("Arial", 10, "bold"),
        )

        axis_y = y_bottom + 66
        canvas.create_line(x_left, axis_y, x_right, axis_y, fill=MUTED, arrow="last")
        for tick in range(6):
            fraction = tick / 5
            x = x_left + fraction * (x_right - x_left)
            time_ms = (t_min + fraction * (t_max - t_min)) / 1000.0
            canvas.create_line(x, axis_y - 4, x, axis_y + 4, fill=MUTED)
            canvas.create_text(x, axis_y + 15, text=f"{time_ms:.2f}", fill=MUTED, font=("Arial", 9))
        canvas.create_text((x_left + x_right) / 2, axis_y + 36, text="Time after jet trigger (ms)", fill=MUTED, font=("Arial", 10))

        reference = {
            TimingMode.VALVE: "N₂ valve trigger",
            TimingMode.GATE_1: "1st laser gate",
            TimingMode.PREDICTED: "two-gate arrival prediction",
        }[mode]
        active = "  •  ACTIVE MODE" if self._config.timing_mode == mode else "  •  representative example"
        canvas.create_text(
            28,
            height - 30,
            anchor="w",
            text=f"Reference: {reference}{active}    |    shot state: {self._active_state}",
            fill=AMBER if self._config.timing_mode == mode else MUTED,
            font=("Arial", 10, "bold"),
        )

    @staticmethod
    def _format_delay(delay_us: float) -> str:
        if delay_us >= 1000.0:
            return f"{delay_us / 1000.0:g} ms"
        return f"{delay_us:g} µs"
