import machine # type: ignore
import dht # type: ignore
import time
import network # type: ignore
import urequests # type: ignore
import utime # type: ignore
import random
import gc

# --- CONFIGURATION ---
WIFI_SSID = "ssid"
WIFI_PASS = "yourpass"
# Replace with your computer's IP address
SERVER_URL = "http://192.168.0.101:5000/api/add" 

# --- PIN INITIALIZATION ---
# Onboard LED (usually GPIO 2) for status
led = machine.Pin(2, machine.Pin.OUT)

# DHT11 on GPIO 15 (D15)
dht_sensor = dht.DHT11(machine.Pin(15))

# I2C for BH1750 (Light Sensor) on SCL=22, SDA=21
i2c = machine.I2C(0, scl=machine.Pin(22), sda=machine.Pin(21))

def blink(times, delay=0.1):
    """Blink the onboard LED to indicate status."""
    for _ in range(times):
        led.value(1)
        utime.sleep(delay)
        led.value(0)
        utime.sleep(delay)

def get_lux():
    """Simple function to read BH1750 light sensor."""
    try:
        addr = 0x23
        i2c.writeto(addr, b'\x10') # Continuous high res mode
        utime.sleep_ms(200)
        data = i2c.readfrom(addr, 2)
        lux = (data[0] << 8 | data[1]) / 1.2
        return round(lux, 1)
    except:
        return 0.0

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASS)
        
        # Wait for connection with timeout (15 seconds)
        max_wait = 15
        while max_wait > 0:
            if wlan.isconnected():
                break
            max_wait -= 1
            print('Waiting for WiFi...')
            blink(1, 0.5) # Blink slowly while connecting
            utime.sleep(0.5)
            
        if not wlan.isconnected():
            print('WiFi Connection Failed!')
            blink(5, 0.1) # Fast blink on failure
            return False
            
    print('WiFi Connected! IP:', wlan.ifconfig()[0])
    blink(3, 0.2) # 3 blinks on success
    return True

# --- MAIN EXECUTION ---
print("System Starting...")
blink(2) # Initial blink

# Connect to WiFi
if not connect_wifi():
    print("Restarting in 5 seconds...")
    utime.sleep(5)
    machine.reset() # Reboot if WiFi fails

while True:
    try:
        # 1. Read DHT11
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        
        # 2. Read Light
        lux = get_lux()
        
        # 3. Generate Mock Voltage and Current
        mock_voltage = 3.3
        mock_current = round(0.2 + random.uniform(-0.05, 0.05), 3)
        
        # Prepare Data
        sensor_data = {
            "temperature": temp,
            "humidity": hum,
            "light": lux,
            "voltage": mock_voltage,
            "current": mock_current
        }
        
        print("Sending:", sensor_data)
        led.value(1) # LED ON while sending
        
        # 4. Send to Python Backend
        response = urequests.post(SERVER_URL, json=sensor_data)
        print("Server Response:", response.status_code)
        response.close()
        
        led.value(0) # LED OFF after sending
        
    except OSError as e:
        print("Network Error:", e)
        led.value(0)
        # Optional: Reconnect logic could go here
    except Exception as e:
        print("Error:", e)
        led.value(0)
    
    gc.collect() # Clean up memory
    utime.sleep(2) # Wait 2 seconds
