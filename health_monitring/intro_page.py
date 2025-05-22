import tkinter as tk
from tkinter import font as tkFont
from PIL import Image, ImageTk
from tkinter import ttk
import serial.tools.list_ports
import platform
import os
import logging

class IntroPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Constants
        self.TITLE_FONT = ("Helvetica", 36, "bold")
        self.LABEL_FONT = ("Helvetica", 16)
        self.BUTTON_FONT = ("Helvetica", 18, "bold")
        self.BG_COLOR = "black"
        self.FG_COLOR = "white"

        try:
            # Background image - handle errors gracefully
            self.screen_width = self.winfo_screenwidth()
            self.screen_height = self.winfo_screenheight()
            
            # Get the absolute path to the image file
            image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "health_monitring", "assets", "home_page.jpg")
            if not os.path.exists(image_path):
                # Try relative path if absolute path doesn't work
                image_path = "assets/home_page.jpg"
                
            if os.path.exists(image_path):
                logging.info(f"Loading background image from: {image_path}")
                self.bg_image = Image.open(image_path)
                self.bg_image = self.bg_image.resize((self.screen_width, self.screen_height), Image.Resampling.LANCZOS)
                self.bg_photo = ImageTk.PhotoImage(self.bg_image)
                bg_label = tk.Label(self, image=self.bg_photo)
                bg_label.place(relwidth=1, relheight=1)
            else:
                logging.error(f"Background image not found at: {image_path}")
                # Create a solid color background instead
                bg_label = tk.Label(self, bg=self.BG_COLOR)
                bg_label.place(relwidth=1, relheight=1)
                
        except Exception as e:
            logging.error(f"Error loading background image: {e}")
            # Create a solid color background instead
            bg_label = tk.Label(self, bg=self.BG_COLOR)
            bg_label.place(relwidth=1, relheight=1)

        # Title label
        title_label = tk.Label(self, text="IIT BHU Health Monitoring App", font=self.TITLE_FONT, fg=self.FG_COLOR, bg=self.BG_COLOR)
        title_label.place(relx=0.5, rely=0.4, anchor="center")

        # COM Port Dropdown
        com_label = tk.Label(self, text="Select COM Port:", font=self.LABEL_FONT, fg=self.FG_COLOR, bg=self.BG_COLOR)
        com_label.place(relx=0.5, rely=0.45, anchor="center")

        self.com_ports = self.get_available_com_ports()
        self.com_port_var = tk.StringVar()
        self.com_port_dropdown = ttk.Combobox(self, textvariable=self.com_port_var, values=self.com_ports, font=self.LABEL_FONT, state="readonly")
        self.com_port_dropdown.place(relx=0.5, rely=0.5, anchor="center")
        if self.com_ports:
            self.com_port_dropdown.current(0)

        # Baud Rate Dropdown
        baud_label = tk.Label(self, text="Select Baud Rate:", font=self.LABEL_FONT, fg=self.FG_COLOR, bg=self.BG_COLOR)
        baud_label.place(relx=0.5, rely=0.6, anchor="center")

        self.baud_rates = ["9600", "19200", "38400", "57600", "115200"]
        self.baud_rate_var = tk.StringVar()
        self.baud_rate_dropdown = ttk.Combobox(self, textvariable=self.baud_rate_var, values=self.baud_rates, font=self.LABEL_FONT, state="readonly")
        self.baud_rate_dropdown.place(relx=0.5, rely=0.65, anchor="center")
        self.baud_rate_dropdown.current(0)

        # Next button
        next_button = tk.Button(self, text="Next", command=self.on_next,
                                font=self.BUTTON_FONT, bg="#4CAF50", fg=self.FG_COLOR, padx=20, pady=10, borderwidth=0,
                                activebackground="#45a049")
        next_button.place(relx=0.5, rely=0.8, anchor="center")

    def get_available_com_ports(self):
        """Get a list of available COM ports including platform-specific ports."""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        # Add Raspberry Pi specific ports if we're on Linux
        if platform.system() != 'Windows':
            rpi_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0', '/dev/ttyAMA0']
            for port in rpi_ports:
                if port not in ports and os.path.exists(port):
                    ports.append(port)
            
            # If no ports found at all on Linux, add common ones as suggestions
            if not ports:
                ports = rpi_ports
                logging.warning("No serial ports detected. Adding common Raspberry Pi ports as suggestions.")
        
        logging.info(f"Available serial ports: {ports}")
        return ports

    def on_next(self):
        """Send selected COM port and baud rate to controller, then go to menu page."""
        selected_com = self.com_port_var.get()
        selected_baud = self.baud_rate_var.get()

        # Make sure both values are selected or provide defaults
        if not selected_com and platform.system() != 'Windows':
            # Default to a common Raspberry Pi port if none selected
            selected_com = '/dev/ttyUSB0'
            logging.warning(f"No COM port selected, defaulting to {selected_com}")
            
        if not selected_baud:
            selected_baud = "9600"  # Default baud rate
            
        logging.info(f"Selected COM port: {selected_com}, Baud rate: {selected_baud}")
        self.controller.set_serial_config(selected_com, selected_baud)
        self.controller.show_page("menu_page")
