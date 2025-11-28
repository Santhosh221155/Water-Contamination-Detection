# Wokwi Setup Guide - Tamil Nadu Water Quality Monitor

## Overview

This guide explains how to set up and use the Wokwi ESP32 simulator with the Water Quality Monitoring System.

## Quick Start

### 1. Access the Application

Open your browser and navigate to:
```
http://localhost:5000
```

### 2. Start the Wokwi Simulator

1. In the left column, you'll see the embedded Wokwi simulator
2. Click the **"Start Simulation"** button in Wokwi
3. The ESP32 will boot up and start reading sensors

### 3. Adjust Potentiometers

The simulator has 6 potentiometers representing water quality sensors:

| Potentiometer | Parameter | Range | Safe Range |
|--------------|-----------|-------|------------|
| pot1 | pH Level | 5.5 - 8.8 | 6.5 - 8.5 |
| pot2 | Sulphate (mg/L) | 69 - 496 | 100 - 400 |
| pot3 | Hardness (mg/L) | 66 - 281 | 80 - 250 |
| pot4 | Conductivity (µS/cm) | 152 - 895 | 200 - 800 |
| pot5 | TDS (mg/L) | 137 - 1178 | 200 - 1000 |
| pot6 | Turbidity (NTU) | 1.3 - 9.4 | 1.5 - 5.0 |

**To adjust**: Click and drag the potentiometer knob or use the slider

### 4. View Serial Output

1. Click the **Serial Monitor** button at the bottom of Wokwi
2. You'll see JSON output every 1 second:
   ```json
   {"pH":7.2,"Sulphate":250,"Hardness":165,"Conductivity":500,"TDS":600,"Turbidity":3.0,"is_safe":1,"timestamp":"5234"}
   ```

### 5. Send Data to Prediction System

**Method 1: Fully Automatic (Recommended)**
1. Open a new terminal
2. Run the bridge script:
   ```bash
   python auto_bridge.py
   ```
3. This will launch a browser window, start the simulation, and **automatically forward all data** to the prediction system.
4. You can just watch the results!

**Method 2: Manual Copy-Paste**
1. Copy a JSON line from the Wokwi serial monitor
2. Paste it into the "Serial Data Input" textarea
3. Click **"Send Data to Prediction"**

**Method 3: Auto-Send (Semi-Automatic)**
1. Copy a JSON line from Wokwi serial monitor
2. Paste into "Serial Data Input" textarea
3. Click **"Enable Auto-Send (Every 2s)"**

### 6. Monitor Predictions

Watch the right column for:
- **ML Prediction**: Safe or Unsafe with confidence score
- **LED Indicators**: Green (Safe) or Red (Unsafe)
- **Consecutive Counter**: Tracks contamination streak
- **Statistics**: Total samples, safe/unsafe counts
- **Sensor Readings**: Real-time values with threshold comparison

### 7. Email Alerts

When water is detected as **Unsafe for 5 consecutive readings**:
1. An email alert is automatically sent to: santhoshsanthosh40253@gmail.com
2. A red alert banner appears at the top of the dashboard
3. The consecutive counter turns red and enlarges

## Wokwi Project Configuration

### Hardware Setup

The Wokwi simulator includes:
- **ESP32 DevKit C V4**
- **6 Potentiometers** (simulating sensors)
- **2 LEDs** (Green = Safe, Red = Unsafe)
- **2 Resistors** (220Ω for LEDs)

### Pin Connections

```
Potentiometers → ESP32
├─ pot1 (pH)           → GPIO 34 (VP)
├─ pot2 (Sulphate)     → GPIO 35 (VN)
├─ pot3 (Hardness)     → GPIO 32
├─ pot4 (Conductivity) → GPIO 33
├─ pot5 (TDS)          → GPIO 25
└─ pot6 (Turbidity)    → GPIO 26

LEDs → ESP32
├─ Green LED → GPIO 13 (via 220Ω resistor)
└─ Red LED   → GPIO 12 (via 220Ω resistor)
```

### Firmware Details

The ESP32 firmware (`water_quality_monitor.ino`):
- Reads all 6 analog sensors every 1 second
- Maps analog values (0-4095) to sensor ranges
- Checks if values are within safe ranges
- Controls LEDs based on water quality
- Outputs JSON data via Serial (115200 baud)

## Testing Scenarios

### Scenario 1: Safe Water
Set potentiometers to mid-range values:
- pH: ~7.0 (middle position)
- Sulphate: ~250 mg/L
- Hardness: ~165 mg/L
- Conductivity: ~500 µS/cm
- TDS: ~600 mg/L
- Turbidity: ~3.0 NTU

**Expected**: Green LED on, "Safe" prediction

### Scenario 2: Contaminated Water
Set any potentiometer outside safe range:
- pH: <6.5 or >8.5 (far left or far right)
- OR Turbidity: >5.0 (far right)

**Expected**: Red LED on, "Unsafe" prediction

### Scenario 3: Email Alert Trigger
1. Set potentiometers to create unsafe water
2. Enable Auto-Send
3. Wait for 5 consecutive unsafe predictions
4. Email alert will be sent
5. Red banner appears on dashboard

## Troubleshooting

### Wokwi Simulator Not Loading
- Check internet connection (Wokwi loads from CDN)
- Try refreshing the page
- Clear browser cache

### Serial Monitor Empty
- Make sure simulation is started
- Check that baud rate is 115200
- Click "Restart" button in Wokwi

### Predictions Not Updating
- Verify WebSocket connection (check connection status badge)
- Ensure JSON format is correct
- Check browser console for errors (F12)

### Email Not Received
1. Check `config.py` for correct email settings
2. Verify SMTP credentials are configured
3. Check spam/junk folder
4. Look at server console for email sending logs

### Auto-Send Not Working
- Ensure valid JSON is in the textarea
- Check that WebSocket is connected
- Try manual send first to verify connection

## Advanced Usage

### Custom Wokwi Project

To use your own Wokwi project:
1. Create a new project at https://wokwi.com
2. Copy the firmware code from `firmware/water_quality_monitor.ino`
3. Copy the diagram from `firmware/diagram.json`
4. Get the project URL
5. Update the iframe src in `templates/index.html`

### Modifying Sensor Ranges

Edit `config.py` to change safe ranges:
```python
SAFE_RANGES = {
    'pH': {'min': 6.5, 'max': 8.5},
    # ... modify as needed
}
```

### Changing Email Alert Threshold

Edit `config.py`:
```python
CONSECUTIVE_CONTAMINATION_THRESHOLD = 5  # Change to desired number
```

## Tips & Best Practices

1. **Start with safe values** to verify system is working
2. **Use Auto-Send** for continuous monitoring
3. **Adjust one potentiometer at a time** to see individual parameter effects
4. **Monitor the consecutive counter** to track contamination streaks
5. **Check email spam folder** if alerts aren't received
6. **Reset the simulation** if values seem stuck

## Support

For issues or questions:
- Check server console logs
- Review browser console (F12)
- Verify all dependencies are installed
- Ensure `config.py` is properly configured

---

**Happy Monitoring! 🌊💧**
