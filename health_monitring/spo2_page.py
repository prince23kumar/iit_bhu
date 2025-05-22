import tkinter as tk
from PIL import Image, ImageTk

class SPO2Page(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Fonts
        self.TITLE_FONT = ("Helvetica", 32, "bold")
        self.DATA_FONT = ("Helvetica", 20)
        self.BUTTON_FONT = ("Helvetica", 16)


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
        self.label = tk.Label(self, text="SpO2 Data", font=self.TITLE_FONT, fg="white", bg="black")
        self.label.place(relx=0.5, rely=0.15, anchor="center")

        # SpO2 Data Label
        self.data_label = tk.Label(self, text="SpO2: -", font=self.DATA_FONT, bg="white", fg="black", padx=20, pady=10)
        self.data_label.place(relx=0.5, rely=0.35, anchor="center")

        # Back Button
        back_button = tk.Button(self, text="Back to Menu", command=lambda: controller.show_page("menu_page"),
                                font=self.BUTTON_FONT, bg="#4CAF50", fg="white", activebackground="#45a049",
                                width=20, height=2, borderwidth=0)
        back_button.place(relx=0.5, rely=0.75, anchor="center")

    def update_data(self, data):
        """Update the displayed SpO2 data."""
        if "spo2" in data:
            spo2_val = data["spo2"]
            print(f"[SPO2Page] Updating SpO2: {spo2_val}")
            self.data_label.config(text=f"SpO2: {spo2_val}")

    def clear_data(self):
        """Clear the displayed data."""
        self.data_label.config(text="SpO2: -")
