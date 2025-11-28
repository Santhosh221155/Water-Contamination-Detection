"""
Email Alert Service for Water Quality Monitoring
Sends alerts when water is contaminated for 5 consecutive readings
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailAlertService:
    def __init__(self, smtp_server, smtp_port, sender_email, sender_password, recipient_email):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipient_email = recipient_email
        
    def send_contamination_alert(self, sensor_data, consecutive_count):
        """
        Send email alert for water contamination
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = '⚠️ URGENT: Water Contamination Alert - Tamil Nadu Water Quality Monitor'
            msg['From'] = self.sender_email
            msg['To'] = self.recipient_email
            
            # Create HTML email body
            html_body = self._create_html_email(sensor_data, consecutive_count)
            
            # Attach HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            print(f"✅ Alert email sent to {self.recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False
    
    def _create_html_email(self, sensor_data, consecutive_count):
        """
        Create HTML email template
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    overflow: hidden;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
                    color: white;
                    padding: 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 24px;
                }}
                .alert-icon {{
                    font-size: 48px;
                    margin-bottom: 10px;
                }}
                .content {{
                    padding: 30px;
                }}
                .alert-box {{
                    background-color: #fff3cd;
                    border-left: 4px solid #ff6a00;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .sensor-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .sensor-table th {{
                    background-color: #f8f9fa;
                    padding: 12px;
                    text-align: left;
                    border-bottom: 2px solid #dee2e6;
                }}
                .sensor-table td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #dee2e6;
                }}
                .unsafe {{
                    color: #dc3545;
                    font-weight: bold;
                }}
                .safe {{
                    color: #28a745;
                }}
                .footer {{
                    background-color: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    font-size: 12px;
                    color: #6c757d;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="alert-icon">⚠️</div>
                    <h1>Water Contamination Alert</h1>
                    <p>Tamil Nadu Water Quality Monitoring System</p>
                </div>
                
                <div class="content">
                    <div class="alert-box">
                        <strong>URGENT ALERT:</strong> Water has been detected as <strong>CONTAMINATED</strong> 
                        for <strong>{consecutive_count} consecutive readings</strong>.
                    </div>
                    
                    <p><strong>Detection Time:</strong> {timestamp}</p>
                    
                    <h3>Current Sensor Readings:</h3>
                    <table class="sensor-table">
                        <thead>
                            <tr>
                                <th>Parameter</th>
                                <th>Current Value</th>
                                <th>Safe Range</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>pH Level</td>
                                <td>{sensor_data.get('pH', 'N/A')}</td>
                                <td>6.5 - 8.5</td>
                                <td class="{'safe' if 6.5 <= sensor_data.get('pH', 0) <= 8.5 else 'unsafe'}">
                                    {'✓ Safe' if 6.5 <= sensor_data.get('pH', 0) <= 8.5 else '✗ Unsafe'}
                                </td>
                            </tr>
                            <tr>
                                <td>Sulphate</td>
                                <td>{sensor_data.get('Sulphate', 'N/A')} mg/L</td>
                                <td>100 - 400 mg/L</td>
                                <td class="{'safe' if 100 <= sensor_data.get('Sulphate', 0) <= 400 else 'unsafe'}">
                                    {'✓ Safe' if 100 <= sensor_data.get('Sulphate', 0) <= 400 else '✗ Unsafe'}
                                </td>
                            </tr>
                            <tr>
                                <td>Hardness</td>
                                <td>{sensor_data.get('Hardness', 'N/A')} mg/L</td>
                                <td>80 - 250 mg/L</td>
                                <td class="{'safe' if 80 <= sensor_data.get('Hardness', 0) <= 250 else 'unsafe'}">
                                    {'✓ Safe' if 80 <= sensor_data.get('Hardness', 0) <= 250 else '✗ Unsafe'}
                                </td>
                            </tr>
                            <tr>
                                <td>Conductivity</td>
                                <td>{sensor_data.get('Conductivity', 'N/A')} µS/cm</td>
                                <td>200 - 800 µS/cm</td>
                                <td class="{'safe' if 200 <= sensor_data.get('Conductivity', 0) <= 800 else 'unsafe'}">
                                    {'✓ Safe' if 200 <= sensor_data.get('Conductivity', 0) <= 800 else '✗ Unsafe'}
                                </td>
                            </tr>
                            <tr>
                                <td>TDS</td>
                                <td>{sensor_data.get('TDS', 'N/A')} mg/L</td>
                                <td>200 - 1000 mg/L</td>
                                <td class="{'safe' if 200 <= sensor_data.get('TDS', 0) <= 1000 else 'unsafe'}">
                                    {'✓ Safe' if 200 <= sensor_data.get('TDS', 0) <= 1000 else '✗ Unsafe'}
                                </td>
                            </tr>
                            <tr>
                                <td>Turbidity</td>
                                <td>{sensor_data.get('Turbidity', 'N/A')} NTU</td>
                                <td>1.5 - 5.0 NTU</td>
                                <td class="{'safe' if 1.5 <= sensor_data.get('Turbidity', 0) <= 5.0 else 'unsafe'}">
                                    {'✓ Safe' if 1.5 <= sensor_data.get('Turbidity', 0) <= 5.0 else '✗ Unsafe'}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <h3>Recommended Actions:</h3>
                    <ul>
                        <li>Immediately stop water consumption from this source</li>
                        <li>Conduct detailed water quality testing</li>
                        <li>Identify and address contamination source</li>
                        <li>Notify local water authorities</li>
                        <li>Consider alternative water sources</li>
                    </ul>
                </div>
                
                <div class="footer">
                    <p>This is an automated alert from Tamil Nadu Water Quality Monitoring System</p>
                    <p>For support, please contact your system administrator</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html

# Test function
if __name__ == "__main__":
    # Example usage (configure with actual credentials)
    print("Email service module loaded successfully")
    print("Configure SMTP settings in config.py before use")
