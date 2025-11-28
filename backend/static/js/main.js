/**
 * Main Dashboard JavaScript
 * Handles WebSocket communication and UI updates for the Water Quality Monitor
 */

// Initialize Socket.IO connection
const socket = io('http://localhost:5000');

// State management
let stats = {
    total: 0,
    safe: 0,
    unsafe: 0
};

// DOM Elements
let connectionStatus, bridgeStatus, predictionResult;
let consecutiveCount, totalSamples, accuracy, alertBanner;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Initializing Water Quality Dashboard...');
    initializeElements();
    setupSocketListeners();
});

/**
 * Initialize DOM element references
 */
function initializeElements() {
    // Status indicators
    connectionStatus = document.getElementById('connectionStatus');
    bridgeStatus = document.getElementById('bridgeStatus');

    // Prediction display
    predictionResult = document.getElementById('predictionResult');

    // Counters
    consecutiveCount = document.getElementById('consecutiveCount');
    totalSamples = document.getElementById('totalSamples');
    accuracy = document.getElementById('accuracy');

    // Alert banner
    alertBanner = document.getElementById('alertBanner');

    console.log('✅ DOM elements initialized');
}

/**
 * Setup WebSocket event listeners
 */
function setupSocketListeners() {
    socket.on('connect', () => {
        console.log('✅ Connected to server');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('❌ Disconnected from server');
        updateConnectionStatus(false);
    });

    socket.on('connection_status', (data) => {
        updateBridgeStatus('connected');
    });

    socket.on('bridge_status', (data) => {
        updateBridgeStatus(data.status);
    });

    socket.on('prediction_update', (data) => {
        console.log('📥 Received prediction update:', data);
        handlePredictionUpdate(data);
    });

    socket.on('email_alert_sent', (data) => {
        showAlertBanner();
    });
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.innerHTML = '<span class="status-dot"></span> Connected';
        connectionStatus.className = 'status-badge connected';
    } else {
        connectionStatus.innerHTML = '<span class="status-dot"></span> Disconnected';
        connectionStatus.className = 'status-badge disconnected';
    }
}

/**
 * Update bridge status indicator
 */
function updateBridgeStatus(status) {
    if (status === 'connected') {
        bridgeStatus.innerHTML = '<span class="status-dot"></span> Bridge: Active';
        bridgeStatus.className = 'status-badge bridge-badge connected';
    } else {
        bridgeStatus.innerHTML = '<span class="status-dot"></span> Bridge: Waiting...';
        bridgeStatus.className = 'status-badge bridge-badge disconnected';
    }
}

/**
 * Handle prediction update from backend
 */
function handlePredictionUpdate(data) {
    // Update prediction display
    updatePredictionDisplay(data);

    // Update sensor readings
    updateSensorReadings(data.sensor_data, data.thresholds);

    // Update statistics
    updateStatistics(data.prediction_value);

    // Update consecutive counter
    updateConsecutiveCounter(data.consecutive_count);
}

/**
 * Update prediction display
 */
function updatePredictionDisplay(data) {
    const isSafe = data.prediction === 'Safe';

    predictionResult.className = `prediction-display ${isSafe ? 'safe' : 'unsafe'}`;
    predictionResult.innerHTML = `
        <div class="pred-icon">${isSafe ? '🛡️' : '⚠️'}</div>
        <div class="pred-value">${data.prediction}</div>
        <div class="pred-conf">AI Confidence: ${data.confidence.toFixed(1)}%</div>
    `;
}

/**
 * Update sensor readings
 */
function updateSensorReadings(sensorData, thresholds) {
    Object.keys(sensorData).forEach(sensor => {
        if (sensor === 'timestamp') return;

        const value = sensorData[sensor];
        const threshold = thresholds?.[sensor];

        // Update value display
        const valueElement = document.getElementById(`sensor-${sensor}`);
        if (valueElement) {
            const decimals = (sensor === 'pH' || sensor === 'Turbidity') ? 1 : 0;
            valueElement.textContent = value.toFixed(decimals);
        }

        // Update status
        const statusElement = document.getElementById(`status-${sensor}`);
        const cardElement = document.querySelector(`[data-sensor="${sensor}"]`);

        if (threshold && statusElement && cardElement) {
            const isSafe = threshold.is_safe;

            // Update card class
            cardElement.className = `sensor-widget ${isSafe ? 'safe' : 'unsafe'}`;

            // Update status text
            statusElement.textContent = isSafe ? 'Normal' : 'Critical';
            statusElement.className = `sensor-status ${isSafe ? 'safe' : 'unsafe'}`;
        }
    });
}

/**
 * Update statistics
 */
function updateStatistics(predictionValue) {
    stats.total++;

    if (predictionValue === 1) {
        stats.safe++;
    } else {
        stats.unsafe++;
    }

    const safeRatio = stats.total > 0 ? (stats.safe / stats.total * 100) : 0;

    // Update displays
    totalSamples.textContent = stats.total;
    accuracy.textContent = `${safeRatio.toFixed(1)}%`;
}

/**
 * Update consecutive counter
 */
function updateConsecutiveCounter(count) {
    consecutiveCount.textContent = count;

    // Add warning styling if approaching threshold
    if (count >= 3) {
        consecutiveCount.style.color = 'var(--unsafe)';
    } else {
        consecutiveCount.style.color = 'var(--text-main)';
    }
}

/**
 * Show alert banner
 */
function showAlertBanner() {
    if (alertBanner) {
        alertBanner.style.display = 'block';
        alertBanner.classList.remove('hidden');

        // Auto-hide after 10 seconds
        setTimeout(() => {
            alertBanner.style.display = 'none';
            alertBanner.classList.add('hidden');
        }, 10000);
    }
}

/**
 * Cleanup on page unload
 */
window.addEventListener('beforeunload', () => {
    socket.disconnect();
});

console.log('✅ Main dashboard script loaded');
