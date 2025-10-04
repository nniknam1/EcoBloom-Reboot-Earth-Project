"""
Alert System Module
Handles notifications via Email, SMS (Twilio), and MQTT
"""
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AlertSystem:
    def __init__(self, config_path="config.json"):
        """Initialize alert system with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.email_config = self.config['alerts']['email']
        self.sms_config = self.config['alerts']['sms']
        self.mqtt_config = self.config['alerts']['mqtt']

        # Initialize clients
        self.twilio_client = None
        self.mqtt_client = None

        self._initialize_services()

    def _initialize_services(self):
        """Initialize external services if enabled"""
        # Twilio for SMS
        if self.sms_config['enabled']:
            try:
                from twilio.rest import Client
                self.twilio_client = Client(
                    self.sms_config['twilio_account_sid'],
                    self.sms_config['twilio_auth_token']
                )
                print("✅ Twilio SMS initialized")
            except ImportError:
                print("⚠️ Twilio not installed. Run: pip install twilio")
            except Exception as e:
                print(f"⚠️ Twilio initialization failed: {e}")

        # MQTT
        if self.mqtt_config['enabled']:
            try:
                import paho.mqtt.client as mqtt
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.connect(
                    self.mqtt_config['broker'],
                    self.mqtt_config['port'],
                    60
                )
                print("✅ MQTT client initialized")
            except ImportError:
                print("⚠️ Paho MQTT not installed. Run: pip install paho-mqtt")
            except Exception as e:
                print(f"⚠️ MQTT initialization failed: {e}")

    def send_email_alert(self, subject, body, detection_result=None):
        """Send email alert to farmer"""
        if not self.email_config['enabled']:
            print("⚠️ Email alerts disabled in config")
            return False

        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            msg['Subject'] = subject

            # Add body
            if detection_result:
                body += f"\n\n📊 Detection Details:\n"
                body += f"- Camera: {detection_result.get('camera_id', 'Unknown')}\n"
                body += f"- Location: {detection_result.get('location', {}).get('name', 'Unknown')}\n"
                body += f"- Pest Count: {detection_result.get('pest_count', 0)}\n"
                body += f"- Risk Level: {detection_result.get('risk_level', 'UNKNOWN')}\n"
                body += f"- Time: {detection_result.get('timestamp', datetime.now().isoformat())}\n"

            msg.attach(MIMEText(body, 'plain'))

            # Connect and send
            with smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(
                    self.email_config['sender_email'],
                    self.email_config['sender_password']
                )
                server.send_message(msg)

            print(f"✅ Email sent: {subject}")
            return True

        except Exception as e:
            print(f"❌ Email failed: {e}")
            return False

    def send_sms_alert(self, message, detection_result=None):
        """Send SMS alert via Twilio"""
        if not self.sms_config['enabled']:
            print("⚠️ SMS alerts disabled in config")
            return False

        if not self.twilio_client:
            print("❌ Twilio client not initialized")
            return False

        try:
            # Format message
            if detection_result:
                location = detection_result.get('location', {}).get('name', 'Unknown')
                pest_count = detection_result.get('pest_count', 0)
                risk = detection_result.get('risk_level', 'UNKNOWN')
                message = f"🚨 {risk} RISK at {location}: {pest_count} pests detected!"

            # Send SMS
            sms = self.twilio_client.messages.create(
                body=message,
                from_=self.sms_config['twilio_phone'],
                to=self.sms_config['recipient_phone']
            )

            print(f"✅ SMS sent: {sms.sid}")
            return True

        except Exception as e:
            print(f"❌ SMS failed: {e}")
            return False

    def publish_mqtt(self, topic=None, payload=None, detection_result=None):
        """Publish pest detection data to MQTT broker"""
        if not self.mqtt_config['enabled']:
            print("⚠️ MQTT disabled in config")
            return False

        if not self.mqtt_client:
            print("❌ MQTT client not initialized")
            return False

        try:
            # Use default topic if not provided
            if topic is None:
                topic = self.mqtt_config['topic']

            # Create payload from detection result
            if payload is None and detection_result:
                payload = {
                    "camera_id": detection_result.get('camera_id'),
                    "location": detection_result.get('location', {}).get('name'),
                    "pest_count": detection_result.get('pest_count'),
                    "risk_level": detection_result.get('risk_level'),
                    "timestamp": detection_result.get('timestamp')
                }
                payload = json.dumps(payload)

            # Publish
            result = self.mqtt_client.publish(topic, payload)

            if result.rc == 0:
                print(f"✅ MQTT published to {topic}")
                return True
            else:
                print(f"❌ MQTT publish failed: {result.rc}")
                return False

        except Exception as e:
            print(f"❌ MQTT error: {e}")
            return False

    def send_alert(self, detection_result):
        """
        Send alerts based on risk level and configured channels
        Main function to call after detection
        """
        risk_level = detection_result.get('risk_level', 'UNKNOWN')
        camera_id = detection_result.get('camera_id', 'Unknown')
        location = detection_result.get('location', {}).get('name', 'Unknown')
        pest_count = detection_result.get('pest_count', 0)

        print(f"\n🔔 Processing alerts for {risk_level} risk detection...")

        # Only send alerts for MEDIUM and HIGH risk
        if risk_level not in ['MEDIUM', 'HIGH']:
            print("ℹ️ Risk level is LOW, skipping alerts")
            return

        # Email alert
        if self.email_config['enabled']:
            subject = f"🚨 Pest Alert: {risk_level} Risk at {location}"
            body = f"""
