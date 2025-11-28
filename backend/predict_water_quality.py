import serial
import json
import joblib
import pandas as pd
import numpy as np
import time
import sys
import os
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for colored console output
init(autoreset=True)

class TamilNaduWaterPredictor:
    def __init__(self, model_path, port='COM3', baudrate=115200):
        self.model_path = model_path
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.safe_count = 0
        self.unsafe_count = 0
        self.total_readings = 0
        
        # Load ML model
        self.load_model()
        
    def load_model(self):
        """Load the trained Tamil Nadu water quality model"""
        try:
            if not os.path.exists(self.model_path):
                print(Fore.RED + f"❌ Model file not found: {self.model_path}")
                print(Fore.YELLOW + "💡 Please ensure 'tamilnadu_water_model.joblib' is in the python_ml folder")
                sys.exit(1)
                
            self.model = joblib.load(self.model_path)
            print(Fore.GREEN + "✅ Tamil Nadu Water Quality Model Loaded Successfully!")
            print(Fore.CYAN + "📊 Model Features: pH, Sulphate, Hardness, Conductivity, TDS, Turbidity")
            print(Fore.CYAN + "🎯 Model Accuracy: 99.75% | Precision: 100% | Recall: 96.88%")
            
        except Exception as e:
            print(Fore.RED + f"❌ Model loading failed: {e}")
            sys.exit(1)
            
    def connect_serial(self):
        """Connect to ESP32 serial port"""
        # Try different ports based on operating system
        if sys.platform.startswith('win'):
            ports_to_try = ['COM3', 'COM4', 'COM5', 'COM6', 'COM7']
        else:
            ports_to_try = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyACM0', '/dev/ttyACM1']
        
        print(Fore.YELLOW + f"🔍 Searching for ESP32 on ports: {', '.join(ports_to_try)}")
        
        for port in ports_to_try:
            try:
                self.ser = serial.Serial(port, self.baudrate, timeout=2)
                time.sleep(2)  # Wait for connection to stabilize
                print(Fore.GREEN + f"✅ Connected to {port} at {self.baudrate} baud")
                return True
            except serial.SerialException:
                continue
            except Exception as e:
                print(Fore.YELLOW + f"⚠️  Error trying {port}: {e}")
                continue
                
        print(Fore.RED + "❌ Could not connect to any serial port")
        print(Fore.YELLOW + "💡 Please check:")
        print(Fore.YELLOW + "   - Wokwi simulation is running")
        print(Fore.YELLOW + "   - No other program is using the serial port")
        return False
    
    def validate_parameters(self, data):
        """Validate parameters against Tamil Nadu pond water ranges"""
        ranges = {
            'pH': (5.5, 8.8, ""),
            'Sulphate': (69, 496, "mg/L"),
            'Hardness': (66, 281, "mg/L"),
            'Conductivity': (152, 895, "µS/cm"),
            'TDS': (137, 1178, "mg/L"),
            'Turbidity': (1.3, 9.4, "NTU")
        }
        
        warnings = []
        for param, (min_val, max_val, unit) in ranges.items():
            value = data[param]
            if value < min_val or value > max_val:
                warnings.append(f"{param}: {value:.2f}{unit} (typical: {min_val}-{max_val}{unit})")
        
        if warnings:
            print(Fore.YELLOW + "⚠️  Parameter(s) outside typical Tamil Nadu ranges:")
            for warning in warnings:
                print(Fore.YELLOW + f"   - {warning}")
        
        return len(warnings) == 0
    
    def read_sensor_data(self):
        """Read and parse sensor data from ESP32"""
        if not self.ser or not self.ser.is_open:
            return None
            
        try:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if not line or not line.startswith("{"):
                return None
                
            data = json.loads(line)
            self.total_readings += 1
            return data
            
        except json.JSONDecodeError:
            return None
        except UnicodeDecodeError:
            return None
        except Exception as e:
            print(Fore.RED + f"❌ Error reading data: {e}")
            return None
    
    def predict_water_quality(self, data):
        """Predict water quality using Tamil Nadu model"""
        try:
            # Create DataFrame with exact feature names and order
            input_data = pd.DataFrame({
                'pH': [data['pH']],
                'Sulphate': [data['Sulphate']],
                'Hardness': [data['Hardness']],
                'Conductivity': [data['Conductivity']],
                'TDS': [data['TDS']],
                'Turbidity': [data['Turbidity']]
            })
            
            # Make prediction
            prediction = self.model.predict(input_data)[0]
            probability = self.model.predict_proba(input_data)[0]
            
            return prediction, probability
            
        except Exception as e:
            print(Fore.RED + f"❌ Prediction error: {e}")
            return None, None
    
    def display_results(self, data, prediction, probability):
        """Display beautifully formatted results"""
        # Determine status and colors
        if prediction == 1:
            status = "✅ SAFE FOR USE"
            status_color = Fore.GREEN + Style.BRIGHT
            led_color = "🟢"
            self.safe_count += 1
        else:
            status = "❌ UNSAFE - DO NOT USE"
            status_color = Fore.RED + Style.BRIGHT
            led_color = "🔴"
            self.unsafe_count += 1
        
        confidence = probability[1] if prediction == 1 else probability[0]
        confidence_color = Fore.GREEN if confidence > 0.7 else Fore.YELLOW if confidence > 0.5 else Fore.RED
        
        # Display header
        print("\n" + "="*60)
        print(Fore.CYAN + Style.BRIGHT + "🌊 TAMIL NADU POND WATER QUALITY ANALYSIS")
        print("="*60)
        
        # Status and confidence
        print(f"{status_color}{status} {led_color}")
        print(f"{Fore.WHITE}Confidence: {confidence_color}{confidence:.2%}")
        print(f"{Fore.WHITE}Reading #: {self.total_readings} | Safe: {Fore.GREEN}{self.safe_count} {Fore.WHITE}| Unsafe: {Fore.RED}{self.unsafe_count}")
        print(f"{Fore.WHITE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Sensor readings
        print("\n" + Fore.CYAN + "🔬 SENSOR READINGS (Tamil Nadu Ranges):")
        print(f"{Fore.WHITE}pH: {data['pH']:.2f} {Fore.YELLOW}(5.5-8.8)")
        print(f"{Fore.WHITE}Sulphate: {data['Sulphate']:.1f} mg/L {Fore.YELLOW}(69-496 mg/L)")
        print(f"{Fore.WHITE}Hardness: {data['Hardness']:.1f} mg/L {Fore.YELLOW}(66-281 mg/L)")
        print(f"{Fore.WHITE}Conductivity: {data['Conductivity']:.1f} µS/cm {Fore.YELLOW}(152-895 µS/cm)")
        print(f"{Fore.WHITE}TDS: {data['TDS']:.1f} mg/L {Fore.YELLOW}(137-1178 mg/L)")
        print(f"{Fore.WHITE}Turbidity: {data['Turbidity']:.2f} NTU {Fore.YELLOW}(1.3-9.4 NTU)")
        
        # Water quality assessment
        print("\n" + Fore.CYAN + "💧 WATER QUALITY ASSESSMENT:")
        self.assess_individual_parameters(data)
        
        print("="*60)
    
    def assess_individual_parameters(self, data):
        """Assess each parameter individually"""
        assessments = []
        
        # pH assessment
        if 6.5 <= data['pH'] <= 8.5:
            assessments.append(f"{Fore.GREEN}✓ pH: Optimal (6.5-8.5)")
        else:
            assessments.append(f"{Fore.RED}✗ pH: Outside optimal range")
        
        # Sulphate assessment
        if data['Sulphate'] <= 250:
            assessments.append(f"{Fore.GREEN}✓ Sulphate: Good")
        elif data['Sulphate'] <= 400:
            assessments.append(f"{Fore.YELLOW}⚠ Sulphate: Moderate")
        else:
            assessments.append(f"{Fore.RED}✗ Sulphate: High")
        
        # Turbidity assessment
        if data['Turbidity'] <= 5.0:
            assessments.append(f"{Fore.GREEN}✓ Turbidity: Clear")
        else:
            assessments.append(f"{Fore.RED}✗ Turbidity: Cloudy")
        
        for assessment in assessments:
            print(f"   {assessment}")
    
    def run(self):
        """Main prediction loop"""
        if not self.connect_serial():
            return
            
        print(Fore.GREEN + "\n🎯 Tamil Nadu Pond Water Monitoring Started!")
        print(Fore.YELLOW + "💡 Adjust potentiometers in Wokwi to simulate different water conditions")
        print(Fore.YELLOW + "📊 Typical Safe Ranges: pH(6.5-8.5), Sulphate(<250), Turbidity(<5.0)")
        print("-" * 60)
        
        consecutive_errors = 0
        max_errors = 5
        
        while True:
            try:
                data = self.read_sensor_data()
                if not data:
                    consecutive_errors += 1
                    if consecutive_errors >= max_errors:
                        print(Fore.YELLOW + "⚠️  No data received. Check Wokwi simulation...")
                        consecutive_errors = 0
                    time.sleep(1)
                    continue
                
                consecutive_errors = 0
                
                # Validate parameters
                self.validate_parameters(data)
                
                # Make prediction
                prediction, probability = self.predict_water_quality(data)
                
                if prediction is not None:
                    self.display_results(data, prediction, probability)
                
                time.sleep(2)  # Wait before next reading
                
            except KeyboardInterrupt:
                self.show_final_summary()
                break
            except Exception as e:
                print(Fore.RED + f"❌ Unexpected error: {e}")
                time.sleep(2)
                consecutive_errors += 1
                if consecutive_errors >= max_errors:
                    print(Fore.RED + "Too many errors. Restarting connection...")
                    break
        
        if self.ser and self.ser.is_open:
            self.ser.close()
    
    def show_final_summary(self):
        """Display final summary when stopping"""
        total = self.safe_count + self.unsafe_count
        if total > 0:
            safe_percentage = (self.safe_count / total) * 100
            print(Fore.CYAN + "\n" + "="*60)
            print(Fore.CYAN + Style.BRIGHT + "📈 MONITORING SESSION SUMMARY")
            print(Fore.CYAN + "="*60)
            print(f"{Fore.WHITE}Total Readings: {total}")
            print(f"{Fore.GREEN}Safe Samples: {self.safe_count} ({safe_percentage:.1f}%)")
            print(f"{Fore.RED}Unsafe Samples: {self.unsafe_count} ({100-safe_percentage:.1f}%)")
            print(Fore.CYAN + "="*60)
        print(Fore.YELLOW + "🛑 Monitoring stopped. Thank you for using Tamil Nadu Water Monitor!")

def main():
    """Main function"""
    print(Fore.CYAN + Style.BRIGHT + """
    🌊 TAMIL NADU POND WATER QUALITY MONITORING SYSTEM
    =================================================
    """)
    
    MODEL_PATH = "tamilnadu_water_model.joblib"
    
    try:
        predictor = TamilNaduWaterPredictor(MODEL_PATH)
        predictor.run()
    except Exception as e:
        print(Fore.RED + f"❌ Application error: {e}")
        print(Fore.YELLOW + "💡 Troubleshooting tips:")
        print(Fore.YELLOW + "   1. Check if model file exists in python_ml folder")
        print(Fore.YELLOW + "   2. Verify all Python dependencies are installed")
        print(Fore.YELLOW + "   3. Ensure Wokwi simulation is running")
        print(Fore.YELLOW + "   4. Check COM port configuration")

if __name__ == "__main__":
    main()