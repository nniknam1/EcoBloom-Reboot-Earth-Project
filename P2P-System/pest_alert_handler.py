"""
Pest Alert Handler - Extends your P2P system with pest-specific message types
Add this to your peer.py to handle pest alerts
"""

import time
import json
from message import Message


class PestAlertHandler:
    """
    Handles pest alert messages in the P2P network
    Integrates with your existing Peer class
    """
    
    def __init__(self, peer):
        self.peer = peer
        self.recent_alerts = []  # Store last 10 alerts
        self.alert_thresholds = {
            'LOW': 15,
            'MEDIUM': 30,
            'HIGH': 45
        }
    
    def calculate_risk_level(self, pest_count):
        """Calculate risk level based on pest count"""
        if pest_count >= self.alert_thresholds['HIGH']:
            return 'HIGH'
        elif pest_count >= self.alert_thresholds['MEDIUM']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def create_pest_alert(self, pest_count, pest_type='whitefly'):
        """
        Create a pest alert message to broadcast
        
        Args:
            pest_count: Number of pests detected
            pest_type: Type of pest (whitefly, thrips, leafminer)
        
        Returns:
            Message object ready to send via P2P
        """
        risk_level = self.calculate_risk_level(pest_count)
        
        alert_message = Message(
            peer_id=self.peer.peer_id,
            target_user_id=None,  # Broadcast to all peers
            message_type="PEST_ALERT",
            data={
                'pest_type': pest_type,
                'pest_count': pest_count,
                'risk_level': risk_level,
                'farm_id': self.peer.peer_id,
                'temperature': self._get_current_temp(),
                'humidity': self._get_current_humidity(),
                'alert_id': f"{self.peer.peer_id}_{int(time.time())}"
            },
            time_stamp=time.time()
        )
        
        return alert_message
    
    def broadcast_pest_alert(self, pest_count, pest_type='whitefly'):
        """
        Broadcast pest alert to all connected peers
        
        Returns:
            Number of peers alerted
        """
        alert_message = self.create_pest_alert(pest_count, pest_type)
        
        # Store in recent alerts
        self.recent_alerts.append({
            'message': alert_message,
            'timestamp': time.time(),
            'sent_to': []
        })
        
        # Keep only last 10 alerts
        if len(self.recent_alerts) > 10:
            self.recent_alerts.pop(0)
        
        # Send to all connected peers
        peers_alerted = 0
        for peer_id in self.peer.connections.keys():
            success = self.peer.send_message_to_peer(peer_id, alert_message)
            if success:
                peers_alerted += 1
                self.recent_alerts[-1]['sent_to'].append(peer_id)
        
        print(f"\n🚨 PEST ALERT BROADCAST")
        print(f"   Risk Level: {alert_message.data['risk_level']}")
        print(f"   Pest Count: {pest_count} {pest_type}s")
        print(f"   Alerted: {peers_alerted} nearby farms")
        print(f"   Message ID: {alert_message.message_id}\n")
        
        return peers_alerted
    
    def handle_received_alert(self, alert_message):
        """
        Process incoming pest alert from neighbor farm
        
        Args:
            alert_message: Message object with PEST_ALERT type
        """
        data = alert_message.data
        source_farm = alert_message.peer_id
        
        # Store the alert
        self.recent_alerts.append({
            'message': alert_message,
            'timestamp': time.time(),
            'received_from': source_farm
        })
        
        # Display alert to farmer
        print(f"\n⚠️  ALERT RECEIVED FROM {source_farm}")
        print(f"   Pest: {data['pest_count']} {data['pest_type']}s")
        print(f"   Risk Level: {data['risk_level']}")
        print(f"   Distance: ~{self._estimate_distance(source_farm)}km")
        print(f"   Recommendation: Check your traps immediately\n")
        
        # Auto-forward to other peers (mesh propagation)
        if alert_message.hop_count < 3:  # Limit hops to prevent loops
            self._forward_alert(alert_message)
    
    def _forward_alert(self, alert_message):
        """Forward received alert to other peers (mesh propagation)"""
        # Don't send back to source or previous hops
        exclude_peers = set(alert_message.path)
        
        forwarded_to = 0
        for peer_id in self.peer.connections.keys():
            if peer_id not in exclude_peers:
                # Create forwarded message
                forwarded_msg = Message(
                    peer_id=self.peer.peer_id,
                    target_user_id=peer_id,
                    message_type="PEST_ALERT",
                    data=alert_message.data,
                    time_stamp=time.time()
                )
                forwarded_msg.message_id = alert_message.message_id  # Keep same ID
                forwarded_msg.hop_count = alert_message.hop_count + 1
                forwarded_msg.path = alert_message.path + [self.peer.peer_id]
                
                self.peer.send_message_to_peer(peer_id, forwarded_msg)
                forwarded_to += 1
        
        if forwarded_to > 0:
            print(f"   ↪ Forwarded alert to {forwarded_to} other farms")
    
    def get_recommendations(self, risk_level):
        """
        Get actionable recommendations based on risk level
        """
        recommendations = {
            'LOW': [
                "Continue normal monitoring schedule",
                "Check sticky traps every 3 days",
                "Maintain good ventilation"
            ],
            'MEDIUM': [
                "Increase trap inspections to daily",
                "Prepare biological controls (ladybugs, lacewings)",
                "Monitor temperature and humidity closely",
                "Consider preventive neem oil application"
            ],
            'HIGH': [
                "IMMEDIATE ACTION REQUIRED",
                "Apply neem oil or insecticidal soap within 24 hours",
                "Remove heavily infested leaves and dispose properly",
                "Increase ventilation to reduce humidity below 60%",
                "Deploy sticky traps in high-density areas",
                "Check again in 48 hours to assess effectiveness",
                "Alert ministry extension officer if infestation persists"
            ]
        }
        
        return recommendations.get(risk_level, recommendations['LOW'])
    
    def _get_current_temp(self):
        """Get current temperature (mock for demo)"""
        # In production, this would read from DHT22 sensor
        import random
        return round(24 + random.random() * 6, 1)  # 24-30°C range
    
    def _get_current_humidity(self):
        """Get current humidity (mock for demo)"""
        # In production, this would read from DHT22 sensor
        import random
        return round(50 + random.random() * 20, 1)  # 50-70% range
    
    def _estimate_distance(self, peer_id):
        """Estimate distance to peer (mock for demo)"""
        # In production, would use GPS coordinates
        import random
        return round(random.uniform(0.5, 4.5), 1)
    
    def print_alert_summary(self):
        """Print summary of recent alerts"""
        print(f"\n{'='*60}")
        print(f"PEST ALERT SUMMARY - {self.peer.peer_id}")
        print(f"{'='*60}")
        
        if not self.recent_alerts:
            print("No recent alerts")
            return
        
        for i, alert_data in enumerate(self.recent_alerts[-5:], 1):
            msg = alert_data['message']
            data = msg.data
            
            if 'sent_to' in alert_data:
                print(f"\n[{i}] SENT ALERT")
                print(f"    Risk: {data['risk_level']}")
                print(f"    Pests: {data['pest_count']} {data['pest_type']}s")
                print(f"    Notified: {len(alert_data['sent_to'])} farms")
            else:
                print(f"\n[{i}] RECEIVED ALERT")
                print(f"    From: {alert_data['received_from']}")
                print(f"    Risk: {data['risk_level']}")
                print(f"    Pests: {data['pest_count']} {data['pest_type']}s")
        
        print(f"\n{'='*60}\n")


# Integration example - Add to your peer.py:
"""
class Peer:
    def __init__(self, host, port):
        # ... existing init code ...
        self.pest_handler = PestAlertHandler(self)
    
    def handle_message(self, message):
        # ... existing message handling ...
        
        if message.message_type == "PEST_ALERT":
            self.pest_handler.handle_received_alert(message)
        elif message.message_type == "MESSAGE":
            # Your existing message handling
            pass
"""