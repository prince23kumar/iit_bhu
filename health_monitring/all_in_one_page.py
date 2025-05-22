import tkinter as tk

class AllInOnePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)

        # Title Label
        self.label = tk.Label(self, text="All-In-One Health Data", font=self.TITLE_FONT, fg="white", bg="Blue")
        self.label.grid(row=0, column=0, columnspan=4, pady=20)

        # Temperature Section
        self.temp_section_label = tk.Label(self, text="Temperature Data", font=self.DATA_FONT, fg="black")
        self.temp_section_label.grid(row=1, column=0, padx=20, pady=10, sticky="n")

        self.temp_labels = []
        for i in range(3):
            label = tk.Label(self, text=f"Temp{i+1}: -", font=self.DATA_FONT, fg="black")
            label.grid(row=i+2, column=0, padx=20, pady=5, sticky="w")
            self.temp_labels.append(label)

        # Gas Section
        self.gas_section_label = tk.Label(self, text="Gas Data", font=self.DATA_FONT, fg="black")
        self.gas_section_label.grid(row=1, column=1, padx=20, pady=10, sticky="n")

        self.gas_labels = []
        for i in range(5):
            label = tk.Label(self, text=f"Gas{i+1}: -", font=self.DATA_FONT, fg="black")
            label.grid(row=i+2, column=1, padx=20, pady=5, sticky="w")
            self.gas_labels.append(label)

        # Heart Rate Section
        self.heartrate_section_label = tk.Label(self, text="Heart Rate Data", font=self.DATA_FONT, fg="black")
        self.heartrate_section_label.grid(row=1, column=2, padx=20, pady=10, sticky="n")

        self.heartrate_label = tk.Label(self, text="Heart Rate: -", font=self.DATA_FONT, fg="black")
        self.heartrate_label.grid(row=2, column=2, padx=20, pady=5, sticky="w")

        # Blood Pressure Section
        self.bp_section_label = tk.Label(self, text="Blood Pressure Data", font=self.DATA_FONT, fg="blue")
        self.bp_section_label.grid(row=1, column=3, padx=20, pady=10, sticky="n")

        self.sbp_label = tk.Label(self, text="SBP: -", font=self.DATA_FONT, fg="black")
        self.sbp_label.grid(row=2, column=3, padx=20, pady=5, sticky="w")

        self.dbp_label = tk.Label(self, text="DBP: -", font=self.DATA_FONT, fg="black")
        self.dbp_label.grid(row=3, column=3, padx=20, pady=5, sticky="w")

        # Back to Menu Button
        self.back_button = tk.Button(self, text="Back to Menu", font=self.DATA_FONT, command=self.go_back_to_menu)
        self.back_button.grid(row=8, column=0, columnspan=4, pady=20)

    def update_data(self, data):
        """Update the displayed data."""
        if "temperatures" in data and len(data["temperatures"]) == 3:
            for i in range(3):
                temp_val = data["temperatures"][i]
                self.temp_labels[i].config(text=f"Temp{i+1}: {temp_val}")

        if "gas" in data and len(data["gas"]) == 5:
            for i in range(5):
                gas_val = data["gas"][i]
                self.gas_labels[i].config(text=f"Gas{i+1}: {gas_val}")

        if "heartrate" in data:
            self.heartrate_label.config(text=f"Heart Rate: {data['heartrate']}")

        if "blood_pressure" in data:
            if "sbp" in data["blood_pressure"]:
                self.sbp_label.config(text=f"SBP: {data['blood_pressure']['sbp']}")
            if "dbp" in data["blood_pressure"]:
                self.dbp_label.config(text=f"DBP: {data['blood_pressure']['dbp']}")

        # Fetch real-time SBP and DBP values from BPPage
        if "bp" in self.controller.pages:
            sbp, dbp = self.controller.pages["bp"].get_bp_values()
            if sbp is not None and dbp is not None:
                self.sbp_label.config(text=f"SBP: {sbp:.1f}")
                self.dbp_label.config(text=f"DBP: {dbp:.1f}")

    def clear_data(self):
        """Clear all displayed data."""
        for i in range(3):
            self.temp_labels[i].config(text=f"Temp{i+1}: -")
        for i in range(5):
            self.gas_labels[i].config(text=f"Gas{i+1}: -")
        self.heartrate_label.config(text="Heart Rate: -")
        self.sbp_label.config(text="SBP: -")
        self.dbp_label.config(text="DBP: -")

    def go_back_to_menu(self):
        """Navigate back to the menu page."""
        self.controller.show_frame("MenuPage")