import tkinter as tk
import logging
import os
from PIL import Image, ImageTk
from tkinter import ttk

class AllInOnePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts & Colors
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)
        self.BUTTON_FONT = ("Helvetica", 16)
        self.BG_COLOR = "#f0f0f0"
        self.BUTTON_BG = "#4CAF50"
        self.BUTTON_FG = "white"
        self.ACTIVE_BG = "#45a049"


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

       
        # Background Image
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        try:
            bg_image = Image.open("assets/menu_background.png")
            bg_image = bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_image)
            self.bg_label = tk.Label(self, image=self.bg_photo)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"[AllInOnePage] Could not load background: {e}")
            self.configure(bg="#f0f0f0")  # Fallback background color


        # Content frame
        self.content_frame = tk.Frame(self, bg='', highlightthickness=0)
        self.content_frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.label = tk.Label(self.content_frame, text="All-In-One Health Data", font=self.TITLE_FONT, fg="white", bg="blue")
        self.label.grid(row=0, column=0, columnspan=6, pady=20)
        self.label.config(bg="lightblue", relief="raised", borderwidth=2)

        self.temp_section_label = tk.Label(self.content_frame, text="Temperature Data", font=self.DATA_FONT, fg="black")
        self.temp_section_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        self.temp_labels = []
        for i in range(3):
            label = tk.Label(self.content_frame, text=f"Temp{i+1}: -", font=self.DATA_FONT, fg="black")
            label.grid(row=i+2, column=0, padx=20, pady=5, sticky="w")
            self.temp_labels.append(label)

        self.gas_section_label = tk.Label(self.content_frame, text="Gas Data", font=self.DATA_FONT, fg="black")
        self.gas_section_label.grid(row=1, column=1, padx=20, pady=10, sticky="n")

        self.gas_labels = []
        for i in range(5):
            label = tk.Label(self.content_frame, text=f"Gas{i+1}: -", font=self.DATA_FONT, fg="black")
            label.grid(row=i+2, column=1, padx=20, pady=5, sticky="w")
            self.gas_labels.append(label)

        self.heartrate_section_label = tk.Label(self.content_frame, text="Heart Rate Data", font=self.DATA_FONT, fg="black")
        self.heartrate_section_label.grid(row=1, column=2, padx=20, pady=10, sticky="n")

        self.heartrate_label = tk.Label(self.content_frame, text="Heart Rate: -", font=self.DATA_FONT, fg="black")
        self.heartrate_label.grid(row=2, column=2, padx=20, pady=5, sticky="w")

        self.bp_section_label = tk.Label(self.content_frame, text="Blood Pressure Data", font=self.DATA_FONT, fg="blue")
        self.bp_section_label.grid(row=1, column=3, padx=20, pady=10, sticky="n")

        self.sbp_label = tk.Label(self.content_frame, text="SBP: -", font=self.DATA_FONT, fg="black")
        self.sbp_label.grid(row=2, column=3, padx=20, pady=5, sticky="w")

        self.dbp_label = tk.Label(self.content_frame, text="DBP: -", font=self.DATA_FONT, fg="black")
        self.dbp_label.grid(row=3, column=3, padx=20, pady=5, sticky="w")

        self.spo2_section_label = tk.Label(self.content_frame, text="SpO2 Data", font=self.DATA_FONT, fg="black")
        self.spo2_section_label.grid(row=1, column=4, padx=20, pady=10, sticky="n")

        self.spo2_label = tk.Label(self.content_frame, text="SpO2: -", font=self.DATA_FONT, fg="black")
        self.spo2_label.grid(row=2, column=4, padx=20, pady=5, sticky="w")

        self.ppg_section_label = tk.Label(self.content_frame, text="PPG Data", font=self.DATA_FONT, fg="black")
        self.ppg_section_label.grid(row=1, column=5, padx=20, pady=10, sticky="n")

        self.ppg_label = tk.Label(self.content_frame, text="PPG: -", font=self.DATA_FONT, fg="black")
        self.ppg_label.grid(row=2, column=5, padx=20, pady=5, sticky="w")

        self.back_button = tk.Button(self.content_frame, text="Back to Menu", font=self.DATA_FONT, command=self.go_back_to_menu)
        self.back_button.grid(row=8, column=0, columnspan=6, pady=20)

        # Styling
        for section in [
            self.temp_section_label,
            self.gas_section_label,
            self.heartrate_section_label,
            self.bp_section_label,
            self.spo2_section_label,
            self.ppg_section_label,
        ]:
            section.config(bg="lightblue", relief="groove", borderwidth=2)

        for label in self.temp_labels + self.gas_labels + [
            self.heartrate_label, self.sbp_label, self.dbp_label, self.spo2_label, self.ppg_label
        ]:
            label.config(bg="white", relief="sunken", borderwidth=1)

        self.back_button.config(bg="lightblue", relief="raised", borderwidth=2)

        # Bind resize event
        self.bind('<Configure>', self.on_resize)

    def on_resize(self, event):
        """Resize background image to match window size"""
        if hasattr(self, 'bg_image_original'):
            resized = self.bg_image_original.resize((event.width, event.height), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(resized)
            self.bg_label.config(image=self.bg_photo)

    def update_data(self, data):
        if "temperatures" in data and len(data["temperatures"]) == 3:
            for i in range(3):
                self.temp_labels[i].config(text=f"Temp{i+1}: {data['temperatures'][i]}")

        if "gas" in data and len(data["gas"]) == 5:
            for i in range(5):
                self.gas_labels[i].config(text=f"Gas{i+1}: {data['gas'][i]}")

        if "heartrate" in data:
            self.heartrate_label.config(text=f"Heart Rate: {data['heartrate']}")

        if "blood_pressure" in data:
            self.sbp_label.config(text=f"SBP: {data['blood_pressure'].get('sbp', '-')}")
            self.dbp_label.config(text=f"DBP: {data['blood_pressure'].get('dbp', '-')}")

        if "spo2" in data:
            self.spo2_label.config(text=f"SpO2: {data['spo2']}")

        if "ppg" in data:
            self.ppg_label.config(text=f"PPG: {data['ppg']}")

        # Real-time BP from BPPage
        if "bp" in self.controller.pages:
            sbp, dbp = self.controller.pages["bp"].get_bp_values()
            if sbp is not None:
                self.sbp_label.config(text=f"SBP: {sbp:.1f}")
            if dbp is not None:
                self.dbp_label.config(text=f"DBP: {dbp:.1f}")

    def clear_data(self):
        for i in range(3):
            self.temp_labels[i].config(text=f"Temp{i+1}: -")
        for i in range(5):
            self.gas_labels[i].config(text=f"Gas{i+1}: -")
        self.heartrate_label.config(text="Heart Rate: -")
        self.sbp_label.config(text="SBP: -")
        self.dbp_label.config(text="DBP: -")
        self.spo2_label.config(text="SpO2: -")
        self.ppg_label.config(text="PPG: -")

    def go_back_to_menu(self):
        logging.info("Navigating back to menu page.")
        self.controller.show_page("menu_page")
