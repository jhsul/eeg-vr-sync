import asyncio
import threading
import tkinter as tk
from datetime import datetime as dt

from eeg import EEGParser
import time
import websockets
import re

eeg_host = "localhost"
eeg_port = 8844

vr_host = "localhost"
vr_port = 8080

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)

        self.connection_status = tk.StringVar(value="Not connected")
        self.data_status = tk.StringVar(value="No data points collected")

        self.data_count = 0

        self.master = master
        self.grid()
        self.create_widgets()

    def create_widgets(self):
        self.connection_label = tk.Label(self, textvariable=self.connection_status)
        self.connection_label.grid(row=0, column=0, padx=10, pady=10)

        self.port_entry = tk.Entry(self, width=5)
        self.port_entry.insert(tk.END, "8894")
        self.port_entry.grid(row=0, column=1, padx=10, pady=10)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_eeg)
        self.connect_button.grid(row=0, column=2, padx=10, pady=10)

        self.data_count_label = tk.Label(self, textvariable=self.data_status)
        self.data_count_label.grid(row=1)

    def connect_eeg(self):
        self.eeg = EEGParser(eeg_host, eeg_port)

        self.eeg_thread = threading.Thread(target=self.eeg.parse_data, args=(self, ))
        self.eeg_thread.start()

root = tk.Tk()
root.title("EEG Sync")
app = Application(master=root)
app.mainloop()


def run_eeg():
    print(f"[{dt.now()}] Connecting to EEG headset")
    eeg = EEGParser(eeg_host, eeg_port)
    eeg.parse_data()
    return eeg.df
