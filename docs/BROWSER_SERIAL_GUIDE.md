# Browser-Based Serial Capture Guide

## Overview

This system now uses **browser-based serial monitoring** to capture data from the embedded Wokwi simulator. This is a cleaner, simpler approach that eliminates the need for external services, API tokens, and complex Python threading.

## How It Works

```
┌─────────────┐         ┌──────────────┐         ┌──────────────┐
│   Wokwi     │ postMsg │  JavaScript  │ WebSock │    Flask     │
│   Iframe    ├────────►│   main.js    ├────────►│   Backend    │
└─────────────┘         └──────────────┘         └──────────────┘
                                                          │
                                                          ▼
                                                   ┌──────────────┐
                                                   │   ML Model   │
                                                   └──────────────┘
```

**Data Flow:**
1. User adjusts potentiometers in Wokwi iframe
2. ESP32 firmware outputs JSON to serial monitor
3. Wokwi iframe sends serial data via `postMessage` API
4. `main.js` captures the message and extracts sensor data
5. Data sent to Flask backend via WebSocket
6. Flask processes data through ML model
7. Prediction results broadcast back to all connected clients
8. UI updates in real-time

## Quick Start

### 1. Start the Server

```bash
python app.py
```

You should see:
```
🌊 Water Quality Monitoring Server - Wokwi Integration
📖 Browser-Based Serial Capture:
   ✅ No API tokens or external services required!
```

### 2. Open the Dashboard

Navigate to: `http://localhost:5000`

### 3. Start the Simulation

- In the embedded Wokwi simulator, click the **green "Start Simulation" button**
- The ESP32 will boot up and start reading sensors

### 4. Adjust Sensors

- Click and drag the potentiometer knobs to simulate different sensor values
- Data automatically flows to the ML model
- Predictions appear in real-time on the right panel

### 5. Monitor Results

Watch for:
- **Connection Status**: Should show "Connected" (green)
- **Bridge Status**: Should show "Bridge: Active" (green) when data is flowing
- **AI Prediction**: Updates with each sensor reading
- **LED Indicators**: Green (Safe) or Red (Unsafe)
- **Sensor Telemetry**: Real-time values with threshold indicators

## Advantages Over Python Client Method

| Feature | Browser-Based | Python Client |
|---------|--------------|---------------|
| **Setup Complexity** | ✅ Simple | ❌ Complex |
| **API Token Required** | ✅ No | ❌ Yes |
| **External Services** | ✅ None | ❌ Wokwi API |
| **Threading** | ✅ None | ❌ Async threads |
| **Connection Issues** | ✅ Rare | ❌ Common |
| **Real-time** | ✅ Instant | ⚠️ Polling |

## Troubleshooting

### Bridge Status Shows "Waiting..."

**Cause:** No data is being received from Wokwi iframe

**Solutions:**
1. Make sure the Wokwi simulation is **started** (green play button)
2. Check browser console (F12) for errors
3. Verify the iframe loaded correctly
4. Try refreshing the page

### No Predictions Appearing

**Cause:** WebSocket not connected or data not flowing

**Solutions:**
1. Check "Connection Status" badge - should be green
2. Open browser console (F12) and look for:
   - `✅ Connected to server`
   - `✅ Wokwi iframe listener setup complete`
3. Restart the Flask server
4. Hard refresh the browser (Ctrl+Shift+R)

### Serial Data Not Captured

**Cause:** Wokwi iframe postMessage may have CORS restrictions

**Solutions:**
1. Check browser console for CORS errors
2. Try the **Python Client Library** as fallback:
   ```bash
   python wokwi_client_service.py
   ```
3. Or use manual copy-paste method (see README_WOKWI.md)

### Browser Console Errors

**Common errors and fixes:**

- `Failed to load resource: net::ERR_CONNECTION_REFUSED`
  - Flask server not running - start with `python app.py`

- `Socket.io connection error`
  - Check firewall settings
  - Verify port 5000 is not blocked

- `Refused to display in a frame because it set 'X-Frame-Options'`
  - This is normal for some Wokwi features
  - Serial data capture should still work

## Technical Details

### JavaScript Event Listener

The `main.js` file listens for `postMessage` events from the Wokwi iframe:

```javascript
window.addEventListener('message', (event) => {
    // Security: Verify origin
    if (event.origin !== 'https://wokwi.com') {
        return;
    }
    
    // Check if this is serial data
    if (event.data.type === 'serial' && event.data.data) {
        handleWokwiSerialData(event.data.data);
    }
});
```

### WebSocket Communication

Data is sent to the backend via Socket.IO:

```javascript
socket.emit('wokwi_serial_data', sensorData);
```

The backend receives it and processes:

```python
@socketio.on('wokwi_serial_data')
def handle_wokwi_data(data):
    prediction, confidence = predict_water_quality(data)
    emit('prediction_update', response, broadcast=True)
```

## Fallback to Python Client

If browser-based capture doesn't work, you can use the Python Client Library:

1. Edit `config.py`:
   ```python
   USE_BROWSER_SERIAL = False
   ```

2. Ensure you have a Wokwi CLI token:
   ```python
   WOKWI_CLI_TOKEN = "your-token-here"
   ```

3. Restart the server - it will auto-start the Python Client

## Comparison with Other Methods

### Method 1: Browser-Based (Current) ✅

- **Pros**: Simple, no tokens, real-time, no external services
- **Cons**: Depends on Wokwi iframe postMessage API
- **Best for**: Most users, production deployments

### Method 2: Python Client Library

- **Pros**: Official Wokwi API, reliable
- **Cons**: Requires token, complex setup, async threading
- **Best for**: Advanced users, when iframe method fails

### Method 3: Manual Copy-Paste

- **Pros**: Always works, no dependencies
- **Cons**: Manual, tedious, not real-time
- **Best for**: Testing, debugging, demos

## Support

If you encounter issues:

1. Check browser console (F12) for JavaScript errors
2. Check Flask server logs for backend errors
3. Verify Wokwi simulation is running
4. Try the Python Client fallback method
5. Review `TROUBLESHOOTING.md` for common issues

---

**Happy Monitoring! 🌊💧**
