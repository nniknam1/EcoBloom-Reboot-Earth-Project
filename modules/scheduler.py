"""
Scheduler Module
Handles automated capture and detection scheduling
"""
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
import schedule

# Import our modules
try:
    from camera_capture import CameraCapture
    from pest_detector import PestDetector
    from data_logger import DataLogger
    from alert_system import AlertSystem
except ImportError:
    # If running from different directory
    import sys
    sys.path.append(str(Path(__file__).parent))
    from camera_capture import CameraCapture
    from pest_detector import PestDetector
    from data_logger import DataLogger
    from alert_system import AlertSystem


class PestMonitorScheduler:
    def __init__(self, config_path="config.json"):
        """Initialize scheduler with all components"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.config_path = config_path
        self.capture_interval = self.config['camera']['capture_interval_minutes']
        self.auto_start = self.config['camera']['auto_start']

        # Initialize components
        self.camera = None
        self.detector = PestDetector(config_path)
        self.logger = DataLogger(config_path)
        self.alerts = AlertSystem(config_path)

        self.running = False
        self.scheduler_thread = None

        print(f"🌱 Pest Monitor Scheduler initialized")
        print(f"📸 Capture interval: every {self.capture_interval} minutes")

    def capture_and_analyze(self):
        """
        Main function: capture image, detect pests, log results, send alerts
        This is the core automated workflow
        """
        print(f"\n{'='*60}")
        print(f"🔄 Starting automated capture and analysis...")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")

        try:
            # Step 1: Capture image
            print("\n1️⃣ Capturing image...")
            if self.camera is None:
                self.camera = CameraCapture(self.config_path)

            capture_metadata = self.camera.capture_image()

            if not capture_metadata:
                print("❌ Image capture failed")
                return

            print(f"✅ Image saved: {capture_metadata['image_path']}")

            # Step 2: Detect pests
            print("\n2️⃣ Analyzing image for pests...")
            detection_result = self.detector.detect_pests(
                capture_metadata['image_path'],
                capture_metadata
            )

            print(f"✅ Detection complete: {detection_result['pest_count']} pests, Risk: {detection_result['risk_level']}")

            # Step 3: Log to database
            print("\n3️⃣ Logging results to database...")
            self.logger.log_detection(detection_result)
            print("✅ Results logged")

            # Step 4: Send alerts if needed
            print("\n4️⃣ Processing alerts...")
            self.alerts.send_alert(detection_result)

            print(f"\n{'='*60}")
            print(f"✅ Automated cycle complete!")
            print(f"{'='*60}\n")

            return detection_result

        except Exception as e:
            print(f"\n❌ Error in capture/analysis cycle: {e}")
            return None

    def schedule_daily_summary(self):
        """Send daily summary report"""
        print("\n📊 Generating daily summary...")

        try:
            stats = self.logger.get_statistics(days=1)

            if stats:
                self.alerts.send_daily_summary(stats)
                print("✅ Daily summary sent")
            else:
                print("⚠️ No data available for summary")

        except Exception as e:
            print(f"❌ Error generating summary: {e}")

    def schedule_cleanup(self):
        """Clean up old data"""
        print("\n🧹 Cleaning up old data...")

        try:
            keep_days = self.config['storage']['keep_images_days']
            deleted = self.logger.cleanup_old_data(keep_days)
            print(f"✅ Cleanup complete: {deleted} records removed")

        except Exception as e:
            print(f"❌ Error during cleanup: {e}")

    def start(self):
        """Start the scheduler"""
        print("\n🚀 Starting Pest Monitor Scheduler...")

        # Set up schedules
        schedule.every(self.capture_interval).minutes.do(self.capture_and_analyze)

        # Daily summary at 6 AM
        schedule.every().day.at("06:00").do(self.schedule_daily_summary)

        # Weekly cleanup on Sundays at 2 AM
        schedule.every().sunday.at("02:00").do(self.schedule_cleanup)

        print(f"\n📋 Scheduled tasks:")
        print(f"  • Capture & Analyze: Every {self.capture_interval} minutes")
        print(f"  • Daily Summary: 6:00 AM")
        print(f"  • Database Cleanup: Sundays at 2:00 AM")

        # Run first capture immediately if auto_start is enabled
        if self.auto_start:
            print(f"\n🎬 Running initial capture...")
            self.capture_and_analyze()

        # Start scheduler loop
        self.running = True

        print(f"\n✅ Scheduler is running!")
        print(f"🛑 Press Ctrl+C to stop\n")

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)

        except KeyboardInterrupt:
            print("\n\n🛑 Stopping scheduler...")
            self.stop()

    def start_background(self):
        """Start scheduler in background thread"""
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            print("⚠️ Scheduler already running")
            return

        self.scheduler_thread = threading.Thread(target=self.start, daemon=True)
        self.scheduler_thread.start()
        print("✅ Scheduler started in background")

    def stop(self):
        """Stop the scheduler"""
        self.running = False

        if self.camera:
            self.camera.cleanup()

        self.logger.close()

        print("✅ Scheduler stopped")

    def run_manual_cycle(self):
        """Manually trigger a capture/analysis cycle"""
        print("\n🖐️ Manual cycle triggered...")
        return self.capture_and_analyze()

    def get_status(self):
        """Get scheduler status and recent activity"""
        cameras = self.logger.get_all_cameras()
        recent = self.logger.get_recent_detections(hours=24, limit=10)
        stats = self.logger.get_statistics(days=7)

        status = {
            "running": self.running,
            "capture_interval_minutes": self.capture_interval,
            "registered_cameras": len(cameras),
            "cameras": cameras,
            "recent_detections": len(recent),
            "last_detection": recent[0] if recent else None,
            "weekly_stats": stats
        }

        return status


# Main execution
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='EcoBloom Pest Detection Scheduler')
    parser.add_argument('--config', default='../config.json', help='Path to config file')
    parser.add_argument('--manual', action='store_true', help='Run single manual cycle')
    parser.add_argument('--status', action='store_true', help='Show status and exit')

    args = parser.parse_args()

    # Initialize scheduler
    scheduler = PestMonitorScheduler(args.config)

    if args.status:
        # Show status
        status = scheduler.get_status()
        print(json.dumps(status, indent=2))

    elif args.manual:
        # Run manual cycle
        result = scheduler.run_manual_cycle()
        if result:
            print("\n✅ Manual cycle complete")

    else:
        # Start automated scheduling
        scheduler.start()
