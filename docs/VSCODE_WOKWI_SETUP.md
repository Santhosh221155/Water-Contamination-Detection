# VS Code Wokwi Extension Setup

## 1. Install the Extension

1. Open VS Code
2. Go to Extensions view (`Ctrl+Shift+X`)
3. Search for **"Wokwi Simulator"**
4. Click **Install**

## 2. Activate License

1. Press `F1` to open Command Palette
2. Type **"Wokwi: Request a License"**
3. Follow the prompt to get a free license from wokwi.com
4. Copy the license key and paste it back in VS Code

## 3. Run the Simulation

1. Open `firmware/water_quality_monitor.ino`
2. Press `F1`
3. Type **"Wokwi: Start Simulator"**
4. The simulation will start, and a serial monitor will open

## 4. Connect to Dashboard

1. Open a new terminal in VS Code
2. Run the bridge script:
   ```bash
   python serial_bridge.py
   ```
3. Start the Flask server (if not running):
   ```bash
   python app.py
   ```
4. Open `http://localhost:5000` in your browser

## Troubleshooting

- **Serial Port Not Found:** Check if Wokwi is running. The bridge tries to auto-detect the port.
- **No Data:** Ensure you are moving the potentiometers in the Wokwi simulator.
- **Connection Refused:** Ensure Flask is running on port 5000.
