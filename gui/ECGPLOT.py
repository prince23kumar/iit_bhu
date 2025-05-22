import tkinter as tk
from tkinter import ttk
import serial
import threading
import time
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt, cheby2

def butter_highpass(cutoff, fs, order=5):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a

def highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order)
    return filtfilt(b, a, data)

def chebyshev_filter(data, stopband_freq, fs, order=4, rs=30):
    nyquist = 0.5 * fs
    low, high = stopband_freq
    stopband_normalized = [low / nyquist, high / nyquist]
    b, a = cheby2(order, rs, stopband_normalized, btype='bandstop', analog=False)
    return filtfilt(b, a, data)

def apply_filters(data, fs):
    filtered_data = highpass_filter(data, cutoff=0.5, fs=fs)
    filtered_data = chebyshev_filter(filtered_data, stopband_freq=(49, 51), fs=fs)
    return filtered_data

class SerialReader:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False

    def start(self):
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
        self.running = True

    def read_data(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline().decode('utf-8').strip()
            try:
                return float(line)
            except ValueError:
                return None
        return None

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

class ECGPlotApp:
    def __init__(self, root, port):
        self.root = root
        self.root.title("ECG Signal Live Plot")
        self.root.geometry("1000x800")
        self.root.configure(bg="#f0f8ff")

        self.serial_reader = SerialReader(port)

        self.data_ecg = []
        self.max_points = 1000
        self.fs = 250

        self.figure = Figure(figsize=(12, 7), dpi=100)
        self.ax_ecg = self.figure.add_subplot(111)
        self.ax_ecg.set_title("ECG Signal")
        self.ax_ecg.set_xlabel("Samples")
        self.ax_ecg.set_ylabel("ECG Value")
        self.ax_ecg.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.control_frame = tk.Frame(self.root, bg="#f0f8ff")
        self.control_frame.pack(side=tk.BOTTOM, pady=20)

        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_reading, width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_reading, width=20)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.reset_button = ttk.Button(self.control_frame, text="Reset", command=self.reset_plot, width=20)
        self.reset_button.pack(side=tk.LEFT, padx=10)

        self.reading_thread = None
        self.running = False

    def start_reading(self):
        if not self.running:
            self.serial_reader.start()
            self.running = True
            self.reading_thread = threading.Thread(target=self.update_plot)
            self.reading_thread.start()

    def stop_reading(self):
        self.running = False
        self.serial_reader.stop()

    def reset_plot(self):
        self.stop_reading()
        self.data_ecg.clear()
        self.ax_ecg.clear()
        self.ax_ecg.set_title("ECG Signal (Reset)")
        self.ax_ecg.set_xlabel("Samples")
        self.ax_ecg.set_ylabel("ECG Value")
        self.ax_ecg.grid(True)
        self.canvas.draw()

    def update_plot(self):
        while self.running:
            value = self.serial_reader.read_data()
            if value is not None:
                if len(self.data_ecg) >= self.max_points:
                    self.data_ecg.pop(0)

                self.data_ecg.append(value)

            if len(self.data_ecg) > 27:
                filtered_data = apply_filters(np.array(self.data_ecg), self.fs)
            else:
                filtered_data = np.array(self.data_ecg)

            time.sleep(1 / self.fs)

            self.ax_ecg.clear()
            self.ax_ecg.plot(filtered_data, label="ECG Signal (Filtered)", color="red")
            self.ax_ecg.set_title("ECG Signal")
            self.ax_ecg.set_xlabel("Samples")
            self.ax_ecg.set_ylabel("ECG Value")
            self.ax_ecg.grid(True)
            self.ax_ecg.legend(loc="upper right")

            self.canvas.draw()

    def on_close(self):
        self.stop_reading()
        self.root.destroy()

if __name__ == "__main__":
    serial_port = "COM11"
    root = tk.Tk()
    app = ECGPlotApp(root, serial_port)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()