import serial
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

PORT = 'COM3'
BAUD = 9600
PHONE_EMAIL = '24243096@drngpit.ac.in'
SENDER_EMAIL = '24243096@drngpit.ac.in'
SENDER_PASSWORD = 'password'
THRESHOLD = 5000

# STATIC LOCATION
LATITUDE = 11.061380890168186
LONGITUDE = 77.03385564264705

class AccidentDashboard:
    def __init__(self):
        self.ser = None
        self.accident_detected = False
        self.last_x = 0
        self.last_y = 0
        self.last_z = 0
        self.alert_start_time = None
        
    def connect_arduino(self):
        try:
            self.ser = serial.Serial(PORT, BAUD, timeout=1)
            time.sleep(2)
            print("Connected to Arduino on COM3")
            return True
        except:
            print("ERROR: Could not connect")
            return False
    
    def send_email_alert(self, x, y, z):
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = PHONE_EMAIL
            msg['Subject'] = 'ACCIDENT DETECTED'
            
            body = f"""
ACCIDENT ALERT!

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Acceleration Values:
X: {x}
Y: {y}
Z: {z}

Location:
Latitude: {LATITUDE}
Longitude: {LONGITUDE}

Check immediately!
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            print("EMAIL SENT to 24243096@drngpit.ac.in")
            return True
        except Exception as e:
            print("ERROR sending email:", e)
            return False
    
    def run(self):
        if not self.connect_arduino():
            return
        
        print("Accident Detection System Started")
        print("Waiting for data...\n")
        
        while True:
            try:
                if self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8').strip()
                    
                    if not line:
                        continue
                    
                    if line.startswith('X:'):
                        try:
                            parts = line.split()
                            x_val = int(parts[0].split(':')[1])
                            y_val = int(parts[1].split(':')[1])
                            z_val = int(parts[2].split(':')[1])
                            
                            self.last_x = x_val
                            self.last_y = y_val
                            self.last_z = z_val
                            
                            print(f"X: {x_val}  Y: {y_val}  Z: {z_val}")
                        except:
                            pass
                    
                    elif "ACCIDENT_DETECTED" in line:
                        self.accident_detected = True
                        self.alert_start_time = time.time()
                        
                        print("\n" + "="*60)
                        print("ACCIDENT DETECTED!")
                        print("="*60)
                        print(f"X: {self.last_x}")
                        print(f"Y: {self.last_y}")
                        print(f"Z: {self.last_z}")
                        print(f"\nLocation:")
                        print(f"Latitude: {LATITUDE}")
                        print(f"Longitude: {LONGITUDE}")
                        print("\n" + "="*60)
                        print("IS THIS A REAL ACCIDENT?")
                        print("Type Y (Yes) or N (No):")
                        print("="*60)
                        
                        # Wait for user input with timeout
                        response = None
                        start_time = time.time()
                        timeout = 6  # 6 seconds timeout
                        
                        while time.time() - start_time < timeout:
                            try:
                                response = input("Your response: ").strip().upper()
                                break
                            except:
                                break
                        
                        if response == 'Y':
                            print("\n✓ Sending email with location...")
                            self.send_email_alert(self.last_x, self.last_y, self.last_z)
                            print("✓ Email sent! Alarm continues for 6 more seconds...")
                            
                            # Keep alarm running for 6 more seconds
                            remaining_time = 6
                            end_time = time.time() + remaining_time
                            
                            while time.time() < end_time:
                                elapsed = end_time - time.time()
                                print(f"  Alarm continues for {elapsed:.1f} seconds...")
                                time.sleep(0.5)
                            
                            print("✓ Alarm stopped")
                            self.accident_detected = False
                            
                        elif response == 'N':
                            print("\n✓ False alert cancelled - Alarm stopped immediately")
                            self.accident_detected = False
                        
                        else:
                            print("\n⚠ No response in 6 seconds - Alarm stopped")
                            self.accident_detected = False
                    
                    elif "ALERT_RESET" in line:
                        if self.accident_detected:
                            self.accident_detected = False
                
            except KeyboardInterrupt:
                print("\nClosing...")
                break
            except Exception as e:
                print(f"Error: {e}")
        
        if self.ser:
            self.ser.close()

if __name__ == "__main__":
    dashboard = AccidentDashboard()
    dashboard.run()