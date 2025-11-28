# Wokwi REST API Integration Guide

This project now uses the **official Wokwi REST API** to connect the simulator to the ML model. No Selenium or browser automation is required!

## How It Works

The system uses the Wokwi REST API endpoint:
```
GET https://api.wokwi.com/v1/projects/<PROJECT_ID>/logs
```

### Data Flow

```
Wokwi Simulator (ESP32)
    ↓
Serial Output (JSON every 1 second)
    ↓
Wokwi API Endpoint
    ↓
wokwi_api_service.py (Polls API every 1 second)
    ↓
Extracts JSON sensor data from logs
    ↓
POST to Flask /api/predict
    ↓
ML Model Prediction
    ↓
WebSocket Broadcast
    ↓
Frontend UI Updates
```

## Configuration

### 1. Project ID

The Wokwi project ID is already configured in `config.py`:
```python
WOKWI_PROJECT_ID = "448703663779075073"
```

To use a different project:
1. Get your project ID from the Wokwi URL: `https://wokwi.com/projects/<PROJECT_ID>`
2. Update `WOKWI_PROJECT_ID` in `config.py`

### 2. API Key (Optional)

Most Wokwi API endpoints work without authentication, but if you need an API key:

1. Go to https://wokwi.com/account/api-keys
2. Generate an API key
3. Set it as an environment variable:
   ```bash
   # Windows
   setx WOKWI_API_KEY "your-api-key-here"
   
   # Linux/Mac
   export WOKWI_API_KEY="your-api-key-here"
   ```

Or add it directly to `config.py`:
```python
WOKWI_API_KEY = "your-api-key-here"
```

### 3. Polling Interval

Adjust how often the API is polled (default: 1 second):
```python
WOKWI_POLL_INTERVAL = 1.0  # seconds
```

## Running the System

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. The API monitoring service starts automatically in the background.

3. **Open your browser:**
   ```
   http://localhost:5000
   ```

4. **Start the Wokwi simulation** (click play button in the embedded simulator)

5. **Watch the predictions update automatically!**

## API Service Features

- ✅ **No Selenium required** - Pure REST API calls
- ✅ **Automatic polling** - Fetches logs every 1 second
- ✅ **Smart parsing** - Extracts JSON sensor data from various log formats
- ✅ **Error handling** - Handles API errors gracefully
- ✅ **Duplicate prevention** - Tracks processed logs to avoid duplicates
- ✅ **Automatic retry** - Continues monitoring even if API is temporarily unavailable

## Troubleshooting

### API Returns 404

- Check that `WOKWI_PROJECT_ID` in `config.py` matches your Wokwi project
- Verify the project exists at: `https://wokwi.com/projects/<PROJECT_ID>`

### API Returns 401/403

- The project may be private - make it public or add an API key
- Check if `WOKWI_API_KEY` is set correctly

### No Data Received

- Make sure the Wokwi simulation is **running** (click play button)
- Check that the ESP32 firmware is outputting JSON to Serial Monitor
- Verify the JSON format matches expected structure:
  ```json
  {"pH":7.2,"Sulphate":250,"Hardness":165,"Conductivity":500,"TDS":600,"Turbidity":3.0,"is_safe":1,"timestamp":"5234"}
  ```

### API Timeout Errors

- Check your internet connection
- The Wokwi API may be temporarily unavailable
- The service will automatically retry

## API Response Format

The service handles multiple response formats:

1. **JSON object with logs array:**
   ```json
   {
     "logs": [
       {"message": "{\"pH\":7.2,...}"},
       ...
     ]
   }
   ```

2. **JSON object with data array:**
   ```json
   {
     "data": [
       {"text": "{\"pH\":7.2,...}"},
       ...
     ]
   }
   ```

3. **Raw text response:**
   ```
   {"pH":7.2,"Sulphate":250,...}
   {"pH":7.3,"Sulphate":251,...}
   ```

The service automatically extracts JSON sensor data from any of these formats.

## Manual Testing

Test the API connection manually:

```python
import requests

project_id = "448703663779075073"
url = f"https://api.wokwi.com/v1/projects/{project_id}/logs"

response = requests.get(url)
print(response.status_code)
print(response.json())
```

## Benefits Over Selenium

- ✅ **Faster** - Direct API calls, no browser overhead
- ✅ **More reliable** - No browser automation failures
- ✅ **Lower resource usage** - No headless browser running
- ✅ **Easier to deploy** - No need for Chrome/Edge drivers
- ✅ **Official method** - Uses Wokwi's supported API

---

**Note:** The old Selenium-based service (`wokwi_monitor_service.py`) is still available but not used by default. The new API service (`wokwi_api_service.py`) is the primary method.

