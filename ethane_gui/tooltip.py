import tkinter as tk

class ToolTip:
    """A simple hover tooltip class for Tkinter widgets."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        # Bind hover events
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        # Position the tooltip slightly offset from the mouse pointer/widget
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # Create a borderless top-level window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window borders/titlebar
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        # Tooltip styling
        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background="#ffffe0",  # Light yellow background
            foreground="black",
            relief="solid",
            borderwidth=1,
            font=("sans-serif", 9, "normal"),
            padx=5,
            pady=3
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            from .tooltip import ToolTip, TOOLTIP_TEXT
            self.tooltip_window.destroy()
            self.tooltip_window = None

TOOLTIP_TEXT = {}
# TOOLTIP_TEXT = {
        # ShotState.ARMED:'arm',
        # ShotState.CONDENSING:'cond',
        # ShotState.POSITIONING:'',
        # ShotState.SETTLING:'',
        # ShotState.JET_TRIGGERED:'',
        # ShotState.GATE_1_SEEN:'',
        # ShotState.GATE_2_SEEN:'',
        # ShotState.LASER_SCHEDULED:'',
        # ShotState.ARRIVAL_CHECKED:'',
        # ShotState.PLUNGING:'',
        # ShotState.COMPLETE:'',

        # }


# # --- Example Usage ---
# root = tk.Tk()
# root.title("Tkinter Tooltip Example")
# root.geometry("300x150")

# # 1. Create a standard Label
# my_label = tk.Label(root, text="Hover over me!", font=("Arial", 12), padding=10 if hasattr(tk.Label, 'padding') else None)
# my_label.pack(pady=40)

# # 2. Attach the ToolTip
# ToolTip(my_label, text="This is your hover tooltip!")

# root.mainloop()
