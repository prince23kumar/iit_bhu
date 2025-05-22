# reader.py
import serial

ser = serial.Serial('COM3', 9600)

try:
    while True:
        if ser.in_waiting:
            line = ser.readline().decode().strip()
            print(f"Received: {line}")
except KeyboardInterrupt:
    print("Stopped reading.")
    ser.close()
