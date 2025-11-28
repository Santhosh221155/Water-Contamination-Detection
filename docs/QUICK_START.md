# Quick Start - Automatic Wokwi Data Capture

## ✅ Installation Complete!

The Wokwi Python Client Library is now installed and configured.

## 🚀 Setup (One-Time)

### Step 1: Get Your Wokwi API Token

1. Go to: **https://wokwi.com/dashboard/ci**
2. Copy your API token
3. Set it as environment variable:

**Windows:**
```cmd
setx WOKWI_CLI_TOKEN "your-token-here"
```

**Linux/Mac:**
```bash
export WOKWI_CLI_TOKEN="your-token-here"
```

**Or add directly to `config.py`:**
```python
WOKWI_CLI_TOKEN = "your-token-here"
```

### Step 2: Run the Application

```bash
python app.py
```

That's it! The system will:
- ✅ Automatically connect to Wokwi
- ✅ Start the simulation
- ✅ Capture serial data in real-time
- ✅ Send to ML model automatically
- ✅ Update UI automatically

**No manual steps needed!**

## 📊 How It Works

```
Wokwi Simulator
    ↓ (WebSocket connection)
Wokwi Python Client
    ↓ (Real-time serial stream)
ML Model Prediction
    ↓ (WebSocket broadcast)
Frontend UI Updates
```

## 🔍 Verify It's Working

1. Start the server: `python app.py`
2. Look for these messages:
   - `✅ Wokwi Client monitoring service started`
   - `✅ Connected to Wokwi`
   - `✅ Simulation started`
   - `📡 Monitoring serial output (automatic, real-time)...`
3. You should see: `📤 Auto→ML: Safe/Unsafe (confidence%) | pH:X.X`
4. Open browser: `http://localhost:5000`
5. Predictions should update automatically!

## ⚠️ Troubleshooting

### "WOKWI_CLI_TOKEN not set"
- Get token from: https://wokwi.com/dashboard/ci
- Set it as shown above

### "wokwi-client not installed"
- Run: `pip install wokwi-client`

### No data flowing
- Make sure Wokwi simulation is running
- Check that project ID is correct in `config.py`
- Verify token is valid

---

**That's it! The system is now fully automatic! 🎉**

