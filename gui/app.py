from __future__ import annotations

import time
import tkinter as tk
from tkinter import messagebox, ttk

from .model import ExperimentConfig, SIMULATION_SEQUENCE, ShotState, SEQUENCE_TT
from .network import NetworkWindow
from .color_scheme import *
from .jetspeed import JetSpeedWindow



class EthaneControlApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Ethane Sprayer Control")
        self.geometry("1120x720")
        self.minsize(980, 640)
        self.configure(bg=BG)

        # self.transport = SimulationTransport()
        # self.state = ShotState.IDLE
        # self._shot_started = 0.0
        # self._scheduled: list[str] = []
        # self._parameter_vars: dict[str, tk.StringVar] = {}
        # self._state_labels: dict[ShotState, tk.Label] = {}
        # self.timeline_window: TimelineWindow | None = None
        self.network_window: NetworkWindow | None = None
        self.jet_speed_window: JetSpeedWindow | None = None



        self._configure_styles()
        self._build_header()
        self._build_body()
        self._build_footer()
        self.open_jet_speed_window()
        # self._load_defaults()
        # self._set_state(ShotState.IDLE)

    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("TLabel", background=PANEL, foreground=TEXT, font=("Arial", 10))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Arial", 22, "bold"))
        style.configure("Sub.TLabel", background=BG, foreground=MUTED, font=("Arial", 10))
        style.configure("Status.TLabel", background=PANEL, foreground=CYAN, font=("Arial", 20, "bold"))
        style.configure("TEntry", fieldbackground="#22333f", foreground=TEXT, insertcolor=TEXT)
        style.configure("Start.TButton", font=("Arial", 12, "bold"), padding=10)

    def _build_header(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 12))
        ttk.Label(header, text="ETHANE SPRAYER", style="Title.TLabel").pack(side="left")

    def _build_body(self) -> None:
        body = ttk.Frame(self)
        body.pack(fill="both", expand=True, padx=22)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        body_left = ttk.Frame(body, style="Panel.TFrame", padding=18)
        body_right = ttk.Frame(body, style="Panel.TFrame", padding=18)
        body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        body_right.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        body_left.columnconfigure(0, weight=1)
        body_left.rowconfigure(2, weight=1)
        body_right.columnconfigure(1, weight=1)



        ttk.Label(body_right, text="EXPERIMENT PARAMETERS", foreground=MUTED).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 10)
        )
        fields = (
            ("requested_delay_us", "Requested delay", "µs"),
            ("gate_spacing_mm", "Gate 1 → Gate 2 ", "mm"),
            ("effective_distance_mm", "Gate 2 → sample", "mm"),
        )
        for row, (name, label, unit) in enumerate(fields, start=1):
            ttk.Label(body_right, text=label).grid(row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar()
            ttk.Entry(body_right, textvariable=var, width=12).grid(
                row=row, column=1, sticky="ew", padx=(12, 8), pady=5
            )
            ttk.Label(body_right, text=unit, foreground=MUTED).grid(row=row, column=2, sticky="w")

        separator = ttk.Separator(body_right)
        separator.grid(row=10, column=0, columnspan=3, sticky="ew", pady=15)
        ttk.Label(body_right, text="EVENT LOG", foreground=MUTED).grid(
            row=11, column=0, sticky="w"
        )
        self.log = tk.Text(
            body_right,
            height=10,
            bg="#0c141a",
            fg="#bfd0d8",
            insertbackground=TEXT,
            relief="flat",
            font=("DejaVu Sans Mono", 9),
            state="disabled",
        )
        self.log.grid(row=12, column=0, columnspan=3, sticky="nsew", pady=(7, 0))
        body_right.rowconfigure(12, weight=1)

    def _build_footer(self) -> None:
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=22, pady=16)
        ttk.Button(footer, text="Measure Jet Speed", command=self.open_jet_speed_window).pack(side="left")
        ttk.Button(footer, text="Network", command=self.open_network_window).pack(side='left')




    def _read_config(self) -> ExperimentConfig:
        try:
            values = {name: float(var.get()) for name, var in self._parameter_vars.items()}
        except ValueError as exc:
            raise ValueError("all parameters must be valid numbers") from exc
        config = ExperimentConfig(**values)
        config.validate()
        return config


    def _parameters_changed(self) -> None:
        self._refresh_mode()
        if self.timeline_window is None or not self.timeline_window.winfo_exists():
            return
        try:
            config = self._read_config()
        except ValueError:
            return
        self.timeline_window.update_config(config)

    def open_jet_speed_window(self) -> None:
        if self.jet_speed_window is not None and self.jet_speed_window.winfo_exists():
            self.jet_speed_window.lift()
            self.jet_speed_window.focus_force()
            return
        self.jet_speed_window = JetSpeedWindow(self)



    def open_network_window(self) -> None:
        if self.network_window is not None and self.network_window.winfo_exists():
            self.network_window.lift()
            self.network_window.focus_force()
            return
        self.network_window = NetworkWindow(self)


   #  def start_shot(self) -> None:
        # if self.state not in (ShotState.IDLE, ShotState.COMPLETE, ShotState.FAULT):
            # return
        # try:
            # config = self._read_config()
        # except ValueError as exc:
            # messagebox.showerror("Invalid parameters", str(exc))
            # return

        # self.reset(clear_log=True)
        # self._shot_started = time.monotonic()
        # self.start_button.configure(state="disabled")
        # self._log("Simulation started; outputs remain disabled")
        # self._log(f"Timing mode: {config.timing_mode.value}")

        # # Physical waits are compressed for a responsive GUI prototype.
        # stages = [
            # (100, ShotState.ARMED),
            # (450, ShotState.CONDENSING),
            # (1500, ShotState.POSITIONING),
            # (1950, ShotState.SETTLING),
            # (2450, ShotState.JET_TRIGGERED),
            # (2800, ShotState.GATE_1_SEEN),
            # (3150, ShotState.GATE_2_SEEN),
            # (3300, ShotState.LASER_SCHEDULED),
            # (3520, ShotState.ARRIVAL_CHECKED),
            # (3900, ShotState.PLUNGING),
            # (4550, ShotState.COMPLETE),
        # ]
        # for delay_ms, state in stages:
            # token = self.after(delay_ms, self._simulation_step, state, config)
            # self._scheduled.append(token)

    # def _simulation_step(self, state: ShotState, config: ExperimentConfig) -> None:
        # self._set_state(state)
        # self._log(state.value)
        # if state == ShotState.JET_TRIGGERED:
            # self._log(f"N₂ pulse: {config.valve_pulse_us:.0f} µs (simulated)")
        # elif state == ShotState.GATE_2_SEEN:
            # gate_1_us = 10_000.0
            # gate_2_us = 12_690.0
            # arrival_us = config.predicted_arrival_us(gate_1_us, gate_2_us)
            # laser_us = config.laser_trigger_us(gate_1_us, gate_2_us)
            # self.prediction_label.configure(
                # text=(
                    # f"Predicted arrival: {arrival_us:,.1f} µs  •  "
                    # f"laser trigger: {laser_us:,.1f} µs"
                # ),
                # fg=CYAN,
            # )
            # self._log(f"Gate transit: {gate_2_us - gate_1_us:,.1f} µs")
            # self._log(f"Predicted arrival timestamp: {arrival_us:,.1f} µs")
        # elif state == ShotState.COMPLETE:
            # self.start_button.configure(state="normal")
            # self._scheduled.clear()

    # def _set_state(self, state: ShotState) -> None:
        # self.state = state
        # self.status_label.configure(text=state.value, foreground=RED if state == ShotState.FAULT else CYAN)
        # for item_state, label in self._state_labels.items():
            # active = item_state == state
            # label.configure(bg=CYAN if active else "#1d2c37", fg=BG if active else MUTED)
        # if self.timeline_window is not None and self.timeline_window.winfo_exists():
            # self.timeline_window.set_state(state.value)

    # def _log(self, message: str) -> None:
        # elapsed = 0.0 if not self._shot_started else time.monotonic() - self._shot_started
        # self.log.configure(state="normal")
        # self.log.insert("end", f"{elapsed:7.3f} s  {message}\n")
        # self.log.see("end")
        # self.log.configure(state="disabled")

    # def abort(self) -> None:
        # if self.state in (ShotState.IDLE, ShotState.COMPLETE, ShotState.FAULT):
            # return
        # for token in self._scheduled:
            # self.after_cancel(token)
        # self._scheduled.clear()
        # self.transport.send("ABORT")
        # self._set_state(ShotState.FAULT)
        # self._log("ABORT requested; simulated outputs forced safe")
        # self.start_button.configure(state="normal")

    # def reset(self, clear_log: bool = False) -> None:
        # for token in self._scheduled:
            # self.after_cancel(token)
        # self._scheduled.clear()
        # self._set_state(ShotState.IDLE)
        # self.start_button.configure(state="normal")
        # self.prediction_label.configure(text="Predicted values appear after Gate 2.", fg=MUTED)
        # if clear_log:
            # self.log.configure(state="normal")
            # self.log.delete("1.0", "end")
            # self.log.configure(state="disabled")
        # else:
            # self._log("Reset to IDLE")


def main() -> None:
    app = EthaneControlApp()
    app.mainloop()
