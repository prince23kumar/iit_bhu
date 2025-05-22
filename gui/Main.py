import tkinter as tk
from tkinter import ttk, messagebox
import serial
import threading
import time
import numpy as np
import pandas as pd
import joblib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import butter, filtfilt, find_peaks, welch
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
import random

import os

# Replace the absolute paths with relative paths
current_dir = os.path.dirname(os.path.abspath(__file__))
model_sbp = joblib.load(os.path.join(current_dir, "sys.joblib"))
model_dbp = joblib.load(os.path.join(current_dir, "dys.joblib"))

# ...existing code...

def butter_highpass_filter(data, cutoff=0.5, fs=100, order=4):
    print(data)
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    padlen = max(12, 3 * max(len(b), len(a)))
    if len(data) < padlen:
        return np.array(data)
    return filtfilt(b, a, data)

def butter_bandpass_filter(data, lowcut=0.5, highcut=8.0, fs=100, order=3):
    from scipy.signal import butter, filtfilt

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')

    desired_padlen = 3 * max(len(a), len(b))
    padlen = min(desired_padlen, len(data) - 1)
    if padlen < 1:
        return np.array(data)

    return filtfilt(b, a, data, padlen=padlen)

def moving_average(data, window_size=5):
    if len(data) < window_size:
        return np.array(data)
    return np.convolve(data, np.ones(window_size)/window_size, mode='valid')

def extract_ppg_features(ppg_array, fs=100):
    features = []
    for sig in ppg_array:
        sig = (sig - np.min(sig)) / (np.max(sig) - np.min(sig) + 1e-8)
        peaks, _   = find_peaks(sig, distance=50)
        valleys, _ = find_peaks(-sig, distance=50)
        if len(peaks)<2 or len(valleys)<2:
            features.append([np.nan]*9)
            continue
        Pp = sig[peaks[0]]; Pv = sig[valleys[0]]
        T1 = peaks[0]-valleys[0]
        T2 = valleys[1]-peaks[0] if len(valleys)>1 else T1
        T3 = peaks[1]-valleys[1] if len(peaks)>1 and len(valleys)>1 else T1
        T4 = valleys[0]-peaks[0]; T5 = peaks[0]-valleys[0]
        ETR = (T4+T5)/(T1+T2+T3) if (T1+T2+T3)!=0 else np.nan
        BD  = T1+T2+T3
        HR  = BD/60
        SVC = (Pp-Pv)/T1 if T1!=0 else np.nan
        DVC = (Pp-Pv)/T2 if T2!=0 else np.nan
        d   = np.diff(sig)
        SMVC = np.max(d);  DMVC = np.min(d)
        PWIR = Pp/Pv if Pv!=0 else np.nan
        PWAT = T1/fs
        features.append([ETR, BD, HR, SVC, DVC, SMVC, DMVC, PWIR, PWAT])
    return np.array(features)

def extract_time_domain_features(sig):
    m   = np.mean(sig, axis=1)
    sd  = np.std(sig, axis=1)
    mx  = np.max(sig, axis=1)
    mn  = np.min(sig, axis=1)
    rng = mx - mn
    sk  = stats.skew(sig, axis=1)
    kt  = stats.kurtosis(sig, axis=1)
    ent = np.apply_along_axis(lambda x: stats.entropy(np.abs(x)), 1, sig)
    return np.column_stack((m, sd, mx, mn, rng, sk, kt, ent))

def extract_frequency_domain_features(sig, fs=125):
    f, psd = welch(sig, fs=fs, nperseg=256, axis=1)
    domf  = f[np.argmax(psd, axis=1)]
    power = np.sum(psd, axis=1)
    return np.column_stack((domf, power))

def extract_ppg_specific_features(sig, fs=125):
    intervals, amps = [], []
    for s in sig:
        pks, _ = find_peaks(s, distance=int(fs*0.5))
        if len(pks)>1:
            intervals.append(np.mean(np.diff(pks))/fs)
            amps.append(np.mean(s[pks]))
        else:
            intervals.append(np.nan); amps.append(np.nan)
    return np.column_stack((intervals, amps))

