import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk

class MenuPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Constants
        self.TITLE_FONT = ("Helvetica", 36, "bold")
        self.BUTTON_FONT = ("Helvetica", 16)
        self.BG_COLOR = "#f5f5f5"
        self.BUTTON_BG = "#4CAF50"
        self.BUTTON_FG = "white"
        self.ACTIVE_BG = "#45a049"

        # Set background image
        self.screen_width = self.winfo_screenwidth()
        self.screen_height = self.winfo_screenheight()

        self.bg_image = Image.open("assets/menu_background.png")  # replace with your bg image path
        self.bg_image = self.bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)

        bg_label = tk.Label(self, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)

        # Title
        title_label = tk.Label(self, text="Health Monitoring Menu", font=self.TITLE_FONT, bg="#000000", fg="white")
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Buttons
        pages = [("PPG", "ppg"), ("Heartrate", "heartrate"), ("ECG", "ecg"),
                 ("SPO2", "spo2"), ("Gas", "gas"), ("Temperatures", "temperatures")]
        
        # Create the regular buttons in the grid
        for i, (text, page_name) in enumerate(pages):
            btn = tk.Button(self, text=text, font=self.BUTTON_FONT,
                            bg=self.BUTTON_BG, fg=self.BUTTON_FG, activebackground=self.ACTIVE_BG,
                            width=18, height=3, borderwidth=0,
                            command=lambda p=page_name: controller.show_page(p))
            btn.place(relx=0.15 + (i % 3) * 0.3, rely=0.35 + (i // 3) * 0.2, anchor="center")
        
        # Create the BP button centered below the other buttons
        bp_button = tk.Button(self, text="Blood Pressure", font=self.BUTTON_FONT,
                           bg=self.BUTTON_BG, fg=self.BUTTON_FG, activebackground=self.ACTIVE_BG,
                           width=18, height=3, borderwidth=0,
                           command=lambda: controller.show_page("bp"))
        bp_button.place(relx=0.45, rely=0.75, anchor="center")
        # Back button
        back_button = tk.Button(self, text="Back", font=self.BUTTON_FONT,
                                bg="#e53935", fg="white", activebackground="#d32f2f",
                                width=18, height=2, borderwidth=0,
                                command=lambda: controller.show_page("intro_page"))
        back_button.place(relx=0.45, rely=0.85, anchor="center")

        # Add icon button for All-in-One Page
        icon_image = Image.open("assets/home_page.jpg")  # Replace with your icon image path
        icon_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
        icon_photo = ImageTk.PhotoImage(icon_image)

        icon_button = tk.Button(self, image=icon_photo, borderwidth=0,
                                command=lambda: controller.show_page("all_in_one_page"))
        icon_button.image = icon_photo  # Keep a reference to avoid garbage collection
        icon_button.place(relx=0.95, rely=0.05, anchor="center")
