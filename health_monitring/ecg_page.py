import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MultipleLocator
import pandas as pd
import os
import datetime

class ECGPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.graph_paused = False

        # Fonts & Colors
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)
        self.BUTTON_FONT = ("Helvetica", 16)
        self.BG_COLOR = "#f0f0f0"
        self.BUTTON_BG = "#4CAF50"
        self.BUTTON_FG = "white"
        self.ACTIVE_BG = "#45a049"

        # Background Image
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        try:
            bg_image = Image.open("assets/menu_background.png")
            bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(self, image=self.bg_photo)
            bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"[ECGPage] Could not load background: {e}")
            self.configure(bg="#f0f0f0")  # Fallback background color

        # Title Label
        self.label = tk.Label(self, text="ECG Data", font=self.TITLE_FONT, fg="white", bg="black")
        self.label.place(relx=0.5, rely=0.1, anchor="center")

        # ECG Data Label
        self.data_label = tk.Label(self, text="ECG: -", font=self.DATA_FONT, bg="white", fg="black", padx=20, pady=10)
        self.data_label.place(relx=0.5, rely=0.2, anchor="center")

        # Graph Setup
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)

        self.toolbar_frame = tk.Frame(self)
        self.toolbar_frame.place(relx=0.5, rely=0.42, anchor="center")

        self.toolbar = NavigationToolbar2Tk(self.canvas, self.toolbar_frame)
        self.toolbar.update()

        self.canvas.get_tk_widget().place(relx=0.5, rely=0.5, anchor="center")

        # Pause/Resume Buttons
        self.pause_button = tk.Button(self, text="Pause Graph", font=self.BUTTON_FONT,
                                      bg="#f44336", fg="white", activebackground="#d32f2f",
                                      width=15, height=2, borderwidth=0,
                                      command=self.pause_graph)
        self.pause_button.place(relx=0.35, rely=0.85, anchor="center")

        self.resume_button = tk.Button(self, text="Resume Graph", font=self.BUTTON_FONT,
                                       bg="#2196F3", fg="white", activebackground="#1976D2",
                                       width=15, height=2, borderwidth=0,
                                       command=self.resume_graph)
        self.resume_button.place(relx=0.65, rely=0.85, anchor="center")

        # Back Button
        back_button = tk.Button(self, text="Back to Menu", font=self.BUTTON_FONT,
                                bg=self.BUTTON_BG, fg=self.BUTTON_FG, activebackground=self.ACTIVE_BG,
                                width=20, height=2, borderwidth=0,
                                command=lambda: controller.show_page("menu_page"))
        back_button.place(relx=0.5, rely=0.9, anchor="center")

        self.after(1000, self.update_graph)  # Start updating graph every 1s

    def update_data(self, data):
        """Update the displayed ECG data."""
        if "ecg" in data:
            ecg_val = data["ecg"]
            print(f"[ECGPage] Updating ECG: {ecg_val}")
            self.data_label.config(text=f"ECG: {ecg_val}")

    def update_graph(self):
        """Read ecg.csv and update the graph if not paused."""
        if not self.graph_paused:
            try:
                file_path = os.path.join("memory", "ecg.csv")
                if not os.path.exists(file_path):
                    print(f"[ECGPage] Warning: {file_path} does not exist")
                    return

                df = pd.read_csv(file_path)

                if df.shape[0] > 0:
                    # Convert timestamps to datetime objects
                    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
                    
                    # Sort by timestamp to ensure chronological order
                    df = df.sort_values('Timestamp')
                    
                    # Calculate seconds from the first timestamp for x-axis
                    first_time = df['Timestamp'].iloc[0]
                    df['Seconds'] = (df['Timestamp'] - first_time).dt.total_seconds()
                    
                    # Limit to last 30 seconds of data for better visualization
                    time_window = 30  # seconds to display
                    if df['Seconds'].max() > time_window:
                        df = df[df['Seconds'] >= df['Seconds'].max() - time_window]
                    
                    self.ax.clear()
                    
                    # Plot data with seconds on x-axis
                    self.ax.plot(df['Seconds'], df['ECG'], label="ECG", color='red', linewidth=1.5)
                    
                    # Set axis limits for consistent view
                    x_min = max(0, df['Seconds'].max() - time_window)
                    x_max = df['Seconds'].max()
                    self.ax.set_xlim(x_min, x_max)
                    
                    y_min = max(0, df['ECG'].min() - 10)  # Ensure we don't go below 0
                    y_max = df['ECG'].max() + 10
                    self.ax.set_ylim(y_min, y_max)

                    self.ax.set_title("Real-time ECG Monitor", fontsize=16)
                    self.ax.set_xlabel("Time (seconds)")
                    self.ax.set_ylabel("ECG (mV)")
                    self.ax.legend(loc="upper right")
                    
                    # Add ECG grid styling
                    self.ax.set_facecolor('#f5f5f5')
                    self.fig.patch.set_facecolor('#e8e8e8')
                    
                    # Add typical ECG grid lines (5mm x 5mm)
                    self.ax.xaxis.set_major_locator(MultipleLocator(5))
                    self.ax.xaxis.set_minor_locator(MultipleLocator(1))
                    self.ax.yaxis.set_major_locator(MultipleLocator(5))
                    self.ax.yaxis.set_minor_locator(MultipleLocator(1))
                    self.ax.grid(which='major', color='#bbbbbb', linestyle='-', linewidth=0.8)
                    self.ax.grid(which='minor', color='#dddddd', linestyle='-', linewidth=0.5)
                    
                    # Add current time annotation
                    current_time = df['Timestamp'].iloc[-1].strftime("%H:%M:%S")
                    self.ax.annotate(f"Current time: {current_time}", 
                                     xy=(0.02, 0.02), 
                                     xycoords='axes fraction',
                                     bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8))
                    
                    # Adjust layout to prevent clipping
                    self.fig.tight_layout()
                    
                    self.canvas.draw()
            except Exception as e:
                print(f"[ECGPage] Failed to update graph: {e}")
        
        # Schedule next update
        self.after(1000, self.update_graph)

    def clear_data(self):
        """Clear the displayed data."""
        self.data_label.config(text="ECG: -")

    def pause_graph(self):
        self.graph_paused = True
        print("[ECGPage] Graph updates paused.")

    def resume_graph(self):
        self.graph_paused = False
        print("[ECGPage] Graph updates resumed.")
