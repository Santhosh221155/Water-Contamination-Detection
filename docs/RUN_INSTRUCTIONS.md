# How to Run the Water Quality Monitoring System

This guide will help you set up and run the Water Quality Monitoring System with Wokwi integration.

## Prerequisites

- Python 3.x installed
- Internet connection (for Wokwi simulator)

## Step 1: Install Dependencies

Open your terminal or command prompt in the project directory (`water` folder) and run:

```bash
pip install -r requirements.txt
```

## Step 2: Configure Email Alerts (Optional)

If you want to enable email alerts when water is detected as unsafe:

1.  Open `config.py`.
2.  Locate the `SENDER_EMAIL` and `SENDER_PASSWORD` variables.
3.  Replace the placeholder values with your Gmail credentials.
    *   **Note:** For Gmail, you must use an **App Password**, not your regular password. [Learn how to generate an App Password](https://support.google.com/accounts/answer/185833).

## Step 3: Run the Application

Start the Flask server by running:

```bash
python app.py
```

You should see output indicating the server is running on `http://localhost:5000`.

## Step 4: Use the Application

1.  Open your web browser and go to `http://localhost:5000`.
2.  **Start Simulation:** In the Wokwi simulator (left side), click the "Start Simulation" button (play icon).
3.  **Adjust Values:** Use the sliders/potentiometers in the simulator to change sensor values.
4.  **Send Data:**
    *   **Manual:** Copy the JSON output from the Wokwi Serial Monitor (bottom of simulator) and paste it into the "Serial Data Input" box on the right. Click "Send Data".
    *   **Auto-Send (Recommended):** Paste one valid JSON line into the input box and click "Enable Auto-Send". The system will now automatically update predictions every 2 seconds.

## Troubleshooting

-   **Missing Modules:** If you get an error like `ModuleNotFoundError`, ensure you ran Step 1 successfully.
-   **Port In Use:** If port 5000 is busy, you can change the `FLASK_PORT` in `config.py`.
