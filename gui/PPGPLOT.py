import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt

class SerialReader:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=3)
            self.running = True
        except serial.SerialException as e:
            messagebox.showerror("Serial Error", f"Failed to connect to {self.port}\n{str(e)}")
            self.running = False

    def read_data(self):
        if self.ser and self.ser.in_waiting > 0:
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

class PPGApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PPG-Based Signal Visualization")
        self.root.geometry("1000x800")
        self.root.configure(bg="#d0f0c0")
        self.data_ppg = []
        self.max_points = 500  # Fixing the x-axis range
        self.running = False
        self.serial_reader = None

        # Serial Port Selection
        ttk.Label(root, text="Serial Port:", background="#d0f0c0").pack(pady=5)
        self.port_entry = ttk.Entry(root)
        self.port_entry.pack(pady=5)
        self.port_entry.insert(0, "COM11")  # Default port

        # Sampling Parameters
        self.param_frame = ttk.Frame(root)
        self.param_frame.pack(pady=10)

        ttk.Label(self.param_frame, text="Sample Rate (Hz):").grid(row=0, column=0)
        self.sample_rate_entry = ttk.Entry(self.param_frame, width=10)
        self.sample_rate_entry.grid(row=0, column=1)
        self.sample_rate_entry.insert(0, "100")

        ttk.Label(self.param_frame, text="Pulse Width:").grid(row=0, column=2)
        self.pulse_width_entry = ttk.Entry(self.param_frame, width=10)
        self.pulse_width_entry.grid(row=0, column=3)
        self.pulse_width_entry.insert(0, "200")

        ttk.Label(self.param_frame, text="Sample Average:").grid(row=0, column=4)
        self.sample_avg_entry = ttk.Entry(self.param_frame, width=10)
        self.sample_avg_entry.grid(row=0, column=5)
        self.sample_avg_entry.insert(0, "4")

        # Create Matplotlib Figure
        self.figure = Figure(figsize=(12, 6), dpi=100)
        self.ax_ppg = self.figure.add_subplot(111)
        self.ax_ppg.set_title("PPG Signal")
        self.ax_ppg.set_ylabel("PPG Value")
        self.ax_ppg.set_xlabel("Time")
        self.ax_ppg.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, self.root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Control Buttons
        self.control_frame = tk.Frame(self.root, bg="#d0f0c0")
        self.control_frame.pack(side=tk.BOTTOM, pady=20)

        self.start_button = ttk.Button(self.control_frame, text="Start", command=self.start_reading)
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(self.control_frame, text="Stop", command=self.stop_reading)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        self.save_button = ttk.Button(self.control_frame, text="Save Data", command=self.save_data)
        self.save_button.pack(side=tk.LEFT, padx=10)

        self.clear_button = ttk.Button(self.control_frame, text="Clear", command=self.clear_data)
        self.clear_button.pack(side=tk.LEFT, padx=10)

    def moving_average(self, data, window_size=5):
        if len(data) < window_size:
            return data  # Not enough data points
        return np.convolve(data, np.ones(window_size) / window_size, mode='valid')

    def butter_highpass_filter(self, data, cutoff=0.5, fs=100, order=5):
        nyquist = 0.5 * fs
        normal_cutoff = cutoff / nyquist  # Ensure proper scaling
        b, a = butter(order, normal_cutoff, btype='high', analog=False)

        # Ensure there are enough points to apply filtfilt
        padlen = max(12, 3 * max(len(b), len(a)))  # Minimum padding length
        if len(data) < padlen:
            return data  # Return raw data if not enough points

        return filtfilt(b, a, data)

    def start_reading(self):
        if not self.running:
            port = self.port_entry.get().strip()
            self.serial_reader = SerialReader(port)
            self.serial_reader.start()
            if self.serial_reader.running:
                self.running = True
                threading.Thread(target=self.update_plot, daemon=True).start()

    def stop_reading(self):
        self.running = False
        if self.serial_reader:
            self.serial_reader.stop()



    def update_plot(self):
        while self.running:
            value = self.serial_reader.read_data()
            if value is not None:
                if len(self.data_ppg) >= self.max_points:
                    self.data_ppg.pop(0)  # Remove the oldest value
                self.data_ppg.append(value)

            time.sleep(0.008)  # Adjust timing for real-time responsiveness

            # Apply High-pass Filter to remove baseline wander
            if len(self.data_ppg) > 18:
                filtered_data = self.butter_highpass_filter(self.data_ppg)
            else:
                filtered_data = self.moving_average(self.data_ppg)

            self.ax_ppg.clear()
            x_values = list(range(len(filtered_data)))

            # Adjust Y-axis dynamically based on visible window range
            if len(filtered_data) > 0:
                min_val, max_val = min(filtered_data), max(filtered_data)
                margin = (max_val - min_val) * 0.1 if max_val > min_val else 5
                self.ax_ppg.set_ylim(min_val - margin, max_val + margin)

            # Set fixed x-axis range (Sliding window effect)
            self.ax_ppg.set_xlim(0, self.max_points)

            self.ax_ppg.plot(x_values, filtered_data, color="green", label="Filtered PPG Signal")

            self.ax_ppg.set_title("PPG Signal (Filtered)")
            self.ax_ppg.set_ylabel("PPG Value")
            self.ax_ppg.set_xlabel("Time")
            self.ax_ppg.grid(True)
            self.ax_ppg.legend()

            self.canvas.draw()
            self.canvas.flush_events()

    def save_data(self):
        pd.DataFrame({"PPG Signal": self.data_ppg}).to_csv("ppg_data.csv", index=False)
        messagebox.showinfo("Success", "PPG data saved successfully!")

    def clear_data(self):
        self.data_ppg.clear()
        self.ax_ppg.clear()
        self.ax_ppg.set_title("PPG Signal")
        self.ax_ppg.set_ylabel("PPG Value")
        self.ax_ppg.set_xlabel("Time")
        self.ax_ppg.grid(True)
        self.canvas.draw()

    def on_close(self):
        self.stop_reading()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = PPGApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()