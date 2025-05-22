# writer.py
import serial
import time
import random

ser = serial.Serial('COM3', 9600)
time.sleep(2)

try:
    while True:
        r = random.randint(500, 900)
        ir = random.randint(500, 900)
        g = random.randint(50, 200)
        data = f"R[{r}] IR[{ir}] G[{g}]\n"
        ser.write(data.encode())
        print(f"Sent: {data.strip()}")
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped writing.")
    ser.close()
