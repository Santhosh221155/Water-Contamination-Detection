# Wokwi Quick Reference

## 🚀 Start Simulation
1. Open `.ino` file
2. `F1` → **"Wokwi: Start Simulator"**

## 🌉 Start Bridge
```bash
python serial_bridge.py
```

## 🌐 Start Server
```bash
python app.py
```

## 📊 Dashboard
Open **http://localhost:5000**

## 🛑 Stop Simulation
`F1` → **"Wokwi: Stop Simulator"**

## 📝 Serial Monitor
- Opens automatically with simulation
- Shows JSON data: `{"pH": 7.2, ...}`

## 🔧 Key Files
- `firmware/water_quality_monitor.ino` - Arduino code
- `firmware/wokwi.toml` - Wokwi configuration
- `firmware/diagram.json` - Circuit diagram
- `serial_bridge.py` - Connects VS Code to Flask