Pest Detection Alert

A {risk_level} risk level has been detected at your farm.

Details:
- Camera: {camera_id}
- Location: {location}
- Pest Count: {pest_count}
- Time: {detection_result.get('timestamp', 'Unknown')}

Please check your traps and consider taking appropriate action.

---
EcoBloom Pest Detection System
            """
            self.send_email_alert(subject, body.strip(), detection_result)

        # SMS alert (for HIGH risk only)
        if self.sms_config['enabled'] and risk_level == 'HIGH':
            self.send_sms_alert("", detection_result)

        # MQTT (for all alerts)
        if self.mqtt_config['enabled']:
            self.publish_mqtt(detection_result=detection_result)

    def send_daily_summary(self, statistics):
        """Send daily summary report"""
        if not self.email_config['enabled']:
            return False

        subject = "📊 Daily Pest Activity Summary"
        body = f"""
Daily Pest Detection Summary

Period: Last 24 hours

Statistics:
- Total Captures: {statistics.get('total_captures', 0)}
- Total Pests Detected: {statistics.get('total_pests', 0)}
- Average Pests per Capture: {statistics.get('avg_pests', 0):.2f}
- Maximum Pests in Single Capture: {statistics.get('max_pests', 0)}

---
EcoBloom Pest Detection System
        """

        return self.send_email_alert(subject, body.strip())

    def test_alerts(self):
        """Test all configured alert channels"""
        print("\n🧪 Testing Alert Channels...")

        test_result = {
            "camera_id": "CAM001",
            "location": {"name": "Test Location"},
            "pest_count": 10,
            "risk_level": "HIGH",
            "timestamp": datetime.now().isoformat()
        }

        # Test email
        if self.email_config['enabled']:
            self.send_email_alert(
                "🧪 Test Alert - EcoBloom",
                "This is a test alert from the EcoBloom pest detection system.",
                test_result
            )

        # Test SMS
        if self.sms_config['enabled']:
            self.send_sms_alert("Test alert from EcoBloom", test_result)

        # Test MQTT
        if self.mqtt_config['enabled']:
            self.publish_mqtt(detection_result=test_result)

        print("\n✅ Alert test complete")

# Test function
if __name__ == "__main__":
    print("🌱 Testing Alert System")

    alert_system = AlertSystem("../config.json")

    # Test with sample detection
    test_detection = {
        "timestamp": datetime.now().isoformat(),
        "camera_id": "CAM001",
        "location": {
            "name": "North Field - Zone A",
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "pest_count": 8,
        "risk_level": "HIGH"
    }

    # Send alert
    alert_system.send_alert(test_detection)