def extract_features(ppg_signal):
    arr = np.asarray(ppg_signal).reshape(1, -1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(arr.T).reshape(1, -1)

    tf = extract_time_domain_features(scaled)
    ff = extract_frequency_domain_features(scaled)
    pf = extract_ppg_specific_features(scaled)
    wf = extract_ppg_features(scaled)

    feats = np.hstack((tf, ff, pf, wf))
    return SimpleImputer(strategy='mean').fit_transform(feats)

def process_ppg_data(data):
    X = extract_features(data)
    sbp = model_sbp.predict(X)[0]
    dbp = model_dbp.predict(X)[0]
    
    return sbp, dbp

class SerialReader:
    def __init__(self, port, baudrate=115200):
        self.port, self.baudrate = port, baudrate
        self.ser = None
        self.running = False

    def start(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=1)
            self.running = True
        except Exception as e:
            messagebox.showerror("Serial Error", str(e))
            self.running = False

    def read_data(self):
        if self.ser and self.ser.in_waiting>0:
            raw = self.ser.readline().decode().strip().split(',')
            try:
                print(f"Serial Data: {raw[0]}")  # Print the data coming from serial input
                return float(raw[0])
            except:
                return None
        return None

    def stop(self):
        self.running = False
        if self.ser:
            self.ser.close()

class PPGApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, padding=10)
        parent.title("BP Predictor")
        parent.geometry("1200x700")
        self.pack(fill="both", expand=True)

        self.data    = []
        self.maxpts  = 500
        self.running = False
        self.reader  = None

        pw = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        pw.pack(fill="both", expand=True)

        left = ttk.Frame(pw, width=300)
        pw.add(left, weight=1)

        sf = ttk.LabelFrame(left, text="Connection & Sampling", padding=10)
        sf.pack(fill="x", pady=5)

        ttk.Label(sf, text="Serial Port:").grid(row=0, column=0, sticky="w")
        self.portE = ttk.Entry(sf, width=12); self.portE.grid(row=0, column=1, padx=5)
        self.portE.insert(0, "/dev/ttyACM0")

        ttk.Label(sf, text="Sample Rate (Hz):").grid(row=1, column=0, sticky="w", pady=5)
        self.srE = ttk.Entry(sf, width=12); self.srE.grid(row=1, column=1, padx=5)
        self.srE.insert(0, "100")

        ttk.Label(sf, text="Pulse Width:").grid(row=2, column=0, sticky="w")
        self.pwE = ttk.Entry(sf, width=12); self.pwE.grid(row=2, column=1, padx=5)
        self.pwE.insert(0, "200")

        ttk.Label(sf, text="Sample Avg:").grid(row=3, column=0, sticky="w", pady=5)
        self.saE = ttk.Entry(sf, width=12); self.saE.grid(row=3, column=1, padx=5)
        self.saE.insert(0, "4")

        bf = ttk.Frame(left)
        bf.pack(fill="x", pady=10)
        self.start_btn = ttk.Button(bf, text="Start", command=self.start)
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.stop_btn  = ttk.Button(bf, text="Stop",  command=self.stop)
        self.stop_btn.pack(side="left", expand=True, fill="x", padx=5)
        self.clear_btn = ttk.Button(bf, text="Clear", command=self.clear)
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=5)

        ef = ttk.LabelFrame(left, text="Estimated BP", padding=10)
        ef.pack(fill="x", pady=5)
        self.bp_var = tk.StringVar(value="SBP: --   DBP: --")
        ttk.Label(ef, textvariable=self.bp_var, font=("Helvetica",16)).pack()

        ttk.Button(left, text="Save Data", command=self.save).pack(fill="x", pady=10)

        right = ttk.Frame(pw); pw.add(right, weight=4)
        fig = Figure(figsize=(8,6), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Filtered Signal")
        self.ax.set_xlabel("Sample"); self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([],[],color="seagreen")
        self.ax.set_xlim(0, self.maxpts); self.ax.set_ylim(0,1)
        canvas = FigureCanvasTkAgg(fig, right)
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas = canvas

    def start(self):
        if not self.running:
            port = self.portE.get().strip()
            if port not in ['/dev/ttyACM0', '/dev/ttyAMA10']:
                messagebox.showerror("Serial Error", "Invalid port. Available ports: /dev/ttyACM0, /dev/ttyAMA10")
                return
            self.reader = SerialReader(port)
            self.reader.start()
            if self.reader.running:
                self.running = True
                threading.Thread(target=self._run, daemon=True).start()

    def stop(self):
        self.running = False
        if self.reader: self.reader.stop()

    def clear(self):
        self.data.clear()
        self.line.set_data([],[])
        self.ax.relim(); self.ax.autoscale_view()
        self.canvas.draw()
        self.bp_var.set("SBP: --   DBP: --")

    def save(self):
        pd.DataFrame({"PPG":self.data}).to_csv("ppg_data.csv", index=False)
        messagebox.showinfo("Saved","Data saved to ppg_data.csv")

    def _run(self):
        fs = int(self.srE.get())
        while self.running:
            v = self.reader.read_data()
            if v is not None:
                print(f"Serial Data: {v}")  # Print the data coming from serial input
                if len(self.data) >= self.maxpts: self.data.pop(0)
                self.data.append(v)
            time.sleep(1 / fs)

            if len(self.data) > 20:
                arr = np.array(self.data)
              #  print(f"Data before filtering: {arr}")  # Debug: Print data before filtering
                try:
                    filt = butter_bandpass_filter(arr,
                                                  lowcut=0.5,
                                                  highcut=8.0,
                                                  fs=fs,
                                                  order=3)
                    print(f"Filtered Data: {filt}")  # Debug: Print filtered data
                except Exception as e:
                    print(f"Filtering error: {e}")  # Debug: Log filtering errors
                    continue

                if len(filt) >= 30:
                    print(f"Data length: {len(filt)}")  # Debug: Print data length
                    try:
                        sbp, dbp = process_ppg_data(filt)
                        self.bp_var.set(f"SBP: {sbp:.1f}   DBP: {dbp:.1f}")
                        print(f"SBP: {sbp:.1f}, DBP: {dbp:.1f}")  # Debug: Print SBP and DBP
                    except Exception as e:
                        print("Prediction error:", e)

                x = np.arange(len(filt))
                self.line.set_data(x, filt)
                mn, mx = filt.min(), filt.max()
                self.ax.set_ylim(mn - 0.1 * (mx - mn), mx + 0.1 * (mx - mn))
                self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = PPGApp(root)
    root.mainloop()