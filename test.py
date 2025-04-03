import serial
import serial.tools.list_ports
from time import sleep

def test_nfc_reader(port_name, baudrate=9600, timeout=2):
    """
    Test NFC reader communication with detailed debugging output
    """
    print(f"\n=== Starting NFC Reader Test on {port_name} ===")
    
    # 1. Check if port exists
    available_ports = [p.device for p in serial.tools.list_ports.comports()]
    print(f"Available ports: {available_ports}")
    
    if port_name not in available_ports:
        print(f"❌ ERROR: Port {port_name} not found!")
        return False
    
    print(f"✅ Port {port_name} found")
    
    
    try:
        # 2. Try to open the serial connection
        with serial.Serial(port=port_name, baudrate=baudrate, timeout=timeout) as ser:
            print(f"✅ Successfully opened {port_name} at {baudrate} baud")
            
            # 3. Flush any existing data in buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            print("✅ Flushed serial buffers")
            
            # 4. Send request to Arduino
            print("Sending request 'R' to Arduino...")
            ser.write(b'R')
            
            # 5. Wait and read response
            print("Waiting for response (2 second timeout)...")
            response = ser.readline()
            
            # 6. Analyze the response
            if not response:
                print("❌ No response received (timeout)")
                print("Possible causes:")
                print("- Arduino not properly connected")
                print("- Wrong baud rate (currently using {baudrate})")
                print("- Arduino code not listening for serial requests")
                print("- NFC reader not properly connected to Arduino")
                return False
            
            try:
                decoded_response = response.decode('utf-8').strip()
                print(f"Raw response: {response} (hex: {response.hex()})")
                print(f"Decoded response: '{decoded_response}'")
                
                if decoded_response.startswith("ERROR:"):
                    print(f"❌ Arduino reported error: {decoded_response}")
                    return False
                
                if len(decoded_response) == 16 and decoded_response.isalnum():
                    print(f"✅ Valid 16-character ID received: {decoded_response}")
                    return True
                else:
                    print(f"❌ Invalid response format: {decoded_response}")
                    print("Expected 16 alphanumeric characters")
                    print("Possible causes:")
                    print("- Arduino code not sending correct format")
                    print("- Serial communication corruption")
                    print("- Wrong baud rate causing garbled data")
                    return False
                    
            except UnicodeDecodeError:
                print(f"❌ Failed to decode response: {response}")
                print("This usually indicates baud rate mismatch or corrupted data")
                print("Try these baud rates: 9600, 19200, 38400, 57600, 115200")
                return False
                
    except serial.SerialException as e:
        print(f"❌ Serial communication error: {str(e)}")
        print("Possible causes:")
        print("- Port already in use by another program")
        print("- Driver issues")
        print("- Hardware connection problem")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    # Configure these values to match your setup
    PORT = 'COM12'  # Change to your actual port
    BAUD_RATE = 9600  # Must match Arduino's Serial.begin() value
    
    print("NFC Reader Diagnostic Tool")
    print("-------------------------")
    
    while True:
        input("Place NFC card near reader and press Enter to test (or Ctrl+C to quit)...")
        success = test_nfc_reader(PORT, BAUD_RATE)
        
        if success:
            print("✔ Test successful!")
        else:
            print("✖ Test failed - see messages above for diagnosis")
        
        print("\n" + "="*50 + "\n")