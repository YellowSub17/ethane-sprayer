
import time
import tkinter as tk

from .network_config import NetworkConfigWindow
from network.client import NetworkClient

from .style import LOG_BG, LOG_FG, TEXT

import socket
import queue



class EthaneControlApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("hello from claude")
        self.geometry("1120x720")
        self.minsize(980, 640)

        self.network_client = NetworkClient()

        self.network_window= None


        self._build_header()
        self._build_body()
        self._build_footer()

        self.process_log_queue()
        self.open_network_window()


    def _build_header(self) -> None:
        header = tk.Frame(self)
        header.pack(fill="x", padx=22, pady=(18, 12))
        tk.Label(header, text="ETHANE SPRAYER", font=("Helvetica", 16, "bold")).pack(side="left")

        # Canvas for the status indicator circle
        self.status_canvas = tk.Canvas(
            header,
            width=16,
            height=16,
            highlightthickness=0,
            bd=0
        )
        self.status_canvas.pack(side="left", padx=(10, 0))

        # Draw the initial circle (x1, y1, x2, y2)
        self.status_indicator = self.status_canvas.create_oval(2, 2, 14, 14, fill="red")

        # Set initial color based on state
        self._update_connection_status()

    def _update_connection_status(self) -> None:
        """Updates the indicator circle color based on self.network_client.connected."""
        color = "green" if self.network_client.connected else "red"
        self.status_canvas.itemconfig(self.status_indicator, fill=color)

        self.after(500, self._update_connection_status)





    def _build_body(self) -> None:
        body = tk.Frame(self)
        body.pack(fill="both", expand=True, padx=22)
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        body_left = tk.Frame(body)
        body_left.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        body_left.columnconfigure(0, weight=1)
        body_left.rowconfigure(2, weight=1)

        laser0 = tk.Button(body_left, text='LASER:0', height=2, command=lambda: self.network_client.send_message('LASER:0')).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        laser1 = tk.Button(body_left, text='LASER:1', height=2, command=lambda: self.network_client.send_message('LASER:1')).grid(row=0, column=1, sticky="ew", padx=2, pady=2)

        steps20 = tk.Button(body_left, text='MOTOR:20', height=2, command=lambda: self.network_client.send_message('MOTOR:20')).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        steps20 = tk.Button(body_left, text='MOTOR:-20', height=2, command=lambda: self.network_client.send_message('MOTOR:-20')).grid(row=1, column=1, sticky="ew", padx=2, pady=2)

        steps20 = tk.Button(body_left, text='MOTOR:ENABLE', height=2, command=lambda: self.network_client.send_message('MOTOR:ENABLE')).grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        steps20 = tk.Button(body_left, text='MOTOR:DISABLE', height=2, command=lambda: self.network_client.send_message('MOTOR:DISABLE')).grid(row=2, column=1, sticky="ew", padx=2, pady=2)



        cmd_entry = tk.Entry(body_left)
        cmd_entry.grid(row=3, column=0, sticky="ew", padx=2, pady=2)
        cmd_entry.insert(0, 'CMD')
        send = tk.Button(body_left, text='SEND', height=2, command=lambda: self.network_client.send_message(cmd_entry.get())).grid(row=3, column=1, sticky="ew", padx=2, pady=2)



        body_right = tk.Frame(body)
        body_right.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        body_right.columnconfigure(1, weight=1)
        body_right.rowconfigure(12, weight=1)

        tk.Label(body_right, text="EVENT LOG").grid(
            row=11, column=0, sticky="w"
        )
        tk.Button(body_right, text="Clear Log", command = self._clear_log).grid(
            row=11, column=1, sticky="e"
                )
        self.log = tk.Text(
            body_right,
            height=10,
            bg=LOG_BG,
            fg=LOG_FG,
            insertbackground=TEXT,
            relief="flat",
            font=("Courier", 12),
            state="disabled",
        )
        self.log.grid(row=12, column=0, columnspan=3, sticky="nsew", pady=(7, 0))


        # laser1 = tkk.Button(command=lambda: self.send_tcp_msg('LASER=1')




    def _build_footer(self) -> None:
        footer = tk.Frame(self)
        footer.pack(fill="x", padx=22, pady=16)
        # tk.Button(footer, text="Measure Jet Speed", command=self.open_jet_speed_window).pack(side="left")
        tk.Button(footer, text="Network", height=2, command=self.open_network_window).pack(side='left')



    def open_network_window(self) -> None:
        if self.network_window is not None and self.network_window.winfo_exists():
            self.network_window.lift()
            self.network_window.focus_force()
            return
        self.network_window = NetworkConfigWindow(self)


    def _log(self, text) -> None:
        self.log.configure(state='normal')
        self.log.insert(tk.END, text)
        self.log.insert(tk.END, '\n')
        self.log.configure(state='disabled')
        self.log.see("end")


    def _clear_log(self,) -> None:
        self.log.configure(state='normal')
        self.log.delete(1.0, tk.END)
        self.log.configure(state='disabled')

    def process_log_queue(self):
        """Polls the network client's rx_queue safely on the main UI thread."""
        try:
          # Drain all pending messages without blocking the GUI
          while True:
            message = self.network_client.log_queue.get_nowait()
            self._log(message)
        except queue.Empty:
          pass

        # Schedule next check in 100ms
        self.after(100, self.process_log_queue)






def main() -> None:
    app = EthaneControlApp()
    app.mainloop()
