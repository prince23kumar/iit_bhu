import tkinter as tk

class HeartRatePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f2f2f2")  # Set background for the entire page
        self.controller = controller

        # Constants
        self.TITLE_FONT = ("Arial", 24)
        self.DATA_FONT = ("Arial", 18)

        # Title label
        self.label = tk.Label(
            self,
            text="Heart Rate Data",
            font=self.TITLE_FONT,
            bg="#f2f2f2",  # Match page background
            fg="black"
        )
        self.label.pack(pady=20)

        # Heart rate display
        self.hr_label = tk.Label(
            self,
            text="Heart Rate: - bpm",
            font=self.DATA_FONT,
            bg="#f2f2f2",
            fg="black"
        )
        self.hr_label.pack(pady=10)

        # Back to Menu button
        back_button = tk.Button(
            self,
            text="Back to Menu",
            command=lambda: controller.show_page("menu_page"),
            font=self.DATA_FONT
        )
        back_button.pack(pady=20)

    def update_data(self, data):
        """Update the displayed heart rate value."""
        if "heartrate" in data:
            print(f"[heartrate_page] Updating ECG: {data['heartrate']}")
            self.hr_label.config(text=f"Heart Rate: {data['heartrate']} bpm")

    def clear_data(self):
        """Clear the displayed heart rate."""
        self.hr_label.config(text="Heart Rate: - bpm")
