import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import pandas as pd
import os

class PPGPage(tk.Frame):
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

        bg_image = Image.open("assets/ppg_background.png")
        bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = tk.Label(self, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)

        # Title Label
        self.label = tk.Label(self, text="PPG Data", font=self.TITLE_FONT, bg="#000000", fg="white")
        self.label.place(relx=0.5, rely=0.1, anchor="center")

        # Data Label
        self.data_label = tk.Label(self, text="IR: -, Red: -, Green: -", font=self.DATA_FONT,
                                   bg="#ffffff", fg="black", padx=20, pady=10)
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
        """Update the displayed PPG data."""
        if "ppg" in data:
            ir, red, green = data["ppg"]
            print(f"[ppg_page] Updating PPG: {ir}, {red}, {green}")
            self.data_label.config(text=f"IR: {ir}, Red: {red}, Green: {green}")

    def update_graph(self):
        """Read ppg.csv and update the graph if not paused."""
        if not self.graph_paused:
            try:
                df = pd.read_csv(os.path.join("memory", "ppg.csv"))

                if df.shape[0] > 0:
                    self.ax.clear()
                    self.ax.plot(df["IR"], label="IR", color='blue')
                    self.ax.plot(df["Red"], label="Red", color='red')
                    self.ax.plot(df["Green"], label="Green", color='green')

                    self.ax.set_title("Real-time PPG Graph", fontsize=16)
                    self.ax.set_xlabel("Samples")
                    self.ax.set_ylabel("Value")
                    self.ax.legend(loc="upper right")
                    self.ax.grid(True)
                    self.canvas.draw()
            except Exception as e:
                print(f"[ppg_page] Failed to update graph: {e}")

        # Schedule next update
        self.after(1000, self.update_graph)


    def clear_data(self):
        """Clear the displayed data."""
        self.data_label.config(text="IR: -, Red: -, Green: -")
        
    def pause_graph(self):
        self.graph_paused = True
        print("[ppg_page] Graph updates paused.")

    def resume_graph(self):
        self.graph_paused = False
        print("[ppg_page] Graph updates resumed.")

