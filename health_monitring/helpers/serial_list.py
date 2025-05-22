import serial.tools.list_ports
import platform
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def get_available_ports():
    """Get available serial ports with platform-specific handling."""
    # Get ports using the standard pyserial method
    standard_ports = [port.device for port in serial.tools.list_ports.comports()]
    logging.info(f"Ports detected by pyserial: {standard_ports}")
    
    # On Raspberry Pi or other Linux systems
    if platform.system() != 'Windows':
        # Common Raspberry Pi serial ports
        rpi_ports = ['/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0', '/dev/ttyAMA0']
        
        # Add ports that exist but weren't detected by pyserial
        for port in rpi_ports:
            if port not in standard_ports and os.path.exists(port):
                standard_ports.append(port)
                logging.info(f"Added Raspberry Pi port: {port}")
    
    return standard_ports

if __name__ == "__main__":
    ports = get_available_ports()
    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"  - {port}")
    else:
        print("No serial ports detected. If using Raspberry Pi, check your connections.")
        print("Common Raspberry Pi ports are: /dev/ttyUSB0, /dev/ttyACM0, /dev/ttyS0, /dev/ttyAMA0")
