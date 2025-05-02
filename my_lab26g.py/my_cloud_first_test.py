import time
import logging
import sys
import random  # Replace with actual sensor library
import threading

sys.path.append("lib")

from arduino_iot_cloud import ArduinoCloudClient

DEVICE_ID = "c498ebcf-4372-4d3a-a712-1897e3ed00e1"
SECRET_KEY = "oQ4pzDCOWdWAQ6rKoVqNUVfl4"

VOLTAGE_THRESHOLD = 40  # percent

def logging_func():
    logging.basicConfig(
        datefmt="%H:%M:%S",
        format="%(asctime)s.%(msecs)03d %(message)s",
        level=logging.INFO,
    )

# Function called when the cloud switch is pressed
def on_switch_changed(client, value):
    print("Switch Pressed! Status is:", value)

# Replace these with actual sensor read functions
def get_temperature():
    return round(20 + random.uniform(-2, 5), 2)  # Simulated °C

def get_humidity():
    return round(50 + random.uniform(-10, 10), 2)  # Simulated %

# Update values in background
def update_value_loop():
    while True:
        temp = get_temperature()
        hum = get_humidity()
        test_val = random.randint(0, 100)

        # Update cloud variables
        client["test_value"] = test_val
        client["test_temperature"] = temp
        client["test_humidity"] = hum

        # Check voltage level
        voltage_low = test_val < VOLTAGE_THRESHOLD
        client["voltage_warning"] = voltage_low  # Cloud variable for warning

        # Print status
        warning_msg = "⚠️ LOW VOLTAGE!" if voltage_low else "✅ Voltage OK"
        print(f"{warning_msg} → test_value: {test_val}%, test_temperature: {temp}°C, test_humidity: {hum}%")

        time.sleep(10)  # update every 10 seconds

if __name__ == "__main__":
    logging_func()

    client = ArduinoCloudClient(device_id=DEVICE_ID, username=DEVICE_ID, password=SECRET_KEY)

    # Register cloud variables
    client.register("test_value")
    client["test_value"] = 20

    client.register("test_switch", value=True, on_write=on_switch_changed)
    client.register("test_temperature")
    client.register("test_humidity")

    # New warning flag for low voltage
    client.register("voltage_warning", value=False)

    # Start background sensor simulation
    threading.Thread(target=update_value_loop, daemon=True).start()

    try:
        client.start()
    except KeyboardInterrupt:
        print("Stopped by user.")
    except Exception as e:
        print(f"Client crashed with error: {e}")
