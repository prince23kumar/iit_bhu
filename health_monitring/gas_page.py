import tkinter as tk

class GasPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)
        self.BUTTON_FONT = ("Helvetica", 16)

        # Title Label
        self.label = tk.Label(self, text="Gas Sensor Data", font=self.TITLE_FONT, fg="white", bg="black")
        self.label.place(relx=0.5, rely=0.1, anchor="center")

        # Labels for each gas value
        self.gas_labels = []
        for i in range(5):
            label = tk.Label(self, text=f"Gas{i+1}: -", font=self.DATA_FONT, bg="white", fg="black", padx=20, pady=5)
            label.place(relx=0.5, rely=0.25 + i * 0.1, anchor="center")
            self.gas_labels.append(label)

        # Back Button
        back_button = tk.Button(self, text="Back to Menu", command=lambda: controller.show_page("menu_page"),
                                font=self.BUTTON_FONT, bg="#4CAF50", fg="white", activebackground="#45a049",
                                width=20, height=2, borderwidth=0)
        back_button.place(relx=0.5, rely=0.8, anchor="center")

    def update_data(self, data):
        """Update the displayed gas sensor data."""
        if "gas" in data and len(data["gas"]) == 5:
            for i in range(5):
                gas_val = data["gas"][i]
                self.gas_labels[i].config(text=f"Gas{i+1}: {gas_val}")
            print(f"[GasPage] Updated gas values: {data['gas']}")

    def clear_data(self):
        """Clear all displayed gas sensor data."""
        for i in range(5):
            self.gas_labels[i].config(text=f"Gas{i+1}: -")
