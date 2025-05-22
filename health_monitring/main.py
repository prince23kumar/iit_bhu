import tkinter as tk
import serial
import logging
import os
import shutil
import platform
import traceback
from datetime import datetime

from intro_page import IntroPage
from menu_page import MenuPage
from ppg_page import PPGPage
from heartrate_page import HeartRatePage
from ecg_page import ECGPage
from spo2_page import SPO2Page
from gas_page import GasPage
from bp_page import BPPage
from all_in_one_page import AllInOnePage
import os
import csv
import logging
from collections import deque
from temperature_page import TemperaturePage

# Configure logging
#logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s",
 #                  filename="health_app.log", filemode="w")
# Also log to console
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

class HealthMonitoringApp:
    def __init__(self, root, folder_name="memory"):
        self.root = root
        self.root.title("Health Monitoring App")
        
        # Get screen dimensions
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        logging.info(f"Screen dimensions: {self.screen_width}x{self.screen_height}")
        
        # Set window size - use geometry instead of fullscreen initially
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        # Uncomment this after the app is working
        # self.root.attributes("-fullscreen", True)
        self.root.bind("<Escape>", lambda event: self.root.destroy())

        # Serial communication settings
        self.com_port = None
        self.baud_rate = None
        self.serial_connection = None
        self.is_reading = False  # Flag to control serial reading
        
        
        # CSV logging setup
        self.max_lines = 100
        self.memory_path = folder_name
        self.files = {
            "ppg": os.path.join(self.memory_path, "ppg.csv"),
            "heartrate": os.path.join(self.memory_path, "heartrate.csv"),
            "ecg": os.path.join(self.memory_path, "ecg.csv"),
            "spo2": os.path.join(self.memory_path, "spo2.csv"),
            "gas": os.path.join(self.memory_path, "gas.csv"),
            "temperatures": os.path.join(self.memory_path, "temperatures.csv"),
            "bp": os.path.join(self.memory_path, "bp.csv"),
        }
        self.buffers = {key: deque(maxlen=self.max_lines) for key in self.files}


        # Data storage
        self.latest_data = []

        # Pages
        self.pages = {}
        
        try:
            self.create_pages()
            # Start with intro page instead of menu page
            self.show_page("intro_page")
        except Exception as e:
            logging.error(f"Error creating pages: {e}")
            logging.error(traceback.format_exc())
            # Show a simple error message on the screen
            error_label = tk.Label(root, text=f"Error initializing app: {str(e)}\n\nCheck health_app.log for details", 
                                  font=("Helvetica", 14), fg="red")
            error_label.pack(expand=True, fill="both", padx=20, pady=20)

    def _get_headers_for_key(self, key):
        headers = {
            "ppg": ["IR", "Red", "Green"],
            "heartrate": ["HeartRate"],
            "ecg": ["ECG"],
            "spo2": ["SPO2"],
            "gas": ["Gas1", "Gas2", "Gas3", "Gas4", "Gas5"],
            "temperatures": ["Temp1", "Temp2", "Temp3"],
            "bp": ["SBP", "DBP"],
        }
        return headers.get(key, ["Value"])

    def update_csv_files(self, parsed_data):
        if not parsed_data:
            return
        # Update internal buffers
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        for key, value in parsed_data.items():
            if isinstance(value, list):
                self.buffers[key].append([timestamp] + value)
            else:
                self.buffers[key].append([timestamp, value])  # Wrap single value in a list

        # Write to CSV files
        for key, filepath in self.files.items():
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Timestamp"] + self._get_headers_for_key(key))
                writer.writerows(self.buffers[key])

        # Update BPPage with PPG data
        if "ppg" in parsed_data:
            self.pages["bp"].update_data({"ppg": parsed_data["ppg"]})

    def create_pages(self):
        """Create all pages and store them in a dictionary."""
        self.pages["menu_page"] = MenuPage(self.root, self)
        self.pages["intro_page"] = IntroPage(self.root, self)

        self.pages["ppg"] = PPGPage(self.root, self)
        self.pages["heartrate"] = HeartRatePage(self.root, self)
        self.pages["ecg"] = ECGPage(self.root, self)
        self.pages["spo2"] = SPO2Page(self.root, self)
        self.pages["gas"] = GasPage(self.root, self)
        self.pages["temperatures"] = TemperaturePage(self.root, self)
        self.pages["bp"] = BPPage(self.root, self)
        self.pages["all_in_one_page"] = AllInOnePage(self.root, self)

    def show_page(self, page_name):
        """Display the requested page and update it with the latest data."""
        for page in self.pages.values():
            page.pack_forget()
            if hasattr(page, "clear_data"):
                page.clear_data()  # Reset page data
        self.pages[page_name].pack(fill="both", expand=True)

        # If data is available, update the displayed page
        if self.latest_data:
            if page_name in self.pages and hasattr(self.pages[page_name], "update_data"):
                self.pages[page_name].update_data(self.latest_data)

    def set_serial_config(self, com_port, baud_rate):
        """Set COM port and baud rate from intro page and start serial communication."""
        self.com_port = com_port
        self.baud_rate = baud_rate
        logging.info(f"COM Port selected: {com_port}, Baud Rate: {baud_rate}")
        self.start_serial_reading()

    def start_serial_reading(self):
        """Start reading from the serial port using after() to update periodically."""
        if self.com_port and self.baud_rate:
            try:
                # Handle platform-specific port names
                port_to_use = self.com_port
                
                # For Raspberry Pi (Linux), try to adapt Windows-style port names
                if platform.system() != 'Windows' and self.com_port.startswith('COM'):
                    # Try to convert COM3 to /dev/ttyUSB0, etc.
                    try:
                        com_num = int(self.com_port.replace('COM', ''))
                        port_to_use = f"/dev/ttyUSB{com_num-1}"  # COM1 might correspond to ttyUSB0
                        logging.info(f"Converted {self.com_port} to {port_to_use}")
                    except ValueError:
                        # Fall back to common Raspberry Pi ports
                        logging.warning(f"Could not convert {self.com_port}. Will try common Raspberry Pi ports.")
                        for potential_port in ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0', '/dev/ttyAMA0']:
                            try:
                                logging.info(f"Trying {potential_port}...")
                                test_connection = serial.Serial(potential_port, int(self.baud_rate), timeout=1)
                                test_connection.close()
                                port_to_use = potential_port
                                logging.info(f"Found working port: {port_to_use}")
                                break
                            except Exception as e:
                                logging.warning(f"Port {potential_port} not available: {e}")
                
                logging.info(f"Attempting to connect to {port_to_use} at {self.baud_rate} baud.")
                self.serial_connection = serial.Serial(port_to_use, int(self.baud_rate), timeout=1)
                self.is_reading = True
                logging.info(f"Successfully connected to {port_to_use} at {self.baud_rate} baud.")
                self.read_serial_data()  # Initial call to start the loop
            except serial.SerialException as e:
                logging.error(f"Error opening serial port: {e}")
                # Don't let serial port errors stop the UI from displaying
                logging.info("Continuing with UI despite serial port error")

    def read_serial_data(self):
        """Read data from the serial port and update pages every 1 millisecond."""
        if self.is_reading and self.serial_connection:
            try:
                if self.serial_connection.in_waiting > 0:
                    data = self.serial_connection.readline().decode('utf-8').strip()
                    if not data:
                        return  # Skip empty lines

                    parsed_data = self.parse_serial_data(data)
                    if parsed_data:
                        self.latest_data = parsed_data
                        
                        
                        self.update_csv_files(parsed_data)

                        
                      #  print ("latest data : " , self.latest_data)
                        # print ("=======================")

                        # Update the current page
                        current_page = self.get_current_page()
                        if current_page in self.pages and hasattr(self.pages[current_page], "update_data"):
                            self.pages[current_page].update_data(self.latest_data)

            except UnicodeDecodeError:
                logging.error("Error decoding serial data. Ensure the baud rate is correct.")
            except serial.SerialException as e:
                logging.error(f"Serial error: {e}")
                self.stop_serial_reading()
            except Exception as e:
                logging.error(f"Unexpected error: {e}")

            # Schedule the next read (every 1 millisecond)
            self.root.after(1, self.read_serial_data)

    def parse_serial_data(self, data):
        """Parse serial data into a dictionary."""
        values = data.split(',')
        if len(values) == 15:  # Ensure correct number of values
            return {
                "ppg": values[0:3],  # IR, Red, Green
                "heartrate": values[3],  # Heartrate
                "ecg": values[4],  # ECG
                "spo2": values[5],  # SPO2
                "gas": values[6:11],  # Gas1 - Gas5
                "temperatures": values[11:14],  # Temp1 - Temp3
                "bp": values[14:16],  # Blood Pressure
            }
        logging.warning(f"Invalid data length: expected 16, got {len(values)}")
        return None

    def get_current_page(self):
        """Find out which page is currently visible."""
        for name, page in self.pages.items():
            if page.winfo_ismapped():
                return name
        return None

    def stop_serial_reading(self):
        """Stop reading from the serial port and close the connection."""
        self.is_reading = False
        if self.serial_connection:
            self.serial_connection.close()
            self.serial_connection = None
            logging.info("Serial connection closed.")



folder_path = "memory" 

if __name__ == "__main__":
    
    # if os.path.exists(folder_path):
    #     shutil.rmtree(folder_path)
    os.makedirs(folder_path, exist_ok=True)
    
    
    root = tk.Tk()
    app = HealthMonitoringApp(root)
    root.mainloop()
