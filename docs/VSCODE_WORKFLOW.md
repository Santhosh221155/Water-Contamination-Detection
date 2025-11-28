# VS Code Wokwi Workflow Guide

## 🎯 Overview

This system uses **Wokwi VS Code extension** for simulation with a **Python serial bridge** to connect to the Flask backend. The web dashboard displays only predictions and sensor telemetry (no embedded simulator).

## 📋 Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Wokwi VS Code  │ Serial  │  Python Bridge   │ WebSocket│  Flask Backend  │
│   Extension     ├────────►│ serial_bridge.py ├─────────►│     app.py      │
└─────────────────┘         └──────────────────┘         └────────┬────────┘
                                                                    │
                                                                    ▼
                                                            ┌───────────────┐
                                                            │   ML Model    │
                                                            └───────┬───────┘
                                                                    │
                                                                    ▼
                                                            ┌───────────────┐
                                                            │  Web Dashboard│
                                                            └───────────────┘
```

## 🚀 Quick Start

### Step 1: Install Wokwi VS Code Extension

1. Open **VS Code**
2. Press `Ctrl+Shift+X` (Extensions)
3. Search: **"Wokwi Simulator"**
4. Click **Install**

**Extension Link:** https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode

### Step 2: Install Python Dependencies

```bash
cd water
pip install -r requirements.txt
```

This installs:
- `pyserial` - For serial communication
- `python-socketio[client]` - For WebSocket client in bridge
- All other project dependencies

### Step 3: Start the System

**Terminal 1 - Flask Backend:**
```bash
python app.py
```

You should see:
```
🌊 Water Quality Monitoring Server - VS Code Wokwi Integration
✅ ML Model: tamilnadu_water_model.joblib
🌐 Server: http://localhost:5000
```

**Terminal 2 - Serial Bridge:**

1. **Click** on potentiometer knobs in the Wokwi simulator
2. **Drag** in circular motion to change values
3. **Watch** serial monitor for JSON output
4. **See** predictions update on web dashboard

### Monitoring Data Flow

**Serial Monitor (VS Code):**
```json
{"pH":7.2,"Sulphate":250,"Hardness":165,"Conductivity":500,"TDS":600,"Turbidity":3.5,"is_safe":1,"timestamp":"12345"}
```

**Bridge Console:**
```
📤 Sent: pH=7.2, TDS=600, Prediction=Safe
```

**Flask Console:**
```
📥 Received data from bridge: {'pH': 7.2, ...}
✅ Prediction: Safe (95.50% confidence)
```

**Web Dashboard:**
- AI Prediction: **Safe** (95.5% confidence)
- Green LED lights up
- Sensor values update
- Telemetry shows all parameters

## 🔧 Configuration

### Serial Port Configuration

Edit `config.py`:

```python
# Serial Communication (for Wokwi bridge)
SERIAL_PORT = "COM3"  # Windows
# SERIAL_PORT = "/dev/ttyUSB0"  # Linux
# SERIAL_PORT = "/dev/cu.usbserial"  # Mac
SERIAL_BAUD_RATE = 115200
```

### Finding the Correct Serial Port

**Windows:**
```powershell
# List all COM ports
mode
```

**Linux/Mac:**
```bash
# List all serial ports
ls /dev/tty*
```

**In VS Code:**
- Check the Wokwi serial monitor title bar
- It shows the port being used

### Auto-Detection

The bridge script attempts to auto-detect the Wokwi port. If it fails, it falls back to `config.SERIAL_PORT`.

## 📊 Dashboard Features

### Setup Instructions Card

The dashboard now shows setup instructions instead of the Wokwi iframe:

1. **Step-by-step guide** to start Wokwi in VS Code
2. **Instructions** to run the serial bridge
3. **Status checklist** showing system components
4. **Help links** to documentation

### Real-Time Predictions

- **AI Prediction** panel with confidence score
- **LED indicators** (Green = Safe, Red = Unsafe)
- **Contamination streak** counter
- **Statistics** (total samples, safe ratio)

### Sensor Telemetry

- **6 sensor widgets** with real-time values
- **Status indicators** (✅ Safe / ⚠️ Unsafe)
- **Safe ranges** displayed for each parameter

## 🐛 Troubleshooting

### Bridge Can't Connect to Serial Port

**Error:**
```
❌ Failed to connect to socket://localhost:4000: ...
```

**Solutions:**
1. **Restart Wokwi Simulation:** Stop and start the simulation to apply `wokwi.toml` changes.
2. **Check wokwi.toml:** Ensure it has the `[serial]` section with `rfc2217://localhost:4000`.
3. **Check Port 4000:** Ensure no other application is using port 4000.

