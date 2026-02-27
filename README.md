# Sensor Dashboard Project

This project consists of two main parts:
1.  **Python Backend (`app.py`)**: A Flask-based server that receives data from sensors and serves a React-based dashboard.
2.  **ESP32 Firmware (`main.py`)**: MicroPython code that runs on an ESP32 microcontroller to read data from sensors and send it to the backend.

## Demo

<video src="static/lib/demo.mp4" controls width="720">
Your browser does not support video playback. You can download and watch the demo:
<a href="static/lib/demo.mp4">Download demo.mp4</a>
</video>

## Getting Started (Python Backend)

1.  **Install Dependencies**: Make sure you have Python installed, then run the following command in your terminal:
    ```bash
    pip install -r requirements.txt
    ```
2.  **Run the Server**:
    ```bash
    python app.py
    ```
3.  **View the Dashboard**: Open your browser and go to `http://localhost:5000/`.

## ESP32 Configuration (`main.py`)

The `main.py` file is intended to be uploaded to your ESP32 microcontroller running MicroPython.

### Configuration Settings
- **`WIFI_SSID` and `WIFI_PASS`**: Update these with your Wi-Fi credentials.
- **`SERVER_URL`**: Update this with your computer's actual IP address (e.g., `http://192.168.1.15:5000/api/add`).

### Linter Warnings
You may see "Import could not be resolved" warnings for modules like `machine`, `dht`, `network`, etc. These are **normal** because these modules only exist on the ESP32 hardware and are not available on a standard PC. The code will work correctly once uploaded to the microcontroller.

## Project Structure
- `app.py`: Flask backend server.
- `main.py`: ESP32 MicroPython script.
- `react_dashboard.html`: The frontend dashboard (React).
- `static/lib/`: Local copies of JavaScript libraries for offline support.
- `sensor_data.json`: The database where readings are stored.
