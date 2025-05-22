import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk  # For handling images
from tkinter import ttk
import serial.tools.list_ports  # For listing available COM ports

PAGES = ["PPG", "Heartrate", "ECG", "SPO2", "Gas", "Temperatures"]


class HealthMonitoringApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Health Monitoring App")
        self.root.attributes("-fullscreen", True)  # Make the app full screen
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        # Get screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.pages = {}
        self.create_intro_page()
        self.create_menu_page()
        self.create_other_pages(PAGES)

        self.show_page("intro_page")

    def create_intro_page(self):
        intro_page = tk.Frame(self.root)
        self.pages["intro_page"] = intro_page

        # Add a background image
        self.bg_image = Image.open("home_page.jpg")  # Replace with your image path
        self.bg_image = self.bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        bg_label = tk.Label(intro_page, image=self.bg_photo)
        bg_label.place(relwidth=1, relheight=1)  # Cover the entire frame

        # Custom font for the title
        title_font = tkFont.Font(family="Helvetica", size=36, weight="bold")

        # Title label
        title_label = tk.Label(
            intro_page,
            text="IIT BHU Health Monitoring App",
            font=title_font,
            fg="white",  # Text color
            bg="black",  # Background color (for contrast)
        )
        title_label.place(relx=0.5, rely=0.4, anchor="center")  # Center the title
        
        # COM Port Dropdown
        com_label = tk.Label(
            intro_page,
            text="Select COM Port:",
            font=("Helvetica", 16),
            fg="white",
            bg="black",
        )
        com_label.place(relx=0.5, rely=0.45, anchor="center")

        self.com_ports = self.get_available_com_ports()  # Get available COM ports
        self.com_port_var = tk.StringVar()
        self.com_port_dropdown = ttk.Combobox(
            intro_page,
            textvariable=self.com_port_var,
            values=self.com_ports,
            font=("Helvetica", 14),
            state="readonly",  # Prevent manual input
        )
        self.com_port_dropdown.place(relx=0.5, rely=0.5, anchor="center")
        if self.com_ports:
            self.com_port_dropdown.current(0)  # Set the first COM port as default

        # Baud Rate Dropdown
        baud_label = tk.Label(
            intro_page,
            text="Select Baud Rate:",
            font=("Helvetica", 16),
            fg="white",
            bg="black",
        )
        baud_label.place(relx=0.5, rely=0.6, anchor="center")

        self.baud_rates = ["9600", "19200", "38400", "57600", "115200"]  # Common baud rates
        self.baud_rate_var = tk.StringVar()
        self.baud_rate_dropdown = ttk.Combobox(
            intro_page,
            textvariable=self.baud_rate_var,
            values=self.baud_rates,
            font=("Helvetica", 14),
            state="readonly",  # Prevent manual input
        )
        self.baud_rate_dropdown.place(relx=0.5, rely=0.65, anchor="center")
        self.baud_rate_dropdown.current(0)  # Set the first baud rate as default

        # Custom font for the button
        button_font = tkFont.Font(family="Helvetica", size=18, weight="bold")

        # Next button
        next_button = tk.Button(
            intro_page,
            text="Next",
            command=lambda: self.show_page("menu_page"),
            font=button_font,
            bg="#4CAF50",  # Green background
            fg="white",    # White text
            padx=20,
            pady=10,
            borderwidth=0,
            activebackground="#45a049",  # Darker green when clicked
        )
        next_button.place(relx=0.5, rely=0.8, anchor="center")  # Center the button


    def create_menu_page(self):
        menu_page = tk.Frame(self.root)
        self.pages["menu_page"] = menu_page

        # Title label
        label = tk.Label(menu_page, text="Menu", font=("Arial", 24))
        label.grid(row=0, column=0, columnspan=6, pady=20)  # Centered across the grid

        # Page names and corresponding page keys
        pages = [
            ("PPG", "ppg"),
            ("Heartrate", "heartrate"),
            ("ECG", "ecg"),
            ("SPO2", "spo2"),
            ("Gas", "gas"),
            ("Temperatures", "temperatures"),
        ]

        # Create buttons in a 2x6 grid
        for i, (text, page_name) in enumerate(pages):
            # First row (row=1)
            button = tk.Button(
                menu_page,
                text=text,
                command=lambda p=page_name: self.show_page(p),
                font=("Arial", 16),
                width=15,
                height=3,
            )
            button.grid(row=1, column=i, padx=10, pady=10)  # Add padding for spacing

            # Second row (row=2)
            button = tk.Button(
                menu_page,
                text=f"{text} Settings",  # Example: "PPG Settings"
                command=lambda p=page_name: self.show_page(f"{p}_settings"),  # Example: "ppg_settings"
                font=("Arial", 14),
                width=15,
                height=2,
            )
            button.grid(row=2, column=i, padx=10, pady=10)  # Add padding for spacing

        # Back button
        back_button = tk.Button(
            menu_page,
            text="Back",
            command=lambda: self.show_page("intro_page"),
            font=("Arial", 16),
            width=15,
            height=2,
        )
        back_button.grid(row=3, column=0, columnspan=6, pady=20)  # Centered across the grid
    
    def get_available_com_ports(self):
        """Get a list of available COM ports."""
        com_ports = [port.device for port in serial.tools.list_ports.comports()]
        return com_ports

    def create_other_pages(self, pages):
        for p in pages:
            page_name = p.lower()
            page = tk.Frame(self.root)
            self.pages[page_name] = page

            label = tk.Label(page, text=f"This is {page_name}", font=("Arial", 24))
            label.pack(pady=self.screen_height // 3)  # Center vertically

            back_button = tk.Button(page, text="Back to Menu", command=lambda: self.show_page("menu_page"), font=("Arial", 16))
            back_button.pack(pady=20)

    def show_page(self, page_name):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[page_name].pack(fill="both", expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = HealthMonitoringApp(root)
    root.mainloop()
    
    
    
