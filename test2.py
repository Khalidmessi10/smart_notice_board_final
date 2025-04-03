import serial
ser = serial.Serial('COM12', 9600, timeout=2)  # Replace with your port
ser.write(b'R\n')
response = ser.readline().decode().strip()
print(f"Received: {response} (Length: {len(response)})")