### Bridge Can't Connect to Flask

**Error:**
```
❌ Failed to connect to Flask backend: Connection refused
```

**Solutions:**
1. Make sure Flask is running (`python app.py`)
2. Check Flask is on port 5000
3. Verify firewall settings

### No Data Appearing on Dashboard

**Symptoms:**
- Dashboard shows "Waiting..."
- Bridge status: "Disconnected"

**Solutions:**
1. Check all three components are running:
   - Wokwi in VS Code ✅
   - `serial_bridge.py` ✅
   - `python app.py` ✅
2. Check bridge console for errors
3. Verify serial data in VS Code serial monitor
4. Refresh the browser

### Serial Data Format Issues

**Error in bridge:**
```
❌ Error processing data: KeyError: 'pH'
```

**Solutions:**
1. Verify firmware is outputting correct JSON format
2. Check serial monitor shows valid JSON
3. Ensure all required fields are present:
   - pH, Sulphate, Hardness, Conductivity, TDS, Turbidity

## 🔄 Workflow Comparison

### Old Workflow (Browser-Based)
```
Browser → Wokwi Iframe → postMessage → JavaScript → WebSocket → Flask
```
- ✅ Simple (no extra scripts)
- ❌ Wokwi embedded in browser
- ❌ Limited debugging

### New Workflow (VS Code-Based)
```
VS Code Wokwi → Serial → Bridge Script → WebSocket → Flask
```
- ✅ Professional development environment
- ✅ Better debugging (VS Code tools)
- ✅ Cleaner dashboard (no iframe)
- ✅ Easier firmware development
- ⚠️ Requires serial bridge script

## 📚 Additional Resources

### Documentation Files

- **VSCODE_WOKWI_SETUP.md** - VS Code extension installation
- **WOKWI_QUICK_REFERENCE.md** - Quick reference card
- **implementation_plan.md** - Technical implementation details

### External Links

- [Wokwi VS Code Extension](https://marketplace.visualstudio.com/items?itemName=wokwi.wokwi-vscode)
- [Wokwi Documentation](https://docs.wokwi.com/vscode/getting-started)
- [ESP32 Arduino Reference](https://docs.espressif.com/projects/arduino-esp32/en/latest/)

## 💡 Tips & Best Practices

### Development Workflow

1. **Edit firmware** in VS Code
2. **Test with Wokwi** extension (F1 → Start Simulator)
3. **Verify serial output** in serial monitor
4. **Run bridge** to connect to backend
5. **Check dashboard** for predictions
6. **Iterate** as needed

### Debugging Tips

- **Check bridge console** for data flow
- **Monitor Flask console** for predictions
- **Use VS Code serial monitor** to verify JSON format
- **Inspect browser console** (F12) for WebSocket errors

### Performance

- Bridge adds minimal latency (< 100ms)
- Serial communication is fast (115200 baud)
- WebSocket provides real-time updates
- Dashboard updates instantly

## 🎓 Learning Resources

### Understanding the System

1. **Serial Communication** - How ESP32 sends data via UART
2. **JSON Format** - Structured data exchange
3. **WebSocket** - Real-time bidirectional communication
4. **Machine Learning** - Random Forest classification

### Extending the System

- Add more sensors to the simulation
- Implement data logging to database
- Create historical charts
- Add email/SMS alerts
- Deploy to cloud (AWS, Azure, GCP)

---

**Happy Monitoring! 🌊💧**
