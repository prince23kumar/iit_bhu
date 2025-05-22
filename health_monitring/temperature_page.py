import tkinter as tk

class TemperaturePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)
        self.BUTTON_FONT = ("Helvetica", 16)

        # Title Label
        self.label = tk.Label(self, text="Temperature Data", font=self.TITLE_FONT, fg="white", bg="black")
        self.label.place(relx=0.5, rely=0.1, anchor="center")

        # Temperature labels
        self.temp_labels = []
        for i in range(3):
            label = tk.Label(self, text=f"Temp{i+1}: -", font=self.DATA_FONT, bg="white", fg="black", padx=20, pady=5)
            label.place(relx=0.5, rely=0.25 + i * 0.1, anchor="center")
            self.temp_labels.append(label)

        # Back Button
        back_button = tk.Button(self, text="Back to Menu", command=lambda: controller.show_page("menu_page"),
                                font=self.BUTTON_FONT, bg="#4CAF50", fg="white", activebackground="#45a049",
                                width=20, height=2, borderwidth=0)
        back_button.place(relx=0.5, rely=0.75, anchor="center")

    def update_data(self, data):
        """Update the displayed temperature data."""
        if "temperatures" in data and len(data["temperatures"]) == 3:
            for i in range(3):
                temp_val = data["temperatures"][i]
                self.temp_labels[i].config(text=f"Temp{i+1}: {temp_val}")
            print(f"[TemperaturePage] Updated temperatures: {data['temperatures']}")

    def clear_data(self):
        """Clear all displayed temperature data."""
        for i in range(3):
            self.temp_labels[i].config(text=f"Temp{i+1}: -")
