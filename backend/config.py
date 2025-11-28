"""
Configuration file for Water Quality Monitoring System
Contains email settings and alert thresholds
"""

import os

# Email Configuration
# IMPORTANT: For Gmail, you need to:
# 1. Enable 2-factor authentication
# 2. Generate an "App Password" at https://myaccount.google.com/apppasswords
# 3. Use the app password instead of your regular password

# Email Settings (Gmail SMTP)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Sender Email (Configure this with your Gmail account)
# IMPORTANT: Replace with your actual Gmail address
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "santhoshsanthosh40253@gmail.com")

# Sender Password (Use App Password for Gmail)
# IMPORTANT: Replace with your Gmail App Password
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "San@221155")

# Recipient Email (Alert destination)
RECIPIENT_EMAIL = "santhoshsanthosh40253@gmail.com"

# Alert Thresholds
CONSECUTIVE_CONTAMINATION_THRESHOLD = 5  # Number of consecutive contaminations before alert

# Tamil Nadu Water Quality Safe Ranges
SAFE_RANGES = {
    'pH': {'min': 6.5, 'max': 8.5},
    'Sulphate': {'min': 100, 'max': 400},
    'Hardness': {'min': 80, 'max': 250},
    'Conductivity': {'min': 200, 'max': 800},
    'TDS': {'min': 200, 'max': 1000},
    'Turbidity': {'min': 1.5, 'max': 5.0}
}

# Server Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
DEBUG_MODE = True

# Serial Communication (for Wokwi bridge)
SERIAL_PORT = "COM3"  # Adjust based on your system
SERIAL_BAUD_RATE = 115200

# WebSocket Configuration
WEBSOCKET_PING_INTERVAL = 25
WEBSOCKET_PING_TIMEOUT = 60

# Model Path
MODEL_PATH = "tamilnadu_water_model.joblib"

# Wokwi Configuration
# Get your project ID from the Wokwi project URL: https://wokwi.com/projects/<PROJECT_ID>
WOKWI_PROJECT_ID = "448703663779075073"  # Your Wokwi project ID

# Browser-Based Serial Capture (Set to False for VS Code Bridge workflow)
USE_BROWSER_SERIAL = False

# Bridge Configuration
BRIDGE_ENABLED = True
BRIDGE_HEARTBEAT_INTERVAL = 5.0  # Seconds
BRIDGE_RECONNECT_DELAY = 2.0     # Seconds

# Wokwi Python Client Token (OPTIONAL - only needed if USE_BROWSER_SERIAL = False)
# Get from: https://wokwi.com/dashboard/ci
# Set as environment variable: export WOKWI_CLI_TOKEN='your-token'
# Or add directly here:
WOKWI_CLI_TOKEN = os.getenv("WOKWI_CLI_TOKEN", "wok_zOZYNTBllcBKthrc9L5sjmkvGfzYCT0430916c2c")

# Optional: Wokwi REST API Key (for REST API method, not used with Client Library)
WOKWI_API_KEY = os.getenv("WOKWI_API_KEY", None)

# Polling interval for Wokwi REST API (in seconds) - not used with Client Library
WOKWI_POLL_INTERVAL = 1.0

# Instructions for Email Setup
"""
TO CONFIGURE EMAIL ALERTS:

1. Gmail Setup (Recommended):
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification
   - Go to https://myaccount.google.com/apppasswords
   - Generate an App Password for "Mail"
   - Copy the 16-character password
   - Set SENDER_EMAIL to your Gmail address
   - Set SENDER_PASSWORD to the app password

2. Environment Variables (More Secure):
   - Set environment variables instead of hardcoding:
     Windows: 
       setx SENDER_EMAIL "your-email@gmail.com"
       setx SENDER_PASSWORD "your-app-password"
     
     Linux/Mac:
       export SENDER_EMAIL="your-email@gmail.com"
       export SENDER_PASSWORD="your-app-password"

3. Alternative: SendGrid (if Gmail doesn't work):
   - Sign up at https://sendgrid.com
   - Get API key
   - Modify email_service.py to use SendGrid API
"""

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB_NAME = "water_quality_db"

# Validation
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    if SENDER_EMAIL == "your-email@gmail.com":
        errors.append("⚠️  SENDER_EMAIL not configured")
    
    if SENDER_PASSWORD == "your-app-password":
        errors.append("⚠️  SENDER_PASSWORD not configured")
    
    if errors:
        print("\n" + "="*60)
        print("⚠️  EMAIL CONFIGURATION REQUIRED")
        print("="*60)
        for error in errors:
            print(error)
        print("\nPlease edit config.py and set your email credentials.")
        print("See instructions in config.py for details.")
        print("="*60 + "\n")
        return False
    
    return True

if __name__ == "__main__":
    if validate_config():
        print("✅ Configuration validated successfully")
    else:
        print("❌ Configuration incomplete")
