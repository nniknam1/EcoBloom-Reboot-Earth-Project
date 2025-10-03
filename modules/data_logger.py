"""
Data Logger Module
Handles SQLite database operations for pest detection history
"""
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

class DataLogger:
    def __init__(self, config_path="config.json"):
        """Initialize database connection"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.db_path = Path(self.config['storage']['local_db_path'])
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = None
        self.cursor = None
        self._initialize_database()

    def _initialize_database(self):
        """Create database tables if they don't exist"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.cursor = self.conn.cursor()

        # Main detections table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                pest_count INTEGER NOT NULL,
                risk_level TEXT NOT NULL,
                image_path TEXT,
                output_path TEXT,
                detection_params TEXT,
                pest_details TEXT
            )
        ''')

        # Camera status table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS camera_status (
                camera_id TEXT PRIMARY KEY,
                location_name TEXT,
                latitude REAL,
                longitude REAL,
                last_capture TEXT,
                total_captures INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')

        # Alerts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                camera_id TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT,
                sent BOOLEAN DEFAULT 0
            )
        ''')

        self.conn.commit()
        print(f"✅ Database initialized: {self.db_path}")

    def log_detection(self, detection_result):
        """
        Log a pest detection result to the database
        """
        timestamp = detection_result.get('timestamp', datetime.now().isoformat())
        camera_id = detection_result.get('camera_id', 'UNKNOWN')
        location = detection_result.get('location', {})

        self.cursor.execute('''
            INSERT INTO detections (
                timestamp, camera_id, location_name, latitude, longitude,
                pest_count, risk_level, image_path, output_path,
                detection_params, pest_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp,
            camera_id,
            location.get('name', ''),
            location.get('latitude', 0.0),
            location.get('longitude', 0.0),
            detection_result['pest_count'],
            detection_result['risk_level'],
            detection_result.get('image_path', ''),
            detection_result.get('output_path', ''),
            json.dumps(detection_result.get('detection_params', {})),
            json.dumps(detection_result.get('pest_details', []))
        ))

        self.conn.commit()
        print(f"📝 Detection logged: {camera_id} - {detection_result['pest_count']} pests")

        # Update camera status
        self._update_camera_status(camera_id, location, timestamp)

        # Check if alert needed
        if detection_result['risk_level'] in ['MEDIUM', 'HIGH']:
            self._create_alert(camera_id, detection_result)

    def _update_camera_status(self, camera_id, location, timestamp):
        """Update camera status in the database"""
        self.cursor.execute('''
            INSERT INTO camera_status (camera_id, location_name, latitude, longitude, last_capture, total_captures)
            VALUES (?, ?, ?, ?, ?, 1)
            ON CONFLICT(camera_id) DO UPDATE SET
                last_capture = ?,
                total_captures = total_captures + 1
        ''', (
            camera_id,
            location.get('name', ''),
            location.get('latitude', 0.0),
            location.get('longitude', 0.0),
            timestamp,
            timestamp
        ))
        self.conn.commit()

    def _create_alert(self, camera_id, detection_result):
        """Create an alert for high pest activity"""
        alert_type = f"{detection_result['risk_level']}_RISK"
        message = f"{detection_result['pest_count']} pests detected at {detection_result.get('location', {}).get('name', camera_id)}"

        self.cursor.execute('''
            INSERT INTO alerts (timestamp, camera_id, alert_type, message, sent)
            VALUES (?, ?, ?, ?, 0)
        ''', (
            detection_result['timestamp'],
            camera_id,
            alert_type,
            message
        ))
        self.conn.commit()
        print(f"🚨 Alert created: {alert_type}")

    def get_recent_detections(self, camera_id=None, hours=24, limit=100):
        """Get recent detections for a specific camera or all cameras"""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        if camera_id:
            query = '''
                SELECT * FROM detections
                WHERE camera_id = ? AND timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            self.cursor.execute(query, (camera_id, cutoff_time, limit))
        else:
            query = '''
                SELECT * FROM detections
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT ?
            '''
            self.cursor.execute(query, (cutoff_time, limit))

        columns = [description[0] for description in self.cursor.description]
        results = []

        for row in self.cursor.fetchall():
            result = dict(zip(columns, row))
            # Parse JSON fields
            result['detection_params'] = json.loads(result['detection_params'])
            result['pest_details'] = json.loads(result['pest_details'])
            results.append(result)

        return results

    def get_statistics(self, camera_id=None, days=7):
        """Get summary statistics for pest activity"""
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

        if camera_id:
            query = '''
                SELECT
                    COUNT(*) as total_captures,
                    SUM(pest_count) as total_pests,
                    AVG(pest_count) as avg_pests,
                    MAX(pest_count) as max_pests,
                    MIN(pest_count) as min_pests
                FROM detections
                WHERE camera_id = ? AND timestamp > ?
            '''
            self.cursor.execute(query, (camera_id, cutoff_time))
        else:
            query = '''
                SELECT
                    COUNT(*) as total_captures,
                    SUM(pest_count) as total_pests,
                    AVG(pest_count) as avg_pests,
                    MAX(pest_count) as max_pests,
                    MIN(pest_count) as min_pests
                FROM detections
                WHERE timestamp > ?
            '''
            self.cursor.execute(query, (cutoff_time,))

        columns = [description[0] for description in self.cursor.description]
        row = self.cursor.fetchone()

        if row:
            stats = dict(zip(columns, row))
            stats['period_days'] = days
            stats['camera_id'] = camera_id or 'ALL'
            return stats

        return None

    def get_trend_analysis(self, camera_id=None, days=7):
        """Analyze pest trends over time"""
        cutoff_time = (datetime.now() - timedelta(days=days)).isoformat()

        if camera_id:
            query = '''
                SELECT
                    DATE(timestamp) as date,
                    COUNT(*) as captures,
                    SUM(pest_count) as total_pests,
                    AVG(pest_count) as avg_pests,
                    MAX(pest_count) as max_pests
                FROM detections
                WHERE camera_id = ? AND timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''
            self.cursor.execute(query, (camera_id, cutoff_time))
        else:
            query = '''
                SELECT
                    DATE(timestamp) as date,
                    COUNT(*) as captures,
                    SUM(pest_count) as total_pests,
                    AVG(pest_count) as avg_pests,
                    MAX(pest_count) as max_pests
                FROM detections
                WHERE timestamp > ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            '''
            self.cursor.execute(query, (cutoff_time,))

        columns = [description[0] for description in self.cursor.description]
        trends = []

        for row in self.cursor.fetchall():
            trends.append(dict(zip(columns, row)))

        return trends

    def get_all_cameras(self):
        """Get list of all registered cameras"""
        self.cursor.execute('SELECT * FROM camera_status')
        columns = [description[0] for description in self.cursor.description]
        cameras = []

        for row in self.cursor.fetchall():
            cameras.append(dict(zip(columns, row)))

        return cameras

    def get_pending_alerts(self):
        """Get alerts that haven't been sent yet"""
        self.cursor.execute('''
            SELECT * FROM alerts
            WHERE sent = 0
            ORDER BY timestamp DESC
        ''')

        columns = [description[0] for description in self.cursor.description]
        alerts = []

        for row in self.cursor.fetchall():
            alerts.append(dict(zip(columns, row)))

        return alerts

    def mark_alert_sent(self, alert_id):
        """Mark an alert as sent"""
        self.cursor.execute('''
            UPDATE alerts
            SET sent = 1
            WHERE id = ?
        ''', (alert_id,))
        self.conn.commit()

    def cleanup_old_data(self, keep_days=30):
        """Remove old detection records"""
        cutoff_time = (datetime.now() - timedelta(days=keep_days)).isoformat()

        self.cursor.execute('''
            DELETE FROM detections
            WHERE timestamp < ?
        ''', (cutoff_time,))

        deleted_count = self.cursor.rowcount
        self.conn.commit()

        print(f"🧹 Cleaned up {deleted_count} old records (older than {keep_days} days)")
        return deleted_count

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("🔒 Database connection closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# Test function
if __name__ == "__main__":
    print("🌱 Testing Data Logger Module")

    with DataLogger("../config.json") as logger:
        # Test data
        test_detection = {
            "timestamp": datetime.now().isoformat(),
            "camera_id": "CAM001",
            "location": {
                "name": "North Field - Zone A",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            "pest_count": 8,
            "risk_level": "HIGH",
            "image_path": "test.jpg",
            "output_path": "test_detected.jpg",
            "pest_details": [{"id": 1, "area": 150}]
        }

        # Log detection
        logger.log_detection(test_detection)

        # Get statistics
        stats = logger.get_statistics()
        print(f"\n📊 Statistics:")
        print(json.dumps(stats, indent=2))

        # Get cameras
        cameras = logger.get_all_cameras()
        print(f"\n📹 Cameras: {len(cameras)}")
