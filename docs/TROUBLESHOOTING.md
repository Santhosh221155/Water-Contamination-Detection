# Troubleshooting Guide - Bridge Connection Issues

## Problem: Data Not Reaching ML Model

If you see data in Wokwi's Serial Monitor but the model isn't showing predictions, follow these steps:

### Quick Fixes

#### 1. **Use the Capture Button** (Easiest Method)
- Look for the **"📋 Capture Serial Data"** button in the bottom-right corner
- Click it to open a dialog
- Copy a JSON line from Wokwi Serial Monitor (e.g., `{"pH":7.2,"Sulphate":250,...}`)
- Paste it into the dialog and click "Send Data"
- The prediction should update immediately

#### 2. **Use Clipboard Paste**
- Copy a JSON line from Wokwi Serial Monitor
- Press `Ctrl+V` (or `Cmd+V` on Mac) anywhere on the page
- The system will automatically detect and send the data

#### 3. **Check Console for Errors**
- Open browser Developer Tools (F12)
- Go to the Console tab
- Look for error messages
- Check if WebSocket is connected (should see "✅ Socket connected")

### Debugging Steps

#### Step 1: Verify WebSocket Connection
1. Open browser console (F12)
2. Check for: `✅ Socket connected for serial capture`
3. If not connected, refresh the page

#### Step 2: Test the System
1. Open browser console (F12)
2. Run this command:
   ```javascript
   fetch('/api/test', {method: 'POST'})
     .then(r => r.json())
     .then(console.log)
   ```
3. This should trigger a test prediction and update the UI

#### Step 3: Check Backend Logs
Look at the terminal where `app.py` is running:
- Should see: `✅ Wokwi API monitoring service started`
- Should see: `📡 Starting to poll Wokwi API...`
- If API fails: `⚠️ Wokwi API not accessible. This is normal...`

#### Step 4: Manual Data Send
If automatic capture isn't working:

1. **Method A: Use Capture Button**
   - Click "📋 Capture Serial Data" button
   - Paste JSON data
   - Click "Send Data"

2. **Method B: Use Browser Console**
   ```javascript
   // In browser console (F12)
   socket.emit('wokwi_serial_data', {
     "pH": 7.2,
     "Sulphate": 250,
     "Hardness": 165,
     "Conductivity": 500,
     "TDS": 600,
     "Turbidity": 3.0,
     "is_safe": 1,
     "timestamp": "1234"
   });
   ```

### Common Issues

#### Issue 1: "Bridge: Connecting..." Never Changes
**Solution:**
- The API might not be accessible (this is normal)
- Use the manual capture button instead
- The frontend bridge will handle data capture

#### Issue 2: Data Visible in Wokwi But Not Reaching Backend
**Solution:**
- Wokwi API endpoint might require authentication
- Use the capture button to manually send data
- Or copy-paste JSON and use clipboard monitoring

#### Issue 3: WebSocket Not Connected
**Solution:**
- Check that Flask server is running
- Refresh the browser page
- Check browser console for connection errors
- Verify firewall isn't blocking WebSocket connections

#### Issue 4: Predictions Show "Waiting..."
**Solution:**
- Make sure Wokwi simulation is running (click play button)
- Use the capture button to send test data
- Check backend terminal for error messages

### Verification Checklist

- [ ] Flask server is running (`python app.py`)
- [ ] Browser shows "Connected" status (green dot)
- [ ] Wokwi simulation is running (play button clicked)
- [ ] Serial Monitor shows JSON output
- [ ] No errors in browser console (F12)
- [ ] No errors in backend terminal

### Testing the Complete Flow

1. **Start Server:**
   ```bash
   python app.py
   ```

2. **Open Browser:**
   ```
   http://localhost:5000
   ```

3. **Start Wokwi Simulation:**
   - Click play button in Wokwi iframe

4. **Send Test Data:**
   - Click "📋 Capture Serial Data" button
   - Paste this test JSON:
     ```json
     {"pH":7.2,"Sulphate":250,"Hardness":165,"Conductivity":500,"TDS":600,"Turbidity":3.0,"is_safe":1,"timestamp":"1234"}
     ```
   - Click "Send Data"

5. **Verify:**
   - Prediction should show "Safe" or "Unsafe"
   - LED indicators should light up
   - Sensor values should update
   - Statistics should increment

### Still Not Working?

1. **Check Backend Logs:**
   - Look for `📥 Received data via WebSocket` messages
   - Look for `📤 API→ML` messages
   - Check for error messages

2. **Check Frontend Console:**
   - Open F12 → Console
   - Look for `📡 Sending data to backend` messages
   - Check for WebSocket connection status

3. **Test WebSocket Directly:**
   ```javascript
   // In browser console
   socket.emit('wokwi_serial_data', {
     "pH": 7.2,
     "Sulphate": 250,
     "Hardness": 165,
     "Conductivity": 500,
     "TDS": 600,
     "Turbidity": 3.0
   });
   ```

4. **Check Model:**
   - Verify `tamilnadu_water_model.joblib` exists
   - Check backend logs for "✅ ML Model loaded"

---

**Remember:** The system has multiple fallback methods. If the API doesn't work, the frontend capture button will always work!

