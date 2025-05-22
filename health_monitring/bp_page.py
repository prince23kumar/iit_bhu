import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import pandas as pd
import joblib
import os
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import find_peaks, welch, butter, filtfilt
from scipy import stats
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import MinMaxScaler
import logging

class BPPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.data = []  # Raw PPG data
        self.filtered_data = []  # Filtered PPG data for display
        self.maxpts = 500
        
        # Load BP prediction models
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.model_sbp = joblib.load(os.path.join(current_dir, "sys.joblib"))
            self.model_dbp = joblib.load(os.path.join(current_dir, "dys.joblib"))
            logging.info("BP models loaded successfully")
        except Exception as e:
            logging.error(f"Error loading BP models: {e}")
            self.model_sbp = None
            self.model_dbp = None
        
        # Use the same layout as the original PPGApp
        pw = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        pw.pack(fill="both", expand=True)

        # Left panel
        left = ttk.Frame(pw, width=300)
        pw.add(left, weight=1)

        # Connection settings frame
        sf = ttk.LabelFrame(left, text="Connection & Sampling", padding=10)
        sf.pack(fill="x", pady=5)

        ttk.Label(sf, text="Source:").grid(row=0, column=0, sticky="w")
        ttk.Label(sf, text="Internal PPG Data").grid(row=0, column=1, padx=5)

        ttk.Label(sf, text="Sample Rate (Hz):").grid(row=1, column=0, sticky="w", pady=5)
        self.srE = ttk.Entry(sf, width=12)
        self.srE.grid(row=1, column=1, padx=5)
        self.srE.insert(0, "100")

        # Button Frame
        bf = ttk.Frame(left)
        bf.pack(fill="x", pady=10)
        
        # Back to menu button
        ttk.Button(bf, text="Back to Menu", 
                  command=lambda: controller.show_page("menu_page")).pack(side="left", expand=True, fill="x", padx=5)
        
        # Clear button
        self.clear_btn = ttk.Button(bf, text="Clear", command=self.clear_data)
        self.clear_btn.pack(side="left", expand=True, fill="x", padx=5)

        # BP Display frame
        ef = ttk.LabelFrame(left, text="Estimated BP", padding=10)
        ef.pack(fill="x", pady=5)
        self.bp_var = tk.StringVar(value="SBP: --   DBP: --")
        ttk.Label(ef, textvariable=self.bp_var, font=("Helvetica", 16)).pack()

        # Right panel for graph
        right = ttk.Frame(pw)
        pw.add(right, weight=4)
        
        fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Filtered Signal")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Amplitude")
        self.line, = self.ax.plot([], [], color="seagreen")
        self.ax.set_xlim(0, self.maxpts)
        self.ax.set_ylim(0, 1)
        
        self.canvas = FigureCanvasTkAgg(fig, right)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def update_data(self, data):
        """Update with data from the main app"""
        logging.info("Updating data in BPPage")
        if not data or "ppg" not in data:
            logging.warning("No PPG data available to update.")
            return

        try:
            ppg_values = data["ppg"]
            if len(ppg_values) >= 1:
                ir_value = float(ppg_values[0])
                logging.debug(f"Received IR value: {ir_value}")

                if len(self.data) >= self.maxpts:
                    self.data.pop(0)
                self.data.append(ir_value)

                if len(self.data) > 20:
                    fs = int(self.srE.get())
                    logging.debug(f"Sample rate: {fs}")

                    try:
                        filt = self.butter_bandpass_filter(
                            np.array(self.data),
                            lowcut=0.5,
                            highcut=8.0,
                            fs=fs,
                            order=3
                        )
                        logging.debug(f"Filtered data length: {len(filt)}")

                        x = np.arange(len(filt))
                        self.line.set_data(x, filt)

                        mn, mx = filt.min(), filt.max()
                        self.ax.set_ylim(mn - 0.1 * (mx - mn), mx + 0.1 * (mx - mn))
                        self.canvas.draw()

                        if len(filt) >= 30:
                            try:
                                sbp, dbp = self.process_ppg_data(filt)
                                self.bp_var.set(f"SBP: {sbp:.1f}   DBP: {dbp:.1f}")
                                logging.info(f"Predicted SBP: {sbp:.1f}, DBP: {dbp:.1f}")
                            except Exception as e:
                                logging.error(f"Prediction error: {e}")
                    except Exception as e:
                        logging.error(f"Filtering error: {e}")
        except Exception as e:
            logging.error(f"Error in BPPage update_data: {e}")
    
    def clear_data(self):
        """Clear all data"""
        self.data.clear()
        self.line.set_data([], [])
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
        self.bp_var.set("SBP: --   DBP: --")
    
    def process_ppg_data(self, data):
        """Process PPG data to get blood pressure values"""
        X = self.extract_features(data)
        sbp = self.model_sbp.predict(X)[0]
        dbp = self.model_dbp.predict(X)[0]
        return sbp, dbp
    
    def get_bp_values(self):
        """Retrieve the current SBP and DBP values."""
        try:
            bp_text = self.bp_var.get()
            sbp, dbp = bp_text.replace("SBP:", "").replace("DBP:", "").split()
            return float(sbp), float(dbp)
        except ValueError:
            return None, None
    
    # Signal processing methods
    def butter_bandpass_filter(self, data, lowcut=0.5, highcut=8.0, fs=100, order=3):
        """Apply bandpass filter to the signal"""
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        
        # Calculate appropriate padding length
        desired_padlen = 3 * max(len(a), len(b))
        padlen = min(desired_padlen, len(data) - 1)
        
        # Make sure padlen is valid
        if padlen < 1:
            return np.array(data)
            
        return filtfilt(b, a, data, padlen=padlen)
    
    def extract_features(self, ppg_signal):
        """Extract features from PPG signal for BP prediction"""
        arr = np.asarray(ppg_signal).reshape(1, -1)
        scaler = MinMaxScaler()
        scaled = scaler.fit_transform(arr.T).reshape(1, -1)
        
        # Extract various feature sets
        tf = self.extract_time_domain_features(scaled)
        ff = self.extract_frequency_domain_features(scaled)
        pf = self.extract_ppg_specific_features(scaled)
        wf = self.extract_ppg_features(scaled)
        
        # Combine all features
        feats = np.hstack((tf, ff, pf, wf))
        
        # Handle missing values
        return SimpleImputer(strategy='mean').fit_transform(feats)
    
    def extract_time_domain_features(self, sig):
        """Extract time domain features from signal"""
        m = np.mean(sig, axis=1)
        sd = np.std(sig, axis=1)
        mx = np.max(sig, axis=1)
        mn = np.min(sig, axis=1)
        rng = mx - mn
        sk = stats.skew(sig, axis=1)
        kt = stats.kurtosis(sig, axis=1)
        ent = np.apply_along_axis(lambda x: stats.entropy(np.abs(x)), 1, sig)
        return np.column_stack((m, sd, mx, mn, rng, sk, kt, ent))
    
    def extract_frequency_domain_features(self, sig, fs=100):
        """Extract frequency domain features"""
        f, psd = welch(sig, fs=fs, nperseg=min(256, sig.shape[1]), axis=1)
        domf = f[np.argmax(psd, axis=1)]
        power = np.sum(psd, axis=1)
        return np.column_stack((domf, power))
    
    def extract_ppg_specific_features(self, sig, fs=100):
        """Extract PPG-specific features"""
        intervals, amps = [], []
        for s in sig:
            pks, _ = find_peaks(s, distance=int(fs*0.5))
            if len(pks) > 1:
                intervals.append(np.mean(np.diff(pks))/fs)
                amps.append(np.mean(s[pks]))
            else:
                intervals.append(np.nan)
                amps.append(np.nan)
        return np.column_stack((intervals, amps))
    
    def extract_ppg_features(self, ppg_array, fs=100):
        """Extract detailed PPG features"""
        features = []
        for sig in ppg_array:
            # Normalize the signal
            sig = (sig - np.min(sig)) / (np.max(sig) - np.min(sig) + 1e-8)
            
            # Find peaks and valleys
            peaks, _ = find_peaks(sig, distance=50)
            valleys, _ = find_peaks(-sig, distance=50)
            
            if len(peaks) < 2 or len(valleys) < 2:
                features.append([np.nan]*9)
                continue
                
            # Calculate PPG features
            Pp = sig[peaks[0]] 
            Pv = sig[valleys[0]]
            
            T1 = peaks[0] - valleys[0]
            T2 = valleys[1] - peaks[0] if len(valleys) > 1 else T1
            T3 = peaks[1] - valleys[1] if len(peaks) > 1 and len(valleys) > 1 else T1
            T4 = valleys[0] - peaks[0]
            T5 = peaks[0] - valleys[0]
            
            ETR = (T4 + T5) / (T1 + T2 + T3) if (T1 + T2 + T3) != 0 else np.nan
            BD = T1 + T2 + T3
            HR = BD / 60
            SVC = (Pp - Pv) / T1 if T1 != 0 else np.nan
            DVC = (Pp - Pv) / T2 if T2 != 0 else np.nan
            
            d = np.diff(sig)
            SMVC = np.max(d)
            DMVC = np.min(d)
            
            PWIR = Pp / Pv if Pv != 0 else np.nan
            PWAT = T1 / fs
            
            features.append([ETR, BD, HR, SVC, DVC, SMVC, DMVC, PWIR, PWAT])
            
        return np.array(features)